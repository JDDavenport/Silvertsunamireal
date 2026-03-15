# Autonomous QA Agent - Comprehensive Architecture

## Executive Summary

This document defines a fully autonomous QA agent capable of testing all 46 user stories in the ACQUISITOR application end-to-end.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS QA ORCHESTRATOR                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   STORY     │  │   TEST      │  │  EXECUTION  │             │
│  │  PARSER     │→ │  GENERATOR  │→ │  ENGINE     │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └──────┬──────┘             │
│         ↑                                   │                    │
│         │                                   ↓                    │
│  ┌──────┴──────┐                    ┌─────────────┐             │
│  │   USER      │                    │   RESULT    │             │
│  │  STORIES    │                    │  ANALYZER   │             │
│  │  (46 total) │                    │             │             │
│  └─────────────┘                    └──────┬──────┘             │
│                                            │                    │
│         ┌──────────────────────────────────┘                    │
│         ↓                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    BUG      │  │   SELF      │  │   REPORT    │             │
│  │  REPORTER   │  │  HEALING    │  │  GENERATOR  │             │
│  │             │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TEST EXECUTION LAYERS                        │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: API Tests (FastAPI backend)                           │
│  Layer 2: E2E Tests (Playwright - React frontend)              │
│  Layer 3: Integration Tests (Full stack)                        │
│  Layer 4: Visual Regression (Screenshots)                       │
│  Layer 5: Performance Tests (Load, response times)              │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Story Parser Module
- Parses USER_STORIES.md into structured test requirements
- Extracts: preconditions, steps, expected results
- Identifies test data requirements
- Maps to appropriate test layer

### 2. Test Generator Module
- Converts stories into executable test code
- Generates Playwright tests for UI
- Generates pytest tests for API
- Creates test data fixtures
- Handles async operations

### 3. Execution Engine
- Runs tests in parallel where safe
- Manages test isolation (clean database state)
- Handles test retries with exponential backoff
- Captures screenshots on failure
- Records execution traces

### 4. Result Analyzer
- Determines pass/fail status
- Categorizes failures (flaky, bug, environment)
- Compares against baselines
- Detects regressions

### 5. Bug Reporter
- Auto-creates GitHub issues for failures
- Includes: screenshot, trace, steps to reproduce
- Assigns severity based on story priority
- Links to failing test

### 6. Self-Healing Module
- Detects UI changes (selectors breaking)
- Suggests selector updates
- Adapts to minor UI changes
- Learns from successful executions

## Tech Stack

### Core Framework
- **Playwright**: Primary E2E testing (React frontend)
- **pytest**: API testing (FastAPI backend)
- **Allure**: Test reporting and visualization
- **Docker**: Test environment isolation

### AI/ML Components
- **LangChain**: LLM integration for test generation
- **Pydantic**: Structured output parsing
- **ChromaDB**: Vector storage for test history
- **OpenAI/Anthropic**: LLM for code generation

### Supporting Tools
- **testcontainers**: Database isolation
- **faker**: Test data generation
- **factory-boy**: Model factories
- **responses**: HTTP mocking
- **freezegun**: Time manipulation

## Test Layers

### Layer 1: API Tests (Backend)
```python
# Example: US-016 Approve Lead
def test_approve_lead(client, auth_headers, db):
    # Given: A lead exists with status 'new'
    lead = LeadFactory(status='new', user_id=auth_headers['user_id'])
    
    # When: POST /leads/{id}/approve
    response = client.post(
        f"/leads/{lead.id}/approve",
        headers=auth_headers
    )
    
    # Then: Status updated to 'approved'
    assert response.status_code == 200
    lead.refresh()
    assert lead.status == 'approved'
```

### Layer 2: E2E Tests (Frontend)
```typescript
// Example: US-016 Approve Lead
test('US-016: User can approve lead', async ({ page }) => {
  // Given: User is logged in and viewing backlog
  await page.goto('/dashboard/backlog');
  await expect(page.locator('[data-testid="lead-card"]')).toBeVisible();
  
  // When: Click approve button
  await page.click('[data-testid="approve-lead-btn"]');
  
  // Then: Lead moves to pipeline
  await page.goto('/dashboard/pipeline');
  await expect(page.locator('[data-testid="pipeline-approved"]')).toContainText('ABC Tech');
});
```

### Layer 3: Integration Tests
- Full user flows
- Database state verification
- Cross-service communication

### Layer 4: Visual Regression
- Screenshot comparison
- Component-level testing
- Responsive design verification

### Layer 5: Performance
- API response times < 200ms
- Page load times < 3s
- Discovery job completion < 5 minutes

## Autonomous Test Generation

### User Story to Test Code

```
Input: US-016 User Story (natural language)
↓
Story Parser → Structured Requirements
↓
LLM Generator → Test Code
↓
Validation → Executable Test
```

### Example Generation

**Input (User Story):**
```
US-016: Approve Lead
As a user I want to approve a lead so it moves to outreach

AC:
- Approve button visible
- Clicking moves to approved status
- Lead disappears from backlog
- Activity logged
- Appears in pipeline
```

**Output (Generated Test):**
```typescript
test('US-016: Approve Lead', async ({ page, auth }) => {
  await test.step('Navigate to backlog', async () => {
    await page.goto('/dashboard/backlog');
    await expect(page).toHaveURL('/dashboard/backlog');
  });
  
  await test.step('Verify lead with approve button', async () => {
    const leadCard = page.locator('[data-testid="lead-card"]').first();
    await expect(leadCard.locator('[data-testid="approve-btn"]')).toBeVisible();
  });
  
  await test.step('Click approve', async () => {
    await page.click('[data-testid="approve-btn"]').first();
    await expect(page.locator('[data-testid="success-toast"]')).toContainText('Lead approved');
  });
  
  await test.step('Verify removed from backlog', async () => {
    await page.reload();
    await expect(page.locator('[data-testid="empty-backlog"]')).toBeVisible();
  });
  
  await test.step('Verify in pipeline', async () => {
    await page.goto('/dashboard/pipeline');
    await expect(page.locator('[data-testid="pipeline-approved"]')).toContainText('ABC Tech');
  });
  
  await test.step('Verify activity logged', async () => {
    await page.goto('/dashboard/crm');
    await expect(page.locator('[data-testid="activity-feed"]')).toContainText('Lead approved');
  });
});
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up Playwright with TypeScript
- [ ] Set up pytest with fixtures
- [ ] Create test database isolation
- [ ] Build test data factories
- [ ] Create authentication helpers

### Phase 2: API Test Suite (Week 2)
- [ ] Test all API endpoints
- [ ] Test authentication flow
- [ ] Test CRUD operations
- [ ] Test CSV import
- [ ] Test email sending (mocked)

### Phase 3: E2E Test Suite (Week 3)
- [ ] Test onboarding flow
- [ ] Test dashboard
- [ ] Test lead backlog
- [ ] Test pipeline
- [ ] Test CRM

### Phase 4: Autonomous Generation (Week 4)
- [ ] Build story parser
- [ ] Build LLM generator
- [ ] Build execution engine
- [ ] Build result analyzer
- [ ] Build self-healing

### Phase 5: Full Automation (Week 5)
- [ ] Run all 46 stories
- [ ] Generate reports
- [ ] Fix failures
- [ ] Achieve 100% pass rate

## Test Data Strategy

### Factories (factory-boy)
```python
class UserFactory(Factory):
    class Meta:
        model = User
    
    email = factory.Faker('email')
    name = factory.Faker('name')
    agent_config = factory.LazyFunction(lambda: {
        'daily_email_limit': 25,
        'auto_approve_threshold': 0
    })

class LeadFactory(Factory):
    class Meta:
        model = Lead
    
    name = factory.Faker('company')
    industry = factory.Iterator(['Technology', 'Healthcare', 'Services'])
    revenue = factory.Faker('random_int', min=500000, max=5000000)
    status = 'new'
    score = factory.Faker('random_int', min=40, max=100)
```

### Database Fixtures
- Clean database per test
- Seed data for specific scenarios
- Transaction rollback after each test

## Running the Tests

### Local Development
```bash
# Run all tests
npm run test:e2e

# Run specific story
npm run test:e2e -- --grep "US-016"

# Run with UI
npm run test:e2e -- --ui

# Debug mode
npm run test:e2e -- --debug
```

### CI/CD
```bash
# Headless in CI
npm run test:e2e:ci

# With Allure report
npm run test:e2e:report

# Parallel execution
npm run test:e2e:parallel
```

## Success Metrics

- **Coverage**: 100% of 46 user stories
- **Pass Rate**: > 95% (allowing for flaky tests)
- **Execution Time**: < 30 minutes for full suite
- **Stability**: < 5% flake rate
- **Bug Detection**: 100% of introduced bugs caught

## Files Structure

```
tests/
├── e2e/
│   ├── auth/
│   │   └── oauth.spec.ts
│   ├── onboarding/
│   │   └── flow.spec.ts
│   ├── dashboard/
│   │   └── overview.spec.ts
│   ├── leads/
│   │   ├── backlog.spec.ts
│   │   └── discovery.spec.ts
│   ├── pipeline/
│   │   └── kanban.spec.ts
│   ├── crm/
│   │   └── contacts.spec.ts
│   ├── email/
│   │   └── compose.spec.ts
│   ├── settings/
│   │   └── configuration.spec.ts
│   └── import/
│       └── csv.spec.ts
├── api/
│   ├── test_auth.py
│   ├── test_leads.py
│   ├── test_pipeline.py
│   ├── test_crm.py
│   ├── test_email.py
│   ├── test_settings.py
│   └── test_import.py
├── fixtures/
│   ├── auth.fixture.ts
│   ├── database.fixture.ts
│   └── leads.fixture.ts
├── factories/
│   ├── user_factory.py
│   ├── lead_factory.py
│   └── activity_factory.py
├── utils/
│   ├── test-data.ts
│   ├── selectors.ts
│   └── assertions.ts
└── autonomous/
    ├── story-parser.ts
    ├── test-generator.ts
    ├── execution-engine.ts
    └── self-healing.ts
```
