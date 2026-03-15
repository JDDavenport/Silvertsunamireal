# ACQUISITOR Test Execution Checklist

## Quick Reference - All 46 User Stories

### ✅ Authentication (1 story)
- [ ] **US-001**: User Registration via Google OAuth

### ✅ Onboarding (8 stories)
- [ ] **US-002**: Professional Background
- [ ] **US-003**: Business Experience  
- [ ] **US-004**: Budget Range
- [ ] **US-005**: Industry Preferences
- [ ] **US-006**: Location Preferences
- [ ] **US-007**: Business Values
- [ ] **US-008**: Timeline
- [ ] **US-009**: Profile Generation

### ✅ Dashboard (3 stories)
- [ ] **US-010**: Dashboard Overview
- [ ] **US-011**: Real-time Updates
- [ ] **US-012**: Agent Status

### ✅ Lead Discovery & Backlog (6 stories)
- [ ] **US-013**: Manual Discovery Trigger
- [ ] **US-014**: View Lead Backlog
- [ ] **US-015**: Lead Scoring Display
- [ ] **US-016**: Approve Lead
- [ ] **US-017**: Reject Lead
- [ ] **US-018**: Auto-Approve High Scores

### ✅ Pipeline Management (4 stories)
- [ ] **US-019**: View Pipeline
- [ ] **US-020**: Move Lead Through Pipeline
- [ ] **US-021**: Pipeline Value Tracking
- [ ] **US-022**: Email Activity in Pipeline

### ✅ CRM - Contact Management (6 stories)
- [ ] **US-023**: View All Contacts
- [ ] **US-024**: Search Contacts
- [ ] **US-025**: View Contact Details
- [ ] **US-026**: Add Note to Contact
- [ ] **US-027**: View Activity History
- [ ] **US-028**: Quick Email from CRM

### ✅ Email Outreach (4 stories)
- [ ] **US-029**: Compose Email
- [ ] **US-030**: Use Email Template
- [ ] **US-031**: Send Email via Gmail
- [ ] **US-032**: Email Rate Limiting

### ✅ Settings & Configuration (4 stories)
- [ ] **US-033**: Configure Email Limits
- [ ] **US-034**: Configure Auto-Approve
- [ ] **US-035**: Configure Discovery Frequency
- [ ] **US-036**: Configure Notifications

### ✅ CSV Import (4 stories)
- [ ] **US-037**: Upload CSV Preview
- [ ] **US-038**: Import CSV Data
- [ ] **US-039**: CSV Format Flexibility
- [ ] **US-040**: Duplicate Detection

### ✅ Security & Error Handling (3 stories)
- [ ] **US-041**: Session Expiration
- [ ] **US-042**: Unauthorized Access
- [ ] **US-043**: API Error Handling

### ✅ Edge Cases (3 stories)
- [ ] **US-044**: Empty State Handling
- [ ] **US-045**: Large Data Handling
- [ ] **US-046**: Mobile Responsiveness

---

## Priority Test Plan

### 🚨 P0 - CRITICAL (Must work for launch)
**Total: 20 stories**

**Authentication & Onboarding (9)**
- US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009

**Dashboard (3)**
- US-010, US-011, US-012

**Lead Management (4)**
- US-014, US-015, US-016, US-017

**Email (3)**
- US-029, US-030, US-031

**Security (1)**
- US-041

### 🔵 P1 - IMPORTANT (Should work for launch)  
**Total: 20 stories**

**Discovery & Pipeline (6)**
- US-013, US-018, US-019, US-020, US-021, US-022

**CRM (6)**
- US-023, US-024, US-025, US-026, US-027, US-028

**Settings (4)**
- US-033, US-034, US-035, US-036

**CSV Import (4)**
- US-037, US-038, US-039, US-040

### ⚪ P2 - NICE TO HAVE (Can add after launch)
**Total: 6 stories**

- US-032 (Email rate limiting)
- US-042, US-043 (Security)
- US-044, US-045, US-046 (Edge cases)

---

## Test by Feature Area

### 🎯 Authentication Flow
```
☐ US-001: OAuth registration/login
☐ US-041: Session expiration
☐ US-042: Data isolation
```

### 🎯 Onboarding Flow
```
☐ US-002 → US-008: Answer all 7 questions
☐ US-009: Verify criteria generated
☐ US-044: Empty state for new users
```

### 🎯 Lead Management
```
☐ US-013: Run discovery
☐ US-014: View backlog
☐ US-015: Check scoring
☐ US-016: Approve lead
☐ US-017: Reject lead
☐ US-018: Auto-approve threshold
☐ US-040: Duplicate detection
```

### 🎯 Pipeline Management
```
☐ US-019: View kanban
☐ US-020: Move lead stages
☐ US-021: Check pipeline value
☐ US-022: Email activity badges
```

### 🎯 CRM
```
☐ US-023: Contact list
☐ US-024: Search
☐ US-025: Contact details
☐ US-026: Add notes
☐ US-027: Activity history
☐ US-028: Quick email
```

### 🎯 Email System
```
☐ US-029: Compose email
☐ US-030: Use templates
☐ US-031: Send via Gmail
☐ US-032: Rate limiting
```

### 🎯 Settings
```
☐ US-033: Email limits
☐ US-034: Auto-approve
☐ US-035: Discovery schedule
☐ US-036: Notifications
```

### 🎯 Data Import
```
☐ US-037: CSV preview
☐ US-038: Import leads
☐ US-039: Flexible formats
☐ US-040: Duplicate handling
```

---

## Testing Quick Start

### Manual Testing (15 min smoke test)
1. **Register** → OAuth with Google
2. **Onboard** → Answer 7 questions
3. **Dashboard** → Verify metrics load
4. **Discovery** → Trigger manual discovery
5. **Backlog** → View and approve a lead
6. **Pipeline** → Move lead to "Outreach"
7. **CRM** → Add note to lead
8. **Email** → Compose (don't send)
9. **Settings** → Change email limit
10. **Import** → Upload test CSV

### Automated Testing (with Playwright/Cypress)
```javascript
// Example test structure
describe('ACQUISITOR E2E', () => {
  describe('Authentication', () => {
    it('US-001: OAuth registration', () => {});
  });
  
  describe('Onboarding', () => {
    it('US-002 → US-009: Complete flow', () => {});
  });
  
  describe('Lead Management', () => {
    it('US-014: View backlog', () => {});
    it('US-016: Approve lead', () => {});
    it('US-017: Reject lead', () => {});
  });
  
  // ... etc
});
```

### API Testing (with Postman/pytest)
```python
# Example API tests
def test_auth():
    # US-001
    pass

def test_discovery():
    # US-013
    pass

def test_approve_lead():
    # US-016
    pass

def test_csv_import():
    # US-038
    pass
```

---

## Coverage Tracking

| Component | Stories | Manual | Automated | Status |
|-----------|---------|--------|-----------|--------|
| Auth | 1 | ☐ | ☐ | Not Started |
| Onboarding | 8 | ☐ | ☐ | Not Started |
| Dashboard | 3 | ☐ | ☐ | Not Started |
| Leads | 6 | ☐ | ☐ | Not Started |
| Pipeline | 4 | ☐ | ☐ | Not Started |
| CRM | 6 | ☐ | ☐ | Not Started |
| Email | 4 | ☐ | ☐ | Not Started |
| Settings | 4 | ☐ | ☐ | Not Started |
| CSV Import | 4 | ☐ | ☐ | Not Started |
| Security | 3 | ☐ | ☐ | Not Started |
| Edge Cases | 3 | ☐ | ☐ | Not Started |
| **TOTAL** | **46** | | | |

---

## Success Criteria

✅ **Launch Ready** = All P0 stories passing (20/46)  
✅ **Production Ready** = All P0 + P1 passing (40/46)  
✅ **Feature Complete** = All 46 stories passing

---

## Files Reference

- **Full Stories**: `USER_STORIES.md` (46 detailed stories)
- **This Checklist**: `TEST_CHECKLIST.md` (this file)
- **Implementation Status**: `IMPLEMENTATION_STATUS.md`
