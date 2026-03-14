/**
 * ACQUISITOR API Types
 * Type-safe definitions for all API responses
 */

// Lead/Company Types
export interface Lead {
  id: string;
  name: string;
  industry: string;
  size: 'small' | 'medium' | 'large';
  revenue: number;
  employees: number;
  location: {
    city: string;
    state: string;
    country: string;
  };
  contact: {
    email: string;
    phone?: string;
    linkedin?: string;
  };
  score: number; // 0-100
  status: 'new' | 'approved' | 'rejected' | 'watchlist';
  source: string;
  discoveredAt: string;
  lastActivityAt: string;
  tags: string[];
  description?: string;
  website?: string;
  valuation?: number;
}

export interface LeadDetail extends Lead {
  notes: Note[];
  activities: Activity[];
  documents: Document[];
  competitors: string[];
  financials?: {
    revenue: number;
    ebitda: number;
    growth: number;
  };
}

export interface Note {
  id: string;
  content: string;
  createdAt: string;
  createdBy: string;
}

export interface Document {
  id: string;
  name: string;
  type: string;
  url: string;
  uploadedAt: string;
}

// Pipeline Types
export type PipelineStage = 'NEW' | 'OUTREACH' | 'ENGAGED' | 'QUALIFIED' | 'BOOKED' | 'CLOSED_WON' | 'CLOSED_LOST';

export interface PipelineLead {
  id: string;
  leadId: string;
  name: string;
  score: number;
  stage: PipelineStage;
  lastActivityAt: string;
  assignedTo?: string;
  priority: 'low' | 'medium' | 'high';
  value?: number;
}

export interface PipelineColumn {
  stage: PipelineStage;
  name: string;
  leads: PipelineLead[];
}

// Activity Types
export interface Activity {
  id: string;
  type: 'lead_discovered' | 'lead_approved' | 'lead_rejected' | 'email_sent' | 'email_opened' | 'email_replied' | 'call_scheduled' | 'call_completed' | 'stage_changed' | 'note_added';
  leadId: string;
  leadName: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
  actor: string;
}

// Metrics Types
export interface OutreachMetrics {
  emailsSent: number;
  emailsOpened: number;
  emailsReplied: number;
  openRate: number;
  replyRate: number;
  period: string;
}

export interface DashboardMetrics {
  totalLeads: number;
  leadsInPipeline: number;
  callsBookedThisWeek: number;
  callsBookedThisMonth: number;
  conversionRate: number;
  averageDealSize: number;
  outreach: OutreachMetrics;
}

// Booking Types
export interface Booking {
  id: string;
  leadId: string;
  leadName: string;
  scheduledAt: string;
  duration: number; // minutes
  type: 'intro' | 'followup' | 'demo' | 'negotiation';
  status: 'scheduled' | 'completed' | 'cancelled' | 'noshow';
  notes?: string;
  calendarLink?: string;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
  meta?: {
    page?: number;
    limit?: number;
    total?: number;
    hasMore?: boolean;
  };
}

export interface ApiError {
  success: false;
  error: string;
  code: string;
  details?: Record<string, string[]>;
}

// Search/Filter Types
export interface LeadFilters {
  search?: string;
  industry?: string;
  size?: string;
  status?: string;
  minScore?: number;
  maxScore?: number;
  location?: string;
  tags?: string[];
}

export interface PaginationParams {
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// INTAKE Module Types
export interface BuyerProfile {
  background: string;
  industries: string[];
  roles: string[];
  acquisitionExperience: 'first-time' | 'experienced';
  motivation: string;
  values: string[];
  locationPreference: string[];
  teamPreference: 'retain' | 'replace' | 'either';
  growthApproach: 'growth' | 'stable';
  budget: { min: number; max: number };
  revenueRange: { min: number; max: number };
  employeeRange: { min: number; max: number };
  financingType: 'cash' | 'financed' | 'sba';
  sdeMultiple: number;
}

export interface SearchCriteria {
  industries: string[];
  excludedIndustries: string[];
  revenueRange: { min: number; max: number };
  employeeRange: { min: number; max: number };
  locationPreference: string[];
  businessAge: { min: number; max: number };
  ownerSituation: string[];
  keywords: string[];
  sdeMultiple: number;
}

export interface OutreachSettings {
  dailyDiscovery: boolean;
  autoOutreach: boolean;
  responseHandling: boolean;
  bookingEnabled: boolean;
}

export interface ActivationRequest {
  criteria: SearchCriteria;
  leads: any[];
  settings: OutreachSettings;
}
