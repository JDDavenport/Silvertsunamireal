# Discovery PRD - Persona-Driven Acquisition Lead Discovery

**Product:** Business Acquisition Service Platform  
**Version:** v1.0 Production Draft  
**Author:** JD Davenport

---

## 1. Product Overview

The Persona-Driven Acquisition Lead Discovery system identifies qualified businesses that match a buyer's acquisition criteria. It converts buyer preferences collected by the Intake Bot into structured search rules, discovers candidate businesses, enriches their data, and returns verified leads with the best available point of contact.

**Output feeds into:** Analyst Agent (evaluates opportunities, initiates outreach)

**Role:** Top-of-funnel deal sourcing engine

---

## 2. Acquisition Platform Pipeline

```
Buyer Intake
    ↓
Persona Payload
    ↓
Lead Discovery Agent ← (this feature)
    ↓
Qualified Leads
    ↓
Analyst Agent
    ↓
Opportunity Evaluation
    ↓
Outreach / Broker Contact
    ↓
Deal Pipeline
    ↓
Closing
```

**Lead Discovery Agent:** Finding acquisition candidates  
**Analyst Agent:** Deeper evaluation, outreach, negotiation, deal progression

---

## 3. Objectives

### Primary
Automatically generate qualified acquisition leads that match buyer personas

### Secondary
- Reduce manual deal sourcing time
- Increase deal flow volume
- Ensure lead quality through deterministic filters
- Produce explainable and auditable lead data
- Enable Analyst Agent decision-making

---

## 4. Users

### Primary: Business Acquisition Buyers

| Persona | Description |
|---------|-------------|
| Marcus | MBA search fund buyer |
| Diane | Lifestyle buyer |
| Ray | Operator buyer |
| Priya | Portfolio builder |
| Jordan | Remote digital buyer |

### Secondary: Analyst Agent
- Review leads
- Analyze financial fit
- Assess acquisition potential
- Initiate outreach

---

## 5. Scope

### In Scope
- Persona-based acquisition search
- Discovery of candidate businesses
- Contact identification
- Data enrichment
- Lead qualification scoring
- Structured lead outputs

### Out of Scope
- Valuation analysis
- Financial modeling
- Negotiation
- Legal diligence
- Deal closing

*(These belong to Analyst Agent)*

---

## 6. System Inputs

**From Intake Bot:**

```json
{
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
  "margin": {
    "min_pct": 20
  },
  "operator_type": "gm_hire",
  "industry_rules": {
    "include": ["any"],
    "exclude": ["food"]
  },
  "max_price": 2100000,
  "max_sde_multiple": 4.0,
  "revenue_trend": ["growing","flat"],
  "distress_ok": false,
  "max_results": 25
}
```

---

## 7. System Outputs

**Structured list of qualified acquisition leads:**

```json
{
  "business_name": "Mountain Valley Plumbing",
  "city": "Provo",
  "state": "UT",
  "owner_name": "David Jensen",
  "contact_email": "david@example.com",
  "contact_phone": "801-555-0191",
  "estimated_revenue_range": "1M-2M",
  "employee_estimate": "8-15",
  "years_in_business": 14,
  "qualification_score": 84,
  "lead_summary": "Local owner-operated plumbing business with estimated $1–2M revenue."
}
```

---

## 8. Functional Requirements

### 8.1 Payload Interpreter
- Validate persona payload
- Normalize industries
- Normalize geography rules
- Convert revenue/SDE fields
- Detect invalid payloads
- **Output:** NormalizedConstraints

### 8.2 Search Planner
- Determine sources
- Generate search queries
- Determine geographic coverage
- Determine industry targets

**Example:**
```
HVAC + Utah radius
Plumbing + Provo + directory search
```

### 8.3 Discovery Agents
Run in parallel across sources:

| Source Type | Example |
|-------------|---------|
| Directories | Google Maps style listings |
| Registries | State business registries |
| Marketplaces | BizBuySell |
| Associations | Industry directories |
| Websites | Company sites |

**Output:** CandidateBusinesses[]

### 8.4 Deduplication
**Rules:**
- Identical domain
- Identical phone
- Identical business name + address
- Fuzzy name + same city

### 8.5 Contact Discovery
**Priority:**
1. Owner
2. Founder
3. President
4. Managing partner
5. Operator
6. General manager
7. Company contact

### 8.6 Data Enrichment
Add missing attributes:
- Revenue estimate
- SDE estimate
- Employee count
- Years in business
- Owner dependency signals
- Revenue trend signals

*All inferred values include confidence scores*

### 8.7 Hard Filter Enforcement
**Mandatory filters:**
- Geography
- Financial range
- Industry rules
- SDE multiple
- Revenue trend
- Staffing requirements
- Deal structure compatibility

*Failing leads → excluded leads*

### 8.8 Lead Qualification

| Category | Weight |
|----------|--------|
| Persona match | 25 |
| Contactability | 20 |
| Operational independence | 20 |
| Financial suitability | 15 |
| Deal structure fit | 10 |
| Data confidence | 10 |

**Threshold:** score ≥ 70

### 8.9 Lead Output Formatting
Each lead includes:
- Normalized fields
- Provenance metadata
- Qualification explanation
- Lead summary

---

## 9. Non-Functional Requirements

### Reliability
Pipeline continues even if sub-agent fails

**Agent status values:**
- success
- partial
- failed

### Performance

| Metric | Target |
|--------|--------|
| Lead generation runtime | < 60 seconds |
| Candidate businesses scanned | ≥ 500 |
| Qualified leads returned | ≤ 25 |

### Observability
Each agent logs:
- agent_name
- status
- records_found
- errors
- execution_time

### Data Integrity
- No fabricated contact data
- Unknown fields remain unknown
- Estimated values include confidence scores

---

## 10. Data Sources

**Allowed:**
- Public directories
- Business registries
- Company websites
- Association listings
- Approved marketplaces

**Blocked:**
- LinkedIn
- Login-required platforms
- Private databases without license

---

## 11. System Architecture

**Recommended Stack:**
- **Backend:** Python + FastAPI
- **Agents:** asyncio workers
- **Scraping:** Playwright
- **Data:** PostgreSQL
- **Validation:** Pydantic schemas
- **Orchestration:** Temporal or task queue

---

## 12. Analyst Agent Integration

**Lead Discovery provides:**
- Structured lead data
- Source attribution
- Confidence indicators

**Analyst Agent responsibilities:**
- Deeper financial analysis
- Synergy analysis
- Owner outreach preparation
- Broker interaction
- Deal qualification

---

## 13. Success Metrics

| Metric | Target |
|--------|--------|
| Qualified leads per run | ≥ 10 |
| Contact discovery rate | ≥ 60% |
| Hard filter pass rate | ≥ 20% |
| Analyst acceptance rate | ≥ 30% |

---

## 14. Risks

| Risk | Mitigation |
|------|------------|
| Inaccurate revenue estimates | Confidence scoring |
| Duplicate businesses | Dedupe agent |
| Scraping restrictions | Source policy |
| Incorrect owner identification | Evidence-based extraction |

---

## 15. Roadmap

### Phase 1 — MVP (Month 1)
**Goal:** Functional deal sourcing engine

**Features:**
- Persona payload ingestion
- Directory discovery agent
- Dedupe agent
- Contact extraction
- Basic enrichment
- Hard filter enforcement
- Qualification scoring
- JSON output

**Result:** 10-25 qualified leads per run

### Phase 2 — Enhanced Discovery (Month 2)
- Additional discovery agents
- Association directory scraping
- Improved industry classification
- Improved contact discovery
- Better deduplication
- Source ranking

**Result:** 2-3× more candidate businesses

### Phase 3 — Acquisition Intelligence (Month 3)
- Improved owner dependency signals
- Better revenue estimation models
- Operational complexity scoring
- Deal structure compatibility detection
- Analyst feedback loop

**Result:** Higher lead quality

### Phase 4 — Analyst Integration (Month 4)
- Direct Analyst Agent pipeline
- Opportunity scoring
- Outreach preparation
- CRM integration

**Result:** Fully automated acquisition pipeline

---

## 16. Future Enhancements

- Machine learning lead ranking
- Industry-specific sourcing agents
- Broker relationship data
- Automated outreach generation
- Buyer portfolio synergy analysis
- Global acquisition search

---

## 17. Final Summary

The Persona-Driven Acquisition Lead Discovery system is the foundational deal sourcing engine for the Business Acquisition Service platform. It transforms buyer preferences into structured acquisition search logic, identifies potential businesses to acquire, and delivers qualified leads to the Analyst Agent for deal evaluation and closing.

**System emphasizes:**
- Deterministic filtering
- Explainable lead scoring
- Reliable contact discovery
- Production-grade observability
- Scalable multi-agent architecture
