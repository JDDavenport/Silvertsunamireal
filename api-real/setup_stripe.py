#!/usr/bin/env python3
"""
Stripe Product Setup Script for ACQUISITOR

This script creates the necessary products and prices in Stripe for:
- Pro Plan: $99/month
- Enterprise Plan: $499/month

Usage:
1. Set STRIPE_SECRET_KEY environment variable
2. Run: python setup_stripe.py
3. Copy the price IDs to your .env.production file
"""

import os
import stripe

# Configuration
PRO_PRICE_MONTHLY = 99 * 100  # $99 in cents
ENTERPRISE_PRICE_MONTHLY = 499 * 100  # $499 in cents


def create_stripe_products():
    """Create Stripe products and prices for ACQUISITOR subscriptions"""
    
    stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not stripe_secret_key:
        print("❌ Error: STRIPE_SECRET_KEY environment variable not set")
        print("   Set it with: export STRIPE_SECRET_KEY=sk_test_...")
        return
    
    stripe.api_key = stripe_secret_key
    
    print("🔧 Setting up Stripe products for ACQUISITOR...\n")
    
    # Create Pro Product
    try:
        pro_product = stripe.Product.create(
            name="ACQUISITOR Pro",
            description="For serious buyers ready to acquire",
            metadata={
                "tier": "pro",
                "features": "unlimited_searches,ai_scoring,outreach,pipeline"
            }
        )
        print(f"✅ Created Pro Product: {pro_product.id}")
        
        pro_price = stripe.Price.create(
            product=pro_product.id,
            unit_amount=PRO_PRICE_MONTHLY,
            currency="usd",
            recurring={"interval": "month"},
            metadata={"tier": "pro"}
        )
        print(f"✅ Created Pro Price: {pro_price.id}")
        print(f"   Amount: ${PRO_PRICE_MONTHLY/100}/month\n")
        
    except stripe.error.StripeError as e:
        print(f"❌ Error creating Pro product: {e}")
        return
    
    # Create Enterprise Product
    try:
        enterprise_product = stripe.Product.create(
            name="ACQUISITOR Enterprise",
            description="For teams and high-volume acquirers",
            metadata={
                "tier": "enterprise",
                "features": "everything_in_pro,unlimited_team,api_access,white_label"
            }
        )
        print(f"✅ Created Enterprise Product: {enterprise_product.id}")
        
        enterprise_price = stripe.Price.create(
            product=enterprise_product.id,
            unit_amount=ENTERPRISE_PRICE_MONTHLY,
            currency="usd",
            recurring={"interval": "month"},
            metadata={"tier": "enterprise"}
        )
        print(f"✅ Created Enterprise Price: {enterprise_price.id}")
        print(f"   Amount: ${ENTERPRISE_PRICE_MONTHLY/100}/month\n")
        
    except stripe.error.StripeError as e:
        print(f"❌ Error creating Enterprise product: {e}")
        return
    
    # Print summary
    print("=" * 60)
    print("🎉 Stripe products created successfully!")
    print("=" * 60)
    print("\nAdd these to your .env.production file:\n")
    print(f"STRIPE_PRO_PRICE_ID={pro_price.id}")
    print(f"STRIPE_ENTERPRISE_PRICE_ID={enterprise_price.id}")
    print("\n" + "=" * 60)
    
    # Webhook setup instructions
    print("\n📡 Next Steps:")
    print("   1. Copy the price IDs above to your .env.production")
    print("   2. Set up webhook endpoint in Stripe Dashboard:")
    print("      - URL: https://your-api.com/billing/webhook")
    print("      - Events to listen for:")
    print("        • checkout.session.completed")
    print("        • invoice.paid")
    print("        • invoice.payment_failed")
    print("        • customer.subscription.deleted")
    print("        • customer.subscription.updated")
    print("   3. Copy the webhook signing secret to STRIPE_WEBHOOK_SECRET")


if __name__ == "__main__":
    create_stripe_products()
