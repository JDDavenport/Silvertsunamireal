# ACQUISITOR Production Deployment Guide

## ✅ Completed

### Frontend (Vercel)
- **Live URL**: https://acquisitor.vercel.app
- **Status**: DEPLOYED
- **Build**: Successful

## ⏳ Manual Steps Required

### Step 1: Deploy Backend to Render

1. Go to https://dashboard.render.com/blueprints
2. Click **"New Blueprint Instance"**
3. Connect your GitHub repo: `JDDavenport/Silvertsunamireal`
4. Select the blueprint file: `api-real/render.yaml`
5. Click **"Apply Blueprint"**

### Step 2: Configure Environment Variables in Render

After the blueprint creates the services, add these environment variables to the `acquisitor-api` service:

| Variable | Value | Source |
|----------|-------|--------|
| `GOOGLE_CLIENT_ID` | YOUR_GOOGLE_CLIENT_ID | Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | YOUR_GOOGLE_CLIENT_SECRET | Google Cloud Console |
| `STRIPE_SECRET_KEY` | sk_live_... | Stripe Dashboard |
| `STRIPE_PUBLISHABLE_KEY` | pk_live_... | Stripe Dashboard |
| `STRIPE_WEBHOOK_SECRET` | whsec_... | Stripe Webhook Setup |
| `STRIPE_PRO_PRICE_ID` | price_... | Stripe Products |

### Step 3: Run Database Migrations

Once the database is created, run:

```bash
# Get the database connection string from Render dashboard
# Then run:
psql $DATABASE_URL -f api-real/migrations/001_add_multi_tenancy.sql
psql $DATABASE_URL -f api-real/migrations/002_add_stripe_columns.sql
```

Or use Render's shell access:
```bash
cd api-real
psql $DATABASE_URL -f migrations/001_add_multi_tenancy.sql
psql $DATABASE_URL -f migrations/002_add_stripe_columns.sql
```

### Step 4: Configure Stripe Webhooks

1. Go to https://dashboard.stripe.com/webhooks
2. Click **"Add endpoint"**
3. Endpoint URL: `https://acquisitor-api.onrender.com/billing/webhook`
4. Select events:
   - `checkout.session.completed`
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
   - `customer.subscription.updated`
5. Copy the webhook signing secret
6. Add to Render env vars as `STRIPE_WEBHOOK_SECRET`

### Step 5: Update Frontend Environment Variables

In Vercel dashboard (or via CLI):
```bash
vercel env add VITE_API_URL production
# Enter: https://acquisitor-api.onrender.com

vercel env add VITE_STRIPE_PUBLISHABLE_KEY production
# Enter: pk_live_...
```

Then redeploy:
```bash
cd v2/web && vercel --prod
```

## 🧪 Post-Deployment Testing

1. Visit https://acquisitor.vercel.app
2. Click "Get Started with Google"
3. Complete OAuth flow
4. Verify dashboard loads with demo leads
5. Test Stripe checkout (use test card: 4242 4242 4242 4242)
6. Verify rate limiting (try creating 51 leads)

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| Frontend | https://acquisitor.vercel.app |
| Backend | https://acquisitor-api.onrender.com (after deploy) |
| Render Dashboard | https://dashboard.render.com/ |
| Stripe Dashboard | https://dashboard.stripe.com/ |
| Vercel Dashboard | https://vercel.com/dashboard |

## 📝 Files Prepared

- `api-real/render.yaml` - Render blueprint
- `api-real/Dockerfile` - Container config
- `api-real/migrations/` - Database migrations
- `v2/web/.env.production` - Frontend env template
