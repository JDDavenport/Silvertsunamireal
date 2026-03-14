# ACQUISITOR MASTER PRD v2.0
## Complete Acquisition Intelligence Platform

**Codename:** ACQUISITOR  
**Author:** JD Davenport  
**Date:** March 14, 2026  
**Classification:** Production Architecture Document

---

# TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Platform Vision](#2-platform-vision)
3. [System Architecture](#3-system-architecture)
4. [Module Specifications](#4-module-specifications)
5. [Data Models](#5-data-models)
6. [API Specifications](#6-api-specifications)
7. [Master Roadmap](#7-master-roadmap)
8. [Success Metrics](#8-success-metrics)

---

# 1. EXECUTIVE SUMMARY

## 1.1 Problem Statement

Buying a small business is a full-time research and outreach job before a single deal closes. The typical search fund operator spends **6-18 months** sourcing deals with:

- **5-10 separate tools** (BizBuySell + Excel + CRM + email + phone + calendar + notes)
- **Manual review** of hundreds of listings
- **Spreadsheet qualification** of leads
- **One-by-one cold emails**
- **Under 1%** conversion rate from lead to closed deal
- **$50-100K/year** spent on analyst salary + broker fees

## 1.2 Solution

**ACQUISITOR** is a full-stack acquisition intelligence platform that replaces the entire analyst + broker + tool stack with a single AI-native system. Built on OpenClaw Agent Tree, it autonomously:

1. **INTAKE** — Captures buyer constraints via conversational bot
2. **SCOUT** — Discovers businesses matching criteria from 6+ sources
3. **QUALIFY** — Scores and filters leads with explainable AI
4. **DEALFLOW** — Manages autonomous outreach, response handling, and booking

## 1.3 Key Differentiators

| Feature | Traditional | ACQUISITOR |
|---------|-------------|------------|
| Cost | $50-100K/year + brokers | $340-620/month |
| Lead Volume | 50-100/month (manual) | 500+/month (automated) |
| Response Time | Hours/days | < 5 minutes |
| Outreach Channels | Email only | Email + SMS + Landing Page |
| Human Touchpoints | Every step | Zero (lead → booked call) |

---

# 2. PLATFORM VISION

## 2.1 North Star

> "An AI agent that autonomously acquires and manages a pipeline of business acquisition leads with zero human intervention between lead identification and booked discovery call, achieving 25+ qualified outreach touches per day."

## 2.2 Hackathon Success Criteria

| Criteria | Target |
|----------|--------|
| Fully Autonomous | Zero human-in-the-loop (lead → booked call) |
| Daily Outreach Volume | 25+ leads/day |
| Multi-Channel | Email + SMS + Landing Page |
| Real-Time Response | < 5 min reply time |
| Call Booking Rate | > 3% of outreach |
| Principal Notification | 100% of booked calls |

---

# 3. SYSTEM ARCHITECTURE

## 3.1 Four-Module Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ACQUISITOR PLATFORM                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌───────────┐ │
│  │   INTAKE    │───▶│    SCOUT    │───▶│   QUALIFY   │───▶│ DEALFLOW  │ │
│  │  (Matching) │    │ (Discovery) │    │  (Scoring)  │    │(Outreach) │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────┬─────┘ │
│         │                                                        │       │
│         │              ┌─────────────────────────────────────────┘       │
│         │              ▼                                                │
│         │       ┌─────────────┐                                         │
│         │       │  DASHBOARD  │                                         │
│         │       │  (Pipeline) │                                         │
│         │       └─────────────┘                                         │
│         │              ▲                                                │
│         └──────────────┘                                                │
│                   EXPLORE                                               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3.2 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend API | Hono (TypeScript) |
| Database | PostgreSQL + pgvector |
| Cache/Queue | Redis |
| Frontend | React (Cloudflare Pages) |
| Compute | Mac Mini (Docker) |
| AI Engine | Claude API (Haiku/Sonnet/Opus) |
| Object Storage | Cloudflare R2 |
| Tunnel | Cloudflare Tunnel |

---

# 4. MODULE SPECIFICATIONS

## 4.1 MODULE: INTAKE (ETA Matching Bot)

### Purpose
Captures buyer constraints into standardized JSON payload for Discovery Agent.

### Five Target Personas

| Persona | Archetype |
|-----------|------------|
| **Marcus** | MBA Searcher |
| **Diane** | Lifestyle Buyer |
| **Ray** | Operator-Acquirer |
| **Priya** | Portfolio Builder |
| **Jordan** | Remote-First Buyer |

### JSON Schema Output

```json
{
  "buyer_id": "uuid",
  "persona_id": "marcus_mba",
  "geography": {
    "type": "radius",
    "radius_mi": 300,
    "anchor_location": "Salt Lake City, UT"
  },
  "financial_target": {
    "metric": "revenue",
    "min": 1000000,
    "max": 5000000
  },
  "margin": { "min_pct": 20 },
  "operator_type": "gm_hire",
  "industry_rules": {
    "include": ["any"],
    "exclude": ["food"]
  },
  "max_sde_multiple": 4.0,
  "max_price": 2100000,
  "revenue_trend": ["growing", "flat"],
  "distress_ok": false
}
```

### Success Metrics

| Metric | Target |
|--------|--------|
| Match Accuracy | > 90% |
| Intake Efficiency | < 10 prompts |
| User Override Rate | < 15% |
| Completion Rate | > 80% |

---

## 4.2 MODULE: SCOUT (Discovery)

### Purpose
Identifies qualified businesses matching buyer persona from 6+ data sources.

### Data Sources

| Source | Type | Refresh Rate |
|--------|------|--------------|
| BizBuySell | Marketplace | Daily |
| BizQuest | Marketplace | Daily |
| State Registries | Public Record | Weekly |
| Google Maps | Directory | Weekly |
| Industry Associations | Directory | Monthly |
| Company Websites | Primary | On-demand |

### Functional Components

1. **Payload Interpreter** — Validate and normalize constraints
2. **Search Planner** — Generate search strategies per source
3. **Discovery Agents** — Parallel execution across sources
4. **Deduplication** — Exact and fuzzy matching
5. **Contact Discovery** — Owner contact identification
6. **Data Enrichment** — Revenue/SDE estimation with confidence
7. **Hard Filter Enforcement** — Mandatory criteria checking
8. **Lead Qualification Scoring** — 0-100 score with explanations

### Success Metrics

| Metric | Target |
|--------|--------|
| Qualified leads per run | ≥ 10 |
| Contact discovery rate | ≥ 60% |
| Hard filter pass rate | ≥ 20% |
| Lead generation runtime | < 60 seconds |

---

## 4.3 MODULE: QUALIFY (Lead Scoring)

### Scoring Model (0-100)

| Factor | Weight | Description |
|--------|--------|-------------|
| Revenue Fit | 25 pts | $2-5M sweet spot alignment |
| Margin Quality | 20 pts | EBITDA margin + improvement potential |
| Owner Exit Signal | 20 pts | Exit motivation strength |
| AI Leverage Score | 20 pts | Operational improvement potential |
| Valuation Reasonableness | 15 pts | Asking price vs earnings/comps |

### Queue Logic

| Score | Action |
|-------|--------|
| 80-100 | Immediate outreach queue |
| 60-79 | Standard outreach queue |
| 40-59 | JD review flag |
| < 40 | Archive with reason |

### User Actions

- **Approve** → Enter DEALFLOW queue
- **Reject** → Archive (improves future scoring)
- **Watchlist** → Monitor, no outreach
- **Re-score** → Force re-evaluation

---

## 4.4 MODULE: DEALFLOW (Outreach & CRM)

### Core Components

| Component | Type | Role |
|-----------|------|------|
| Lead Sourcer | Cron | Daily lead scraping |
| Outreach Engine | Cron | 25+ emails + SMS daily |
| Inbox Monitor | Event Hook | Gmail classification |
| Response Agent | Skill | AI reply generation |
| Booking Agent | Skill | Signal detection + booking |
| Notification Agent | Event Hook | Telegram/email alerts |
| Pipeline Brain | Heartbeat | Daily cycle management |

### Channel Strategy

| Channel | Volume | Tool |
|---------|--------|------|
| Email | 15-20/day | Gmail API + Warmup |
| SMS | 10-15/day | Twilio API |
| Landing Page | Passive | React + Cloudflare |

### Email Sequences

**Sequence A: Direct Owner Outreach**
- Day 0: Introduction (reference business details)
- Day 3: Value-add insight
- Day 7: Direct ask + Cal.com link
- Day 14: Breakup message

**Sequence B: Broker Outreach**
- Day 0: Professional buyer intro
- Day 5: Reference specific listings
- Day 12: Market insight share

**Sequence C: Landing Page Inbound**
- Immediate: Acknowledge + qualifying questions
- +30 min: Cal.com link if qualified
- +24 hrs: SMS follow-up

### Pipeline States

| State | Transition |
|-------|------------|
| NEW | → OUTREACH after scoring |
| OUTREACH | → ENGAGED on reply |
| ENGAGED | → QUALIFIED on buying signal |
| QUALIFIED | → BOOKED on confirmation |
| BOOKED | → JD_REVIEW after call |
| JD_REVIEW | → LOI / CLOSED |

---

# 5. DATA MODELS

## Core Entities

### buyers
- id, email, name, phone, persona_id, constraints (JSONB)

### leads
- id, buyer_id, source, business_name, owner_contact
- financials (revenue, ebitda, asking_price)
- location (city, state, lat, lng)
- description + embedding (vector)
- score, score_breakdown, ai_assessment
- pipeline_state, status, timestamps

### outreach_messages
- id, lead_id, channel, direction, subject, body
- classification, sequence_name, sent_at, opened_at, replied_at

### bookings
- id, lead_id, cal_event_id, scheduled_at, meeting_url, status

### notifications
- id, buyer_id, lead_id, type, priority, message, channel, sent_at

---

# 6. API SPECIFICATIONS

## Key Endpoints

### INTAKE
```
POST /api/intake/start
POST /api/intake/answer
GET  /api/intake/:id
```

### SCOUT
```
GET /api/scout/search
GET /api/scout/leads
GET /api/scout/leads/:id
```

### QUALIFY
```
GET    /api/qualify/queue
POST   /api/qualify/leads/:id/approve
POST   /api/qualify/leads/:id/reject
POST   /api/qualify/leads/:id/watchlist
```

### DEALFLOW
```
GET  /api/dealflow/pipeline
GET  /api/dealflow/activity
GET  /api/dealflow/metrics
GET  /api/dealflow/bookings
POST /api/dealflow/outreach/send
POST /api/dealflow/webhooks/cal
```

---

# 7. MASTER ROADMAP

## Phase 0: Foundation ✓ COMPLETE
**Duration:** Week 1  
**Status:** DELIVERED

### Deliverables
| Component | Status |
|-----------|--------|
| Monorepo structure | ✅ Complete |
| Database schema (12 tables) | ✅ Complete |
| Hono API backend | ✅ Complete |
| React frontend shell | ✅ Complete |
| Docker Compose setup | ✅ Complete |
| SOUL.md + AGENTS.md | ✅ Complete |

### Code Delivered
- 34 files created
- 8,792 lines of code
- GitHub repo: https://github.com/JDDavenport/Silvertsunamireal

---

## Phase 1: Core Agents
**Duration:** Weeks 2-4  
**Status:** IN PROGRESS (80% Complete)

### Week 2: Discovery & Scraping

#### Day 8-9: Discovery Agent
| Task | Priority | Owner | Deliverable |
|------|----------|-------|-------------|
| Payload Interpreter | P0 | Builder | Constraint parsing, validation |
| Search Planner | P0 | Builder | Source selection, query generation |
| Discovery Agents (4) | P0 | Builder | Directory, Registry, Marketplace, Website |
| Contact Discovery | P1 | Builder | Owner contact identification |
| Deduplication Engine | P1 | Builder | Fuzzy matching, similarity scoring |

**Deliverables:**
- `agents/scout/payload_interpreter.py`
- `agents/scout/search_planner.py`
- `agents/scout/discovery_agents/` (4 modules)
- `agents/scout/contact_discovery.py`
- `agents/scout/deduplication.py`

#### Day 10-11: BizBuySell Scraper
| Task | Priority | Deliverable |
|------|----------|-------------|
| Playwright scraper | P0 | bizbuysell.py with pagination |
| Data extraction | P0 | Parse all listing fields |
| PostgreSQL storage | P0 | Insert with deduplication |
| Rate limiting | P1 | Respectful delays |
| Error handling | P1 | Retry logic, logging |

**Deliverables:**
- `scrapers/bizbuysell.py`
- CLI interface: `python bizbuysell.py --pages 5 --location "Texas"`

#### Day 12-14: Data Enrichment
| Task | Priority | Deliverable |
|------|----------|-------------|
| Revenue estimation | P1 | Industry comps × employees |
| SDE calculation | P1 | Revenue × margin benchmarks |
| Owner dependency signals | P2 | Founder mentions, team size |
| Confidence scoring | P2 | 0-1 score per inference |

**Deliverables:**
- `agents/scout/enrichment.py`
- Confidence scoring model

**Phase 1 Week 2 Gates:**
- [ ] Can discover 500+ candidates in < 60 seconds
- [ ] Contact discovery rate ≥ 60%
- [ ] Deduplication accuracy > 95%

---

### Week 3: QUALIFY Module

#### Day 15-17: Scoring Engine
| Task | Priority | Owner | Deliverable |
|------|----------|-------|-------------|
| Scoring algorithm | P0 | Builder | 0-100 composite score |
| Weight configuration | P0 | Builder | Adjustable criteria weights |
| Score explanation | P1 | Builder | Human-readable rationale |
| Comparable deals | P1 | Builder | Similar business lookup |

**Deliverables:**
- `agents/qualify/scoring.py`
- `agents/qualify/comps.py`
- Score configuration UI

#### Day 18-19: AI Assessment
| Task | Priority | Deliverable |
|------|----------|-------------|
| Assessment generation | P1 | Claude-generated summaries |
| Why fit / Key risks | P1 | Structured output |
| Discovery questions | P2 | Call prep questions |
| Improvement estimates | P2 | AI leverage assessment |

**Deliverables:**
- `agents/qualify/assessment.py`
- Structured assessment JSON

#### Day 20-21: User Actions
| Task | Priority | Deliverable |
|------|----------|-------------|
| Approve/Reject flow | P0 | Database updates, queue management |
| Watchlist | P1 | Monitor without outreach |
| Action logging | P1 | Audit trail |

**Deliverables:**
- QUALIFY API endpoints
- Action handler logic

**Phase 1 Week 3 Gates:**
- [ ] Scoring completes in < 2 seconds per lead
- [ ] Score accuracy validated against human judgment
- [ ] AI assessments are actionable

---

### Week 4: DEALFLOW Core

#### Day 22-24: Outreach Engine
| Task | Priority | Owner | Deliverable |
|------|----------|-------|-------------|
| Gmail API integration | P0 | Builder | OAuth, send/receive |
| Twilio SMS | P0 | Builder | Send/receive SMS |
| Sequence templates | P0 | Builder | A/B/C sequences |
| Personalization | P1 | Builder | Dynamic field injection |
| Scheduler | P1 | Builder | Optimal send times |

**Deliverables:**
- `agents/dealflow/outbox.py`
- `agents/dealflow/sequences.py`
- `agents/dealflow/scheduler.py`

#### Day 25-27: Inbox & Response
| Task | Priority | Deliverable |
|------|----------|-------------|
| Gmail webhook | P0 | Inbox Monitor with classification |
| Email classifier | P0 | 8-category classification (Haiku) |
| Response Agent | P0 | Contextual reply generation |
| Model routing | P1 | Haiku/Sonnet/Opus selection |
| Guardrails | P1 | Compliance checking |

**Deliverables:**
- `agents/dealflow/inbox_monitor.py`
- `agents/dealflow/response_agent.py`

#### Day 28-30: Booking & Notifications
| Task | Priority | Deliverable |
|------|----------|-------------|
| Signal detection | P0 | Explicit/implicit buying signals |
| Cal.com integration | P0 | Webhook handlers, booking flow |
| Confirmation messages | P1 | Email + SMS confirmations |
| Reminder system | P1 | 24-hour SMS reminders |
| Telegram alerts | P0 | Critical notification pipeline |
| Email backup | P1 | SMTP notification fallback |

**Deliverables:**
- `agents/dealflow/booking_agent.py`
- `agents/dealflow/notification_agent.py`

**Phase 1 Week 4 Gates:**
- [ ] 25 emails + SMS sent daily
- [ ] Response classification < 2 seconds
- [ ] Call booking rate > 3%
- [ ] 100% of bookings trigger notifications

---

## Phase 2: Integration & Polish
**Duration:** Weeks 5-6

### Week 5: Integration

#### Day 31-33: Pipeline Brain
| Task | Priority | Deliverable |
|------|----------|-------------|
| Heartbeat setup | P0 | Daily cycle automation |
| 6 AM sourcing | P0 | Lead Sourcer cron |
| 8 AM brief | P0 | Telegram morning summary |
| Auto-optimization | P1 | A/B test result application |

**Deliverables:**
- `agents/pipeline_brain.py`
- Daily heartbeat configuration

#### Day 34-35: Frontend Integration
| Task | Priority | Deliverable |
|------|----------|-------------|
| EXPLORE view | P0 | Lead discovery UI |
| DASHBOARD view | P0 | Pipeline kanban board |
| Lead detail page | P0 | Score breakdown, actions |
| Activity feed | P1 | Real-time updates |
| Metrics panel | P1 | Outreach statistics |

**Deliverables:**
- React components for all views
- WebSocket integration

#### Day 36-37: End-to-End Testing
| Task | Priority | Deliverable |
|------|----------|-------------|
| Full pipeline test | P0 | Lead → booking flow |
| Error injection | P1 | Failure mode testing |
| Performance testing | P1 | Load testing at 50 leads/day |
| Security audit | P2 | OWASP top 10 check |

**Phase 2 Week 5 Gates:**
- [ ] Full autonomous flow works end-to-end
- [ ] No critical errors in 48-hour test
- [ ] Frontend renders all data correctly

---

### Week 6: Polish & Launch Prep

#### Day 38-40: UI/UX Polish
| Task | Priority | Deliverable |
|------|----------|-------------|
| Loading states | P1 | Skeleton screens, spinners |
| Error states | P1 | Friendly error messages |
| Empty states | P2 | Helpful empty views |
| Responsive design | P2 | Mobile-friendly layout |

#### Day 41-42: Documentation
| Task | Priority | Deliverable |
|------|----------|-------------|
| API docs | P0 | OpenAPI specification |
| Deployment guide | P1 | Docker setup instructions |
| Environment setup | P1 | .env.example, secrets guide |
| Troubleshooting | P2 | Common issues, fixes |

**Phase 2 Week 6 Gates:**
- [ ] All UI polished and responsive
- [ ] Documentation complete
- [ ] Ready for production deployment

---

## Phase 3: Production Launch
**Duration:** Week 7

### Day 43-45: Production Deployment
| Task | Priority | Deliverable |
|------|----------|-------------|
| Environment setup | P0 | Production .env configured |
| Database migration | P0 | Production PostgreSQL |
| Domain setup | P0 | DNS, SSL certificates |
| Monitoring | P1 | Uptime alerts, error tracking |

### Day 46-48: Soft Launch
| Task | Priority | Deliverable |
|------|----------|-------------|
| Beta testing | P0 | 5 test users, feedback |
| Bug fixes | P0 | Critical issues resolved |
| Performance tuning | P1 | Query optimization |
| Cost monitoring | P1 | API spend tracking |

### Day 49: Public Launch
| Task | Priority | Deliverable |
|------|----------|-------------|
| Launch announcement | P0 | Social media, email |
| Hackathon submission | P0 | Podium.com entry |
| Demo video | P0 | Full loop walkthrough |
| Press kit | P1 | Screenshots, description |

**Phase 3 Gates:**
- [ ] Live in production
- [ ] Hackathon submission complete
- [ ] Demo video recorded

---

## Phase 4: Scale & Intelligence
**Duration:** Weeks 8-12

### Week 8-9: Enhanced Discovery
| Feature | Description |
|---------|-------------|
| Additional sources | LinkedIn, Crunchbase, AngelList |
| Industry-specific agents | HVAC, plumbing, SaaS specialists |
| Geographic expansion | Multi-state, national coverage |
| Predictive sourcing | ML-based lead ranking |

### Week 10-11: Advanced Outreach
| Feature | Description |
|---------|-------------|
| A/B testing framework | Subject line, body variants |
| Send-time optimization | Per-recipient optimal timing |
| Personalization v2 | Deep research, custom angles |
| Multi-touch sequences | 7+ touch sequences |

### Week 12: Platform Features
| Feature | Description |
|---------|-------------|
| Multi-tenant support | Multiple buyers per instance |
| Broker portal | Dedicated broker interface |
| Mobile app | iOS/Android companion |
| API access | Third-party integrations |

---

# 8. SUCCESS METRICS

## Platform-Level Metrics

| Metric | Phase 1 Target | Phase 2 Target | Phase 3 Target |
|--------|----------------|----------------|----------------|
| Daily Outreach Volume | 25 leads | 40 leads | 75 leads |
| Email Open Rate | > 40% | > 50% | > 60% |
| Reply Rate | > 8% | > 12% | > 18% |
| Call Booking Rate | > 2% | > 3% | > 5% |
| Response Time | < 5 min | < 2 min | < 1 min |
| Autonomy Rate | > 90% | > 95% | > 98% |
| Cost per Booked Call | < $50 | < $30 | < $15 |
| Monthly API Cost | < $500 | < $400 | < $300 |

## Module-Specific Metrics

### INTAKE
- Match accuracy: > 90%
- Completion rate: > 80%
- Avg prompts to complete: < 10

### SCOUT
- Leads per run: ≥ 10 qualified
- Contact discovery: ≥ 60%
- Runtime: < 60 seconds

### QUALIFY
- Scoring accuracy: > 85%
- AI assessment usefulness: > 4/5

### DEALFLOW
- Emails delivered: > 95%
- SMS delivered: > 98%
- Call booking: > 3%
- JD notifications: 100%

---

# APPENDIX: Current Status

## Built Components ✓

### SCOUT
- ✅ Payload Interpreter
- ✅ Search Planner  
- ✅ Discovery Agents (4)
- ✅ Contact Discovery
- ✅ Deduplication
- ✅ BizBuySell Scraper

### DEALFLOW
- ✅ Outbox (Gmail/Twilio)
- ✅ Sequences (A/B/C)
- ✅ Scheduler
- ✅ Inbox Monitor
- ✅ Response Agent
- ✅ Booking Agent
- ✅ Notification Agent

### Infrastructure
- ✅ Database schema
- ✅ API backend
- ✅ React frontend
- ✅ Docker setup

## Remaining Work

1. **Integration Testing** — Wire all components
2. **Pipeline Brain** — Daily heartbeat automation
3. **Frontend Polish** — Connect to APIs
4. **Environment Setup** — Production config
5. **Documentation** — Deployment guide

---

*Document Version: 2.0*  
*Last Updated: March 14, 2026*  
*Repository: https://github.com/JDDavenport/Silvertsunamireal*
