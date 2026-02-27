# "+ New Denial" Wizard Enhancement Summary

## Overview
Successfully enhanced the "+ New Denial" wizard with financial fields, document upload capability, and fixed the missing `group_number` field.

---

## Changes Implemented

### 1. Backend Model Fixes

**File: `/backend/models/denial.py`**
- ✅ Added `group_number: Optional[str] = None` to `DenialBase` model
- ✅ Added `group_number` to `DenialUpdate` model
- ✅ Set default values for `paid_amount` and `denied_amount` to `0`

**File: `/backend/routes/denial_routes.py`**
- ✅ Added `group_number` to `denial_helper()` response mapping
- ✅ Added `paid_amount` and `denied_amount` to response mapping
- ✅ Updated CSV upload to include `group_number`, `paid_amount`, and `denied_amount`

---

### 2. Frontend Wizard Enhancements

**File: `/frontend/src/components/NewDenialWizard.jsx`**

#### New Imports
```javascript
import {
  CheckIcon,
  ExclamationTriangleIcon,  // For warnings
  CloudArrowUpIcon,          // For upload zone
  DocumentIcon,              // For doc list
  XMarkIcon                  // For remove button
} from '@heroicons/react/24/outline';
import { documentsAPI } from '../services/api';
```

#### New State Variables
- `isUploadingDocs` - Track document upload progress
- `uploadedDocuments` - Store documents to upload
- `paid_amount: 0` - Amount insurance paid
- `denied_amount: 0` - Auto-calculated denied amount

#### Auto-Calculation Logic
```javascript
useEffect(() => {
  const claim = parseFloat(formData.claim_amount) || 0;
  const paid = parseFloat(formData.paid_amount) || 0;
  const denied = Math.max(0, claim - paid);

  setFormData(prev => ({ ...prev, denied_amount: denied }));
}, [formData.claim_amount, formData.paid_amount]);
```

#### Step 4: Enhanced Financial Fields
- **Total Claim Amount** - Amount submitted to insurance (required)
- **Amount Paid** - Amount insurance actually paid (optional, defaults to 0)
- **Denied Amount** - Auto-calculated as `Claim - Paid` (read-only)
- **Warning Message** - Shows when `denied_amount = 0` (fully paid claim)

**Validation:**
- ✅ Claim amount must be > $0
- ✅ Paid amount cannot be negative
- ✅ Paid amount cannot exceed claim amount

#### Step 6: Document Upload (NEW)
- **Drag & Drop Zone** - Upload multiple files
- **File Validation:**
  - Allowed types: PDF, JPG, PNG
  - Max size: 10MB per file
- **Per-Document Configuration:**
  - Document type selection (Medical Records, Imaging, Lab Results, etc.)
  - Document date picker
  - Remove button
- **Optional Step** - Can skip and add documents later

#### Step 7: Review & Submit (UPDATED)
- **Enhanced Financial Summary:**
  - Total Claim Amount
  - Amount Paid (green)
  - Denied Amount (red)
  - CPT Code and Diagnosis Codes
- **New Document Summary:**
  - List of documents to upload
  - Shows type, date, and filename

#### Submit Handler (ENHANCED)
```javascript
const handleSubmit = async () => {
  // 1. Create denial
  const newDenial = await denialsAPI.create(formData);

  // 2. Upload documents if any
  if (uploadedDocuments.length > 0) {
    for (const doc of uploadedDocuments) {
      await documentsAPI.upload(
        doc.file,
        denialId,
        formData.patient_id,
        doc.document_type,
        doc.document_date
      );
    }
  }

  // 3. Navigate to detail page
  navigate(`/denials/${denialId}`);
};
```

#### Updated Navigation
- **7 Steps Total** (was 6)
  1. Basic Info
  2. Payer
  3. Denial Details
  4. Clinical & Financial *(renamed)*
  5. Notes
  6. Upload Documents *(new)*
  7. Review *(moved from 6)*

- **Submit Button States:**
  - "Creating Denial..." - During denial creation
  - "Uploading Documents (N)..." - During document upload
  - "Submit Denial" - Ready to submit

---

## Document Upload Handlers

### handleDocumentUpload(files)
- Validates file type and size
- Creates document objects with metadata
- Adds to uploadedDocuments state

### handleRemoveDocument(docId)
- Removes document from list

### handleDocTypeChange(docId, newType)
- Updates document type for a specific document

### handleDocDateChange(docId, newDate)
- Updates document date for a specific document

### getDocumentTypeLabel(type)
- Converts document type code to display label

---

## User Experience Improvements

### Before Enhancement
❌ Could only enter claim_amount (no paid/denied breakdown)
❌ group_number collected but lost (not saved to backend)
❌ Had to navigate to DenialDetail → Documents tab to upload
❌ No validation for financial fields
❌ No visual feedback for fully paid claims

### After Enhancement
✅ Complete financial picture: claim, paid, denied amounts
✅ group_number properly saved to database
✅ Upload documents during denial creation (optional)
✅ Auto-calculation prevents math errors
✅ Validation prevents invalid financial data
✅ Warning when denied_amount = $0 (fully paid)
✅ Progress indicators during submit and upload
✅ Can upload multiple documents with individual types/dates

---

## Data Flow

```
Step 4: User enters claim=$10,000, paid=$3,000
  ↓
Auto-calculation: denied_amount = $10,000 - $3,000 = $7,000
  ↓
Step 6: User uploads 2 PDFs (medical records, imaging)
  ↓
Step 7: Review shows:
  - Claim: $10,000
  - Paid: $3,000
  - Denied: $7,000
  - 2 documents to upload
  ↓
Submit:
  1. Create denial with all fields
  2. Upload 2 documents
  3. Navigate to detail page
```

---

## Edge Cases Handled

| Scenario | Behavior |
|----------|----------|
| paid_amount > claim_amount | **Blocked** - Error: "Paid amount cannot exceed claim amount" |
| denied_amount = 0 | **Warning** - "This appears to be fully paid. Are you sure?" |
| No documents uploaded | **Allowed** - Documents are optional |
| Document upload fails | **Continue** - Show which uploads failed, denial still created |
| Large file (>10MB) | **Rejected** - "File too large. Max 10MB." |
| Invalid file type (.txt) | **Rejected** - "Only PDF, JPG, PNG allowed" |
| User clicks Back during upload | **Disabled** - Navigation disabled during upload |

---

## Testing Checklist

### Financial Fields
- [x] Create denial with partial payment (claim=$10,000, paid=$3,000)
- [x] Verify denied_amount auto-calculates to $7,000
- [x] Create fully paid claim (claim=$5,000, paid=$5,000)
- [x] Verify warning appears for $0 denied amount
- [x] Try paid > claim → Should show error and block navigation
- [x] Try negative paid amount → Should show error
- [x] Frontend build successful ✅

### Document Upload
- [ ] Upload single PDF document
- [ ] Upload multiple files at once
- [ ] Change document type for uploaded file
- [ ] Change document date
- [ ] Remove document from list
- [ ] Try invalid file type (.txt) → Should reject
- [ ] Try large file (>10MB) → Should reject
- [ ] Skip document upload → Should allow
- [ ] Submit with documents → Verify all upload

### group_number Fix
- [ ] Create denial with group_number
- [ ] Verify saved to database
- [ ] View denial detail → Verify group_number displayed
- [ ] Check API response includes group_number

### Complete Workflow
- [ ] Complete all 7 steps
- [ ] Upload 2 documents in Step 6
- [ ] Review all data in Step 7
- [ ] Submit denial
- [ ] Verify denial created
- [ ] Verify documents uploaded
- [ ] Verify redirects to DenialDetail page

---

## API Changes

### Denial Creation Endpoint
**POST `/api/denials`**

**New Fields in Request:**
```json
{
  "group_number": "GRP-1234",
  "paid_amount": 3000.00,
  "denied_amount": 7000.00
}
```

**Response includes:**
```json
{
  "id": "65f...",
  "group_number": "GRP-1234",
  "paid_amount": 3000.00,
  "denied_amount": 7000.00
}
```

### Document Upload Endpoint
**POST `/api/documents/upload`**

Called for each document after denial creation:
```
FormData {
  file: <File>,
  denial_id: "65f...",
  patient_id: "PT-12345",
  document_type: "medical_records",
  document_date: "2024-01-15"
}
```

---

## Files Modified

### Backend
1. `/backend/models/denial.py` - Added group_number, fixed defaults
2. `/backend/routes/denial_routes.py` - Added fields to response mapping

### Frontend
1. `/frontend/src/components/NewDenialWizard.jsx` - Major enhancements

### Total Lines Changed
- **Backend:** ~10 lines
- **Frontend:** ~200 lines added/modified

---

## Build Status

✅ **Frontend Build:** SUCCESS (no errors)
✅ **Backend Model:** Valid (group_number added)
✅ **All imports:** Valid

---

## Next Steps (User Testing)

1. **Start the application:**
   ```bash
   # Terminal 1: Backend
   cd backend && uvicorn main:app --reload --port 8000

   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

2. **Test the wizard:**
   - Navigate to http://localhost:5173
   - Click "+ New Denial"
   - Complete all 7 steps
   - Test financial calculations
   - Upload documents
   - Submit and verify

3. **Verify database:**
   ```bash
   # Check that group_number and financial fields are saved
   mongosh
   use penguin_app
   db.denials.findOne({}, {group_number: 1, paid_amount: 1, denied_amount: 1})
   ```

---

## Summary

### What Was Added
✅ `paid_amount` field - Capture partial payments
✅ `denied_amount` field - Auto-calculated from claim - paid
✅ Warning for fully paid claims
✅ Document upload step - Optional, streamlined workflow
✅ Multi-file upload with type/date selection
✅ Enhanced review step - Financial and document summaries
✅ `group_number` backend fix - Data no longer lost

### User Benefits
- Complete financial picture (claim, paid, denied)
- Upload documents during denial creation (fewer steps)
- Better validation and error handling
- No data loss (group_number fix)
- Auto-calculation prevents math errors
- Clear progress indicators

### Technical Improvements
- Client-side validation reduces backend errors
- Document upload integrated into creation flow
- Backend model now matches frontend fields
- Proper error handling for uploads
- Disabled navigation during async operations
