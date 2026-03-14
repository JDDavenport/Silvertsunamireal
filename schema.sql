-- ACQUISITOR PostgreSQL Database Schema
-- Complete schema for SCOUT, QUALIFY, and DEALFLOW modules
-- Includes pgvector extension for AI embeddings

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgvector";

-- ============================================================================
-- USERS (foundation table for foreign key references)
-- ============================================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SCOUT MODULE
-- ============================================================================

-- Market Listings: Raw business listings scraped from marketplaces
CREATE TABLE market_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source VARCHAR(100) NOT NULL,
    source_url TEXT,
    source_id VARCHAR(255),
    business_name VARCHAR(500) NOT NULL,
    industry VARCHAR(200),
    sub_industry VARCHAR(200),
    revenue_estimate DECIMAL(15, 2),
    ebitda_estimate DECIMAL(15, 2),
    asking_price DECIMAL(15, 2),
    sde_multiple DECIMAL(5, 2),
    location_city VARCHAR(200),
    location_state VARCHAR(100),
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    description TEXT,
    description_embedding VECTOR(1536),  -- OpenAI text-embedding-3-small/large
    owner_name VARCHAR(500),
    broker_name VARCHAR(500),
    years_in_operation INTEGER,
    employee_count INTEGER,
    listing_date DATE,
    days_on_market INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    raw_data_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_latitude CHECK (location_lat IS NULL OR (location_lat >= -90 AND location_lat <= 90)),
    CONSTRAINT valid_longitude CHECK (location_lng IS NULL OR (location_lng >= -180 AND location_lng <= 180)),
    CONSTRAINT positive_revenue CHECK (revenue_estimate IS NULL OR revenue_estimate >= 0),
    CONSTRAINT positive_ebitda CHECK (ebitda_estimate IS NULL OR ebitda_estimate >= 0),
    CONSTRAINT positive_asking_price CHECK (asking_price IS NULL OR asking_price >= 0)
);

-- Market Snapshots: Aggregated market data over time
CREATE TABLE market_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    snapshot_date DATE NOT NULL,
    industry VARCHAR(200),
    geography VARCHAR(200),
    total_listings INTEGER DEFAULT 0,
    median_asking_price DECIMAL(15, 2),
    median_sde_multiple DECIMAL(5, 2),
    median_days_on_market INTEGER,
    new_listings INTEGER DEFAULT 0,
    removed_listings INTEGER DEFAULT 0,
    snapshot_data_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT positive_total_listings CHECK (total_listings >= 0),
    CONSTRAINT positive_new_listings CHECK (new_listings >= 0),
    CONSTRAINT positive_removed_listings CHECK (removed_listings >= 0)
);

-- Saved Searches: User-configured search alerts
CREATE TABLE saved_searches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    filters_json JSONB NOT NULL DEFAULT '{}',
    notification_enabled BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- DEALFLOW MODULE (must come before QUALIFY for FK references)
-- ============================================================================

-- Leads: Qualified business opportunities in the pipeline
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_name VARCHAR(500) NOT NULL,
    owner_name VARCHAR(500),
    owner_email VARCHAR(255),
    owner_phone VARCHAR(50),
    status VARCHAR(50) DEFAULT 'new',
    pipeline_state VARCHAR(50) DEFAULT 'inbox',
    score DECIMAL(5, 2),
    source VARCHAR(100),
    source_url TEXT,
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_score CHECK (score IS NULL OR (score >= 0 AND score <= 100))
);

-- Outreach Messages: All communication with leads
CREATE TABLE outreach_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    channel VARCHAR(50) NOT NULL,  -- email, sms, linkedin, phone
    direction VARCHAR(10) NOT NULL, -- inbound, outbound
    subject VARCHAR(500),
    body TEXT,
    sent_at TIMESTAMP WITH TIME ZONE,
    delivered_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT valid_channel CHECK (channel IN ('email', 'sms', 'linkedin', 'phone', 'other')),
    CONSTRAINT valid_direction CHECK (direction IN ('inbound', 'outbound'))
);

-- Bookings: Scheduled meetings with leads
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    cal_event_id VARCHAR(255),
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    meeting_url TEXT,
    status VARCHAR(50) DEFAULT 'scheduled',  -- scheduled, completed, cancelled, no_show
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT positive_duration CHECK (duration_minutes > 0)
);

-- Pipeline Metrics: Historical pipeline analytics
CREATE TABLE pipeline_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_date DATE NOT NULL,
    state VARCHAR(50) NOT NULL,
    count INTEGER DEFAULT 0,
    total_value DECIMAL(15, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT positive_count CHECK (count >= 0)
);

-- Notifications: User notification queue
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- new_lead, score_update, meeting_reminder, etc.
    priority VARCHAR(20) DEFAULT 'normal',  -- low, normal, high, urgent
    message TEXT NOT NULL,
    data_json JSONB DEFAULT '{}',
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_priority CHECK (priority IN ('low', 'normal', 'high', 'urgent'))
);

-- ============================================================================
-- QUALIFY MODULE
-- ============================================================================

-- Lead Scores: AI-generated qualification scores
CREATE TABLE lead_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    total_score DECIMAL(5, 2) NOT NULL,
    revenue_fit_score DECIMAL(5, 2),
    margin_quality_score DECIMAL(5, 2),
    exit_signal_score DECIMAL(5, 2),
    ai_leverage_score DECIMAL(5, 2),
    valuation_score DECIMAL(5, 2),
    custom_scores_json JSONB DEFAULT '{}',
    scoring_config_version INTEGER DEFAULT 1,
    ai_assessment_text TEXT,
    comparable_deals_json JSONB,
    scored_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_total_score CHECK (total_score >= 0 AND total_score <= 100),
    CONSTRAINT valid_revenue_fit CHECK (revenue_fit_score IS NULL OR (revenue_fit_score >= 0 AND revenue_fit_score <= 100)),
    CONSTRAINT valid_margin_quality CHECK (margin_quality_score IS NULL OR (margin_quality_score >= 0 AND margin_quality_score <= 100)),
    CONSTRAINT valid_exit_signal CHECK (exit_signal_score IS NULL OR (exit_signal_score >= 0 AND exit_signal_score <= 100)),
    CONSTRAINT valid_ai_leverage CHECK (ai_leverage_score IS NULL OR (ai_leverage_score >= 0 AND ai_leverage_score <= 100)),
    CONSTRAINT valid_valuation CHECK (valuation_score IS NULL OR (valuation_score >= 0 AND valuation_score <= 100))
);

-- Scoring Configs: User-defined scoring criteria
CREATE TABLE scoring_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    config_name VARCHAR(255) NOT NULL,
    criteria_weights_json JSONB NOT NULL DEFAULT '{}',
    industry_preferences JSONB DEFAULT '[]',
    geography_preferences JSONB DEFAULT '[]',
    revenue_min DECIMAL(15, 2),
    revenue_max DECIMAL(15, 2),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT valid_revenue_range CHECK (revenue_min IS NULL OR revenue_max IS NULL OR revenue_min <= revenue_max)
);

-- User Actions: Audit trail of user decisions
CREATE TABLE user_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL,  -- approve, reject, flag, note, etc.
    reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Watchlist: User-saved leads of interest
CREATE TABLE watchlist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    lead_id UUID NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, lead_id)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);

-- Market Listings indexes
CREATE INDEX idx_market_listings_source ON market_listings(source);
CREATE INDEX idx_market_listings_source_id ON market_listings(source_id);
CREATE INDEX idx_market_listings_industry ON market_listings(industry);
CREATE INDEX idx_market_listings_sub_industry ON market_listings(sub_industry);
CREATE INDEX idx_market_listings_location_state ON market_listings(location_state);
CREATE INDEX idx_market_listings_location_city ON market_listings(location_city);
CREATE INDEX idx_market_listings_status ON market_listings(status);
CREATE INDEX idx_market_listings_listing_date ON market_listings(listing_date);
CREATE INDEX idx_market_listings_revenue_estimate ON market_listings(revenue_estimate);
CREATE INDEX idx_market_listings_asking_price ON market_listings(asking_price);
CREATE INDEX idx_market_listings_sde_multiple ON market_listings(sde_multiple);
CREATE INDEX idx_market_listings_broker_name ON market_listings(broker_name);
CREATE INDEX idx_market_listings_created_at ON market_listings(created_at);
CREATE INDEX idx_market_listings_embedding ON market_listings USING ivfflat (description_embedding vector_cosine_ops);

-- Market Snapshots indexes
CREATE INDEX idx_market_snapshots_date ON market_snapshots(snapshot_date);
CREATE INDEX idx_market_snapshots_industry ON market_snapshots(industry);
CREATE INDEX idx_market_snapshots_geography ON market_snapshots(geography);
CREATE INDEX idx_market_snapshots_date_industry ON market_snapshots(snapshot_date, industry);

-- Saved Searches indexes
CREATE INDEX idx_saved_searches_user_id ON saved_searches(user_id);
CREATE INDEX idx_saved_searches_notification ON saved_searches(notification_enabled) WHERE notification_enabled = TRUE;

-- Leads indexes
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_pipeline_state ON leads(pipeline_state);
CREATE INDEX idx_leads_score ON leads(score);
CREATE INDEX idx_leads_source ON leads(source);
CREATE INDEX idx_leads_business_name ON leads(business_name);
CREATE INDEX idx_leads_owner_email ON leads(owner_email);
CREATE INDEX idx_leads_created_at ON leads(created_at);
CREATE INDEX idx_leads_approved_at ON leads(approved_at);

-- Outreach Messages indexes
CREATE INDEX idx_outreach_messages_lead_id ON outreach_messages(lead_id);
CREATE INDEX idx_outreach_messages_channel ON outreach_messages(channel);
CREATE INDEX idx_outreach_messages_direction ON outreach_messages(direction);
CREATE INDEX idx_outreach_messages_sent_at ON outreach_messages(sent_at);
CREATE INDEX idx_outreach_messages_replied_at ON outreach_messages(replied_at);
CREATE INDEX idx_outreach_messages_lead_sent ON outreach_messages(lead_id, sent_at);

-- Bookings indexes
CREATE INDEX idx_bookings_lead_id ON bookings(lead_id);
CREATE INDEX idx_bookings_scheduled_at ON bookings(scheduled_at);
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_scheduled_status ON bookings(scheduled_at, status);

-- Pipeline Metrics indexes
CREATE INDEX idx_pipeline_metrics_date ON pipeline_metrics(metric_date);
CREATE INDEX idx_pipeline_metrics_state ON pipeline_metrics(state);
CREATE INDEX idx_pipeline_metrics_date_state ON pipeline_metrics(metric_date, state);

-- Notifications indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, read_at) WHERE read_at IS NULL;
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_priority ON notifications(priority);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);

-- Lead Scores indexes
CREATE INDEX idx_lead_scores_lead_id ON lead_scores(lead_id);
CREATE INDEX idx_lead_scores_total_score ON lead_scores(total_score);
CREATE INDEX idx_lead_scores_scored_at ON lead_scores(scored_at);
CREATE INDEX idx_lead_scores_config_version ON lead_scores(scoring_config_version);

-- Scoring Configs indexes
CREATE INDEX idx_scoring_configs_user_id ON scoring_configs(user_id);
CREATE INDEX idx_scoring_configs_user_default ON scoring_configs(user_id, is_default) WHERE is_default = TRUE;

-- User Actions indexes
CREATE INDEX idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX idx_user_actions_lead_id ON user_actions(lead_id);
CREATE INDEX idx_user_actions_action ON user_actions(action);
CREATE INDEX idx_user_actions_created_at ON user_actions(created_at);
CREATE INDEX idx_user_actions_user_lead ON user_actions(user_id, lead_id);

-- Watchlist indexes
CREATE INDEX idx_watchlist_user_id ON watchlist(user_id);
CREATE INDEX idx_watchlist_lead_id ON watchlist(lead_id);
CREATE INDEX idx_watchlist_created_at ON watchlist(created_at);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_market_listings_updated_at BEFORE UPDATE ON market_listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_searches_updated_at BEFORE UPDATE ON saved_searches
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON leads
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scoring_configs_updated_at BEFORE UPDATE ON scoring_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active leads with scores
CREATE VIEW leads_with_scores AS
SELECT 
    l.*,
    ls.total_score,
    ls.revenue_fit_score,
    ls.margin_quality_score,
    ls.exit_signal_score,
    ls.ai_leverage_score,
    ls.valuation_score,
    ls.scored_at
FROM leads l
LEFT JOIN lead_scores ls ON l.id = ls.lead_id
WHERE l.status != 'archived';

-- Pipeline summary by state
CREATE VIEW pipeline_summary AS
SELECT 
    pipeline_state,
    COUNT(*) as lead_count,
    AVG(score) as avg_score,
    MIN(created_at) as oldest_lead,
    MAX(updated_at) as most_recent_activity
FROM leads
WHERE status = 'active'
GROUP BY pipeline_state;

-- Market activity summary
CREATE VIEW market_activity_summary AS
SELECT 
    source,
    DATE(created_at) as date,
    COUNT(*) as listings_added,
    AVG(asking_price) as avg_asking_price,
    AVG(sde_multiple) as avg_sde_multiple
FROM market_listings
GROUP BY source, DATE(created_at)
ORDER BY date DESC;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE market_listings IS 'Raw business listings scraped from various marketplace sources';
COMMENT ON TABLE market_snapshots IS 'Aggregated market statistics captured at regular intervals';
COMMENT ON TABLE saved_searches IS 'User-defined search filters with optional notification alerts';
COMMENT ON TABLE leads IS 'Qualified business opportunities in the acquisition pipeline';
COMMENT ON TABLE lead_scores IS 'AI-generated qualification scores and component breakdowns';
COMMENT ON TABLE scoring_configs IS 'User-configurable scoring criteria and weights';
COMMENT ON TABLE user_actions IS 'Audit trail of all user decisions on leads';
COMMENT ON TABLE watchlist IS 'User-saved leads for quick access and monitoring';
COMMENT ON TABLE outreach_messages IS 'All communication history with leads across channels';
COMMENT ON TABLE bookings IS 'Scheduled meetings and calls with leads';
COMMENT ON TABLE pipeline_metrics IS 'Historical pipeline analytics for trend analysis';
COMMENT ON TABLE notifications IS 'User notification queue for system events';
