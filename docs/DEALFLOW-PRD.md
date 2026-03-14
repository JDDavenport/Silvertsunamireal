# DEALFLOW PRD - Autonomous Deal Sourcing Agent

**Codename:** DEALFLOW  
**Platform:** OpenClaw Agent Tree  
**Author:** JD Davenport  
**Version:** 1.0 | March 2026

---

## 1. Executive Summary

DEALFLOW is a fully autonomous deal sourcing and acquisition outreach agent. It replaces the traditional search fund analyst + broker relationship with an AI agent that:

- Sources qualified acquisition targets
- Manages multi-channel outreach (email + SMS)
- Monitors and responds to inbound communication
- Books discovery calls
- Keeps the principal informed via Telegram/email

**Hackathon Success Criteria:**
| Criteria | Target |
|----------|--------|
| Fully Autonomous | Zero human-in-the-loop (lead → booked call) |
| Daily Outreach | 25+ leads/day |
| Multi-Channel | Email + SMS + Landing Page |
| Real-Time Response | < 5 min reply time |
| Call Booking Rate | > 3% of outreach |
| Principal Notification | 100% of booked calls |

---

## 2. System Architecture

### Core Components

| Component | Type | Role |
|-----------|------|------|
| **Lead Sourcer** | Cron Job | Scrape/qualify leads from BizBuySell, BizQuest, LinkedIn |
| **Outreach Engine** | Cron Job | Send 25+ personalized emails + SMS daily |
| **Inbox Monitor** | Event Hook | Watch Gmail, classify replies, trigger responses |
| **SMS Monitor** | Event Hook | Watch Twilio inbound SMS, classify and respond |
| **Response Agent** | Skill | Generate contextual replies based on conversation history |
| **Booking Agent** | Skill | Detect buying signals, push Cal.com link, confirm bookings |
| **Notification Agent** | Event Hook | Alert JD via Telegram + email |
| **Pipeline Brain** | Heartbeat | Daily pipeline review, re-prioritize, adjust strategy |
| **Landing Page** | Skill | Public-facing 'Sell Your Business' page |

---

## 3. Lead Sourcer (Cron Job)

### Data Sources
1. **BizBuySell / BizQuest** - Scrape listings matching criteria
2. **LinkedIn Sales Navigator** - Owner exit signals
3. **State Business Registrations** - Aging businesses (15+ years)
4. **Broker Feeds** - Email parsing/API
5. **Google Maps / Yelp** - Local business signals
6. **Landing Page Inbound** - Self-submitted leads

### Lead Qualification Criteria (ICP)
| Attribute | Criteria |
|-----------|----------|
| Revenue | $1M-$10M (sweet spot $2-5M) |
| EBITDA Margin | > 15% |
| Industry | Services, light manufacturing, B2B SaaS, healthcare, home services |
| Geography | US-based, remote-manageable |
| Owner Situation | Retirement, burnout, health, strategic exit |
| Asking Multiple | < 4x SDE asset-light, < 5x recurring |
| AI Opportunity | High operational leverage |

### Lead Scoring Model (0-100)
| Factor | Weight |
|--------|--------|
| Revenue Fit | 25 pts |
| Margin Quality | 20 pts |
| Owner Exit Signal | 20 pts |
| AI Leverage Score | 20 pts |
| Valuation Reasonableness | 15 pts |

**Queue Logic:**
- 60+ → Outreach queue automatically
- 40-59 → JD review flag
- < 40 → Archive

### Schedule
- **6:00 AM ET** - Full scrape of all sources
- **Every 4 hours** - Incremental check on primary sources
- **Weekly** - Re-score existing pipeline

---

## 4. Outreach Engine (Cron Job)

### Channel Strategy
| Channel | Volume | Tool |
|---------|--------|------|
| Email | 15-20/day | Gmail API + Warmup |
| SMS | 10-15/day | Twilio API |
| Landing Page | Passive | React on Cloudflare |

### Email Sequence Templates

**Sequence A: Direct Owner Outreach (Cold)**
- Day 0: Introduction (reference specific business details)
- Day 3: Value Add (industry insight)
- Day 7: Direct Ask (clear acquisition interest + Cal.com link)
- Day 14: Breakup (final touch, leave door open)

**Sequence B: Broker/Intermediary**
- Day 0: Professional buyer introduction
- Day 5: Reference specific listings
- Day 12: Market insight share

**Sequence C: Landing Page Inbound**
- Immediate: Acknowledge + qualifying questions
- +30 min: If qualified, Cal.com link
- +24 hrs: SMS follow-up if no response

### SMS Templates
- **Follow-Up:** "Hi [Name], JD here. I sent you an email about [Business] - would love to chat. [Cal.com link]"
- **Reminder:** "Looking forward to our call tomorrow at [time]. [Zoom link] - JD"
- **Inbound Response:** "Thanks for reaching out about selling, [Name]. Can you chat this week? [Cal.com link]"

### Send Schedule
- **Email:** Tue-Thu 9-11 AM recipient local time
- **SMS:** Tue-Thu 10 AM - 2 PM recipient local time
- **Rate Limit:** Max 3 emails/hour from primary domain
- **Domain Warmup:** Week 1: 5/day, increasing by 5/week to 25/day

---

## 5. Inbox Monitor (Event Hook)

### Email Classification
| Category | Action |
|----------|--------|
| **INTERESTED** | Route to Booking Agent |
| **QUESTION** | Route to Response Agent |
| **NOT_NOW** | Schedule nurture (30/60/90 day) |
| **NOT_INTERESTED** | Mark closed-lost |
| **UNSUBSCRIBE** | Remove all sequences |
| **BOUNCE** | Mark invalid, try alternate |
| **AUTO_REPLY** | Pause sequence, resume after OOO |
| **BROKER_REPLY** | Route to Response Agent (broker mode) |

### Architecture
- **Trigger:** Gmail push → Cloudflare Tunnel → OpenClaw Event Hook
- **Latency:** Classification < 2s, response generation < 30s, total reply < 5 min
- **Thread Context:** Load full email thread before responding
- **Deduplication:** Track message IDs

---

## 6. Response Agent (Skill)

### Model Routing
| Scenario | Model | Rationale |
|----------|-------|-----------|
| Email Classification | Haiku | Fast, cheap, accurate |
| Standard Reply | Sonnet | Good quality, reasonable cost |
| Complex Negotiation | Opus | Nuanced responses |
| Lead Scoring | Sonnet | Multi-factor analysis |
| SMS Generation | Haiku | Short messages, fast |

### Guardrails
- ❌ Never commit to specific deal terms
- ❌ Never misrepresent (if asked "are you AI?", acknowledge + redirect)
- ❌ Never pressure (respect 'no' immediately)
- ✅ Always escalate legal/financial questions to JD
- ✅ CAN-SPAM: Unsubscribe in every email, physical address
- ✅ TCPA: SMS only with prior relationship or explicit consent

---

## 7. Booking Agent (Skill)

### Buying Signal Detection
- **Explicit:** "I'd like to talk", "when can we meet", "send me more info"
- **Implicit:** Multiple replies, detailed financial questions, forwarding to partner
- **Broker Signal:** Offering CIM, requesting proof of funds

### Booking Flow
1. Signal detected by Response Agent
2. Generate reply with Cal.com link
3. Cal.com webhook fires on booking
4. Notification Agent sends Telegram + email to JD
5. Confirmation email + SMS to lead
6. 24-hour reminder SMS
7. Post-call: Pipeline Brain updates status

### Cal.com Integration
- **Current:** https://jddavenport.com/book
- **Event Types:** 30-min Discovery Call, 15-min Quick Intro
- **Availability:** Synced with Google Calendar
- **Webhooks:** booking.created, booking.cancelled, booking.rescheduled

---

## 8. Landing Page

### Page Structure
- **Hero:** "Looking to Sell Your Business? I Want It."
- **Value Props:** No Brokers, Fast Timeline (30-60 days), Operational Expertise
- **About:** JD bio - MBA, Deloitte, tech + operations background
- **Qualifying Form:** Business name, revenue, industry, owner info, why selling
- **Embedded Calendar:** Cal.com for immediate booking
- **Social Proof:** Testimonials/credibility markers

### Tech Stack
- **Frontend:** React on Cloudflare Pages
- **Form Backend:** Hono API → PostgreSQL → triggers Sequence C
- **Analytics:** Plausible/PostHog
- **SEO:** "sell my business [city]", "business buyer", "sell business no broker"

---

## 9. Notification Agent (Event Hook)

### Triggers
| Event | Priority | Telegram | Email |
|-------|----------|----------|-------|
| Call Booked | CRITICAL | Immediate + Pin | Yes |
| Hot Lead Reply | HIGH | Immediate | Yes |
| Lead Needs Escalation | HIGH | Immediate | Yes |
| Daily Pipeline Summary | MEDIUM | 8 AM | Yes |
| Outreach Completed | LOW | End of day batch | No |
| System Error | CRITICAL | Immediate | Yes |
| Weekly Metrics | MEDIUM | Sunday 6 PM | Yes |

### Telegram Format
```
[DEALFLOW] [PRIORITY] [EVENT TYPE]
Lead: [Business Name] | [Revenue] | [Score]
Context: [1-2 sentence summary]
Action Required: [Yes/No + what to do]
Thread: [Link to conversation]
```

---

## 10. Pipeline Brain (Heartbeat)

### Daily Heartbeat Cycle
- **6:00 AM** - Source: Run Lead Sourcer, ingest new leads
- **6:30 AM** - Score: Score new leads, re-score existing
- **7:00 AM** - Plan: Select today's 25+ outreach targets
- **8:00 AM** - Brief JD: Send daily pipeline summary (Telegram)
- **9:00 AM-5:00 PM** - Execute: Send emails/SMS, process replies
- **6:00 PM** - Review: Analyze results, flag leads needing intervention
- **9:00 PM** - Optimize: A/B test analysis, adjust scoring weights

### Pipeline States
| State | Description | Auto-Transition |
|-------|-------------|-----------------|
| NEW | Just sourced | → OUTREACH after scoring |
| OUTREACH | Active sequence | → ENGAGED on reply |
| ENGAGED | Conversation active | → QUALIFIED on buying signal |
| QUALIFIED | Booking attempted | → BOOKED on confirmation |
| BOOKED | Call scheduled | → JD_REVIEW after call |
| JD_REVIEW | Evaluating post-call | Manual → LOI/CLOSED |
| NURTURE | Not now, future potential | → OUTREACH after period |

---

## 11. Database Schema

### Key Tables
- **leads** - Core pipeline with state, score, source tracking
- **outreach_messages** - Multi-channel communication history
- **bookings** - Meeting scheduler with Cal.com integration
- **pipeline_metrics** - Historical analytics
- **notifications** - User notification queue

### Extensions
- **pgvector** - Semantic search on lead descriptions and conversations

---

## 12. Third-Party Integrations

| Service | Purpose | Cost Estimate | Priority |
|---------|---------|---------------|----------|
| Gmail API | Email send/receive | Free (Workspace) | P0 |
| Twilio | SMS | ~$75/mo | P0 |
| Cal.com | Scheduling | $12/mo | P0 |
| Telegram Bot | JD notifications | Free | P0 |
| Claude API | AI reasoning | $200-400/mo | P0 |
| Cloudflare Pages | Landing page | Free tier | P1 |
| Email Warmup | Deliverability | ~$30/mo | P1 |
| Scraping Proxies | Lead sourcing | ~$50/mo | P1 |

**Total Monthly:** $370-570 (vs. $50-100K/year human analyst)

---

## 13. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- PostgreSQL schema setup
- SOUL.md configuration
- Lead Sourcer v1 (BizBuySell scraper)
- Lead scoring model v1
- Gmail API integration
- Inbox Monitor with classification
- Response Agent v1
- Cal.com webhook
- Notification Agent
- Outreach Engine v1 (10 leads/day, email-only)

**Milestone:** First autonomous email → reply → booking → notification loop

### Phase 2: Multi-Channel + Landing Page (Week 3-4)
- Twilio SMS integration
- SMS Monitor Event Hook
- Landing page deployment
- Landing page form → Sequence C
- Migrate Cal.com to primary domain
- Add BizQuest, LinkedIn, Google Maps sourcing
- Email warmup schedule
- Scale to 25 leads/day
- Daily pipeline summary

**Milestone:** 25 leads/day across email + SMS, landing page live

### Phase 3: Intelligence + Optimization (Week 5-6)
- Pipeline Brain Heartbeat
- A/B testing framework
- Semantic search (pgvector)
- Send-time optimization
- Weekly metrics report
- Plaud transcript integration
- Nurture sequences
- Broker relationship management

**Milestone:** Self-optimizing agent with measurable improvement

### Phase 4: Hackathon Polish (Week 7-8)
- DEALFLOW dashboard (React)
- Demo video recording
- Hackathon submission narrative
- OpenClaw marketplace listing
- Stress test: 50 leads/day for 3 days
- Presentation deck
- Edge case hardening

**Milestone:** Hackathon submission complete, agent fully autonomous

---

## 14. Success Metrics

| Metric | Target | Good | Great |
|--------|--------|------|-------|
| Daily Outreach Volume | 25/day | 30+ | 50+ |
| Email Open Rate | > 40% | > 50% | > 60% |
| Reply Rate | > 8% | > 12% | > 18% |
| Positive Reply Rate | > 3% | > 5% | > 8% |
| Call Booking Rate | > 2% | > 3% | > 5% |
| Response Time | < 5 min | < 2 min | < 1 min |
| Autonomy Rate | > 90% | > 95% | > 98% |
| Monthly API Cost | < $500 | < $350 | < $250 |
| Cost per Booked Call | < $50 | < $30 | < $15 |

---

## 15. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Email deliverability issues | High | High | Domain warmup, SPF/DKIM/DMARC, warmup service |
| AI generates inappropriate response | Medium | High | SOUL.md guardrails, review queue, escalation rules |
| CAN-SPAM/TCPA violation | Low | Critical | Built-in compliance, unsubscribe handling, consent tracking |
| API cost overrun | Medium | Low | Smart model routing, daily budget caps, cost monitoring |
| Scraping blocked | Medium | Medium | Rotating proxies, rate limiting, multiple sources |
| Cal.com downtime | Low | Medium | Fallback to email scheduling, retry logic |

---

## 16. Hackathon Differentiators

**Why This Wins:**
1. **Real Business, Real Revenue** - Every booked call = potential multi-million dollar transaction
2. **True Full-Loop Autonomy** - Lead sourcing through booked call with zero human touch
3. **Multi-Channel Orchestration** - Email + SMS + landing page + calendar + Telegram
4. **Built on a Platform** - Not a standalone script, proves OpenClaw as generalizable agent OS
5. **Smart Cost Architecture** - Haiku/Sonnet/Opus routing = <$500/mo vs. $100K+ human
6. **Compliance-First** - CAN-SPAM and TCPA baked in from day one
7. **Measurable Metrics** - Every action tracked, dashboard tells story with data

---

*Built on OpenClaw. Powered by Agent Tree.*  
*For entrepreneurs who buy businesses.*
