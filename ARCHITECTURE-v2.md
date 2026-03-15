# ACQUISITOR V2 - Complete Architecture

## Vision
Autonomous acquisition platform where each user gets their own AI agent that discovers, scores, and contacts businesses on their behalf - with full visibility and control.

## User Flow

### Phase 1: Onboarding (First Visit)
1. **Landing Page** → CTA "Find My Business"
2. **Gmail OAuth** → Authenticate (creates user account)
3. **Intake Chatbot** → 5-10 minute conversation capturing:
   - Professional background
   - Acquisition experience
   - Budget range
   - Industry preferences
   - Location preferences
   - Values/priorities
   - Timeline
4. **Criteria Review** → AI generates search criteria, user approves/modifies
5. **Dashboard Creation** → Dynamically spins up personalized dashboard

### Phase 2: Active Dashboard
- **Agent Status Panel** - Real-time view of what agent is doing
- **Lead Backlog** - Discovered leads waiting for approval
- **Active Pipeline** - Approved leads in various stages
- **CRM View** - All contacts and interactions
- **Configuration Panel** - Adjust agent behavior
- **Analytics** - Market insights and performance metrics

## Core Components

### 1. Authentication System
```
/auth
  - /login - Gmail OAuth
  - /callback - OAuth callback
  - /logout

User model:
- id (UUID)
- email (Gmail)
- name
- created_at
- is_active
- agent_config (JSON)
```

### 2. Onboarding Chatbot
```
/onboarding
  - Chat interface
  - Progressive disclosure (5-10 steps)
  - Contextual questions based on previous answers
  - Criteria preview and editing

Stores in: buyer_profiles table
```

### 3. Dynamic Dashboard
```
/dashboard
  - Real-time WebSocket connection
  - Agent status component
  - Lead backlog (approval queue)
  - Pipeline view
  - CRM table
  - Config panel
  - Analytics charts
```

### 4. Autonomous Agent (Per User)
Each user gets their own agent instance that:
- Discovers leads matching criteria
- Scores them with AI
- Generates personalized emails
- Sends them (with rate limiting)
- Monitors replies
- Books calls

Agent configuration:
- Daily email limit (default: 10)
- Discovery frequency (default: daily)
- Auto-approve threshold (default: off)
- Reply handling mode (manual/auto)

### 5. Real-Time Updates
WebSocket server pushes:
- New leads discovered
- Emails sent
- Replies received
- Status changes
- Agent activity logs

## Database Schema

### users
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    agent_config TEXT -- JSON
);
```

### buyer_profiles
```sql
CREATE TABLE buyer_profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    background TEXT,
    industries TEXT, -- JSON array
    budget_min INTEGER,
    budget_max INTEGER,
    revenue_min INTEGER,
    revenue_max INTEGER,
    location_preference TEXT, -- JSON array
    values TEXT, -- JSON array
    timeline TEXT,
    criteria TEXT, -- JSON generated criteria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### leads (user-specific)
```sql
CREATE TABLE leads (
    id TEXT PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    name TEXT,
    industry TEXT,
    revenue INTEGER,
    employees INTEGER,
    city TEXT,
    state TEXT,
    description TEXT,
    source TEXT,
    source_url TEXT,
    score INTEGER DEFAULT 0,
    status TEXT DEFAULT 'new', -- new, approved, rejected, outreach, engaged, booked
    email TEXT,
    phone TEXT,
    ai_assessment TEXT,
    email_sent INTEGER DEFAULT 0,
    email_sent_at TIMESTAMP,
    reply_received INTEGER DEFAULT 0,
    reply_classification TEXT,
    call_booked INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP
);
```

### agent_activities
```sql
CREATE TABLE agent_activities (
    id INTEGER PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    type TEXT, -- discovery, scoring, email_sent, reply_received, call_booked
    lead_id TEXT,
    description TEXT,
    metadata TEXT, -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### email_logs
```sql
CREATE TABLE email_logs (
    id INTEGER PRIMARY KEY,
    user_id TEXT REFERENCES users(id),
    lead_id TEXT,
    to_email TEXT,
    subject TEXT,
    body TEXT,
    sent_at TIMESTAMP,
    sequence_step INTEGER DEFAULT 0
);
```

## API Endpoints

### Auth
```
POST /auth/login
GET /auth/callback
POST /auth/logout
GET /auth/me
```

### Onboarding
```
POST /onboarding/profile - Save profile from chatbot
GET /onboarding/criteria - Get AI-generated criteria
POST /onboarding/approve - Approve criteria and activate
```

### Dashboard
```
GET /dashboard/stats - User's stats
GET /dashboard/agent-status - Current agent activity
GET /dashboard/leads/backlog - Leads needing approval
GET /dashboard/leads/pipeline - Active leads
GET /dashboard/activities - Recent agent activities
```

### Leads
```
GET /leads - All leads for user
POST /leads/:id/approve - Approve lead
POST /leads/:id/reject - Reject lead
POST /leads/:id/score - AI score lead
POST /leads/:id/email - Send email
POST /leads/:id/book - Book call
```

### Agent Config
```
GET /agent/config - Get current config
POST /agent/config - Update config
POST /agent/pause - Pause agent
POST /agent/resume - Resume agent
```

### WebSocket
```
WS /ws/dashboard - Real-time updates
```

## Frontend Routes

```
/ - Landing page
/login - Auth page
/onboarding - Chatbot flow
/dashboard - Main dashboard
  - /backlog - Lead approval queue
  - /pipeline - Active deals
  - /crm - All contacts
  - /settings - Agent configuration
```

## Real-Time Features

### Agent Status Display
Shows:
- Current activity: "Scanning BizBuySell..." / "Drafting email to Summit Dental..." / "Waiting for replies..."
- Last activity timestamp
- Daily stats: leads discovered, emails sent, replies received
- Health indicator: 🟢 Active / 🟡 Paused / 🔴 Error

### Live Lead Backlog
- Real-time updates as leads are discovered
- One-click approve/reject
- Preview card with score and summary
- Batch actions

### Pipeline Updates
- Cards move automatically as status changes
- Color-coded by stage
- Drag to manually change stage
- Click for detail view

## Agent Configuration Options

Users can configure:
1. **Email Settings**
   - Daily send limit (1-25)
   - Send window (e.g., 9 AM - 5 PM)
   - Signature

2. **Discovery Settings**
   - Frequency: Daily, Every 2 days, Weekly
   - Sources: BizBuySell, LinkedIn, etc.
   - Auto-approve threshold (score > X)

3. **Reply Handling**
   - Manual: Notify me, I reply
   - Semi-auto: Draft reply for my approval
   - Auto: Reply to simple questions

4. **Notification Preferences**
   - Email digest: Daily/Weekly
   - Real-time alerts: High-score leads, replies
   - Quiet hours

## Technical Stack

### Backend
- FastAPI (Python)
- SQLite (user-specific databases or table prefixes)
- WebSocket for real-time
- APScheduler for cron jobs
- Gmail API via gog CLI
- Claude API for AI

### Frontend
- React + TypeScript
- Tailwind CSS (dark mode)
- React Router
- WebSocket client
- Recharts for analytics

### Deployment
- Frontend: Vercel
- Backend: Railway or fly.io
- Database: SQLite (single instance, user-scoped tables)

## Key Files to Create

1. `api/main.py` - FastAPI server
2. `api/auth.py` - Authentication routes
3. `api/agent.py` - Agent orchestration
4. `api/websocket.py` - WebSocket handler
5. `web/src/App.tsx` - Main app with auth
6. `web/src/views/Onboarding.tsx` - Chatbot
7. `web/src/views/Dashboard.tsx` - Main dashboard
8. `web/src/components/AgentStatus.tsx` - Live status
9. `web/src/components/LeadBacklog.tsx` - Approval queue
10. `web/src/components/Pipeline.tsx` - Deal pipeline
11. `web/src/components/CRM.tsx` - Contact management
12. `web/src/components/ConfigPanel.tsx` - Settings

## Implementation Order

1. Auth system + user model
2. Onboarding chatbot
3. Basic dashboard shell
4. Agent status component
5. Lead discovery (real scraper)
6. Lead backlog with approval
7. Pipeline view
8. Email sending
9. Real-time updates (WebSocket)
10. CRM view
11. Config panel
12. Analytics
13. End-to-end testing

## Success Criteria

- User can sign up with Gmail
- Complete onboarding chatbot
- See real leads discovered for THEM
- Approve leads and see them move to pipeline
- Receive actual emails from businesses
- Configure agent behavior
- Watch agent work in real-time
- Full transparency into all activities
