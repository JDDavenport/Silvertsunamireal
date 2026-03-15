import { http, HttpResponse } from 'msw';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Mock data
const mockLeads = [
  {
    id: 'lead-1',
    name: 'ABC Technology LLC',
    industry: 'Technology',
    revenue: 2500000,
    employees: 25,
    city: 'Salt Lake City',
    state: 'UT',
    description: 'A well-established technology company serving enterprise clients for over 15 years.',
    score: 85,
    status: 'new',
    email: 'contact@abctech.com',
    phone: '(801) 555-0101',
    source: 'Utah Division of Corporations',
    ai_assessment: {
      score: 85,
      assessment: 'Strong technology company with established client base. Revenue is stable and the owner appears to be approaching retirement age.',
      reasons: [
        '15+ years in business',
        'Strong revenue ($2.5M)',
        'Technology sector matches your criteria',
        'Located in target area (Utah)'
      ],
      risks: [
        'High employee count may indicate owner-dependent operations',
        'Technology sector can be volatile'
      ]
    }
  },
  {
    id: 'lead-2',
    name: 'Summit Services Inc',
    industry: 'Services',
    revenue: 1800000,
    employees: 12,
    city: 'Provo',
    state: 'UT',
    description: 'Professional services firm specializing in business consulting.',
    score: 72,
    status: 'new',
    email: 'info@summitservices.com',
    source: 'BizBuySell',
    ai_assessment: {
      score: 72,
      assessment: 'Established service business with consistent revenue. Owner looking to retire within 2 years.',
      reasons: [
        '12 years operational history',
        'Recurring revenue model',
        'Owner retirement timeline aligns with your goals'
      ],
      risks: [
        'Service businesses can be owner-dependent',
        'Lower revenue than target range'
      ]
    }
  },
  {
    id: 'lead-3',
    name: 'Peak Manufacturing',
    industry: 'Manufacturing',
    revenue: 5200000,
    employees: 48,
    city: 'Ogden',
    state: 'UT',
    description: 'Custom manufacturing facility with strong regional presence.',
    score: 91,
    status: 'approved',
    email: 'sales@peakmanufacturing.com',
    source: 'Directory',
    ai_assessment: {
      score: 91,
      assessment: 'Excellent manufacturing opportunity with strong financials and established operations.',
      reasons: [
        'High revenue ($5.2M)',
        '20+ years in business',
        'Diversified client base',
        'Real estate included'
      ],
      risks: [
        'Manufacturing requires significant capital investment',
        'Equipment may need updates'
      ]
    }
  }
];

const mockUser = {
  id: 'test-user-id',
  email: 'test@example.com',
  name: 'Test User',
  agent_config: {
    daily_email_limit: 25,
    auto_approve_threshold: 0,
    discovery_frequency: 'daily'
  }
};

const mockStats = {
  total_leads: 3,
  new_leads: 2,
  active_leads: 1,
  emails_sent: 5,
  recent_activities: [
    { id: 'act-1', type: 'discovery', description: 'Discovered 3 new leads', timestamp: new Date().toISOString() },
    { id: 'act-2', type: 'email_sent', description: 'Email sent to ABC Technology', timestamp: new Date(Date.now() - 3600000).toISOString() }
  ]
};

export const handlers = [
  // Auth endpoints
  http.post(`${API_URL}/auth/google`, () => {
    return HttpResponse.json({
      token: 'mock-jwt-token',
      user: mockUser
    });
  }),

  // Dashboard stats
  http.get(`${API_URL}/dashboard/stats`, () => {
    return HttpResponse.json(mockStats);
  }),

  // Leads endpoints
  http.get(`${API_URL}/api/scout/leads`, ({ request }) => {
    const url = new URL(request.url);
    const status = url.searchParams.get('status');
    
    if (status === 'new') {
      return HttpResponse.json({ data: mockLeads.filter(l => l.status === 'new') });
    }
    
    return HttpResponse.json({ data: mockLeads });
  }),

  // Approve lead
  http.post(`${API_URL}/api/leads/:id/approve`, ({ params }) => {
    const lead = mockLeads.find(l => l.id === params.id);
    if (lead) {
      lead.status = 'approved';
      return HttpResponse.json({ success: true });
    }
    return HttpResponse.json({ error: 'Lead not found' }, { status: 404 });
  }),

  // Reject lead
  http.post(`${API_URL}/api/leads/:id/reject`, ({ params }) => {
    const lead = mockLeads.find(l => l.id === params.id);
    if (lead) {
      lead.status = 'rejected';
      return HttpResponse.json({ success: true });
    }
    return HttpResponse.json({ error: 'Lead not found' }, { status: 404 });
  }),

  // Settings endpoints
  http.get(`${API_URL}/api/settings`, () => {
    return HttpResponse.json({
      data: {
        daily_email_limit: 25,
        auto_approve_threshold: 0,
        discovery_frequency: 'daily',
        notification_email: mockUser.email,
        notification_preferences: {
          new_leads: true,
          email_replies: true,
          daily_summary: true
        }
      }
    });
  }),

  http.post(`${API_URL}/api/settings`, () => {
    return HttpResponse.json({ success: true });
  }),

  // Discovery
  http.post(`${API_URL}/api/discovery/run`, () => {
    return HttpResponse.json({ 
      success: true, 
      message: 'Discovery started',
      leads_found: 3
    });
  }),

  // Pipeline
  http.get(`${API_URL}/api/pipeline`, () => {
    return HttpResponse.json({ 
      data: mockLeads.filter(l => l.status !== 'new' && l.status !== 'rejected')
    });
  }),

  // Email templates
  http.get(`${API_URL}/api/email/templates`, () => {
    return HttpResponse.json({
      data: [
        {
          id: 'intro',
          name: 'Introduction',
          subject: 'Acquisition Opportunity - {{business_name}}',
          body: 'Hi {{owner_name}},\n\nMy name is {{sender_name}} and I\'m reaching out regarding {{business_name}}.'
        },
        {
          id: 'followup',
          name: 'Follow-up',
          subject: 'Following up - {{business_name}}',
          body: 'Hi {{owner_name}},\n\nI wanted to follow up on my previous message.'
        }
      ]
    });
  }),

  // Send email
  http.post(`${API_URL}/api/leads/:id/send-email`, () => {
    return HttpResponse.json({ 
      success: true, 
      message_id: 'mock-message-id' 
    });
  }),

  // CRM - Notes
  http.get(`${API_URL}/api/leads/:id/notes`, () => {
    return HttpResponse.json({
      data: [
        { id: 'note-1', content: 'Initial contact made', type: 'note', created_at: new Date().toISOString() }
      ]
    });
  }),

  http.post(`${API_URL}/api/leads/:id/notes`, () => {
    return HttpResponse.json({ success: true, note_id: 'new-note-id' });
  }),

  // CRM - Activities
  http.get(`${API_URL}/api/leads/:id/activities`, () => {
    return HttpResponse.json({
      data: [
        { id: 'act-1', type: 'discovery', description: 'Lead discovered', timestamp: new Date().toISOString() }
      ]
    });
  }),

  // CSV Import
  http.post(`${API_URL}/api/leads/import`, () => {
    return HttpResponse.json({ 
      success: true, 
      imported: 5, 
      total_in_file: 5,
      errors: [],
      column_mapping: { name: 'Business Name', industry: 'Industry' }
    });
  }),

  http.post(`${API_URL}/api/leads/import/validate`, () => {
    return HttpResponse.json({
      success: true,
      preview: mockLeads.slice(0, 3),
      total: 3,
      column_mapping: { name: 'Business Name', industry: 'Industry' },
      errors: []
    });
  })
];
