import { Hono } from 'hono';
import { serve } from '@hono/node-server';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { Client } from 'pg';
import Redis from 'ioredis';
import { config } from 'dotenv';

config();

// Database connection
const pgClient = new Client({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/acquisitor',
});

// Redis connection
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

// Initialize connections
async function initConnections() {
  try {
    await pgClient.connect();
    console.log('✅ PostgreSQL connected');

    // Test Redis connection
    await redis.ping();
    console.log('✅ Redis connected');
  } catch (error) {
    console.error('❌ Database connection failed:', error);
    process.exit(1);
  }
}

// Mock data generators
function generateMockLeads(page: number, limit: number, filters: any) {
  const industries = ['Technology', 'Healthcare', 'Finance', 'Manufacturing', 'Retail', 'Services', 'Real Estate'];
  const sizes = ['small', 'medium', 'large'];
  const statuses = ['new', 'approved', 'rejected', 'watchlist'];
  
  const leads = [];
  const startId = (page - 1) * limit;
  
  for (let i = 0; i < limit; i++) {
    const id = startId + i + 1;
    const industry = industries[Math.floor(Math.random() * industries.length)];
    const size = sizes[Math.floor(Math.random() * sizes.length)] as 'small' | 'medium' | 'large';
    const status = statuses[Math.floor(Math.random() * statuses.length)] as any;
    const score = Math.floor(Math.random() * 100);
    
    // Filter by search
    if (filters.search && !`Company ${id}`.toLowerCase().includes(filters.search.toLowerCase()) && 
        !industry.toLowerCase().includes(filters.search.toLowerCase())) {
      continue;
    }
    
    // Filter by industry
    if (filters.industry && industry !== filters.industry) continue;
    
    // Filter by size
    if (filters.size && size !== filters.size) continue;
    
    // Filter by status
    if (filters.status && status !== filters.status) continue;
    
    // Filter by min score
    if (filters.minScore && score < parseInt(filters.minScore)) continue;
    
    leads.push({
      id: `lead-${id}`,
      name: `Company ${id}`,
      industry,
      size,
      revenue: Math.floor(Math.random() * 10000000) + 500000,
      employees: Math.floor(Math.random() * 500) + 10,
      location: {
        city: ['San Francisco', 'New York', 'Austin', 'Seattle', 'Denver', 'Boston'][Math.floor(Math.random() * 6)],
        state: ['CA', 'NY', 'TX', 'WA', 'CO', 'MA'][Math.floor(Math.random() * 6)],
        country: 'USA',
      },
      contact: {
        email: `contact@company${id}.com`,
        phone: Math.random() > 0.5 ? `+1-555-${String(Math.floor(Math.random() * 9000) + 1000)}` : undefined,
      },
      score,
      status,
      source: ['LinkedIn', 'Crunchbase', 'AngelList', 'Manual', 'Scraper'][Math.floor(Math.random() * 5)],
      discoveredAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      lastActivityAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      tags: ['acquisition', industry.toLowerCase(), size].filter(() => Math.random() > 0.3),
      description: `A ${size} ${industry.toLowerCase()} company with strong growth potential.`,
      website: `https://company${id}.com`,
      valuation: Math.random() > 0.3 ? Math.floor(Math.random() * 50000000) + 1000000 : undefined,
    });
  }
  
  return {
    leads,
    meta: {
      page,
      limit,
      total: 150, // Simulated total
      hasMore: page * limit < 150,
    },
  };
}

function generateMockPipeline() {
  const stages = ['NEW', 'OUTREACH', 'ENGAGED', 'QUALIFIED', 'BOOKED'];
  const pipeline = [];
  
  for (let i = 0; i < 25; i++) {
    const stage = stages[Math.floor(Math.random() * stages.length)];
    pipeline.push({
      id: `pipeline-${i + 1}`,
      leadId: `lead-${i + 1}`,
      name: `Company ${i + 1}`,
      score: Math.floor(Math.random() * 100),
      stage,
      lastActivityAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      assignedTo: Math.random() > 0.3 ? ['Alice', 'Bob', 'Charlie'][Math.floor(Math.random() * 3)] : undefined,
      priority: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
      value: Math.random() > 0.5 ? Math.floor(Math.random() * 50000000) + 1000000 : undefined,
    });
  }
  
  return pipeline;
}

function generateMockActivities(limit: number) {
  const types = ['lead_discovered', 'lead_approved', 'lead_rejected', 'email_sent', 'email_opened', 'email_replied', 'call_scheduled', 'call_completed', 'stage_changed', 'note_added'];
  const activities = [];
  
  for (let i = 0; i < limit; i++) {
    const type = types[Math.floor(Math.random() * types.length)];
    activities.push({
      id: `activity-${i + 1}`,
      type,
      leadId: `lead-${Math.floor(Math.random() * 50) + 1}`,
      leadName: `Company ${Math.floor(Math.random() * 50) + 1}`,
      timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
      metadata: type === 'stage_changed' ? {
        previousStage: 'NEW',
        newStage: 'OUTREACH',
      } : type === 'email_sent' ? {
        emailSubject: 'Introduction and Partnership Opportunity',
      } : undefined,
      actor: ['Alice', 'Bob', 'Charlie', 'System'][Math.floor(Math.random() * 4)],
    });
  }
  
  return activities.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}

function generateMockMetrics() {
  const emailsSent = Math.floor(Math.random() * 500) + 100;
  const emailsOpened = Math.floor(emailsSent * 0.35);
  const emailsReplied = Math.floor(emailsSent * 0.12);
  
  return {
    totalLeads: 150,
    leadsInPipeline: 25,
    callsBookedThisWeek: Math.floor(Math.random() * 10) + 2,
    callsBookedThisMonth: Math.floor(Math.random() * 30) + 10,
    conversionRate: 0.15 + Math.random() * 0.1,
    averageDealSize: 5000000 + Math.random() * 10000000,
    outreach: {
      emailsSent,
      emailsOpened,
      emailsReplied,
      openRate: emailsOpened / emailsSent,
      replyRate: emailsReplied / emailsSent,
      period: 'Last 30 days',
    },
  };
}

function generateMockBookings(upcoming = true) {
  const types = ['intro', 'followup', 'demo', 'negotiation'];
  const statuses = ['scheduled', 'completed', 'cancelled', 'noshow'];
  const bookings = [];
  const count = upcoming ? 10 : 5;
  
  for (let i = 0; i < count; i++) {
    const scheduledAt = upcoming 
      ? new Date(Date.now() + Math.random() * 7 * 24 * 60 * 60 * 1000)
      : new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000);
    
    bookings.push({
      id: `booking-${i + 1}`,
      leadId: `lead-${Math.floor(Math.random() * 50) + 1}`,
      leadName: `Company ${Math.floor(Math.random() * 50) + 1}`,
      scheduledAt: scheduledAt.toISOString(),
      duration: [30, 45, 60][Math.floor(Math.random() * 3)],
      type: types[Math.floor(Math.random() * types.length)],
      status: upcoming ? 'scheduled' : statuses[Math.floor(Math.random() * statuses.length)],
      notes: Math.random() > 0.5 ? 'Prepare pitch deck and financials' : undefined,
      calendarLink: upcoming ? `https://calendar.example.com/booking-${i + 1}` : undefined,
    });
  }
  
  return bookings.sort((a, b) => new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime());
}

// Create Hono app
const app = new Hono();

// Middleware
app.use(logger());
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? ['https://acquisitor.app', 'http://localhost:5173'] 
    : '*',
  credentials: true,
}));

// Health check endpoint
app.get('/health', async (c) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    services: {
      database: 'unknown',
      redis: 'unknown',
    },
  };

  try {
    await pgClient.query('SELECT 1');
    health.services.database = 'connected';
  } catch {
    health.services.database = 'disconnected';
    health.status = 'degraded';
  }

  try {
    await redis.ping();
    health.services.redis = 'connected';
  } catch {
    health.services.redis = 'disconnected';
    health.status = 'degraded';
  }

  const statusCode = health.status === 'healthy' ? 200 : 503;
  return c.json(health, statusCode);
});

// API routes
app.get('/', (c) => {
  return c.json({
    name: 'ACQUISITOR API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      leads: '/api/scout/leads',
      pipeline: '/api/pipeline',
      activity: '/api/activity',
      metrics: '/api/metrics',
      bookings: '/api/bookings',
    },
  });
});

// Scout/Leads endpoints
app.get('/api/scout/leads', async (c) => {
  const page = parseInt(c.req.query('page') || '1');
  const limit = parseInt(c.req.query('limit') || '20');
  const search = c.req.query('search');
  const industry = c.req.query('industry');
  const size = c.req.query('size');
  const status = c.req.query('status');
  const minScore = c.req.query('minScore');
  
  const { leads, meta } = generateMockLeads(page, limit, {
    search,
    industry,
    size,
    status,
    minScore,
  });
  
  return c.json({
    success: true,
    data: leads,
    meta,
  });
});

app.get('/api/scout/leads/:id', async (c) => {
  const id = c.req.param('id');
  const { leads } = generateMockLeads(1, 1, {});
  const lead = leads[0];
  lead.id = id;
  
  return c.json({
    success: true,
    data: {
      ...lead,
      notes: [
        {
          id: 'note-1',
          content: 'Initial discovery - strong fit for acquisition criteria.',
          createdAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          createdBy: 'Alice',
        },
      ],
      activities: generateMockActivities(5).filter(a => a.leadId === id),
      documents: [
        {
          id: 'doc-1',
          name: 'Financial_Statements_2024.pdf',
          type: 'pdf',
          url: '/documents/financials.pdf',
          uploadedAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
        },
      ],
      competitors: ['Competitor A', 'Competitor B'],
      financials: {
        revenue: lead.revenue,
        ebitda: lead.revenue * 0.15,
        growth: 0.25 + Math.random() * 0.5,
      },
    },
  });
});

app.patch('/api/scout/leads/:id/status', async (c) => {
  const id = c.req.param('id');
  const body = await c.req.json();
  const { leads } = generateMockLeads(1, 1, {});
  const lead = leads[0];
  lead.id = id;
  lead.status = body.status;
  
  return c.json({
    success: true,
    data: lead,
  });
});

// Pipeline endpoints
app.get('/api/pipeline', async (c) => {
  return c.json({
    success: true,
    data: generateMockPipeline(),
  });
});

app.patch('/api/pipeline/:leadId/stage', async (c) => {
  const leadId = c.req.param('leadId');
  const body = await c.req.json();
  const pipeline = generateMockPipeline();
  const lead = pipeline.find(l => l.leadId === leadId) || pipeline[0];
  lead.leadId = leadId;
  lead.stage = body.stage;
  lead.lastActivityAt = new Date().toISOString();
  
  return c.json({
    success: true,
    data: lead,
  });
});

// Activity endpoints
app.get('/api/activity', async (c) => {
  const limit = parseInt(c.req.query('limit') || '20');
  
  return c.json({
    success: true,
    data: generateMockActivities(limit),
  });
});

// Metrics endpoints
app.get('/api/metrics', async (c) => {
  return c.json({
    success: true,
    data: generateMockMetrics(),
  });
});

// Bookings endpoints
app.get('/api/bookings', async (c) => {
  const upcoming = c.req.query('upcoming') !== 'false';
  
  return c.json({
    success: true,
    data: generateMockBookings(upcoming),
  });
});

app.post('/api/bookings', async (c) => {
  const body = await c.req.json();
  
  return c.json({
    success: true,
    data: {
      id: `booking-${Date.now()}`,
      ...body,
    },
  }, 201);
});

// Start server
const PORT = parseInt(process.env.PORT || '3001', 10);

initConnections().then(() => {
  serve({
    fetch: app.fetch,
    port: PORT,
  });

  console.log(`🚀 API server running on http://localhost:${PORT}`);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully');
  await pgClient.end();
  await redis.quit();
  process.exit(0);
});

process.on('SIGINT', async () => {
  console.log('SIGINT received, shutting down gracefully');
  await pgClient.end();
  await redis.quit();
  process.exit(0);
});

export { app, pgClient, redis };
