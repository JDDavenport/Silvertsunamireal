import type { Lead, LeadDetail, PipelineLead, Activity, DashboardMetrics, Booking } from '../types';

// Mock leads matching REAL database from Telegram bot
export const mockLeads: Lead[] = [
  {
    id: 'lead_001',
    name: 'Alpine Auto Repair',
    industry: 'Automotive',
    size: 'medium',
    revenue: 1200000,
    employees: 8,
    location: { city: 'Salt Lake City', state: 'UT', country: 'USA' },
    contact: { email: 'owner@alpineautorepair.com' },
    score: 0,
    status: 'new',
    source: 'BizBuySell',
    discoveredAt: '2026-03-14T17:30:00Z',
    lastActivityAt: '2026-03-14T17:30:00Z',
    tags: ['automotive', 'repair', 'established'],
    description: 'Established auto repair shop with loyal customer base. Owner retiring after 25 years.',
    website: 'https://alpineautorepair.com',
    valuation: 3600000
  },
  {
    id: 'lead_002',
    name: 'Summit Dental Practice',
    industry: 'Healthcare',
    size: 'medium',
    revenue: 2800000,
    employees: 12,
    location: { city: 'Park City', state: 'UT', country: 'USA' },
    contact: { email: 'owner@summitdental.com' },
    score: 0,
    status: 'new',
    source: 'BizBuySell',
    discoveredAt: '2026-03-14T17:30:00Z',
    lastActivityAt: '2026-03-14T17:30:00Z',
    tags: ['healthcare', 'dental', 'profitable'],
    description: 'Profitable dental practice in growing area. Steady patient flow.',
    valuation: 8400000
  },
  {
    id: 'lead_003',
    name: 'TechFlow Solutions',
    industry: 'Technology',
    size: 'medium',
    revenue: 2750000,
    employees: 18,
    location: { city: 'Salt Lake City', state: 'UT', country: 'USA' },
    contact: { email: 'sarah@techflowsolutions.com', linkedin: 'linkedin.com/in/sarahchen' },
    score: 0,
    status: 'new',
    source: 'LinkedIn',
    discoveredAt: '2026-03-14T17:30:00Z',
    lastActivityAt: '2026-03-14T17:30:00Z',
    tags: ['saas', 'b2b', 'recurring-revenue', 'high-margin'],
    description: 'SaaS business with 85% recurring revenue. Serial entrepreneur founders.',
    website: 'https://techflowsolutions.com',
    valuation: 8500000
  }
];

// Mock pipeline leads
export const mockPipelineLeads: PipelineLead[] = [
  {
    id: '101',
    leadId: 'lead_001',
    name: 'Alpine Auto Repair',
    score: 0,
    stage: 'NEW',
    lastActivityAt: '2026-03-14T17:30:00Z',
    priority: 'medium',
    value: 3600000
  },
  {
    id: '102',
    leadId: 'lead_002',
    name: 'Summit Dental Practice',
    score: 0,
    stage: 'NEW',
    lastActivityAt: '2026-03-14T17:30:00Z',
    priority: 'high',
    value: 8400000
  },
  {
    id: '103',
    leadId: 'lead_003',
    name: 'TechFlow Solutions',
    score: 0,
    stage: 'NEW',
    lastActivityAt: '2026-03-14T17:30:00Z',
    priority: 'high',
    value: 8500000
  }
];

// Mock activities
export const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'lead_discovered',
    leadId: 'lead_001',
    leadName: 'Alpine Auto Repair',
    timestamp: '2026-03-14T17:30:00Z',
    actor: 'system',
    metadata: { source: 'BizBuySell', auto: true }
  },
  {
    id: '2',
    type: 'lead_discovered',
    leadId: 'lead_002',
    leadName: 'Summit Dental Practice',
    timestamp: '2026-03-14T17:30:00Z',
    actor: 'system',
    metadata: { source: 'BizBuySell', auto: true }
  },
  {
    id: '3',
    type: 'lead_discovered',
    leadId: 'lead_003',
    leadName: 'TechFlow Solutions',
    timestamp: '2026-03-14T17:30:00Z',
    actor: 'system',
    metadata: { source: 'LinkedIn', auto: true }
  }
];

// Mock dashboard metrics - synced with real database
export const mockMetrics: DashboardMetrics = {
  totalLeads: 3,
  leadsInPipeline: 0,
  callsBookedThisWeek: 0,
  callsBookedThisMonth: 0,
  conversionRate: 0,
  averageDealSize: 6833333,
  outreach: {
    emailsSent: 0,
    emailsOpened: 0,
    emailsReplied: 0,
    openRate: 0,
    replyRate: 0,
    period: 'last_7_days'
  }
};

// Mock bookings
export const mockBookings: Booking[] = [];

// Generate lead detail with extended info
export function getMockLeadDetail(id: string): LeadDetail | undefined {
  const lead = mockLeads.find(l => l.id === id);
  if (!lead) return undefined;
  
  return {
    ...lead,
    notes: [],
    activities: mockActivities.filter(a => a.leadId === id),
    documents: [],
    competitors: [],
    financials: {
      revenue: lead.revenue,
      ebitda: Math.floor(lead.revenue * 0.22),
      growth: 12
    }
  };
}
