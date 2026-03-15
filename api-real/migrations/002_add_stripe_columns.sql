-- ACQUISITOR Stripe Migration
-- Run this to add Stripe columns to existing users table

-- Add subscription columns to users table
ALTER TABLE users 
    ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(50) DEFAULT 'inactive',
    ADD COLUMN IF NOT EXISTS stripe_customer_id VARCHAR(255),
    ADD COLUMN IF NOT EXISTS stripe_subscription_id VARCHAR(255);

-- Ensure tier column exists (may already exist)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'tier') THEN
        ALTER TABLE users ADD COLUMN tier VARCHAR(20) DEFAULT 'free';
    END IF;
END $$;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_stripe_customer 
    ON users(stripe_customer_id) 
    WHERE stripe_customer_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_stripe_subscription 
    ON users(stripe_subscription_id) 
    WHERE stripe_subscription_id IS NOT NULL;

-- Migration complete
SELECT 'Stripe columns added successfully' as status;
