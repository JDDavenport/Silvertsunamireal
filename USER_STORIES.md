# ACQUISITOR User Stories - Complete Test Suite

## Overview
This document contains comprehensive user stories covering every feature of the ACQUISITOR platform. Each story includes acceptance criteria and test steps for validation.

---

## 🔐 AUTHENTICATION & ONBOARDING

### US-001: User Registration via Google OAuth
**As a** prospective buyer  
**I want to** sign up using my Google account  
**So that** I can quickly access the platform without creating a new password

**Acceptance Criteria:**
- [ ] Google OAuth button visible on landing page
- [ ] Clicking button initiates OAuth flow
- [ ] New user is created in database on first login
- [ ] Existing user is authenticated on subsequent logins
- [ ] JWT token is generated and stored
- [ ] User is redirected to onboarding (first time) or dashboard (returning)

**Test Steps:**
1. Visit landing page
2. Click "Get Started with Google"
3. Select Google account
4. Approve permissions
5. Verify redirect to onboarding (new user) or dashboard (existing)

**Expected Result:** User is authenticated and JWT token is valid

---

### US-002: Onboarding - Professional Background
**As a** new user  
**I want to** share my professional background  
**So that** the AI can understand my experience and expertise

**Acceptance Criteria:**
- [ ] Chat interface displays first question about background
- [ ] User can type response
- [ ] Response is captured and stored
- [ ] AI acknowledges and moves to next question

**Test Steps:**
1. Complete OAuth registration
2. Verify first question about professional background appears
3. Type: "10 years in software engineering, last 3 as CTO"
4. Verify response is saved
5. Verify next question appears

**Expected Result:** Background stored in user profile

---

### US-003: Onboarding - Business Experience
**As a** new user  
**I want to** indicate my business ownership experience  
**So that** the AI can tailor acquisition strategies

**Acceptance Criteria:**
- [ ] Second question asks about prior business ownership
- [ ] User can indicate first acquisition vs. experienced
- [ ] Response influences AI recommendations

**Test Steps:**
1. Complete background question
2. Verify question about business experience appears
3. Select "First acquisition"
4. Verify acknowledgment

**Expected Result:** Experience level stored in profile

---

### US-004: Onboarding - Budget Range
**As a** new user  
**I want to** specify my acquisition budget  
**So that** the system filters for appropriately priced businesses

**Acceptance Criteria:**
- [ ] Question asks for budget range
- [ ] Natural language input accepted ("$500K-$2M")
- [ ] System parses and stores numeric range

**Test Steps:**
1. Complete experience question
2. Enter: "$1M to $5M"
3. Verify system acknowledges range

**Expected Result:** Budget range parsed and stored

---

### US-005: Onboarding - Industry Preferences
**As a** new user  
**I want to** select industries of interest  
**So that** discovery focuses on relevant businesses

**Acceptance Criteria:**
- [ ] Question asks for industry preferences
- [ ] Multiple industries can be specified
- [ ] System extracts keywords from natural language

**Test Steps:**
1. Complete budget question
2. Enter: "Technology, Healthcare, and Business Services"
3. Verify industries are parsed into array

**Expected Result:** Industries stored as: ["Technology", "Healthcare", "Business Services"]

---

### US-006: Onboarding - Location Preferences
**As a** new user  
**I want to** specify geographic preferences  
**So that** discovery focuses on businesses in my target area

**Acceptance Criteria:**
- [ ] Question asks for location preferences
- [ ] States, regions, or "nationwide" accepted
- [ ] System normalizes to state codes

**Test Steps:**
1. Complete industry question
2. Enter: "Utah, Colorado, and Arizona"
3. Verify locations stored as state codes

**Expected Result:** Locations stored as: ["UT", "CO", "AZ"]

---

### US-007: Onboarding - Business Values
**As a** new user  
**I want to** describe what I value in a business  
**So that** AI scoring prioritizes aligned opportunities

**Acceptance Criteria:**
- [ ] Question asks about business priorities
- [ ] Free-form text accepted
- [ ] Used in AI assessment criteria

**Test Steps:**
1. Complete location question
2. Enter: "Steady cash flow, established team, growth potential"
3. Verify response stored

**Expected Result:** Values stored for AI scoring

---

### US-008: Onboarding - Timeline
**As a** new user  
**I want to** specify my acquisition timeline  
**So that** outreach timing can be optimized

**Acceptance Criteria:**
- [ ] Final question asks about timeline
- [ ] Options: 6 months, 1 year, exploring
- [ ] Completion triggers criteria generation

**Test Steps:**
1. Complete values question
2. Enter: "Within 6 months"
3. Verify completion screen appears
4. Verify "Go to Dashboard" button visible

**Expected Result:** Onboarding complete, criteria generated

---

### US-009: Profile Generation
**As a** user completing onboarding  
**I want to** see my search criteria summary  
**So that** I can confirm my preferences are captured correctly

**Acceptance Criteria:**
- [ ] Summary displayed with all collected info
- [ ] Search criteria auto-generated
- [ ] Can proceed to dashboard

**Test Steps:**
1. Complete all 7 onboarding questions
2. Verify summary displayed:
   - Industries: ["Technology", "Healthcare", "Services"]
   - Revenue Range: $1M-$5M
   - Location: ["UT", "CO", "AZ"]
   - Target: Owners looking to retire
3. Click "Go to Dashboard"

**Expected Result:** Criteria saved, redirected to dashboard

---

## 📊 DASHBOARD & ANALYTICS

### US-010: Dashboard Overview
**As an** authenticated user  
**I want to** see a dashboard overview with key metrics  
**So that** I can quickly understand my pipeline status

**Acceptance Criteria:**
- [ ] Total leads count displayed
- [ ] New leads count displayed
- [ ] Active pipeline count displayed
- [ ] Emails sent count displayed
- [ ] Agent status panel shows current activity
- [ ] Recent activity feed visible

**Test Steps:**
1. Log in and navigate to /dashboard
2. Verify all metrics panels load
3. Verify agent status shows "Scanning for leads..."
4. Verify recent activity feed populated

**Expected Result:** All dashboard widgets display correct data

---

### US-011: Real-time Dashboard Updates
**As a** dashboard user  
**I want to** see updates in real-time  
**So that** I don't need to refresh the page

**Acceptance Criteria:**
- [ ] WebSocket connection established
- [ ] New leads appear without refresh
- [ ] Status changes reflect immediately
- [ ] Email counts update in real-time

**Test Steps:**
1. Open dashboard in browser
2. In another window, trigger new lead discovery
3. Verify new lead appears automatically
4. Verify stats counters increment

**Expected Result:** Updates received via WebSocket, UI reflects changes

---

### US-012: Agent Status Monitoring
**As a** user  
**I want to** see what my AI agent is currently doing  
**So that** I know the system is working

**Acceptance Criteria:**
- [ ] Agent status panel visible
- [ ] Shows current activity (e.g., "Scanning BizBuySell")
- [ ] Shows last activity timestamp
- [ ] Daily stats visible (leads discovered, emails sent)

**Test Steps:**
1. Navigate to dashboard
2. Verify agent status panel shows current activity
3. Verify timestamp is recent (< 1 hour)
4. Verify daily stats counters

**Expected Result:** Agent status accurately reflects system activity

---

## 🔍 LEAD DISCOVERY & BACKLOG

### US-013: Manual Discovery Trigger
**As a** user  
**I want to** manually trigger lead discovery  
**So that** I can find new opportunities on demand

**Acceptance Criteria:**
- [ ] "Run Discovery" button available
- [ ] Clicking triggers background job
- [ ] Notification when complete
- [ ] New leads appear in backlog

**Test Steps:**
1. Navigate to dashboard
2. Click "Run Discovery" button
3. Verify "Discovery running..." message
4. Wait for completion notification
5. Navigate to Lead Backlog
6. Verify new leads appeared

**Expected Result:** New leads discovered based on user criteria

---

### US-014: View Lead Backlog
**As a** user  
**I want to** see all new leads awaiting review  
**So that** I can evaluate potential acquisitions

**Acceptance Criteria:**
- [ ] List of "new" status leads displayed
- [ ] Each lead shows: name, industry, revenue, score
- [ ] Expandable details with AI assessment
- [ ] Filter/sort options available

**Test Steps:**
1. Navigate to /dashboard/backlog
2. Verify list of new leads loads
3. Verify each lead card shows:
   - Business name
   - Industry
   - Revenue
   - Score badge (color-coded)
4. Click on a lead to expand

**Expected Result:** Backlog displays all new leads with details

---

### US-015: Lead Scoring Display
**As a** user reviewing leads  
**I want to** see why a lead received its score  
**So that** I can understand the AI assessment

**Acceptance Criteria:**
- [ ] Score displayed prominently (0-100)
- [ ] Color-coded: 80+ green, 60-79 yellow, <60 gray
- [ ] AI assessment visible when expanded
- [ ] Reasons for score listed
- [ ] Key risks identified

**Test Steps:**
1. Navigate to Lead Backlog
2. Click on a lead with score >= 80
3. Verify green badge displayed
4. Verify AI assessment section visible
5. Verify "Why it's a fit" reasons listed
6. Verify "Key risks" listed

**Expected Result:** Score breakdown and rationale visible

---

### US-016: Approve Lead
**As a** user  
**I want to** approve a lead to move to outreach  
**So that** the AI can begin contacting the owner

**Acceptance Criteria:**
- [ ] "Approve" button visible on each lead
- [ ] Clicking moves lead to "approved" status
- [ ] Lead disappears from backlog
- [ ] Activity logged
- [ ] Lead appears in pipeline

**Test Steps:**
1. Navigate to Lead Backlog
2. Find a lead with high score
3. Click "Approve" button
4. Verify lead removed from backlog
5. Navigate to Pipeline
6. Verify lead in "Approved" column
7. Check activity log for "Lead approved"

**Expected Result:** Lead status changed to "approved", moved to pipeline

---

### US-017: Reject Lead
**As a** user  
**I want to** reject a lead that doesn't fit  
**So that** my backlog stays focused on quality opportunities

**Acceptance Criteria:**
- [ ] "Reject" button visible on each lead
- [ ] Clicking moves lead to "rejected" status
- [ ] Lead disappears from backlog
- [ ] Activity logged
- [ ] Lead does not appear in pipeline

**Test Steps:**
1. Navigate to Lead Backlog
2. Find a lead with low score
3. Click "Reject" button
4. Verify lead removed from backlog
5. Verify lead not in Pipeline
6. Check activity log for "Lead rejected"

**Expected Result:** Lead status changed to "rejected"

---

### US-018: Auto-Approve High-Scoring Leads
**As a** user  
**I want to** automatically approve leads above a score threshold  
**So that** I don't need to manually review every high-quality lead

**Acceptance Criteria:**
- [ ] Setting available to configure auto-approve threshold
- [ ] Leads scoring above threshold skip backlog
- [ ] Auto-approved leads go directly to pipeline
- [ ] User receives notification

**Test Steps:**
1. Go to Settings
2. Set Auto-Approve Threshold to 85
3. Trigger discovery
4. Verify leads with score >= 85 bypass backlog
5. Verify they appear directly in pipeline

**Expected Result:** High-scoring leads auto-approved per settings

---

## 📈 PIPELINE MANAGEMENT

### US-019: View Pipeline
**As a** user  
**I want to** see all leads in my acquisition pipeline  
**So that** I can track progress from approval to closing

**Acceptance Criteria:**
- [ ] Kanban board with 5 columns displayed
- [ ] Columns: Approved, Outreach, Engaged, Qualified, Booked
- [ ] Leads displayed in appropriate columns
- [ ] Pipeline value calculated

**Test Steps:**
1. Navigate to /dashboard/pipeline
2. Verify 5 columns visible
3. Verify approved leads in first column
4. Verify total pipeline value displayed

**Expected Result:** Pipeline accurately reflects all non-new leads

---

### US-020: Move Lead Through Pipeline
**As a** user  
**I want to** move leads between pipeline stages  
**So that** I can track deal progression

**Acceptance Criteria:**
- [ ] Can click on lead in pipeline
- [ ] "Move to [Next Stage]" button visible
- [ ] Clicking updates lead status
- [ ] Lead moves to next column
- [ ] Activity logged

**Test Steps:**
1. Navigate to Pipeline
2. Click on lead in "Approved" column
3. Click "Move to Outreach"
4. Verify lead moves to Outreach column
5. Verify activity logged

**Expected Result:** Lead status updated, visible in new column

---

### US-021: Pipeline Value Tracking
**As a** user  
**I want to** see the total value of my pipeline  
**So that** I understand the scale of opportunities

**Acceptance Criteria:**
- [ ] Total pipeline value displayed
- [ ] Calculated from sum of all pipeline lead revenues
- [ ] Updates as leads move/add/remove

**Test Steps:**
1. Navigate to Pipeline
2. Note total pipeline value
3. Approve a new lead with $2M revenue
4. Verify pipeline value increased by $2M

**Expected Result:** Pipeline value accurately reflects total opportunity

---

### US-022: Email Activity in Pipeline
**As a** user  
**I want to** see email activity for each lead  
**So that** I know if outreach is working

**Acceptance Criteria:**
- [ ] Email count badge on leads with emails sent
- [ ] Reply indicator for leads that responded
- [ ] Visual distinction for engaged leads

**Test Steps:**
1. Send email to lead in pipeline
2. Verify email count badge appears
3. When reply received, verify reply indicator

**Expected Result:** Email activity visible on pipeline cards

---

## 👥 CRM (CONTACT MANAGEMENT)

### US-023: View All Contacts
**As a** user  
**I want to** see all my leads in a contact list  
**So that** I can find specific businesses quickly

**Acceptance Criteria:**
- [ ] Contact list view available
- [ ] All leads displayed (not just new)
- [ ] Search/filter functionality
- [ ] Sort by name, score, date

**Test Steps:**
1. Navigate to /dashboard/crm
2. Verify contact list loads
3. Verify search box works
4. Verify can sort by different columns

**Expected Result:** All leads accessible in CRM view

---

### US-024: Search Contacts
**As a** user  
**I want to** search for specific contacts  
**So that** I can find leads quickly

**Acceptance Criteria:**
- [ ] Search box visible
- [ ] Search by name, industry, city
- [ ] Results filter in real-time
- [ ] Clear search option

**Test Steps:**
1. Navigate to CRM
2. Type "Technology" in search
3. Verify only tech companies shown
4. Clear search
5. Type "Salt Lake"
6. Verify only SLC companies shown

**Expected Result:** Search filters contacts correctly

---

### US-025: View Contact Details
**As a** user  
**I want to** see full details for a contact  
**So that** I have all information in one place

**Acceptance Criteria:**
- [ ] Clicking contact shows detail panel
- [ ] Shows: name, industry, revenue, location, description
- [ ] Shows contact info (email, phone, website)
- [ ] Shows notes history
- [ ] Shows activity history

**Test Steps:**
1. Navigate to CRM
2. Click on a contact
3. Verify detail panel opens
4. Verify all fields displayed
5. Verify notes section visible
6. Verify activity history visible

**Expected Result:** Complete contact information displayed

---

### US-026: Add Note to Contact
**As a** user  
**I want to** add notes to a contact  
**So that** I can track conversations and thoughts

**Acceptance Criteria:**
- [ ] Note input field visible
- [ ] Can type and save note
- [ ] Note appears in history
- [ ] Timestamp recorded
- [ ] Activity logged

**Test Steps:**
1. Navigate to CRM
2. Select a contact
3. Type note: "Called owner, interested in discussing"
4. Click save
5. Verify note appears in history
6. Verify activity logged

**Expected Result:** Note saved and visible in contact history

---

### US-027: View Activity History
**As a** user  
**I want to** see all activity for a contact  
**So that** I have full context of interactions

**Acceptance Criteria:**
- [ ] Activity feed visible for each contact
- [ ] Shows: discovery, emails sent, replies, status changes
- [ ] Chronological order
- [ ] Timestamps displayed

**Test Steps:**
1. Navigate to CRM
2. Select contact with history
3. Verify activity feed shows:
   - When lead was discovered
   - Emails sent
   - Status changes
4. Verify chronological order

**Expected Result:** Complete activity history visible

---

### US-028: Quick Email from CRM
**As a** user  
**I want to** send an email directly from the contact view  
**So that** I can quickly reach out to owners

**Acceptance Criteria:**
- [ ] Email button visible on contact with email
- [ ] Clicking opens email compose modal
- [ ] Pre-filled with contact's email
- [ ] Templates available

**Test Steps:**
1. Navigate to CRM
2. Select contact with email
3. Click email button
4. Verify compose modal opens
5. Verify email pre-filled
6. Verify templates available

**Expected Result:** Email compose opens with contact context

---

## ✉️ EMAIL OUTREACH

### US-029: Compose Email
**As a** user  
**I want to** compose an email to a business owner  
**So that** I can initiate acquisition discussions

**Acceptance Criteria:**
- [ ] Email compose modal accessible
- [ ] To field pre-filled (if known)
- [ ] Subject field editable
- [ ] Body field with text area
- [ ] Send button

**Test Steps:**
1. Navigate to Pipeline or CRM
2. Select lead with email
3. Click "Send Email"
4. Verify compose modal opens
5. Fill subject: "Acquisition Opportunity"
6. Fill body with message

**Expected Result:** Email ready to send

---

### US-030: Use Email Template
**As a** user  
**I want to** use pre-written email templates  
**So that** I can send professional outreach quickly

**Acceptance Criteria:**
- [ ] Template selector visible
- [ ] Templates: Introduction, Follow-up, Discovery
- [ ] Selecting template populates subject and body
- [ ] Variables auto-replaced (business_name, owner_name, etc.)

**Test Steps:**
1. Open email compose
2. Click template dropdown
3. Select "Introduction" template
4. Verify subject populated: "Acquisition Opportunity - [Business Name]"
5. Verify body populated with template text
6. Verify variables replaced with lead data

**Expected Result:** Template loaded with personalized content

---

### US-031: Send Email via Gmail
**As a** user  
**I want to** send emails through my Gmail account  
**So that** responses come to my inbox and are tracked

**Acceptance Criteria:**
- [ ] Email sends via Gmail API
- [ ] Email appears in sent folder
- [ ] Lead status updated to "outreach"
- [ ] Activity logged
- [ ] Email count incremented

**Test Steps:**
1. Ensure Gmail authenticated
2. Compose email to lead
3. Click "Send"
4. Verify success message
5. Check Gmail sent folder
6. Verify lead status changed to "outreach"
7. Verify activity logged

**Expected Result:** Email sent via Gmail, tracked in system

---

### US-032: Email Rate Limiting
**As a** user  
**I want to** have daily email limits  
**So that** I don't exceed Gmail sending limits or appear spammy

**Acceptance Criteria:**
- [ ] Daily limit configurable in settings
- [ ] Cannot send more than limit per day
- [ ] Warning when approaching limit
- [ ] Queue or block when limit reached

**Test Steps:**
1. Set daily limit to 3 in settings
2. Send 3 emails
3. Attempt to send 4th email
4. Verify warning or block

**Expected Result:** Email sending respects daily limit

---

## ⚙️ SETTINGS & CONFIGURATION

### US-033: Configure Email Limits
**As a** user  
**I want to** set my daily email sending limit  
**So that** I control outreach volume

**Acceptance Criteria:**
- [ ] Slider control for daily limit (5-100)
- [ ] Current value displayed
- [ ] Save button
- [ ] Success confirmation

**Test Steps:**
1. Navigate to Settings
2. Find "Daily Email Limit" section
3. Move slider to 25
4. Click Save
5. Verify success message
6. Verify setting persisted

**Expected Result:** Email limit saved and applied

---

### US-034: Configure Auto-Approve
**As a** user  
**I want to** set an auto-approve score threshold  
**So that** high-quality leads bypass manual review

**Acceptance Criteria:**
- [ ] Slider for threshold (0-100, 0 = off)
- [ ] Current value displayed
- [ ] Explanation of functionality
- [ ] Save button

**Test Steps:**
1. Navigate to Settings
2. Find "Auto-Approval" section
3. Set threshold to 80
4. Click Save
5. Verify success message

**Expected Result:** Leads >= 80 score auto-approved

---

### US-035: Configure Discovery Frequency
**As a** user  
**I want to** set how often discovery runs  
**So that** I control lead flow

**Acceptance Criteria:**
- [ ] Options: Hourly, Daily, Weekly, Manual
- [ ] Current selection highlighted
- [ ] Save button
- [ ] Applied to scheduled jobs

**Test Steps:**
1. Navigate to Settings
2. Find "Discovery Schedule" section
3. Click "Daily"
4. Click Save
5. Verify discovery runs daily

**Expected Result:** Discovery scheduled per preference

---

### US-036: Configure Notifications
**As a** user  
**I want to** choose what notifications I receive  
**So that** I stay informed without spam

**Acceptance Criteria:**
- [ ] Checkboxes for: new leads, email replies, daily summary
- [ ] Email address field
- [ ] Save button
- [ ] Test notification option

**Test Steps:**
1. Navigate to Settings
2. Find "Notifications" section
3. Check "New leads" and "Email replies"
4. Enter notification email
5. Click Save

**Expected Result:** Notifications configured

---

## 📁 CSV IMPORT

### US-037: Upload CSV Preview
**As a** user  
**I want to** upload a CSV file and preview before importing  
**So that** I can verify the data looks correct

**Acceptance Criteria:**
- [ ] CSV upload interface
- [ ] Auto-detects column mapping
- [ ] Shows preview of first 5 rows
- [ ] Shows detected column mappings
- [ ] Shows any errors

**Test Steps:**
1. Navigate to Import page (or use API)
2. Upload CSV with columns: Business Name, Industry, Revenue, City, State
3. Verify preview shows
4. Verify column mapping correct
5. Verify no errors

**Expected Result:** Preview displays correctly mapped data

---

### US-038: Import CSV Data
**As a** user  
**I want to** import leads from a CSV file  
**So that** I can use external data sources

**Acceptance Criteria:**
- [ ] CSV content accepted
- [ ] Leads created in database
- [ ] Duplicates skipped
- [ ] Import summary returned
- [ ] Activity logged

**Test Steps:**
1. Prepare CSV with 10 businesses
2. POST to /api/leads/import
3. Verify response shows count imported
4. Navigate to Lead Backlog
5. Verify new leads appear
6. Check activity log for import event

**Expected Result:** Leads imported, duplicates handled

---

### US-039: CSV Format Flexibility
**As a** user  
**I want to** import CSVs with different column names  
**So that** I don't need to reformat exports

**Acceptance Criteria:**
- [ ] Accepts variations: "Company" vs "Business Name"
- [ ] Accepts variations: "Annual Revenue" vs "Revenue"
- [ ] Accepts variations: "Email Address" vs "Email"
- [ ] Auto-detects common formats

**Test Steps:**
1. Import CSV with "Company" column
2. Import CSV with "Annual Revenue" column
3. Import CSV with "Email Address" column
4. Verify all map correctly

**Expected Result:** Flexible column name detection

---

### US-040: Duplicate Detection
**As a** user  
**I want to** prevent duplicate leads  
**So that** my database stays clean

**Acceptance Criteria:**
- [ ] Detects duplicates by name + city
- [ ] Skips duplicates during import
- [ ] Reports skipped count
- [ ] Does not block import

**Test Steps:**
1. Import CSV with 5 leads
2. Import same CSV again
3. Verify 0 new leads added
4. Verify response shows 5 duplicates skipped

**Expected Result:** Duplicates detected and skipped

---

## 🔒 SECURITY & ERROR HANDLING

### US-041: Session Expiration
**As a** user  
**I want to** be logged out when my session expires  
**So that** my account stays secure

**Acceptance Criteria:**
- [ ] JWT tokens expire after set time
- [ ] Expired token redirects to login
- [ ] User notified of expiration
- [ ] Can log back in seamlessly

**Test Steps:**
1. Log in
2. Wait for token expiration (or manually expire)
3. Attempt API call
4. Verify 401 response
5. Verify redirect to login

**Expected Result:** Secure session handling

---

### US-042: Unauthorized Access
**As a** user  
**I want to** only access my own data  
**So that** my leads are private

**Acceptance Criteria:**
- [ ] Users cannot view other users' leads
- [ ] API endpoints verify ownership
- [ ] 403 error for unauthorized access

**Test Steps:**
1. User A creates lead
2. User B attempts to access lead via API
3. Verify 403 forbidden response
4. Verify User B cannot see lead in their list

**Expected Result:** Data isolation enforced

---

### US-043: API Error Handling
**As a** user  
**I want to** see helpful error messages  
**So that** I understand what went wrong

**Acceptance Criteria:**
- [ ] Network errors show retry option
- [ ] Validation errors show what to fix
- [ ] Server errors show generic message
- [ ] Errors logged for debugging

**Test Steps:**
1. Disconnect network
2. Try to load dashboard
3. Verify error message shown
4. Reconnect and retry
5. Verify recovery works

**Expected Result:** Graceful error handling

---

## 🔄 EDGE CASES

### US-044: Empty State Handling
**As a** new user  
**I want to** see helpful empty states  
**So that** I know what to do next

**Acceptance Criteria:**
- [ ] Empty backlog shows "No leads yet" message
- [ ] Empty pipeline shows getting started guide
- [ ] Empty CRM shows how to add contacts

**Test Steps:**
1. Create new account
2. Navigate to Lead Backlog
3. Verify helpful empty state message
4. Navigate to Pipeline
5. Verify getting started guide

**Expected Result:** Helpful guidance for new users

---

### US-045: Large Data Handling
**As a** user with many leads  
**I want to** the app to remain performant  
**So that** I can manage large pipelines

**Acceptance Criteria:**
- [ ] Pagination for large lists
- [ ] Lazy loading for activities
- [ ] Search works with 1000+ leads
- [ ] Dashboard loads quickly

**Test Steps:**
1. Import 500 leads via CSV
2. Navigate to Lead Backlog
3. Verify pagination works
4. Verify search response < 1 second

**Expected Result:** Performance acceptable with large datasets

---

### US-046: Mobile Responsiveness
**As a** mobile user  
**I want to** use the app on my phone  
**So that** I can manage leads on the go

**Acceptance Criteria:**
- [ ] Layout adjusts to mobile screen
- [ ] Touch-friendly buttons
- [ ] Readable text without zooming
- [ ] Pipeline horizontally scrollable

**Test Steps:**
1. Open app on mobile device
2. Navigate through all screens
3. Verify readable layout
4. Test touch interactions

**Expected Result:** Usable on mobile devices

---

## ✅ TEST SUMMARY

| Category | Stories | Priority |
|----------|---------|----------|
| Authentication | 1 | P0 |
| Onboarding | 8 | P0 |
| Dashboard | 3 | P0 |
| Lead Discovery | 6 | P0 |
| Pipeline | 4 | P1 |
| CRM | 6 | P1 |
| Email | 4 | P0 |
| Settings | 4 | P1 |
| CSV Import | 4 | P1 |
| Security | 3 | P0 |
| Edge Cases | 3 | P2 |
| **Total** | **46** | |

**P0 = Critical, P1 = Important, P2 = Nice to have**

---

## 🧪 TEST EXECUTION PLAN

### Phase 1: Core Flow (P0)
- US-001 to US-009 (Auth + Onboarding)
- US-010 to US-012 (Dashboard)
- US-014 to US-017 (Lead Backlog)
- US-029 to US-031 (Email)
- US-041 to US-042 (Security)

### Phase 2: Management (P1)
- US-013, US-018 (Discovery + Auto-approve)
- US-019 to US-022 (Pipeline)
- US-023 to US-028 (CRM)
- US-033 to US-036 (Settings)

### Phase 3: Data Import (P1)
- US-037 to US-040 (CSV Import)

### Phase 4: Polish (P2)
- US-044 to US-046 (Edge cases)

---

## 📝 NOTES

- Each story can be converted into automated tests using Playwright/Cypress
- API stories can be tested with Postman or automated API tests
- Manual testing checklist for QA before releases
- User acceptance testing (UAT) guide for stakeholders
