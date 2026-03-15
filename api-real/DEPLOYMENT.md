# ACQUISITOR API - Production Deployment Guide

## Overview

This guide covers deploying the ACQUISITOR API with multi-tenant security, rate limiting, and connection pooling.

## Pre-Deployment Checklist

- [ ] Database schema migrated with user_id columns
- [ ] Redis instance available for rate limiting
- [ ] Environment variables configured
- [ ] SSL certificates configured
- [ ] Backup strategy in place

## Architecture Changes (v2.0)

### Security Improvements
1. **Multi-tenancy**: All queries now filter by `user_id`
2. **Rate limiting**: Per-user daily limits based on subscription tier
3. **Connection pooling**: asyncpg pool (min=5, max=20)
4. **Row-level security**: Each user can only access their own data

### Database Schema
```
users
  - id (UUID, PK)
  - email (UNIQUE)
  - name
  - tier (free|pro|enterprise)
  - email_provider (JSONB)
  - email_provider_type
  - created_at, updated_at

leads
  - id (UUID, PK)
  - user_id (UUID, FK, INDEXED)  <-- NEW
  - business_name, owner_name, etc.
  - status, pipeline_state
  - created_at, updated_at

activities
  - id (UUID, PK)
  - user_id (UUID, FK, INDEXED)  <-- ENFORCED
  - type, description
  - timestamp

outreach_messages  <-- NEW TABLE
  - id (UUID, PK)
  - user_id (UUID, FK, INDEXED)
  - lead_id (UUID, FK)
  - subject, body, status
  - provider, provider_message_id

bookings  <-- NEW TABLE
  - id (UUID, PK)
  - user_id (UUID, FK, INDEXED)
  - lead_id (UUID, FK)
  - scheduled_at, status

rate_limits  <-- NEW TABLE
  - id (UUID, PK)
  - user_id (UUID, FK)
  - resource_type (leads|emails|scrapes)
  - count, reset_at
```

## Deployment Steps

### 1. Database Migration

Run the migration SQL on your PostgreSQL database:

```bash
# Using psql
psql $DATABASE_URL -f migrations/001_add_multi_tenancy.sql

# Or using Railway CLI
railway connect postgres
\i migrations/001_add_multi_tenancy.sql
```

**Critical**: If you have existing data, backfill user_id:
```sql
-- Option 1: Assign all existing leads to first admin
UPDATE leads SET user_id = (
  SELECT id FROM users WHERE role = 'admin' LIMIT 1
) WHERE user_id IS NULL;

-- Option 2: Create a migration admin and assign to them
INSERT INTO users (email, name, role, tier) 
VALUES ('migration@temp.com', 'Migration User', 'admin', 'enterprise');

UPDATE leads SET user_id = (
  SELECT id FROM users WHERE email = 'migration@temp.com'
) WHERE user_id IS NULL;
```

### 2. Redis Setup

**Option A: Railway**
```bash
railway add --plugin redis
```

**Option B: Upstash (Serverless)**
1. Create account at https://upstash.com
2. Create Redis database
3. Copy Redis URL

**Option C: Render**
Redis is included with Render Blueprint (see render.yaml)

### 3. Environment Variables

Copy `.env.production` and fill in values:

```bash
cp .env.production .env
# Edit .env with your values
```

Required variables:
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `JWT_SECRET` - Random 32+ character string
- `GOOGLE_CLIENT_ID` - From Google Cloud Console
- `GOOGLE_CLIENT_SECRET` - From Google Cloud Console
- `FRONTEND_URL` - Your Vercel/frontend URL

Generate JWT secret:
```bash
openssl rand -hex 32
```

### 4. Deploy to Render (Recommended)

The `render.yaml` Blueprint handles everything:

```bash
# 1. Push code to GitHub
git add .
git commit -m "Add multi-tenancy and security fixes"
git push

# 2. Go to https://dashboard.render.com/blueprints
# 3. Connect your repo
# 4. Render auto-creates:
#    - Web service for API
#    - PostgreSQL database
#    - Redis instance

# 5. Add environment variables in Render dashboard:
#    - GOOGLE_CLIENT_ID
#    - GOOGLE_CLIENT_SECRET
#    - FRONTEND_URL
```

### 5. Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Add PostgreSQL if not already added
railway add --plugin postgresql

# Add Redis
railway add --plugin redis

# Set environment variables
railway vars set JWT_SECRET=$(openssl rand -hex 32)
railway vars set GOOGLE_CLIENT_ID=your-client-id
railway vars set GOOGLE_CLIENT_SECRET=your-client-secret
railway vars set FRONTEND_URL=https://your-frontend.vercel.app

# Deploy
railway up

# Get deployment URL
railway domain
```

### 6. Deploy to Heroku (Alternative)

```bash
# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Add Redis
heroku addons:create heroku-redis:mini

# Set environment variables
heroku config:set JWT_SECRET=$(openssl rand -hex 32)
heroku config:set GOOGLE_CLIENT_ID=your-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret
heroku config:set FRONTEND_URL=https://your-frontend.vercel.app

# Deploy
git push heroku main

# Run migrations
heroku pg:psql < migrations/001_add_multi_tenancy.sql
```

## Post-Deployment Verification

### 1. Health Check
```bash
curl https://your-api-url/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "version": "2.0.0"
}
```

### 2. Test Multi-Tenancy

**User A creates a lead:**
```bash
curl -X POST https://your-api-url/leads \
  -H "Authorization: Bearer USER_A_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"business_name": "Test Lead A"}'
```

**User B tries to access User A's lead:**
```bash
curl https://your-api-url/leads/{lead_id} \
  -H "Authorization: Bearer USER_B_TOKEN"
```

Expected: `404 Not Found`

### 3. Test Rate Limiting

**Check limits:**
```bash
curl https://your-api-url/user/limits \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Exceed free tier (51 leads):**
```bash
for i in {1..55}; do
  curl -X POST https://your-api-url/leads \
    -H "Authorization: Bearer FREE_USER_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"business_name": "Test '$i'"}'
done
```

Expected after 50: `429 Rate limit exceeded`

### 4. Test Connection Pool

```bash
# Run 100 concurrent requests
ab -n 100 -c 100 -H "Authorization: Bearer TOKEN" \
  https://your-api-url/leads
```

All should succeed without connection errors.

## Rate Limits by Tier

| Tier | Leads/Day | Emails/Day | Scrapes/Day |
|------|-----------|------------|-------------|
| Free | 50 | 25 | 10 |
| Pro | Unlimited | 500 | 100 |
| Enterprise | Unlimited | Unlimited | Unlimited |

## Monitoring & Alerts

### Database Connection Pool
Monitor these metrics:
- Active connections
- Pool exhaustion errors
- Query latency

### Rate Limiting
Monitor:
- 429 response rate
- Redis connection errors
- Rate limit table growth

### Security
Monitor:
- 401/403 response rates
- Unusual query patterns
- Failed authentication attempts

## Troubleshooting

### "Column user_id does not exist"
Migration not applied. Run:
```bash
psql $DATABASE_URL -f migrations/001_add_multi_tenancy.sql
```

### "Redis connection failed"
- Check REDIS_URL is correct
- Verify Redis instance is running
- API will fallback to DB rate limiting (slower)

### "Connection pool exhausted"
- Increase max_size in main.py
- Check for connection leaks
- Monitor slow queries

### "User sees other user's data"
CRITICAL: Schema not migrated. Stop deployment and apply migration.

## Rollback Plan

If issues occur:

1. **Immediate**: Set `ENABLE_RATE_LIMITING=false` env var
2. **Database**: Restore from pre-migration backup
3. **Code**: Revert to previous git commit
4. **Deploy**: Push rollback to production

## Security Checklist

- [ ] JWT_SECRET is 32+ random characters
- [ ] Database credentials not in code
- [ ] Redis has authentication enabled
- [ ] CORS restricted to production domain
- [ ] SSL/TLS enabled
- [ ] Rate limiting enabled
- [ ] User isolation verified
- [ ] SQL injection tests passed
- [ ] Authentication required on all endpoints

## Support

For deployment issues:
1. Check logs: `railway logs` or `heroku logs --tail`
2. Verify health: `curl /health`
3. Test database: `psql $DATABASE_URL -c "SELECT 1"`
4. Test Redis: `redis-cli -u $REDIS_URL ping`
