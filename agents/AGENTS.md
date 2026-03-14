# ACQUISITOR - Agent Tree

## Agent Hierarchy

```
ACQUISITOR (Platform Orchestrator)
├── SCOUT (Market Intelligence Agent)
│   ├── BizBuySell Scraper
│   ├── BizQuest Scraper
│   ├── Market Snapshot Aggregator
│   └── Research Assistant
├── QUALIFY (Lead Scoring Agent)
│   ├── Scoring Engine
│   ├── Comparable Deal Matcher
│   └── AI Assessment Generator
└── DEALFLOW (Outreach & CRM Agent)
    ├── Inbox Monitor
    ├── Response Agent
    ├── SMS Agent
    └── Booking Agent
```

## Agent Descriptions

### SCOUT - Market Intelligence Agent
**Role:** Discover and map the acquisition landscape
**Tools:** Playwright scrapers, pgvector, market analysis skills
**Cron Jobs:** Daily scrapes at 6 AM, weekly trend analysis
**Memory:** Market snapshots, listing archive, saved searches

### QUALIFY - Lead Scoring Agent
**Role:** Evaluate and score leads for fit
**Tools:** Scoring algorithms, pgvector similarity search, Claude API
**Cron Jobs:** Score new listings hourly, weekly model evaluation
**Memory:** Score history, user preferences, rejection patterns

### DEALFLOW - Outreach & CRM Agent
**Role:** Execute autonomous outreach and manage pipeline
**Tools:** Gmail API, Twilio, Cal.com, Telegram
**Cron Jobs:** Outreach engine (25+/day), Pipeline Brain daily heartbeat
**Memory:** Conversation history, engagement patterns, pipeline state

## Integration Points

**SCOUT → QUALIFY:** New listings trigger automatic scoring
**QUALIFY → DEALFLOW:** Approved leads enter outreach queue
**DEALFLOW → SCOUT:** Engagement data feeds back to scoring model
**All → Platform:** Metrics and activity feed to Dashboard

## Communication Protocol

Agents communicate via:
1. Database state changes (PostgreSQL)
2. Redis pub/sub for real-time events
3. Direct API calls for synchronous operations
4. Event hooks for asynchronous workflows

## Failure Handling

- Each agent has retry logic with exponential backoff
- Failed operations logged to notification center
- Critical failures escalate to human via Telegram
- Degraded mode: agents continue operating with reduced functionality

## Scaling Considerations

Current target: 25 leads/day outreach
Phase 2 target: 100 leads/day
Phase 3 target: 250+ leads/day with multi-tenant support

Agents are stateless where possible, allowing horizontal scaling.
