# ACQUISITOR Stripe Integration Setup

This document explains how to set up Stripe subscription billing for ACQUISITOR.

## Overview

ACQUISITOR uses Stripe for subscription billing with three tiers:
- **Free**: $0/month - Limited features
- **Pro**: $99/month - Full features for individual buyers
- **Enterprise**: $499/month - Team features + API access

## Setup Steps

### 1. Create Stripe Account

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Complete account setup (test mode works for development)
3. Get your API keys from Developers → API keys

### 2. Create Products and Prices

**Option A: Using the Setup Script**

```bash
cd ~/projects/silver-tsunami-real/api-real
export STRIPE_SECRET_KEY=sk_test_...
python setup_stripe.py
```

**Option B: Manual Setup in Dashboard**

1. Go to Products → Add Product
2. Create "ACQUISITOR Pro":
   - Price: $99/month
   - Recurring: Monthly
3. Create "ACQUISITOR Enterprise":
   - Price: $499/month
   - Recurring: Monthly

### 3. Configure Environment Variables

Add to `api-real/.env.production`:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Product Price IDs (from setup script or dashboard)
STRIPE_PRO_PRICE_ID=price_...
STRIPE_ENTERPRISE_PRICE_ID=price_...
```

Add to `v2/web/.env.production`:

```bash
VITE_STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### 4. Set Up Webhooks

1. In Stripe Dashboard, go to Developers → Webhooks
2. Add endpoint:
   - URL: `https://your-api.com/billing/webhook`
   - Events to listen for:
     - `checkout.session.completed`
     - `invoice.paid`
     - `invoice.payment_failed`
     - `customer.subscription.deleted`
     - `customer.subscription.updated`
3. Copy the Signing Secret → `STRIPE_WEBHOOK_SECRET`

### 5. Run Database Migration

```bash
# Connect to your PostgreSQL database
psql $DATABASE_URL -f migrations/002_add_stripe_columns.sql
```

### 6. Test the Integration

Use Stripe test mode with card: `4242 4242 4242 4242`

1. Go to pricing page
2. Click "Upgrade to Pro"
3. Complete checkout with test card
4. Verify subscription is active in dashboard

## API Endpoints

### Public Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/billing/config` | GET | Get publishable key and price IDs |

### Authenticated Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/billing/checkout-session` | POST | Create checkout session |
| `/billing/subscription` | GET | Get current subscription status |
| `/billing/portal` | POST | Create customer portal session |

### Webhook Endpoint

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/billing/webhook` | POST | Receive Stripe webhooks |

## Webhook Events Handled

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Activate subscription, upgrade tier |
| `invoice.paid` | Confirm subscription active |
| `invoice.payment_failed` | Mark subscription past_due |
| `customer.subscription.deleted` | Downgrade to free |
| `customer.subscription.updated` | Update subscription status |

## Tier Enforcement

Rate limits are enforced based on user tier:

```python
FREE_TIER = {"leads": 50, "emails": 25, "scrapes": 10}
PRO_TIER = {"leads": float('inf'), "emails": 500, "scrapes": 100}
ENTERPRISE_TIER = {"leads": float('inf'), "emails": float('inf'), "scrapes": float('inf')}
```

The middleware checks the user's tier from the database on each request.

## Troubleshooting

### Webhook Errors

- **Signature verification failed**: Check `STRIPE_WEBHOOK_SECRET` is correct
- **No user_id in metadata**: Checkout session wasn't created with metadata

### Subscription Not Activating

- Check webhook is receiving events in Stripe Dashboard
- Verify database migration ran successfully
- Check API logs for errors

### Checkout Not Working

- Verify `STRIPE_PUBLISHABLE_KEY` in frontend
- Verify `STRIPE_SECRET_KEY` and price IDs in backend
- Check browser console for errors

## Going Live

1. Switch to live mode in Stripe Dashboard
2. Replace test keys with live keys
3. Update webhook URL to production
4. Update `FRONTEND_URL` to production domain
5. Test with a real card ($1 authorization, refunded)

## Files Modified/Created

- `api-real/src/main.py` - Billing endpoints and webhooks
- `api-real/requirements.txt` - Added stripe package
- `api-real/.env.production` - Stripe configuration
- `api-real/setup_stripe.py` - Product setup script
- `api-real/migrations/002_add_stripe_columns.sql` - Database migration
- `v2/web/src/App.tsx` - Added checkout route
- `v2/web/src/views/CheckoutResult.tsx` - Checkout success/cancel page
- `v2/web/src/views/LandingPage.tsx` - Updated pricing tiers
- `v2/web/src/components/landing/Pricing.tsx` - Checkout integration
- `v2/web/src/components/SubscriptionBadge.tsx` - Dashboard badge
- `v2/web/src/hooks/useCheckout.ts` - Checkout hook
- `v2/web/src/hooks/useSubscription.ts` - Subscription status hook
- `v2/web/src/lib/stripe.ts` - Stripe loader
- `v2/web/.env.production` - Frontend Stripe key
