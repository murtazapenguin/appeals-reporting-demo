# Visual Workflow Diagram: Before vs After Fix

## Before Fix: 7-Step Wizard with Document Upload

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEW DENIAL WIZARD (BEFORE)                    │
│                         7 STEPS - SLOW                           │
└─────────────────────────────────────────────────────────────────┘

User clicks "+ New Denial"
        │
        ▼
┌─────────────────────┐
│  Step 1: Basic Info │
│  ├─ Claim Number    │
│  ├─ Patient Name    │
│  ├─ Patient ID      │
│  └─ Provider        │
└─────────────────────┘
        │ NEXT
        ▼
┌─────────────────────┐
│   Step 2: Payer     │
│  ├─ Insurance Payer │
│  ├─ Policy Number   │
│  └─ Group Number    │
└─────────────────────┘
        │ NEXT
        ▼
┌─────────────────────────────┐
│  Step 3: Denial Details     │
│  ├─ Service Date: 2025-11-06│ ← Important for date range
│  ├─ Denial Date: 2026-01-21 │ ← Important for date range
│  ├─ Denial Category         │
│  └─ Denial Reason           │
└─────────────────────────────┘
        │ NEXT
        ▼
┌────────────────────────────────┐
│ Step 4: Clinical & Financial   │
│  ├─ Claim Amount: $25,000      │
│  ├─ Paid Amount: $0            │
│  ├─ Denied Amount: $25,000     │
│  ├─ CPT Code: 27447            │
│  └─ Diagnosis Codes: M17.11    │
└────────────────────────────────┘
        │ NEXT
        ▼
┌─────────────────────┐
│   Step 5: Notes     │
│  ├─ Internal Notes  │
│  └─ Priority        │
└─────────────────────┘
        │ NEXT
        ▼
╔═════════════════════════════════════════════════════════════╗
║  Step 6: Upload Documents ❌ PROBLEM STEP                   ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ Drop files or click to upload                        │   ║
║  └──────────────────────────────────────────────────────┘   ║
║  ┌──────────────────────────────────────────────────────┐   ║
║  │ 📄 medical_record.pdf                                │   ║
║  │    Type: Medical Records                             │   ║
║  │    Date: 2026-01-29 ❌ HARDCODED TO TODAY            │   ║
║  │          (8 days AFTER denial_date)                  │   ║
║  └──────────────────────────────────────────────────────┘   ║
║                                                              ║
║  ⚠️  Problems:                                               ║
║  • No guidance on valid date range                          ║
║  • No warning that date is wrong                            ║
║  • User doesn't know document will be ignored               ║
║  • Slows down denial creation                               ║
╚═════════════════════════════════════════════════════════════╝
        │ NEXT
        ▼
┌─────────────────────┐
│  Step 7: Review     │
│  ├─ All info        │
│  └─ Documents (1)   │
└─────────────────────┘
        │ SUBMIT (slow - uploading documents)
        ▼
┌─────────────────────────────────────────┐
│  Creating denial...                     │
│  Uploading documents (1)...   ⏳ SLOW   │
└─────────────────────────────────────────┘
        │ 5-10 seconds later
        ▼
┌─────────────────────────────────────────┐
│       Denial Detail Page                │
│                                         │
│  Documents (1):                         │
│  ✓ medical_record.pdf (2026-01-29)     │
└─────────────────────────────────────────┘
        │ User clicks "Evaluate Criteria"
        ▼
╔═════════════════════════════════════════╗
║  Criteria Evaluation                    ║
║  ┌─────────────────────────────────┐   ║
║  │ Valid Date Range:               │   ║
║  │ 2025-08-08 to 2026-01-21       │   ║
║  │                                 │   ║
║  │ Document Date: 2026-01-29      │   ║
║  │ Status: ❌ OUT OF RANGE         │   ║
║  └─────────────────────────────────┘   ║
║                                         ║
║  ❌ Result: "No patient documents      ║
║             found in the required      ║
║             date range"                ║
║                                         ║
║  Cannot generate appeal letter 😞       ║
╚═════════════════════════════════════════╝
```

---

## After Fix: 6-Step Wizard + Smart Document Upload

```
┌─────────────────────────────────────────────────────────────────┐
│                     NEW DENIAL WIZARD (AFTER)                    │
│                         6 STEPS - FAST ✅                        │
└─────────────────────────────────────────────────────────────────┘

User clicks "+ New Denial"
        │
        ▼
┌─────────────────────┐
│  Step 1: Basic Info │
│  ├─ Claim Number    │
│  ├─ Patient Name    │
│  ├─ Patient ID      │
│  └─ Provider        │
└─────────────────────┘
        │ NEXT
        ▼
┌─────────────────────┐
│   Step 2: Payer     │
│  ├─ Insurance Payer │
│  ├─ Policy Number   │
│  └─ Group Number    │
└─────────────────────┘
        │ NEXT
        ▼
┌─────────────────────────────┐
│  Step 3: Denial Details     │
│  ├─ Service Date: 2025-11-06│ ← Stored for later use
│  ├─ Denial Date: 2026-01-21 │ ← Stored for later use
│  ├─ Denial Category         │
│  └─ Denial Reason           │
└─────────────────────────────┘
        │ NEXT
        ▼
┌────────────────────────────────┐
│ Step 4: Clinical & Financial   │
│  ├─ Claim Amount: $25,000      │
│  ├─ Paid Amount: $0            │
│  ├─ Denied Amount: $25,000     │
│  ├─ CPT Code: 27447            │
│  └─ Diagnosis Codes: M17.11    │
└────────────────────────────────┘
        │ NEXT
        ▼
┌─────────────────────┐
│   Step 5: Notes     │
│  ├─ Internal Notes  │
│  └─ Priority        │
└─────────────────────┘
        │ NEXT
        ▼
┌─────────────────────┐
│  Step 6: Review ✅  │  ← Moved from Step 7
│  ├─ All info        │
│  └─ No documents    │  ← No document section
└─────────────────────┘
        │ SUBMIT (fast - no uploads)
        ▼
┌─────────────────────────────────────────┐
│  Creating denial...   ⚡ FAST            │
└─────────────────────────────────────────┘
        │ 1-2 seconds later
        ▼
╔═════════════════════════════════════════════════════════════╗
║            Denial Detail Page                               ║
║                                                             ║
║  ┌───────────────────────────────────────────────────┐     ║
║  │  Documents (0)                                    │     ║
║  │  ┌─────────────────────────────────────┐         │     ║
║  │  │  📤 Upload Document                 │         │     ║
║  │  └─────────────────────────────────────┘         │     ║
║  └───────────────────────────────────────────────────┘     ║
╚═════════════════════════════════════════════════════════════╝
        │ User clicks "Upload Document"
        ▼
╔═════════════════════════════════════════════════════════════╗
║            Document Upload Modal ✨ SMART                   ║
║                                                             ║
║  ┌──────────────────────────────────────────────────┐      ║
║  │ 📄 Drop PDF here or click to upload              │      ║
║  └──────────────────────────────────────────────────┘      ║
║                                                             ║
║  Document Type: [Medical Records ▼]                        ║
║                                                             ║
║  Document Date: [2025-11-06] ✅ SMART DEFAULT              ║
║                 └─ Defaults to service_date!               ║
║                                                             ║
║  ℹ️  Valid range for evaluation:                           ║
║     2025-08-08 to 2026-01-21                               ║
║     └─ Visual hint shows valid range                       ║
║                                                             ║
║  ✅ Benefits:                                               ║
║  • Date defaults to service_date (in range)                ║
║  • User sees valid range immediately                       ║
║  • Visual feedback prevents errors                         ║
╚═════════════════════════════════════════════════════════════╝
        │ User uploads medical_record.pdf
        ▼
┌─────────────────────────────────────────┐
│       Denial Detail Page                │
│                                         │
│  Documents (1):                         │
│  ✓ medical_record.pdf (2025-11-06) ✅  │
└─────────────────────────────────────────┘
        │ User clicks "Evaluate Criteria"
        ▼
╔═════════════════════════════════════════╗
║  Criteria Evaluation                    ║
║  ┌─────────────────────────────────┐   ║
║  │ Valid Date Range:               │   ║
║  │ 2025-08-08 to 2026-01-21       │   ║
║  │                                 │   ║
║  │ Document Date: 2025-11-06      │   ║
║  │ Status: ✅ IN RANGE             │   ║
║  └─────────────────────────────────┘   ║
║                                         ║
║  ✅ Result: Found 1 document           ║
║                                         ║
║  ✅ Evidence extracted successfully     ║
║  ✅ Can generate appeal letter 😊       ║
╚═════════════════════════════════════════╝
```

---

## Date Validation Warning Flow

```
User opens upload modal
        │
        ▼
┌─────────────────────────────────────────┐
│  Document Date: [2025-11-06] ✅         │
│  ℹ️  Valid range: 2025-08-08 to        │
│     2026-01-21                          │
│  └─ No warning (date is in range)      │
└─────────────────────────────────────────┘
        │ User changes date to 2026-01-29
        ▼
╔═════════════════════════════════════════╗
║  Document Date: [2026-01-29] ⚠️         ║
║  ℹ️  Valid range: 2025-08-08 to        ║
║     2026-01-21                          ║
║                                         ║
║  ┌─────────────────────────────────┐   ║
║  │ ⚠️  Warning: This date is       │   ║
║  │ outside the evaluation range.   │   ║
║  │ Documents may not be included   │   ║
║  │ in criteria evaluation.         │   ║
║  └─────────────────────────────────┘   ║
║  └─ Amber warning box appears          ║
╚═════════════════════════════════════════╝
        │ User realizes mistake
        │ Changes date back to 2025-11-06
        ▼
┌─────────────────────────────────────────┐
│  Document Date: [2025-11-06] ✅         │
│  ℹ️  Valid range: 2025-08-08 to        │
│     2026-01-21                          │
│  └─ Warning cleared                     │
└─────────────────────────────────────────┘
        │ Uploads successfully
        ▼
    Document in range! ✅
```

---

## Date Range Calculation Visual

```
TIMELINE: Denial for Knee Surgery
═══════════════════════════════════════════════════════════════

              90 days before        Service        Denial
                service               Date           Date
                   │                   │              │
                   ▼                   ▼              ▼
  ────────────┬───────────────────┬─────────────┬────────┬──────
              │                   │             │        │
          Aug 8                Nov 6         Jan 21   Jan 29
          2025                  2025          2026     2026
              │                   │             │        │
              └───────────────────┴─────────────┘        │
                                  │                      │
                     ✅ VALID RANGE (135 days)          │
                                                         │
                                                ❌ OUT OF RANGE
                                                   (OLD DEFAULT)

KEY:
├─ Aug 8, 2025:  Start of valid range (service_date - 90 days)
├─ Nov 6, 2025:  Service date (surgery performed) ← NEW DEFAULT ✅
├─ Jan 21, 2026: Denial date (insurance denies claim)
└─ Jan 29, 2026: Today (old default - 8 days too late) ❌

Documents dated Nov 6, 2025 ✅ IN RANGE → Found by evaluation
Documents dated Jan 29, 2026 ❌ OUT OF RANGE → Ignored by evaluation
```

---

## Multi-Denial Workflow

```
SCENARIO: User creates 2 denials with different dates

┌─────────────────────────────────────────────────────────────┐
│                      Denial #1                              │
│  Service Date: 2025-11-06                                   │
│  Denial Date: 2026-01-21                                    │
│  Valid Range: 2025-08-08 to 2026-01-21                     │
└─────────────────────────────────────────────────────────────┘
        │ Upload document
        ▼
    Default Date: 2025-11-06 ✅
    Date Range: 2025-08-08 to 2026-01-21 ✅

┌─────────────────────────────────────────────────────────────┐
│                      Denial #2                              │
│  Service Date: 2025-10-15 (different!)                     │
│  Denial Date: 2026-01-15 (different!)                      │
│  Valid Range: 2025-07-17 to 2026-01-15                     │
└─────────────────────────────────────────────────────────────┘
        │ Upload document
        ▼
    Default Date: 2025-10-15 ✅ (NOT 2025-11-06!)
    Date Range: 2025-07-17 to 2026-01-15 ✅ (Different range!)

✅ Each denial has its own correct default date
✅ No state pollution between denials
✅ Date ranges calculated independently
```

---

## Component Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    DenialDetail.jsx                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ const [denial, setDenial] = useState(null)           │  │
│  │                                                       │  │
│  │ denial = {                                           │  │
│  │   id: "12345",                                       │  │
│  │   service_date: "2025-11-06", ← Passed to modal     │  │
│  │   denial_date: "2026-01-21"   ← Passed to modal     │  │
│  │   patient_id: "PAT-12345"                           │  │
│  │   ...                                               │  │
│  │ }                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  <DocumentUploadModal                                      │
│    isOpen={isUploadModalOpen}                             │
│    denial={denial} ← NEW PROP                             │
│    onUpload={handleDocumentUpload}                        │
│  />                                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              DocumentUploadModal.jsx                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ const DocumentUploadModal = ({ denial }) => {        │  │
│  │                                                       │  │
│  │   // Smart default calculation                       │  │
│  │   const getDefaultDocumentDate = () => {            │  │
│  │     if (!denial) return today;                      │  │
│  │     return denial.service_date ||                   │  │
│  │            denial.denial_date ||                    │  │
│  │            today;                                   │  │
│  │   };                                                │  │
│  │                                                       │  │
│  │   // Date range calculation                          │  │
│  │   const calculateStartDate = (serviceDate) => {     │  │
│  │     const date = new Date(serviceDate);             │  │
│  │     date.setDate(date.getDate() - 90);              │  │
│  │     return date.toISOString().split('T')[0];        │  │
│  │   };                                                │  │
│  │                                                       │  │
│  │   // Validation                                      │  │
│  │   const isDateOutOfRange = (docDate) => {           │  │
│  │     const start = calculateStartDate(               │  │
│  │       denial.service_date                           │  │
│  │     );                                              │  │
│  │     const end = denial.denial_date;                 │  │
│  │     return docDate < start || docDate > end;        │  │
│  │   };                                                │  │
│  │                                                       │  │
│  │   // UI                                              │  │
│  │   return (                                           │  │
│  │     <input type="date"                              │  │
│  │       value={getDefaultDocumentDate()}              │  │
│  │     />                                              │  │
│  │     {isDateOutOfRange(date) && <Warning />}        │  │
│  │   );                                                │  │
│  │ }                                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Benefits Summary

### Before Fix ❌
- 7-step wizard (slow)
- Documents uploaded during creation
- Date hardcoded to today
- No guidance on valid dates
- No validation warnings
- High rate of "No documents found" errors

### After Fix ✅
- 6-step wizard (fast)
- Documents uploaded later (optional)
- Date defaults to service_date (smart)
- Visual date range hint
- Real-time validation warnings
- Low rate of evaluation errors

### User Journey Improvement
```
BEFORE:
Create Denial → Upload Docs → Submit (slow) → Evaluate → ❌ Error

AFTER:
Create Denial (fast) → Upload Docs (smart dates) → Evaluate → ✅ Success
```

---

## Testing Checkpoints

Use this diagram while testing to verify each step:

### ✅ Checkpoint 1: Wizard Step Count
- [ ] Progress indicator shows 6 steps (not 7)
- [ ] No "Upload Documents" step between "Notes" and "Review"

### ✅ Checkpoint 2: Smart Default Date
- [ ] Upload modal shows service_date as default
- [ ] Not showing today's date

### ✅ Checkpoint 3: Date Range Hint
- [ ] Gray text shows valid range below date picker
- [ ] Range matches (service_date - 90) to denial_date

### ✅ Checkpoint 4: Validation Warning
- [ ] Amber warning appears when date is outside range
- [ ] Warning disappears when date is corrected
- [ ] Upload still works with warning

### ✅ Checkpoint 5: Criteria Evaluation
- [ ] Documents with correct dates are found
- [ ] No "No documents found" error
- [ ] Evidence extracted successfully

---

**Visual Reference for Testing:** Use this diagram during manual testing
**Documentation:** See TESTING_GUIDE.md for detailed test scenarios
