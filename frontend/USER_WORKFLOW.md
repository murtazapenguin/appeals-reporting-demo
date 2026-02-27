# Healthcare Claim Denial Appeal Management - User Workflow

## User States

### 1. Logged Out
- No access to application
- Only sees Login page
- Can enter email and password

### 2. Logged In (Main Application)
- Has authenticated session
- Can access all screens
- Can navigate via sidebar

### 3. In Workflow (Processing Denials)
- Viewing/editing denial records
- Evaluating criteria
- Generating appeal letters
- Reviewing documents

---

## Screen Inventory

| Screen | Route | Entry Points | Exit Points | Purpose |
|--------|-------|--------------|-------------|---------|
| **Login** | `/login` | Direct URL, Logout | Login success → Dashboard | Authenticate user |
| **Dashboard** | `/dashboard` | Login success, Sidebar, Logo | Sidebar nav, Quick actions | View metrics and KPIs |
| **Denials List** | `/denials` | Sidebar, Dashboard buttons | Row click → Detail, New button → Wizard | Browse all denials |
| **New Denial Wizard** | `/denials/new` | Denials List, Dashboard | Complete → Detail, Cancel → List | Create new denial (manual) |
| **Denial Detail** | `/denials/:id` | List row click, Wizard complete | Back → List, Sidebar | View/edit denial, evaluate criteria, generate appeal |

---

## User Journeys

### Journey 1: Login and View Dashboard
1. User navigates to application
2. Sees Login page
3. Enters email and password
4. Clicks "Sign In"
5. Redirected to Dashboard
6. Views metrics cards (Total Open, Urgent, High Probability, Recovered)
7. Views charts (Recovery Trends, Success Rate by Payer)
8. Views Performance table by Denial Category

**Success Criteria:** User sees current metrics and trends

---

### Journey 2: Submit New Denial (Manual Entry)
1. User clicks "Add New Denial" (Dashboard or Denials List)
2. Lands on New Denial Wizard - Step 1: Basic Info
   - Enter: Claim #, Patient Name, Patient ID, DOB, Provider Name, Provider ID
   - Click "Next"
3. Step 2: Payer
   - Enter: Payer Name, Payer ID, Policy Number
   - Click "Next"
4. Step 3: Denial Details
   - Enter: Service Date, Denial Date, Denial Code, Category, Reason
   - Click "Next"
5. Step 4: Clinical Info
   - Enter: Claim Amount, CPT Code, ICD-10 Codes, Service Description
   - Click "Next"
6. Step 5: Notes
   - Enter: Internal Notes, Priority Level
   - Click "Next"
7. Step 6: Review & Submit
   - Review all entered data
   - Click "Submit Denial"
8. Redirected to Denial Detail page

**Success Criteria:** Denial created and visible in list

---

### Journey 3: Upload Denials via CSV
1. User clicks "Upload CSV" button on Denials List
2. File picker opens
3. User selects CSV file (with headers: claim_number, patient_name, patient_id, payer_name, service_date, denial_date, denial_code, denial_category, claim_amount, procedure_code, diagnosis)
4. CSV uploads and processes
5. Denials List refreshes with new records

**Success Criteria:** All CSV rows appear as new denials

---

### Journey 4: Evaluate Criteria and Generate Appeal
1. User navigates to Denial Detail page
2. Clicks "Criteria Evaluation" tab
3. Clicks "Evaluate Criteria" button
4. AI evaluates medical necessity criteria vs. patient documents
5. Results display: "4 of 5 criteria met (80%)"
6. For each criterion:
   - **MET:** Shows question, status badge, evidence sources (clickable)
   - **NOT MET:** Shows question, status badge, missing documents needed
7. User clicks evidence link → switches to Documents tab → scrolls to page → highlights bounding box
8. User returns to Criteria Evaluation tab
9. Clicks "Generate Appeal" button
10. Switches to Appeal Letter tab
11. Sees structured letter with all sections:
    - Provider letterhead
    - RE: block
    - Denied Services table
    - Diagnosis codes
    - Clinical Justification (5 subsections)
    - Conclusion
    - Enclosed documents
12. Clicks "Download PDF" → saves locally
13. Clicks "Submit Appeal" → confirms → appeal marked as submitted

**Success Criteria:** Appeal generated, downloaded, and submitted

---

### Journey 5: Review Documents with Evidence Highlighting
1. User on Denial Detail page
2. Clicks "Criteria Evaluation" tab
3. Sees criterion: "Patient has documented chronic pain for >6 months" - MET
4. Clicks evidence link: "Progress Note 2024-03-15 - Page 2"
5. App switches to "Documents" tab
6. Document viewer auto-scrolls to Page 2
7. Pink bounding box highlights text: "Patient reports chronic lower back pain ongoing since 2023-09"
8. User confirms evidence supports criterion

**Success Criteria:** User can trace criteria to source evidence

---

## State Transitions

| From State | Action | To State |
|------------|--------|----------|
| Logged Out | Enter credentials + Submit | Logged In (Dashboard) |
| Dashboard | Click "Add New Denial" | New Denial Wizard |
| Dashboard | Click "View All Denials" | Denials List |
| Denials List | Click row | Denial Detail (Overview) |
| Denials List | Click "Upload CSV" | File picker → List refresh |
| Denials List | Click "New Denial" | New Denial Wizard |
| New Denial Wizard | Click "Next" (Steps 1-5) | Next step |
| New Denial Wizard | Click "Back" | Previous step |
| New Denial Wizard | Click "Cancel" | Denials List |
| New Denial Wizard | Click "Submit Denial" (Step 6) | Denial Detail |
| Denial Detail | Click tab (Overview, Criteria, Documents, Appeal) | Switch active tab |
| Denial Detail (Criteria) | Click "Evaluate Criteria" | Criteria results display |
| Denial Detail (Criteria) | Click evidence link | Documents tab with highlighting |
| Denial Detail (Criteria) | Click "Generate Appeal" | Appeal Letter tab |
| Denial Detail (Appeal) | Click "Download PDF" | PDF downloads |
| Denial Detail (Appeal) | Click "Submit Appeal" | Status updated to "submitted" |
| Denial Detail | Click Back button | Denials List |
| Any logged-in screen | Click Logout | Login page |

---

## Key Interactions

### Dashboard Metrics Cards (CRITICAL for Value Visibility)
- **Total Open Denials:** Count + $ amount at risk
- **Urgent Appeals:** Count with ≤7 days to deadline
- **High Probability:** Count with ≥70% win rate
- **Recovered This Month:** $ amount + success rate %
- **Total Recovered (YTD):** $ amount + claim count

### Criteria Evaluation Display
```
Criteria Evaluation: 4 of 5 met (80%)
[Progress bar showing 80%]

✅ Patient has documented chronic pain for >6 months - MET
   Evidence:
   [Progress Note 2024-03-15 - Page 2] (clickable)
   "Patient reports chronic lower back pain ongoing since 2023-09"

✅ Conservative treatment tried and failed - MET
   Evidence:
   [Physical Therapy Records - Page 5] (clickable)
   "Patient completed 8 weeks PT without improvement"

❌ MRI shows structural abnormality - NOT MET
   Missing Documents: MRI report from 2024-03-10
```

### Document Viewer Behavior
- Click evidence link in Criteria Evaluation
- Document Viewer:
  1. Switches to Documents tab
  2. Loads correct document
  3. Scrolls to specified page
  4. Highlights bounding box (normalized coords [x1,y1,x2,y2,x3,y3,x4,y4])
  5. Bounding box color: #fc459d (pink)

### Appeal Letter Structure
```
[Provider Letterhead]
Provider Name
Address
Phone

[Date]

RE: Appeal for Claim CLM-12345
Patient: John Doe
Date of Service: 03/15/2024

Dear Appeals Committee,

[Section 1: Introduction]
[Section 2: Denied Services Table]
[Section 3: Diagnosis Codes]
[Section 4: Clinical Justification]
  - Subsection A: Medical Necessity
  - Subsection B: Conservative Treatment
  - Subsection C: Clinical Findings
  - Subsection D: Physician Recommendation
  - Subsection E: Supporting Evidence
[Section 5: Conclusion]

Enclosed Documents:
- Progress Notes (2023-09 to 2024-03)
- Physical Therapy Records
- MRI Report

Sincerely,
Dr. Provider Name
```

---

## Navigation Paths

### Sidebar (Always Available When Logged In)
- Dashboard
- All Denials
- New Denial

### Quick Actions
- **Dashboard:** "Add New Denial", "View All Denials"
- **Denials List:** "Upload CSV", "New Denial"
- **Denial Detail:** "Evaluate Criteria", "Generate Appeal", "Download PDF", "Submit Appeal"

---

## Error Handling

| Scenario | User Sees | System Behavior |
|----------|-----------|-----------------|
| Login fails | Red error message | Stays on login page |
| CSV upload fails | Alert: "Failed to upload CSV. Check format." | List unchanged |
| Network error during load | Alert: "Network error. Try again." | Previous state |
| Criteria evaluation fails | Alert: "Failed to evaluate. Try again." | Criteria tab without results |
| Appeal generation fails | Alert: "Failed to generate. Try again." | No letter displayed |
| PDF download fails | Alert: "Failed to download. Try again." | No file downloaded |

---

## Data Flow Summary

1. **Login:** email + password → API → token stored → redirect to Dashboard
2. **Dashboard Metrics:** API calls → metricsAPI.getDashboard(), getByPayer(), getByCategory(), getTrends()
3. **Denials List:** API call → denialsAPI.getAll(filters)
4. **CSV Upload:** file → denialsAPI.uploadCSV() → list refresh
5. **New Denial:** form data → denialsAPI.create() → redirect to detail
6. **Criteria Evaluation:** denialId → criteriaAPI.evaluate() → results with evidence
7. **Evidence Click:** evidence coords → PDFViewer boundingBoxes prop → auto-scroll + highlight
8. **Generate Appeal:** denialId → appealsAPI.generateLetter() → structured letter
9. **Download PDF:** denialId → appealsAPI.downloadPDF() → blob → browser download
10. **Submit Appeal:** denialId → appealsAPI.submit() → status update

---

## End States

| Journey | End State | Outcome |
|---------|-----------|---------|
| Login and View Dashboard | Dashboard visible with metrics | User informed of current status |
| Submit New Denial | Denial Detail page | Denial created, ready for processing |
| Upload CSV | Denials List with new rows | Bulk import complete |
| Evaluate Criteria | Criteria results displayed | User knows which criteria met/not met |
| Generate Appeal | Appeal Letter displayed | Letter ready for review |
| Submit Appeal | Appeal status = "submitted" | Appeal sent to payer |
| Logout | Login page | Session cleared |
