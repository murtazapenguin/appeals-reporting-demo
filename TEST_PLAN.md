# Testing Plan for "+ New Denial" Wizard Enhancements

## Pre-Test Setup

1. **Start Backend:**
   ```bash
   cd /Users/vaatsav/Desktop/claim-appeals-v2/backend
   uvicorn main:app --reload --port 8000
   ```

2. **Start Frontend:**
   ```bash
   cd /Users/vaatsav/Desktop/claim-appeals-v2/frontend
   npm run dev
   ```

3. **Open Application:**
   - Navigate to http://localhost:5173
   - Login with demo credentials

---

## Test 1: Financial Fields - Partial Payment

### Steps:
1. Click "+ New Denial" button
2. **Step 1 - Basic Info:**
   - Claim Number: `TEST-001`
   - Patient Name: `John Doe`
   - Patient ID: `PT-12345`
   - Provider: Select any provider
   - Click "Next"

3. **Step 2 - Payer:**
   - Insurance Payer: Select "Blue Cross Blue Shield"
   - Policy Number: `POL-123456`
   - Group Number: `GRP-7890` *(verify this gets saved)*
   - Click "Next"

4. **Step 3 - Denial Details:**
   - Service Date: Select any date
   - Denial Date: Select any date
   - Denial Category: "Medical Necessity"
   - Click "Next"

5. **Step 4 - Clinical & Financial:**
   - **Total Claim Amount:** `10000`
   - **Amount Paid:** `3000`
   - **Denied Amount:** Should auto-calculate to `7000` ✅
   - Procedure Code: Select any CPT code
   - Diagnosis Codes: `M54.5, M25.511`
   - Click "Next"

6. **Step 5 - Notes:**
   - Internal Notes: "Test partial payment scenario"
   - Priority: "Normal"
   - Click "Next"

7. **Step 6 - Upload Documents:**
   - Click "Skip" or upload if you have test files
   - Click "Next"

8. **Step 7 - Review:**
   - Verify Financial Summary shows:
     - Total Claim: $10,000
     - Amount Paid: $3,000 (green)
     - Denied Amount: $7,000 (red)
   - Click "Submit Denial"

### Expected Results:
✅ Denial created successfully
✅ Redirects to denial detail page
✅ Financial breakdown visible on detail page
✅ group_number saved and visible

### Verification:
```bash
# Check database
mongosh
use penguin_app
db.denials.findOne(
  {claim_number: "TEST-001"},
  {
    claim_amount: 1,
    paid_amount: 1,
    denied_amount: 1,
    group_number: 1
  }
)
```

**Expected Output:**
```json
{
  "claim_amount": 10000,
  "paid_amount": 3000,
  "denied_amount": 7000,
  "group_number": "GRP-7890"
}
```

---

## Test 2: Financial Fields - Fully Paid Claim (Warning)

### Steps:
1. Follow Test 1 steps 1-3
2. **Step 4 - Clinical & Financial:**
   - Total Claim Amount: `5000`
   - Amount Paid: `5000`
   - **Denied Amount:** Should auto-calculate to `0` ✅
   - **Warning should appear:** "Fully Paid Claim" ⚠️
   - Verify warning message: "The denied amount is $0. This appears to be a fully paid claim."
   - Continue with form submission

### Expected Results:
✅ Warning displays (amber background)
✅ Can still submit the denial (not blocked)
✅ Denial created with denied_amount = 0

---

## Test 3: Financial Fields - Validation Errors

### Test 3a: Paid > Claim
1. **Step 4:**
   - Total Claim Amount: `5000`
   - Amount Paid: `6000`
   - Click "Next"

**Expected:**
❌ Alert: "Paid amount cannot exceed claim amount"
❌ Blocked from proceeding to next step

### Test 3b: Negative Paid Amount
1. **Step 4:**
   - Total Claim Amount: `5000`
   - Amount Paid: `-100`
   - Click "Next"

**Expected:**
❌ Alert: "Paid amount cannot be negative"
❌ Blocked from proceeding

### Test 3c: Zero Claim Amount
1. **Step 4:**
   - Total Claim Amount: `0`
   - Amount Paid: `0`
   - Click "Next"

**Expected:**
❌ Alert: "Claim amount must be greater than $0"
❌ Blocked from proceeding

---

## Test 4: Document Upload - Single File

### Steps:
1. Follow Test 1 steps 1-5
2. **Step 6 - Upload Documents:**
   - Click "Drop files here or click to browse"
   - Select 1 PDF file
   - Verify file appears in list with:
     - File name
     - File size in KB
     - Document type dropdown (default: Medical Records)
     - Document date (default: today)
     - Remove button (X)
   - Change document type to "Imaging"
   - Change document date to last week
   - Click "Next"

3. **Step 7 - Review:**
   - Verify "Documents to Upload (1)" section appears
   - Shows file name, type, and date
   - Click "Submit Denial"
   - Watch button text change:
     - "Creating Denial..." → "Uploading Documents (1)..." → Navigate

### Expected Results:
✅ Document uploaded successfully
✅ Appears in DenialDetail → Documents tab
✅ Document type and date match selections

---

## Test 5: Document Upload - Multiple Files

### Steps:
1. **Step 6:**
   - Upload 3 files at once (PDF, JPG, PNG)
   - Set different types:
     - File 1: Medical Records
     - File 2: Lab Results
     - File 3: Imaging
   - Set different dates for each
   - Remove File 2 (Lab Results)
   - Verify only 2 files remain
   - Click "Next"

2. **Step 7:**
   - Verify "Documents to Upload (2)" shows correct files
   - Submit

### Expected Results:
✅ Only 2 documents uploaded (File 2 removed)
✅ Both appear in DenialDetail
✅ Types and dates match selections

---

## Test 6: Document Upload - Validation

### Test 6a: Invalid File Type
1. Try to upload a .txt file

**Expected:**
❌ Alert: "filename.txt: Invalid file type. Only PDF, JPG, PNG allowed."
❌ File not added to list

### Test 6b: Large File
1. Try to upload a file > 10MB

**Expected:**
❌ Alert: "filename.pdf: File too large. Max 10MB."
❌ File not added to list

### Test 6c: Skip Documents
1. Don't upload any files
2. Click "Next"

**Expected:**
✅ Allowed to proceed
✅ "No documents uploaded yet" message shown
✅ Can submit denial without documents

---

## Test 7: Document Upload - Upload Failure

### Simulate Upload Failure:
1. Upload 2 documents
2. Stop backend before submitting
3. Click "Submit Denial"

### Expected Results:
✅ Denial created successfully
❌ Document uploads fail
✅ User sees error in console
✅ Still redirects to denial detail page
⚠️ Documents not in database (expected behavior)

---

## Test 8: group_number Field Persistence

### Steps:
1. Create denial with group_number = "GRP-TEST-123"
2. Submit denial
3. Navigate to denial detail page
4. Verify group_number displayed in payer section

### Database Verification:
```bash
db.denials.findOne(
  {group_number: "GRP-TEST-123"},
  {group_number: 1, payer_name: 1, policy_number: 1}
)
```

**Expected:**
```json
{
  "group_number": "GRP-TEST-123",
  "payer_name": "Blue Cross Blue Shield",
  "policy_number": "POL-123456"
}
```

---

## Test 9: CSV Upload with New Fields

### Create Test CSV:
```csv
claim_number,patient_name,patient_id,provider_name,payer_name,service_date,denial_date,denial_category,claim_amount,paid_amount,denied_amount,procedure_code,diagnosis_codes,group_number
CSV-001,Jane Smith,PT-99999,Dr. Wilson,Aetna,2024-01-15,2024-02-01,Medical Necessity,15000,5000,10000,27447,M54.5,GRP-CSV-001
```

### Steps:
1. Go to Denials page
2. Click "Upload CSV"
3. Select the test CSV file
4. Verify import success message

### Verification:
```bash
db.denials.findOne(
  {claim_number: "CSV-001"},
  {
    claim_amount: 1,
    paid_amount: 1,
    denied_amount: 1,
    group_number: 1
  }
)
```

**Expected:**
```json
{
  "claim_amount": 15000,
  "paid_amount": 5000,
  "denied_amount": 10000,
  "group_number": "GRP-CSV-001"
}
```

---

## Test 10: Complete End-to-End Workflow

### Scenario: Partially Paid Knee Surgery Denial

1. **Create Denial:**
   - Claim: CLM-KNEE-2024
   - Patient: Sarah Johnson, PT-55555
   - Provider: Dr. Sarah Wilson
   - Payer: United Healthcare
   - Policy: POL-UHC-789
   - Group: GRP-UHC-123
   - Service Date: Last month
   - Denial Date: This week
   - Category: Medical Necessity
   - Claim Amount: $25,000
   - Paid Amount: $8,000
   - Denied Amount: $17,000 (auto-calculated)
   - CPT: 27447 (Total Knee Arthroplasty)
   - Diagnosis: M54.5, M25.511

2. **Upload 2 Documents:**
   - medical_record.pdf (Medical Records, service date)
   - imaging.pdf (Imaging, service date)

3. **Review:**
   - Verify all financial data
   - Verify 2 documents listed
   - Submit

4. **Verify on Detail Page:**
   - Financial breakdown shows correctly
   - Both documents appear in Documents tab
   - group_number visible in Payer Info section

5. **Generate Appeal:**
   - Click "Generate Appeal Letter"
   - Verify appeal letter references correct amounts
   - Check that denied amount ($17,000) is used

### Expected Results:
✅ All fields saved correctly
✅ Documents uploaded and accessible
✅ Appeal letter uses correct financial data
✅ No data loss

---

## Performance Test

### Test 11: Navigation During Async Operations

1. Start creating denial
2. At Step 6, upload 3 large files (8MB each)
3. Click "Next" to review
4. Click "Submit Denial"
5. **During upload, try to:**
   - Click "Back" → Should be disabled ✅
   - Click "Cancel" → Should be disabled ✅
   - Click submit button again → Should be disabled ✅

**Expected:**
✅ All navigation disabled during upload
✅ Button shows "Uploading Documents (3)..."
✅ User cannot interrupt upload process

---

## Regression Tests

### Test 12: Existing Denials Still Work

1. Navigate to existing denial (created before enhancement)
2. Verify it displays correctly
3. Edit the denial
4. Verify update works

**Expected:**
✅ Old denials without paid_amount/denied_amount still display
✅ Defaults to 0 for missing fields
✅ Can edit and update

---

## Browser Compatibility

### Test 13: Cross-Browser Testing

Test the wizard in:
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

**Focus on:**
- File upload drag & drop
- Number input fields
- Auto-calculation updates
- Form validation

---

## Summary Checklist

- [ ] Test 1: Partial payment scenario ✅
- [ ] Test 2: Fully paid claim warning ✅
- [ ] Test 3: Financial validation errors ✅
- [ ] Test 4: Single document upload ✅
- [ ] Test 5: Multiple document upload ✅
- [ ] Test 6: Document validation ✅
- [ ] Test 7: Upload failure handling ✅
- [ ] Test 8: group_number persistence ✅
- [ ] Test 9: CSV upload with new fields ✅
- [ ] Test 10: Complete E2E workflow ✅
- [ ] Test 11: Navigation during async ops ✅
- [ ] Test 12: Backward compatibility ✅
- [ ] Test 13: Cross-browser testing ✅

---

## Bug Report Template

If you find issues, report using this format:

```markdown
**Test:** [Test number and name]
**Expected:** [What should happen]
**Actual:** [What actually happened]
**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Screenshots:** [If applicable]
**Console Errors:** [If any]
```

---

## Success Criteria

All tests pass when:
✅ Financial fields calculate correctly
✅ Validation prevents invalid data
✅ Documents upload successfully
✅ group_number saves to database
✅ No console errors
✅ All data persists correctly
✅ UI is responsive and intuitive
✅ No data loss on submission
