# ACQUISITOR - Acquisition Intelligence Platform

**Codename:** ACQUISITOR  
**Full Stack Platform** for entrepreneurs, search fund operators, and independent sponsors acquiring $1M-$10M revenue businesses.

Built on OpenClaw | Powered by Agent Tree

---

## 🎯 Mission

Replace the $100K/year analyst + fragmented tool stack with a single AI-native platform that autonomously finds, qualifies, and contacts business sellers.

**The Old Way:**
- BizBuySell + Excel + CRM + Email client + Phone + Calendar + Notes = 5-10 separate tools
- 6-18 months sourcing deals manually
- Under 1% conversion rate from lead to closed deal

**ACQUISITOR Way:**
- One platform, one price: $340-620/month
- 25+ leads/day autonomous outreach
- AI handles research → qualification → outreach → booking
- Human focuses on closing, not finding

---

## 🏗️ Three Modules

### SCOUT - Market Intelligence & Discovery
Research and map the entrepreneurship-through-acquisition market.

**Answers:** *"What does the acquisition market look like right now, and where should I be looking?"*

- Market Overview Dashboard (real-time landscape view)
- Industry Analysis (deep-dive verticals, multiples, trends)
- Geographic Heatmaps (listing density, underserved markets)
- Listing Aggregation (unified feed from all sources, deduplicated)
- AI Research Assistant (chat interface for market queries)

### QUALIFY - Lead Scoring & Due Diligence Prep
Score, filter, and prepare leads for outreach.

**Answers:** *"Is this lead worth my time? Does it meet my criteria?"*

- Automated Lead Scoring (0-100 composite score)
- Configurable Scoring Weights
- Lead Detail Pages (business overview, score breakdown, comps)
- Comparable Deal Analysis
- AI Qualification Notes

### DEALFLOW - Autonomous Outreach & CRM
Manage autonomous multi-channel outreach and pipeline.

**Answers:** *"What's happening with my active leads? Who needs my attention?"*

- Autonomous Email + SMS outreach (25+/day)
- Real-time inbox monitoring with AI classification
- SMS monitoring and response
- Cal.com booking automation
- Pipeline Kanban board
- Telegram/email notifications

---

## 🖥️ Two Views

### EXPLORE - Discovery Mindset
*"I'm looking for opportunities. Show me what's out there."*

Left sidebar navigation:
- Market Overview (SCOUT home)
- Industry Deep Dives (SCOUT)
- Lead Discovery (SCOUT + QUALIFY)
- Lead Detail (QUALIFY)
- Saved Searches (SCOUT)
- Watchlist (QUALIFY)

### DASHBOARD - Execution Mindset
*"I have active leads. Show me where things stand."*

Left sidebar navigation:
- Pipeline Overview (DEALFLOW kanban)
- Today's Activity (DEALFLOW feed)
- Outreach Performance (DEALFLOW metrics)
- Booked Calls (DEALFLOW calendar)
- Weekly Report (all modules)
- Agent Status (system health)

---

## 📊 Scoring Model (QUALIFY)

| Factor | Weight | Scoring Logic |
|--------|--------|---------------|
| Revenue Fit | 25 pts | $2-5M = 100%, $1-2M or $5-7M = 80%, $7-10M = 50%, <$1M = 20%, >$10M = 0% |
| Margin Quality | 20 pts | >25% EBITDA = 100%, scales down to 0% at <10% |
| Owner Exit Signal | 20 pts | Listed/retirement = 100%, aging owner = 60%, inferred = 30% |
| AI Operational Leverage | 20 pts | High manual/low tech = 100%, already automated = 20% |
| Valuation | 15 pts | <3x SDE = 100%, 3-4x = 75%, 4-5x = 40%, >5x = 10% |

---

## 🏛️ Architecture

| Component | Technology |
|-----------|------------|
| Backend API | Hono (TypeScript) |
| Database | PostgreSQL + pgvector |
| Cache/Queue | Redis |
| Frontend | React (Cloudflare Pages) |
| Tunnel | Cloudflare Tunnel |
| Compute | Mac Mini (Docker Compose) |
| AI Engine | Claude API (Haiku/Sonnet/Opus) |
| Object Storage | Cloudflare R2 |

---

## 🗓️ Implementation Roadmap

### Phase 0: Foundation Sprint (Days 1-3)
- Monorepo structure: `/api`, `/web`, `/agents`, `/scrapers`
- PostgreSQL schema for all modules
- Docker Compose services
- React shell with EXPLORE/DASHBOARD toggle
- Cloudflare Tunnel endpoints
- SOUL.md for platform identity

### Phase 1: SCOUT MVP (Days 4-10)
- BizBuySell scraper (Playwright)
- BizQuest scraper
- Market snapshot aggregator
- Market Overview page
- Lead Discovery page
- Saved searches

### Phase 2: QUALIFY MVP (Days 11-17)
- Lead scoring engine
- Comparable deal matching (pgvector)
- AI qualification assessment
- Lead Detail page
- Scoring config CRUD
- Onboarding wizard

### Phase 3: DEALFLOW Integration (Days 18-28)
- Gmail API integration
- Twilio SMS
- Cal.com webhooks
- Telegram notifications
- Pipeline Kanban
- Activity feed
- Landing page

### Phase 4: Intelligence Layer (Days 29-35)
- AI Research Assistant
- Geographic heatmaps
- Pipeline Brain heartbeat
- A/B testing framework
- Weekly Report
- Agent Status page

### Phase 5: Polish and Launch (Days 36-42)
- UI polish
- Onboarding flow
- Stress testing (50 leads/day)
- Demo video
- Hackathon submission

---

## 💰 Cost Model

| Line Item | Monthly |
|-----------|---------|
| Claude API | $200-400 |
| Twilio (SMS) | $50-100 |
| Cal.com Pro | $12 |
| Cloudflare | $5-15 |
| Scraping Proxies | $30-50 |
| Email Warmup | $30 |
| Domain + Email | $10 |
| **TOTAL** | **$340-620/month** |

**vs. $50-100K/year** for human analyst + tools

---

## 🎤 Hackathon Narrative

**The Problem:** Buying a small business takes 12-18 months of manual research and outreach. Search fund operators spend $50-100K/year on analysts and broker fees before closing a single deal.

**The Solution:** ACQUISITOR is an AI-powered acquisition platform that does the entire sourcing-to-booked-call workflow autonomously.

**The Demo:** 
1. SCOUT discovers a real business listing this morning
2. QUALIFY scores it at 82/100 with AI-generated assessment
3. DEALFLOW sends personalized outreach email
4. Simulated reply triggers autonomous response and Cal.com booking
5. Telegram notification arrives with full context

**Total human involvement: ZERO**

**The Impact:** $340-620/month replaces $100K+/year. Every booked call is a potential multi-million dollar acquisition.

---

Built by JD Davenport on OpenClaw | March 2026
