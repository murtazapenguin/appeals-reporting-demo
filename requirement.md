# Healthcare Claim Denial Appeal Management App

## Project Overview

A full-stack application that helps medical billing staff manage, analyze, and appeal insurance claim denials for medical necessity. The app intelligently retrieves patient documents, evaluates medical necessity criteria against payer policies, and generates structured appeal letters.

---

### Phase 1: ui-builder
- Create React frontend with complete user workflows
- Output: USER_WORKFLOW.md + API_REQUIREMENTS.md
- Constraints: Vite, React Router, Tailwind CSS v4, PenguinAI branding

### Phase 2: api-builder
- Create FastAPI backend with MongoDB
- Include seed data for testing
- Constraints: Motor async driver, Pydantic models, JWT auth

### Phase 2.5: ai-integrator
- Add OCR and LLM extraction capabilities
- Implement bounding box mapping for evidence highlighting
- Constraints: MUST use penguin-ai-sdk (see AI Providers section)

### Phase 3: quality-tester
- Browser testing with Claude in Chrome
- Generate test report and apply fixes
- Constraints: MANDATORY browser testing to verify all workflows

---

## REQUIREMENTS SPECIFICATION

### REQUIREMENT 1: Claim Submission Options

Users have 2 options to submit denied claims:

**Option 1: Manual Entry**
- Click "New Denial" button
- 6-step wizard flow:
  1. Basic Info
  2. Payer
  3. Denial Details
  4. Clinical Info
  5. Notes
  6. Review

**Option 2: CSV Upload**
- Upload CSV file with all relevant details
- Required CSV headers:
  - claim_number, patient_name, patient_id, provider_name, provider_id
  - payer_name, service_date, denial_date, denial_code, denial_category
  - claim_amount, procedure_code, diagnosis

---

### REQUIREMENT 2: Patient Document Folder Structure

Documents are organized in this folder structure:

```
/documents
├── {Patient_ID}/
│   ├── {YYYY}/
│   │   ├── {MM}/
│   │   │   ├── {DD}/
│   │   │   │   ├── Medical_Records.pdf
│   │   │   │   ├── Lab_Results.pdf
│   │   │   │   └── Clinical_Notes.pdf
```

Example:
```
/documents
├── PT001/
│   ├── 2024/
│   │   ├── 10/
│   │   │   ├── 15/
│   │   │   │   └── Operative_Report.pdf
│   │   │   └── 20/
│   │   │       └── Physical_Therapy_Notes.pdf
│   │   └── 11/
│   │       └── 05/
│   │           └── MRI_Report.pdf
```

---

### REQUIREMENT 3: Document Date Range Filtering

**CRITICAL**: Fetch documents within specific date range:
- **Start Date**: 90 days BEFORE date of service
- **End Date**: Date of denial

Example:
- Service Date: October 15, 2024
- Denial Date: November 28, 2024
- **Fetch documents from**: July 17, 2024 → November 28, 2024

---

### REQUIREMENT 4: Medical Necessity Criteria System

**CRITICAL**: Store medical necessity criteria as QUESTIONS at **payer + CPT code combination** level.

#### Data Model: Medical Policies

Each policy record contains:
- payer_id and payer_name
- cpt_code and cpt_description
- denial_category
- policy_name
- effective_date
- criteria_questions (array of question objects)
- clinical_guidelines (references to authoritative sources)
- historical_overturn_rate
- average_processing_days

#### Criteria Question Structure

Each question contains:
- id (unique identifier)
- category (e.g., "Conservative Treatment", "Diagnostic Evidence")
- question (the actual question text)
- required (boolean)
- weight (numeric priority)
- evidence_keywords (array of terms to search for)
- document_types_expected (what documents might contain evidence)
- response_type (e.g., "boolean")

#### Example Criteria Questions (Total Knee Arthroplasty):

1. **Conservative Treatment**: "Has the patient completed at least 6 months of conservative treatment (physical therapy, NSAIDs, injections)?"

2. **Diagnostic Evidence**: "Does imaging show bone-on-bone contact or Grade IV cartilage loss?"

3. **Functional Limitation**: "Is there documented significant functional limitation affecting daily activities?"

4. **Treatment Failure**: "Has the patient's condition failed to improve despite conservative measures?"

#### Criteria Display UI Requirements

When user views a claim, display:

1. **Criteria Summary**: "4 of 5 criteria met (80%)"

2. **For EACH criterion**:
   - Question text
   - Status: ✓ MET or ✗ NOT MET
   - If MET: Evidence sources with clickable links to document location
   - If NOT MET: What documents are needed, why it's not met

3. **For EACH shortlisted document**:
   - Which criteria it supports
   - WHY it meets those criteria (extracted text)
   - If any criteria NOT met by this doc, explain why

Example UI:
```
┌─────────────────────────────────────────────────────────────┐
│ MEDICAL NECESSITY CRITERIA              4 of 5 MET (80%)   │
├─────────────────────────────────────────────────────────────┤
│ ✓ CRITERION 1: Conservative Treatment                  MET │
│   Has patient completed 6+ months of conservative treatment?│
│   Evidence Found:                                           │
│   • "Patient completed 8 months of PT..." (Page 3)         │
│     📄 Physical_Therapy_Records.pdf [Click to view →]      │
├─────────────────────────────────────────────────────────────┤
│ ✗ CRITERION 3: BMI Documentation                   NOT MET │
│   Is BMI documented as < 40 or with bariatric clearance?   │
│   ⚠ Missing Evidence                                       │
│   Requires: Medical Records, Pre-op Assessment             │
│   [Upload Document] [Request from Provider]                │
└─────────────────────────────────────────────────────────────┘
```

---

### REQUIREMENT 5: Evidence Viewer with Scroll-to-Evidence

**CRITICAL**: Human-in-the-loop product - users must quickly verify evidence.

#### Scroll-to-Evidence Flow:
1. User clicks evidence link in criteria panel
2. System switches to Document Viewer tab
3. PDF scrolls to correct page
4. Bounding box highlights the evidence text
5. Highlight pulses/flashes to draw attention

#### Bounding Box Data Structure:
- document_id
- document_name
- page_number
- bounding_box (normalized 0-1 coordinates: [x1, y1, x2, y2, x3, y3, x4, y4])
- extracted_text

---

### REQUIREMENT 6: Appeal Letter Format

Generate appeal letters with the following structure:

```
1. PROVIDER LETTERHEAD
   - Practice name
   - Address
   - Phone/Fax
   - NPI and Tax ID

2. DATE

3. RECIPIENT
   - Payer name
   - Claims Appeals Department
   - Address

4. RE: BLOCK
   - Post-Claim Appeal – Medical Necessity Denial
   - Patient Name
   - Date of Birth
   - Policy Number
   - Group Number
   - Claim Number (ICN)
   - Date of Service
   - Denial Date
   - Rendering Provider

5. DENIED SERVICES TABLE
   - CPT Code | Description | Units | Billed Amount
   - Total amount

6. ASSOCIATED DIAGNOSIS CODES
   - List of ICD-10 codes with descriptions

7. REASON FOR APPEAL
   - Paragraph explaining disagreement with denial

8. CLINICAL JUSTIFICATION (5 SUBSECTIONS - REQUIRED)

   a. Patient Clinical History and Conservative Treatment Failure
      - Duration of symptoms
      - Physical therapy completed (dates)
      - Medications tried and failed
      - Injections with limited relief

   b. Diagnostic Imaging Findings
      - MRI findings (date)
      - X-ray findings
      - Severity documented

   c. Intraoperative Findings and Medical Necessity of Each CPT Code
      - Why each procedure was necessary

   d. Adherence to Clinical Guidelines and Standards of Care
      - Professional society guidelines reference
      - Payer's own medical policy reference
      - Peer-reviewed literature

   e. Post-Operative Outcome
      - Clinical improvement documented
      - Pain scores (pre-op vs post-op)
      - Return to function

9. CONCLUSION
   - Request to overturn denial and approve payment

10. ENCLOSED DOCUMENTATION
    - Numbered list of supporting documents

11. SIGNATURE BLOCK
    - Provider signature
    - Credentials
    - NPI
    - CC: Patient, Practice Administrator
```

---

### REQUIREMENT 7: Enhanced Dashboard Metrics

**CRITICAL**: Show value provided over time and revenue visibility for client.

#### Required Metrics Cards:

| Total Open Denials | Urgent Appeals | High Probability | Recovered This Month | Total Recovered (YTD) |
|-------------------|----------------|------------------|---------------------|----------------------|
| Count + $ at risk | ≤7 days deadline | ≥70% win rate | Amount + rate | Amount + claim count |

#### Required Charts:

1. **Recovery Trends** (Line Chart)
   - Month-over-month recovered amounts
   - Month-over-month win rate

2. **Success Rate by Payer** (Bar Chart)
   - Win rate percentage per payer
   - Amount recovered per payer

3. **Performance by Denial Category** (Table)
   - Category | Denials | Won | Win Rate | Recovered

#### Metrics to Track:

**Volume Metrics:**
- total_denials_received
- total_appeals_submitted
- total_appeals_won
- total_appeals_lost
- total_appeals_pending

**Financial Metrics (CLIENT REVENUE VISIBILITY):**
- total_amount_at_risk
- total_amount_recovered
- average_claim_amount
- recovery_rate

**Performance Metrics:**
- win_rate
- average_time_to_resolution (days)
- average_time_to_appeal (days from denial to appeal)

**Breakdowns:**
- by_payer: [{ payer, denials, won, win_rate, recovered }]
- by_category: [{ category, denials, won, win_rate, recovered }]
- by_cpt: [{ cpt_code, denials, win_rate, recovered }]

**Trends:**
- monthly_trends: [{ month, denials, recovered, win_rate }]

---

## API STRUCTURE

```
/api
├── /auth
│   ├── POST /login
│   └── GET /me
│
├── /denials
│   ├── GET /                              # List with filters
│   ├── GET /{id}                          # Get details
│   ├── POST /                             # Create
│   ├── PUT /{id}                          # Update
│   └── PUT /{id}/status                   # Update status
│
├── /medical-policies
│   ├── GET /                              # List all
│   ├── GET /lookup?payer_id=X&cpt_code=Y  # Lookup by payer+CPT
│   ├── POST /                             # Create
│   └── PUT /{id}                          # Update
│
├── /documents
│   ├── GET /patient/{patient_id}          # All docs for patient
│   ├── GET /patient/{patient_id}/date-range  # Date-filtered docs
│   ├── GET /{id}/page/{page}              # Get page image
│   ├── POST /upload                       # Upload
│   └── POST /{id}/analyze                 # AI analysis
│
├── /criteria-evaluation
│   ├── POST /evaluate                     # Evaluate criteria vs docs
│   └── GET /denial/{denial_id}            # Get evaluation results
│
├── /appeals
│   ├── POST /generate-letter              # Generate letter
│   ├── GET /{id}/download                 # Download PDF
│   └── POST /{id}/submit                  # Submit appeal
│
└── /metrics
    ├── GET /dashboard                     # Summary metrics
    ├── GET /by-payer                      # Payer breakdown
    ├── GET /by-category                   # Category breakdown
    └── GET /trends                        # Historical trends
```

---

## DATABASE COLLECTIONS

1. **denials** - Claim denials with criteria evaluation results
2. **medical_policies** - Payer + CPT code criteria questions
3. **patient_documents** - Documents with folder structure metadata
4. **appeal_packages** - Generated appeal letters
5. **appeal_metrics** - Aggregated metrics for dashboard

---

## BRANDING

- Primary Color: `#fc459d` (PenguinAI pink)
- Secondary: `#38bdf8`
- Accent: `#f472b6`
- Background: `#171717` (dark)
- Success: `#10b981`
- Warning: `#f59e0b`
- Error: `#ef4444`
- Glass Effect: `bg-white/80 backdrop-blur-sm` (for cards/panels)

---

## PDF VIEWER

**CRITICAL CONSTRAINT**: The PDF viewer component MUST use the data-labelling-library.

- **MUST use**: PDFViewer from `/Users/vaatsav/Desktop/claude-code-agents/data-labelling-library/`
- **FORBIDDEN**: pdf.js, react-pdf, @react-pdf/renderer, or any other PDF libraries
- **Container requirement**: PDFViewer container MUST have explicit height (e.g., `h-screen`, `h-full`, or fixed pixel height)
- The PDFViewer supports bounding box overlays for evidence highlighting

---

## AI PROVIDERS

**CRITICAL CONSTRAINT**: All AI operations MUST use `penguin-ai-sdk`. Direct use of openai, anthropic, pytesseract, langchain, or boto3 is FORBIDDEN.

| Capability | Provider | SDK Usage |
|------------|----------|-----------|
| OCR | Azure Document Intelligence | `penguin.ocr` module |
| LLM | Gemini or Bedrock Claude | `penguin.llm` LLM client |

---

## VERIFICATION CHECKLIST

Before completing, verify ALL requirements are implemented:

- [ ] Manual denial entry (New Denial button)
- [ ] CSV file upload for bulk denials
- [ ] Patient document folder structure (PatientID/Date/PDFs)
- [ ] Date range filtering (90 days before service → denial date)
- [ ] Medical policies at payer + CPT code level
- [ ] Criteria stored as questions
- [ ] Criteria evaluation showing met/not met
- [ ] For each doc: WHY it meets/doesn't meet criteria
- [ ] Scroll-to-evidence in document viewer
- [ ] Bounding box highlights
- [ ] Appeal letter with full structure (5 clinical subsections)
- [ ] Dashboard metrics for client value visibility
- [ ] Recovery amount tracking
- [ ] Success rate by payer/category
