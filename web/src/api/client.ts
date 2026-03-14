/**
 * ACQUISITOR API Client
 * Type-safe fetch wrapper with error handling and retries
 */

import type { 
  Lead, 
  LeadDetail, 
  PipelineLead, 
  PipelineStage,
  Activity, 
  DashboardMetrics, 
  Booking,
  LeadFilters,
  PaginationParams,
  ApiResponse,
  ApiError 
} from '../types';
import { mockLeads, mockPipelineLeads, mockActivities, mockMetrics, mockBookings, getMockLeadDetail } from '../data/mock';

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';
const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true' || true; // Default to true for demo

// Default request timeout (ms)
const DEFAULT_TIMEOUT = 30000;

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

// Custom error class for API errors
export class ApiClientError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public code?: string,
    public details?: Record<string, string[]>
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

// Helper to delay between retries
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Type guard for ApiError
function isApiError(data: unknown): data is ApiError {
  return (
    typeof data === 'object' &&
    data !== null &&
    'success' in data &&
    data.success === false &&
    'error' in data
  );
}

// Main fetch wrapper with retries and error handling
async function fetchWithRetry<T>(
  url: string,
  options: RequestInit = {},
  retries = MAX_RETRIES
): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
    });

    clearTimeout(timeoutId);

    // Parse response body
    let data: unknown;
    const contentType = response.headers.get('content-type');
    if (contentType?.includes('application/json')) {
      data = await response.json();
    } else {
      data = { success: false, error: await response.text() };
    }

    // Handle HTTP errors
    if (!response.ok) {
      // Check for retryable errors
      if (
        retries > 0 &&
        (response.status === 429 || // Rate limit
          response.status >= 500 || // Server errors
          response.status === 408) // Timeout
      ) {
        await delay(RETRY_DELAY * (MAX_RETRIES - retries + 1));
        return fetchWithRetry<T>(url, options, retries - 1);
      }

      if (isApiError(data)) {
        throw new ApiClientError(
          data.error,
          response.status,
          data.code,
          data.details
        );
      }

      throw new ApiClientError(
        `HTTP Error ${response.status}: ${response.statusText}`,
        response.status
      );
    }

    return data as T;
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle network errors with retry
    if (
      retries > 0 &&
      (error instanceof TypeError || // Network error
        error instanceof DOMException) // Abort error
    ) {
      await delay(RETRY_DELAY * (MAX_RETRIES - retries + 1));
      return fetchWithRetry<T>(url, options, retries - 1);
    }

    // Re-throw API client errors
    if (error instanceof ApiClientError) {
      throw error;
    }

    // Wrap unknown errors
    throw new ApiClientError(
      error instanceof Error ? error.message : 'Unknown error occurred'
    );
  }
}

// Build query string from filters and pagination
function buildQueryString(
  filters?: LeadFilters,
  pagination?: PaginationParams
): string {
  const params = new URLSearchParams();

  if (filters) {
    if (filters.search) params.set('search', filters.search);
    if (filters.industry) params.set('industry', filters.industry);
    if (filters.size) params.set('size', filters.size);
    if (filters.status) params.set('status', filters.status);
    if (filters.minScore !== undefined) params.set('minScore', String(filters.minScore));
    if (filters.maxScore !== undefined) params.set('maxScore', String(filters.maxScore));
    if (filters.location) params.set('location', filters.location);
    if (filters.tags?.length) params.set('tags', filters.tags.join(','));
  }

  if (pagination) {
    if (pagination.page !== undefined) params.set('page', String(pagination.page));
    if (pagination.limit !== undefined) params.set('limit', String(pagination.limit));
    if (pagination.sortBy) params.set('sortBy', pagination.sortBy);
    if (pagination.sortOrder) params.set('sortOrder', pagination.sortOrder);
  }

  const query = params.toString();
  return query ? `?${query}` : '';
}

// API Client methods
export const apiClient = {
  // Health check
  health: async (): Promise<{ status: string; services: { database: string; redis: string } }> => {
    if (USE_MOCK_DATA) {
      return { status: 'healthy', services: { database: 'connected', redis: 'connected' } };
    }
    const response = await fetchWithRetry<ApiResponse<{ status: string; services: { database: string; redis: string } }>>(
      `${API_BASE_URL}/health`
    );
    return response.data;
  },

  // Leads
  getLeads: async (
    filters?: LeadFilters,
    pagination?: PaginationParams
  ): Promise<{ leads: Lead[]; meta: { page: number; limit: number; total: number; hasMore: boolean } }> => {
    if (USE_MOCK_DATA) {
      let filtered = [...mockLeads];
      
      // Apply filters
      if (filters?.search) {
        const search = filters.search.toLowerCase();
        filtered = filtered.filter(l => 
          l.name.toLowerCase().includes(search) ||
          l.industry.toLowerCase().includes(search)
        );
      }
      if (filters?.industry && filters.industry !== 'All') {
        filtered = filtered.filter(l => l.industry === filters.industry);
      }
      if (filters?.status && filters.status !== 'All') {
        filtered = filtered.filter(l => l.status === filters.status);
      }
      if (filters?.minScore !== undefined) {
        filtered = filtered.filter(l => l.score >= filters.minScore!);
      }
      
      // Apply sorting
      const sortBy = pagination?.sortBy || 'score';
      const sortOrder = pagination?.sortOrder || 'desc';
      filtered.sort((a, b) => {
        const aVal = a[sortBy as keyof Lead];
        const bVal = b[sortBy as keyof Lead];
        if (sortOrder === 'desc') return (bVal as number) - (aVal as number);
        return (aVal as number) - (bVal as number);
      });
      
      const page = pagination?.page || 1;
      const limit = pagination?.limit || 12;
      const start = (page - 1) * limit;
      const paginated = filtered.slice(start, start + limit);
      
      return {
        leads: paginated,
        meta: { page, limit, total: filtered.length, hasMore: start + limit < filtered.length }
      };
    }
    
    const query = buildQueryString(filters, pagination);
    const response = await fetchWithRetry<ApiResponse<Lead[]>>(
      `${API_BASE_URL}/api/scout/leads${query}`
    );
    return {
      leads: response.data,
      meta: {
        page: response.meta?.page ?? 1,
        limit: response.meta?.limit ?? 20,
        total: response.meta?.total ?? 0,
        hasMore: response.meta?.hasMore ?? false,
      },
    };
  },

  getLeadById: async (id: string): Promise<LeadDetail> => {
    if (USE_MOCK_DATA) {
      const leadDetail = getMockLeadDetail(id);
      if (!leadDetail) throw new ApiClientError('Lead not found', 404);
      return leadDetail;
    }
    const response = await fetchWithRetry<ApiResponse<LeadDetail>>(
      `${API_BASE_URL}/api/scout/leads/${id}`
    );
    return response.data;
  },

  updateLeadStatus: async (
    id: string,
    status: Lead['status']
  ): Promise<Lead> => {
    if (USE_MOCK_DATA) {
      const lead = mockLeads.find(l => l.id === id);
      if (!lead) throw new ApiClientError('Lead not found', 404);
      lead.status = status;
      return lead;
    }
    const response = await fetchWithRetry<ApiResponse<Lead>>(
      `${API_BASE_URL}/api/scout/leads/${id}/status`,
      {
        method: 'PATCH',
        body: JSON.stringify({ status }),
      }
    );
    return response.data;
  },

  approveLead: async (id: string): Promise<Lead> => {
    return apiClient.updateLeadStatus(id, 'approved');
  },

  rejectLead: async (id: string): Promise<Lead> => {
    return apiClient.updateLeadStatus(id, 'rejected');
  },

  addToWatchlist: async (id: string): Promise<Lead> => {
    return apiClient.updateLeadStatus(id, 'watchlist');
  },

  // Pipeline
  getPipeline: async (): Promise<PipelineLead[]> => {
    if (USE_MOCK_DATA) {
      return mockPipelineLeads;
    }
    const response = await fetchWithRetry<ApiResponse<PipelineLead[]>>(
      `${API_BASE_URL}/api/pipeline`
    );
    return response.data;
  },

  moveLeadStage: async (
    leadId: string,
    stage: PipelineStage
  ): Promise<PipelineLead> => {
    if (USE_MOCK_DATA) {
      const lead = mockPipelineLeads.find(l => l.id === leadId);
      if (!lead) throw new ApiClientError('Lead not found', 404);
      lead.stage = stage;
      lead.lastActivityAt = new Date().toISOString();
      return lead;
    }
    const response = await fetchWithRetry<ApiResponse<PipelineLead>>(
      `${API_BASE_URL}/api/pipeline/${leadId}/stage`,
      {
        method: 'PATCH',
        body: JSON.stringify({ stage }),
      }
    );
    return response.data;
  },

  // Activity
  getActivities: async (limit = 20): Promise<Activity[]> => {
    if (USE_MOCK_DATA) {
      return mockActivities.slice(0, limit);
    }
    const response = await fetchWithRetry<ApiResponse<Activity[]>>(
      `${API_BASE_URL}/api/activity?limit=${limit}`
    );
    return response.data;
  },

  // Metrics
  getMetrics: async (): Promise<DashboardMetrics> => {
    if (USE_MOCK_DATA) {
      return mockMetrics;
    }
    const response = await fetchWithRetry<ApiResponse<DashboardMetrics>>(
      `${API_BASE_URL}/api/metrics`
    );
    return response.data;
  },

  // Bookings
  getBookings: async (upcoming = true): Promise<Booking[]> => {
    if (USE_MOCK_DATA) {
      if (upcoming) {
        return mockBookings.filter(b => new Date(b.scheduledAt) > new Date());
      }
      return mockBookings;
    }
    const response = await fetchWithRetry<ApiResponse<Booking[]>>(
      `${API_BASE_URL}/api/bookings?upcoming=${upcoming}`
    );
    return response.data;
  },

  createBooking: async (booking: Omit<Booking, 'id'>): Promise<Booking> => {
    if (USE_MOCK_DATA) {
      const newBooking = { ...booking, id: String(mockBookings.length + 1) };
      mockBookings.push(newBooking);
      return newBooking;
    }
    const response = await fetchWithRetry<ApiResponse<Booking>>(
      `${API_BASE_URL}/api/bookings`,
      {
        method: 'POST',
        body: JSON.stringify(booking),
      }
    );
    return response.data;
  },

  // INTAKE - Activate autonomous outreach
  activateOutreach: async (request: any): Promise<{ success: boolean; message: string }> => {
    if (USE_MOCK_DATA) {
      // Simulate successful activation
      console.log('🤖 Automation activated:', request);
      return {
        success: true,
        message: 'Autonomous outreach activated successfully'
      };
    }
    const response = await fetchWithRetry<ApiResponse<{ success: boolean; message: string }>>(
      `${API_BASE_URL}/api/intake/activate`,
      {
        method: 'POST',
        body: JSON.stringify(request),
      }
    );
    return response.data;
  },
};

// Export base URL for WebSocket connections
export { API_BASE_URL };
