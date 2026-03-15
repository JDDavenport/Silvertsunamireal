# ACQUISITOR COMPLETION ROADMAP
## All 46 User Stories → Fully Working

**Start Time:** 2026-03-14 22:15 MDT  
**Target Completion:** 2026-03-15 18:00 MDT  
**Total Estimated Hours:** 14-16 hours

---

## PHASE 1: FOUNDATION (Hours 1-3)
**Goal:** Get core infrastructure working

### 1.1 Set Up Heartbeat Tracking (15 min)
- [ ] Create heartbeat state file
- [ ] Define completion criteria
- [ ] Set up progress tracking

### 1.2 Fix OAuth/Routes (30 min)
- [ ] Create /auth/callback route handler
- [ ] Mock Google OAuth for tests
- [ ] Add test-only authentication bypass

### 1.3 Add Toast Notification System (45 min)
- [ ] Install react-hot-toast
- [ ] Create ToastContainer component
- [ ] Add to App.tsx
- [ ] Use in LeadBacklog (approve/reject)

### 1.4 Set Up MSW (Mock Service Worker) (60 min)
- [ ] Install MSW
- [ ] Create handlers for all API endpoints
- [ ] Set up browser integration
- [ ] Create test data fixtures

### 1.5 Create Test Data Factories (30 min)
- [ ] User factory
- [ ] Lead factory with all statuses
- [ ] Activity factory
- [ ] Seed script for test database

**Phase 1 Success Criteria:**
- `npm run test:auth` passes
- Toast notifications work
- MSW intercepts API calls
- Test database seeded

---

## PHASE 2: AUTH & ONBOARDING (Hours 3-5)
**Goal:** US-001 to US-009 passing

### 2.1 Auth Tests (US-001) (30 min)
- [ ] Add remaining test IDs to LandingPage
- [ ] Mock Google OAuth response
- [ ] Fix callback handling
- [ ] Verify JWT token storage

### 2.2 Onboarding Tests (US-002 to US-009) (90 min)
- [ ] Add test IDs to Onboarding.tsx
- [ ] Create 7-step flow test
- [ ] Mock chat responses
- [ ] Verify criteria generation
- [ ] Test completion redirect

**Phase 2 Success Criteria:**
- All auth tests pass
- All onboarding tests pass
- 9/46 stories complete

---

## PHASE 3: DASHBOARD & LEADS (Hours 5-8)
**Goal:** US-010 to US-018 passing

### 3.1 Dashboard Tests (US-010 to US-012) (60 min)
- [ ] Add remaining test IDs
- [ ] Mock stats API response
- [ ] Test WebSocket connection
- [ ] Verify agent status display

### 3.2 Lead Discovery Tests (US-013) (30 min)
- [ ] Add test ID to discovery button
- [ ] Mock discovery API
- [ ] Test manual trigger

### 3.3 Lead Backlog Tests (US-014 to US-018) (90 min)
- [ ] Finish test IDs in LeadBacklog
- [ ] Create lead cards with mock data
- [ ] Test approve/reject flow
- [ ] Test AI assessment display
- [ ] Test auto-approve threshold

**Phase 3 Success Criteria:**
- Dashboard loads with stats
- Lead backlog shows leads
- Approve/reject works
- 18/46 stories complete

---

## PHASE 4: PIPELINE & CRM (Hours 8-11)
**Goal:** US-019 to US-028 passing

### 4.1 Pipeline Tests (US-019 to US-022) (90 min)
- [ ] Add test IDs to PipelineView
- [ ] Create kanban columns
- [ ] Test drag-and-drop (or move buttons)
- [ ] Test pipeline value calculation
- [ ] Test email activity badges

### 4.2 CRM Tests (US-023 to US-028) (90 min)
- [ ] Add test IDs to CRMView
- [ ] Test contact list
- [ ] Test search functionality
- [ ] Test contact details
- [ ] Test add note
- [ ] Test activity history
- [ ] Test quick email

**Phase 4 Success Criteria:**
- Pipeline shows leads in columns
- CRM shows contacts
- Notes and activities work
- 28/46 stories complete

---

## PHASE 5: EMAIL & SETTINGS (Hours 11-13)
**Goal:** US-029 to US-036 passing

### 5.1 Email Tests (US-029 to US-032) (60 min)
- [ ] Add test IDs to EmailCompose
- [ ] Test compose modal
- [ ] Test templates
- [ ] Mock Gmail API

### 5.2 Settings Tests (US-033 to US-036) (60 min)
- [ ] Add test IDs to SettingsPanel
- [ ] Test email limit slider
- [ ] Test auto-approve slider
- [ ] Test discovery schedule
- [ ] Test notification toggles

**Phase 5 Success Criteria:**
- Email compose works
- Settings save correctly
- 36/46 stories complete

---

## PHASE 6: IMPORT & EDGE CASES (Hours 13-14)
**Goal:** US-037 to US-046 passing

### 6.1 CSV Import Tests (US-037 to US-040) (45 min)
- [ ] Create import page/route
- [ ] Add test IDs
- [ ] Test CSV upload
- [ ] Test preview
- [ ] Test duplicate detection

### 6.2 Security Tests (US-041 to US-043) (30 min)
- [ ] Test session expiration
- [ ] Test unauthorized access
- [ ] Test error handling

### 6.3 Edge Case Tests (US-044 to US-046) (15 min)
- [ ] Test empty states
- [ ] Test mobile responsiveness

**Phase 6 Success Criteria:**
- CSV import works
- Security tests pass
- 46/46 stories complete

---

## PHASE 7: FINAL VALIDATION (Hours 14-16)
**Goal:** All tests passing, production ready

### 7.1 Full Test Suite Run (30 min)
- [ ] Run all tests: `npm run test`
- [ ] Document any failures
- [ ] Fix critical issues

### 7.2 Cross-Browser Testing (30 min)
- [ ] Test in Chromium
- [ ] Test in Firefox
- [ ] Test in WebKit
- [ ] Test mobile view

### 7.3 CI/CD Integration (30 min)
- [ ] Create GitHub Actions workflow
- [ ] Set up test reporting
- [ ] Configure test artifacts

### 7.4 Documentation (30 min)
- [ ] Update TEST_RESULTS.md
- [ ] Create troubleshooting guide
- [ ] Document test commands

**Phase 7 Success Criteria:**
- 100% test pass rate
- All 46 stories verified
- CI/CD pipeline green
- Heartbeats turned off

---

## PROGRESS TRACKING

### Heartbeat State File
Location: `~/projects/silver-tsunami-real/.heartbeat/state.json`

Update every 30 minutes with:
- Current phase
- Stories completed
- Blockers
- ETA

### Daily Milestones

| Time | Milestone | Stories Complete |
|------|-----------|------------------|
| 01:00 | Phase 1 Done | 0 (infrastructure) |
| 03:00 | Phase 2 Done | 9 |
| 06:00 | Phase 3 Done | 18 |
| 09:00 | Phase 4 Done | 28 |
| 11:00 | Phase 5 Done | 36 |
| 12:00 | Phase 6 Done | 46 |
| 14:00 | Phase 7 Done | 46 + CI/CD |

---

## COMPLETION CRITERIA

Project is COMPLETE when:
1. [ ] All 46 user story tests pass
2. [ ] No test failures across all browsers
3. [ ] CI/CD pipeline passes
4. [ ] Documentation complete
5. [ ] Heartbeat turned off
6. [ ] Final commit: "All 46 user stories fully tested and working"

---

## COMMANDS FOR TRACKING

```bash
# Quick test run
cd v2/web && npm run test:ci 2>&1 | tail -20

# Check status
grep -c "✓" test-results/results.json 2>/dev/null || echo "0"

# Stories complete
grep -l "passed" test-results/*.json 2>/dev/null | wc -l
```

**LET'S BUILD.**
