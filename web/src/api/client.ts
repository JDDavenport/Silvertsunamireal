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

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

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
    const response = await fetchWithRetry<ApiResponse<LeadDetail>>(
      `${API_BASE_URL}/api/scout/leads/${id}`
    );
    return response.data;
  },

  updateLeadStatus: async (
    id: string,
    status: Lead['status']
  ): Promise<Lead> => {
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
    const response = await fetchWithRetry<ApiResponse<PipelineLead[]>>(
      `${API_BASE_URL}/api/pipeline`
    );
    return response.data;
  },

  moveLeadStage: async (
    leadId: string,
    stage: PipelineStage
  ): Promise<PipelineLead> => {
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
    const response = await fetchWithRetry<ApiResponse<Activity[]>>(
      `${API_BASE_URL}/api/activity?limit=${limit}`
    );
    return response.data;
  },

  // Metrics
  getMetrics: async (): Promise<DashboardMetrics> => {
    const response = await fetchWithRetry<ApiResponse<DashboardMetrics>>(
      `${API_BASE_URL}/api/metrics`
    );
    return response.data;
  },

  // Bookings
  getBookings: async (upcoming = true): Promise<Booking[]> => {
    const response = await fetchWithRetry<ApiResponse<Booking[]>>(
      `${API_BASE_URL}/api/bookings?upcoming=${upcoming}`
    );
    return response.data;
  },

  createBooking: async (booking: Omit<Booking, 'id'>): Promise<Booking> => {
    const response = await fetchWithRetry<ApiResponse<Booking>>(
      `${API_BASE_URL}/api/bookings`,
      {
        method: 'POST',
        body: JSON.stringify(booking),
      }
    );
    return response.data;
  },
};

// Export base URL for WebSocket connections
export { API_BASE_URL };
