-- Migration: Add multi-tenancy support to ACQUISITOR API
-- This migration adds user_id columns to all user-owned tables
-- and creates necessary indexes for performance

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. LEADS TABLE - Add user_id for multi-tenancy
-- ============================================
ALTER TABLE leads ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE;

-- Create index for fast user-scoped queries
CREATE INDEX IF NOT EXISTS idx_leads_user_id ON leads(user_id);
CREATE INDEX IF NOT EXISTS idx_leads_user_id_status ON leads(user_id, status);
CREATE INDEX IF NOT EXISTS idx_leads_user_id_pipeline ON leads(user_id, pipeline_state);

-- ============================================
-- 2. ACTIVITIES TABLE - Ensure user_id exists and is indexed
-- ============================================
-- Note: activities already has user_id, just need to ensure index
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_user_id_timestamp ON activities(user_id, timestamp DESC);

-- ============================================
-- 3. USER_ACTIONS TABLE - Already has user_id, ensure index
-- ============================================
CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_user_id_created ON user_actions(user_id, created_at DESC);

-- ============================================
-- 4. OUTREACH_MESSAGES TABLE - Create new table with multi-tenancy
-- ============================================
CREATE TABLE IF NOT EXISTS outreach_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    lead_email VARCHAR(255),
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'email',
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,
    provider VARCHAR(50), -- gmail, sendgrid, etc.
    provider_message_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_outreach_messages_user_id ON outreach_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_outreach_messages_user_id_status ON outreach_messages(user_id, status);
CREATE INDEX IF NOT EXISTS idx_outreach_messages_lead_id ON outreach_messages(lead_id);

-- ============================================
-- 5. BOOKINGS TABLE - Create new table with multi-tenancy
-- ============================================
CREATE TABLE IF NOT EXISTS bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID REFERENCES leads(id) ON DELETE SET NULL,
    lead_email VARCHAR(255),
    lead_phone VARCHAR(50),
    booking_type VARCHAR(50) DEFAULT 'call',
    status VARCHAR(50) DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    notes TEXT,
    calendar_event_id VARCHAR(255),
    meeting_link TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_bookings_user_id_scheduled ON bookings(user_id, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_bookings_lead_id ON bookings(lead_id);

-- ============================================
-- 6. USERS TABLE - Add subscription tier and email provider
-- ============================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS tier VARCHAR(50) DEFAULT 'free';
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_provider JSONB DEFAULT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_provider_type VARCHAR(50) DEFAULT NULL;
ALTER TABLE users ADD COLUMN IF NOT EXISTS rate_limit_reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

CREATE INDEX IF NOT EXISTS idx_users_tier ON users(tier);

-- ============================================
-- 7. RATE_LIMITS TABLE - For tracking per-user rate limits
-- ============================================
CREATE TABLE IF NOT EXISTS rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    resource_type VARCHAR(50) NOT NULL, -- 'leads', 'emails', 'scrapes'
    count INTEGER DEFAULT 0,
    reset_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, resource_type)
);

CREATE INDEX IF NOT EXISTS idx_rate_limits_user_id ON rate_limits(user_id);
CREATE INDEX IF NOT EXISTS idx_rate_limits_user_resource ON rate_limits(user_id, resource_type);

-- ============================================
-- 8. Create updated_at triggers for new tables
-- ============================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
DROP TRIGGER IF EXISTS update_outreach_messages_updated_at ON outreach_messages;
CREATE TRIGGER update_outreach_messages_updated_at
BEFORE UPDATE ON outreach_messages
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_bookings_updated_at ON bookings;
CREATE TRIGGER update_bookings_updated_at
BEFORE UPDATE ON bookings
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_rate_limits_updated_at ON rate_limits;
CREATE TRIGGER update_rate_limits_updated_at
BEFORE UPDATE ON rate_limits
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 9. Backfill user_id for existing leads (assign to first admin user or create placeholder)
-- ============================================
-- Note: Run this after migration to assign existing leads to users
-- UPDATE leads SET user_id = (SELECT id FROM users WHERE role = 'admin' LIMIT 1) WHERE user_id IS NULL;

-- ============================================
-- Migration Complete
-- ============================================
