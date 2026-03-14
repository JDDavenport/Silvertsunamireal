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
    },
  });
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
