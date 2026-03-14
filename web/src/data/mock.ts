import type { Lead, LeadDetail, PipelineLead, Activity, DashboardMetrics, Booking, PipelineStage } from '../types';

// Mock leads for demo
export const mockLeads: Lead[] = [
  {
    id: '1',
    name: 'Mountain Valley Plumbing',
    industry: 'Services',
    size: 'medium',
    revenue: 1350000,
    employees: 10,
    location: { city: 'Provo', state: 'UT', country: 'USA' },
    contact: { email: 'david@mountainvalleyplumbing.com', phone: '801-555-0101' },
    score: 84,
    status: 'approved',
    source: 'BizBuySell',
    discoveredAt: '2026-03-14T06:00:00Z',
    lastActivityAt: '2026-03-14T14:30:00Z',
    tags: ['plumbing', 'hvac', 'recurring-revenue'],
    description: 'Established plumbing business with consistent revenue and owner looking to retire. Strong local reputation and recurring maintenance contracts.',
    website: 'https://mountainvalleyplumbing.com',
    valuation: 4200000
  },
  {
    id: '2',
    name: 'TechFlow Solutions',
    industry: 'Technology',
    size: 'medium',
    revenue: 2750000,
    employees: 18,
    location: { city: 'Salt Lake City', state: 'UT', country: 'USA' },
    contact: { email: 'sarah@techflowsolutions.com', phone: '801-555-0102', linkedin: 'linkedin.com/in/sarahchen' },
    score: 91,
    status: 'new',
    source: 'LinkedIn',
    discoveredAt: '2026-03-14T06:15:00Z',
    lastActivityAt: '2026-03-14T09:00:00Z',
    tags: ['saas', 'b2b', 'recurring-revenue', 'high-margin'],
    description: 'High-margin SaaS business with 85% recurring revenue. Founders are serial entrepreneurs looking to exit.',
    website: 'https://techflowsolutions.com',
    valuation: 8500000
  },
  {
    id: '3',
    name: 'Premier Home Healthcare',
    industry: 'Healthcare',
    size: 'large',
    revenue: 3500000,
    employees: 50,
    location: { city: 'Lehi', state: 'UT', country: 'USA' },
    contact: { email: 'jennifer@premierhomehealth.com', phone: '801-555-0103' },
    score: 76,
    status: 'watchlist',
    source: 'State Registry',
    discoveredAt: '2026-03-14T06:30:00Z',
    lastActivityAt: '2026-03-14T08:00:00Z',
    tags: ['healthcare', 'medicare', 'aging-population'],
    description: 'Growing healthcare business serving aging population. Medicare-certified with strong referral network.',
    valuation: 10500000
  },
  {
    id: '4',
    name: 'Rocky Mountain Manufacturing',
    industry: 'Manufacturing',
    size: 'large',
    revenue: 4850000,
    employees: 28,
    location: { city: 'Ogden', state: 'UT', country: 'USA' },
    contact: { email: 'mike@rmmfg.com', phone: '801-555-0104' },
    score: 68,
    status: 'rejected',
    source: 'BizBuySell',
    discoveredAt: '2026-03-13T16:00:00Z',
    lastActivityAt: '2026-03-13T16:00:00Z',
    tags: ['manufacturing', 'aerospace', 'capital-intensive'],
    description: 'Established manufacturer with diverse customer base. Strong relationships with aerospace and defense contractors.',
    valuation: 15000000
  },
  {
    id: '5',
    name: 'Green Valley Landscaping',
    industry: 'Services',
    size: 'small',
    revenue: 975000,
    employees: 15,
    location: { city: 'St. George', state: 'UT', country: 'USA' },
    contact: { email: 'tom@greenvalleylandscaping.com', phone: '435-555-0105' },
    score: 72,
    status: 'new',
    source: 'Google Maps',
    discoveredAt: '2026-03-14T07:00:00Z',
    lastActivityAt: '2026-03-14T10:00:00Z',
    tags: ['landscaping', 'seasonal', 'outdoor-services'],
    description: 'Recurring revenue model with annual maintenance contracts. Owner retiring after 20 years.',
    valuation: 2900000
  },
  {
    id: '6',
    name: 'DataSync Analytics',
    industry: 'Technology',
    size: 'medium',
    revenue: 2000000,
    employees: 12,
    location: { city: 'Park City', state: 'UT', country: 'USA' },
    contact: { email: 'michael@datasync.io', phone: '435-555-0106', linkedin: 'linkedin.com/in/michaeltorres' },
    score: 88,
    status: 'approved',
    source: 'Industry Directory',
    discoveredAt: '2026-03-14T07:15:00Z',
    lastActivityAt: '2026-03-14T11:45:00Z',
    tags: ['data-analytics', 'b2b', 'consulting', 'high-margin'],
    description: 'High-margin data analytics firm with Fortune 500 clients. Strong technical team in place.',
    website: 'https://datasync.io',
    valuation: 6800000
  }
];

// Mock pipeline leads
export const mockPipelineLeads: PipelineLead[] = [
  {
    id: '101',
    leadId: '1',
    name: 'Mountain Valley Plumbing',
    score: 84,
    stage: 'QUALIFIED' as PipelineStage,
    lastActivityAt: '2026-03-14T14:30:00Z',
    priority: 'high',
    value: 4200000
  },
  {
    id: '102',
    leadId: '2',
    name: 'TechFlow Solutions',
    score: 91,
    stage: 'OUTREACH' as PipelineStage,
    lastActivityAt: '2026-03-14T09:00:00Z',
    priority: 'high',
    value: 8500000
  },
  {
    id: '103',
    leadId: '6',
    name: 'DataSync Analytics',
    score: 88,
    stage: 'ENGAGED' as PipelineStage,
    lastActivityAt: '2026-03-14T11:45:00Z',
    priority: 'high',
    value: 6800000
  },
  {
    id: '104',
    leadId: '3',
    name: 'Premier Home Healthcare',
    score: 76,
    stage: 'NEW' as PipelineStage,
    lastActivityAt: '2026-03-14T08:00:00Z',
    priority: 'medium',
    value: 10500000
  },
  {
    id: '105',
    leadId: '201',
    name: 'Summit Financial Advisors',
    score: 82,
    stage: 'BOOKED' as PipelineStage,
    lastActivityAt: '2026-03-14T10:15:00Z',
    priority: 'high',
    value: 6500000
  }
];

// Mock activities
export const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'email_sent',
    leadId: '2',
    leadName: 'TechFlow Solutions',
    timestamp: '2026-03-14T09:00:00Z',
    actor: 'system',
    metadata: { sequence: 'A', step: 1, subject: 'Question about TechFlow Solutions' }
  },
  {
    id: '2',
    type: 'email_replied',
    leadId: '1',
    leadName: 'Mountain Valley Plumbing',
    timestamp: '2026-03-14T14:30:00Z',
    actor: 'david@mountainvalleyplumbing.com',
    metadata: { sentiment: 'positive', classification: 'INTERESTED' }
  },
  {
    id: '3',
    type: 'lead_discovered',
    leadId: '2',
    leadName: 'TechFlow Solutions',
    timestamp: '2026-03-14T06:15:00Z',
    actor: 'system',
    metadata: { source: 'LinkedIn', score: 91 }
  },
  {
    id: '4',
    type: 'lead_approved',
    leadId: '6',
    leadName: 'DataSync Analytics',
    timestamp: '2026-03-14T07:30:00Z',
    actor: 'JD',
    metadata: { score: 88 }
  },
  {
    id: '5',
    type: 'call_scheduled',
    leadId: '201',
    leadName: 'Summit Financial Advisors',
    timestamp: '2026-03-14T10:15:00Z',
    actor: 'system',
    metadata: { scheduledAt: '2026-03-17T15:00:00Z', duration: 30 }
  },
  {
    id: '6',
    type: 'email_sent',
    leadId: '5',
    leadName: 'Green Valley Landscaping',
    timestamp: '2026-03-14T10:00:00Z',
    actor: 'system',
    metadata: { sequence: 'A', step: 3 }
  }
];

// Mock dashboard metrics
export const mockMetrics: DashboardMetrics = {
  totalLeads: 156,
  leadsInPipeline: 24,
  callsBookedThisWeek: 3,
  callsBookedThisMonth: 12,
  conversionRate: 6.4,
  averageDealSize: 5200000,
  outreach: {
    emailsSent: 47,
    emailsOpened: 31,
    emailsReplied: 8,
    openRate: 66,
    replyRate: 17,
    period: 'last_7_days'
  }
};

// Mock bookings
export const mockBookings: Booking[] = [
  {
    id: '1',
    leadId: '201',
    leadName: 'Summit Financial Advisors',
    scheduledAt: '2026-03-17T15:00:00Z',
    duration: 30,
    type: 'intro',
    status: 'scheduled',
    notes: 'Discovery call - prepare CIM overview',
    calendarLink: 'https://cal.com/jd/discovery-call'
  },
  {
    id: '2',
    leadId: '202',
    leadName: 'Alpine Logistics',
    scheduledAt: '2026-03-18T10:00:00Z',
    duration: 30,
    type: 'followup',
    status: 'scheduled',
    notes: 'Second call - discuss valuation expectations'
  },
  {
    id: '3',
    leadId: '203',
    leadName: 'Pioneer Construction',
    scheduledAt: '2026-03-19T14:00:00Z',
    duration: 45,
    type: 'intro',
    status: 'scheduled',
    notes: 'Initial discovery - high priority lead'
  }
];

// Generate lead detail with extended info
export function getMockLeadDetail(id: string): LeadDetail | undefined {
  const lead = mockLeads.find(l => l.id === id);
  if (!lead) return undefined;
  
  return {
    ...lead,
    notes: [
      { id: '1', content: 'Owner looking to retire in 12-18 months', createdAt: '2026-03-14T08:00:00Z', createdBy: 'system' },
      { id: '2', content: 'Strong recurring revenue from maintenance contracts', createdAt: '2026-03-14T08:05:00Z', createdBy: 'system' }
    ],
    activities: mockActivities.filter(a => a.leadId === id),
    documents: [
      { id: '1', name: 'CIM_2026.pdf', type: 'pdf', url: '#', uploadedAt: '2026-03-14T06:00:00Z' }
    ],
    competitors: ['Regional Plumbing Inc', 'Citywide HVAC'],
    financials: {
      revenue: lead.revenue,
      ebitda: Math.floor(lead.revenue * 0.22),
      growth: 12
    }
  };
}
