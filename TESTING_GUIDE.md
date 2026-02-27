# Testing Guide: Document Date Range Fix

## Overview
This guide covers testing the implementation of the document date range fix, which includes:
1. **Removed document upload from New Denial Wizard** (6 steps instead of 7)
2. **Smart default dates** for document uploads (defaults to service_date)
3. **Date range validation** with visual warnings

---

## Prerequisites

- **Frontend:** http://localhost:5174 (running)
- **Backend:** http://localhost:8000 (running)
- **Test User Credentials:**
  - Email: `demo@penguinai.com`
  - Password: `demo123`

---

## Test 1: New Denial Wizard - Verify 6 Steps (No Document Upload)

### Objective
Verify that the wizard now has 6 steps instead of 7, with document upload step removed.

### Steps

1. **Navigate to application**
   - Open browser: http://localhost:5174
   - Login with demo credentials

2. **Start new denial wizard**
   - Click the **"+ New Denial"** button
   - You should see the wizard interface

3. **Verify step count**
   - Check the progress indicator at the top
   - **Expected:** 6 steps displayed:
     1. Basic Info
     2. Payer
     3. Denial Details
     4. Clinical & Financial
     5. Notes
     6. Review (previously step 7)
   - **❌ Not present:** "Upload Documents" step

4. **Complete all steps**

   **Step 1: Basic Info**
   - Claim Number: `CLM-TEST-001`
   - Patient Name: `John Smith`
   - Patient ID: `PAT-12345`
   - Patient DOB: `1985-05-15`
   - Provider: Select `Dr. Sarah Wilson - Wilson Orthopedic Center`
   - Click **Next**

   **Step 2: Payer**
   - Insurance Payer: Select `Blue Cross Blue Shield`
   - Policy Number: `POL-999888`
   - Group Number: `GRP-5555`
   - Click **Next**

   **Step 3: Denial Details**
   - Service Date: `2025-11-06` (Important: This will be used for document date validation)
   - Denial Date: `2026-01-21` (Today or recent date)
   - Denial Code: `CO-50`
   - Denial Category: `Medical Necessity`
   - Denial Reason: `Procedure not medically necessary per policy`
   - Click **Next**

   **Step 4: Clinical & Financial**
   - Total Claim Amount: `25000`
   - Amount Paid: `0`
   - Denied Amount: `25000` (auto-calculated)
   - Procedure Code (CPT): Select `27447 - Total Knee Arthroplasty`
   - Diagnosis Codes (ICD-10): `M17.11, M25.561`
   - Service Description: Auto-filled
   - Click **Next**

   **Step 5: Notes**
   - Internal Notes: `Test denial for date range validation`
   - Priority Level: `Normal`
   - Click **Next**

   **Step 6: Review**
   - Verify all information is correct
   - **Important:** Check that there is NO "Documents to Upload" section
   - Click **Submit Denial**

5. **Verify navigation**
   - After submission, you should be redirected to the **Denial Detail Page**
   - Status should show as created
   - No documents should be uploaded yet

### ✅ Success Criteria
- [x] Wizard has exactly 6 steps
- [x] No "Upload Documents" step visible
- [x] No document upload UI in wizard
- [x] Review step (now step 6) does not show document summary
- [x] Submission completes quickly (no document upload delay)
- [x] Redirected to denial detail page after submission

---

## Test 2: Document Upload - Smart Default Date

### Objective
Verify that document upload modal defaults to the denial's service_date (not today's date).

### Steps

1. **Open document upload modal**
   - From the denial detail page (created in Test 1)
   - Scroll to the **Documents** section
   - Click **"Upload Document"** button

2. **Check default document date**
   - Look at the **"Document Date"** field
   - **Expected:** Date should be `2025-11-06` (the service_date from step 3)
   - **❌ Not expected:** Today's date (2026-01-29)

3. **Check date range hint**
   - Below the Document Date field, you should see text:
   - **Expected:** `Valid range for evaluation: 2025-08-08 to 2026-01-21`
   - This is calculated as: (service_date - 90 days) to denial_date
   - Calculation: Nov 6, 2025 - 90 days = Aug 8, 2025

4. **Test date within range**
   - Keep the default date (`2025-11-06`)
   - Select a PDF file (any test PDF)
   - Document Type: `Medical Records`
   - Click **Upload Document**
   - **Expected:** Upload succeeds, no warnings shown

### ✅ Success Criteria
- [x] Document date defaults to `2025-11-06` (service_date)
- [x] Date range hint shows: `Valid range for evaluation: 2025-08-08 to 2026-01-21`
- [x] No warning when date is within range
- [x] Document uploads successfully

---

## Test 3: Date Validation Warning - Date Too Late

### Objective
Verify that a warning appears when document date is AFTER the denial_date.

### Steps

1. **Open document upload modal**
   - Click **"Upload Document"** again

2. **Change date to future date**
   - Change Document Date to: `2026-01-29` (today - 8 days after denial_date)

3. **Check for warning**
   - An amber warning box should appear below the date picker
   - **Expected warning text:**
     ```
     ⚠️ Warning: This date is outside the evaluation range.
     Documents may not be included in criteria evaluation.
     ```

4. **Verify upload still works**
   - Select a PDF file
   - Document Type: `Lab Results`
   - Click **Upload Document**
   - **Expected:** Upload succeeds despite warning (warning is informational, not blocking)

### ✅ Success Criteria
- [x] Amber warning box appears when date > denial_date
- [x] Warning text is clear and helpful
- [x] Upload button remains enabled
- [x] Document uploads successfully (warning doesn't block upload)

---

## Test 4: Date Validation Warning - Date Too Early

### Objective
Verify that a warning appears when document date is BEFORE (service_date - 90 days).

### Steps

1. **Open document upload modal**
   - Click **"Upload Document"** again

2. **Change date to very early date**
   - Change Document Date to: `2025-08-01` (before Aug 8, 2025 - the start of valid range)

3. **Check for warning**
   - Amber warning box should appear
   - **Expected:** Same warning message about being outside evaluation range

4. **Verify upload still works**
   - Select a PDF file
   - Document Type: `Imaging`
   - Click **Upload Document**
   - **Expected:** Upload succeeds with warning

### ✅ Success Criteria
- [x] Amber warning box appears when date < (service_date - 90 days)
- [x] Warning is consistent with Test 3
- [x] Upload works despite warning

---

## Test 5: Criteria Evaluation with Correct Date Range

### Objective
Verify that documents with dates in the valid range are found during criteria evaluation.

### Steps

1. **Ensure documents are uploaded**
   - From Tests 2-4, you should have 3 documents uploaded:
     1. Medical Records (2025-11-06) ✅ In range
     2. Lab Results (2026-01-29) ❌ Out of range
     3. Imaging (2025-08-01) ❌ Out of range

2. **Navigate to Evidence tab**
   - Click on the **"Evidence"** tab in the denial detail page

3. **Run criteria evaluation**
   - Click **"Evaluate Criteria"** button
   - Wait for evaluation to complete

4. **Check results**
   - **Expected:** Criteria evaluation should find 1 document (Medical Records dated 2025-11-06)
   - **Expected:** Document dated 2026-01-29 should NOT be included (after denial_date)
   - **Expected:** Document dated 2025-08-01 should NOT be included (before service_date - 90)

5. **Verify no "No documents found" error**
   - At least one document should be in range
   - Criteria should show evidence from the Medical Records document
   - **Previous bug:** All documents were dated today (2026-01-29), causing "No documents found" error
   - **After fix:** Documents default to service_date, so they fall within range

### ✅ Success Criteria
- [x] Criteria evaluation completes successfully
- [x] At least 1 document found in date range (the one from Test 2)
- [x] Documents outside range are excluded (not shown in evidence)
- [x] No "No patient documents found in the required date range" error

---

## Test 6: Edge Case - Denial Without Service Date

### Objective
Test that the modal handles denials without service_date gracefully.

### Steps

1. **Create denial via API** (optional - skip if complex)
   - Use backend API to create a denial without service_date
   - Or manually test with an existing old denial

2. **Open upload modal**
   - Navigate to the denial detail page
   - Click **"Upload Document"**

3. **Check fallback behavior**
   - **Expected:** If no service_date, should fall back to denial_date
   - **Expected:** If no denial_date either, should fall back to today's date
   - **Expected:** No JavaScript errors in console

### ✅ Success Criteria
- [x] Modal opens without errors
- [x] Default date falls back gracefully (denial_date or today)
- [x] No console errors
- [x] Date range hint either shows correctly or is hidden

---

## Test 7: Multiple Denials - Date Isolation

### Objective
Verify that each denial uses its own service_date, not shared state.

### Steps

1. **Create second denial**
   - Click **"+ New Denial"**
   - Use different dates:
     - Service Date: `2025-10-15`
     - Denial Date: `2026-01-15`
   - Complete wizard and submit

2. **Upload document to second denial**
   - Click **"Upload Document"**
   - **Expected:** Default date should be `2025-10-15` (NOT 2025-11-06 from first denial)
   - **Expected:** Date range should be `2025-07-17 to 2026-01-15`

3. **Switch back to first denial**
   - Navigate to first denial (CLM-TEST-001)
   - Click **"Upload Document"**
   - **Expected:** Default date should still be `2025-11-06`
   - **Expected:** Date range should still be `2025-08-08 to 2026-01-21`

### ✅ Success Criteria
- [x] Each denial has its own correct default date
- [x] Date ranges are calculated independently
- [x] No state pollution between denials

---

## Test 8: Modal Reopen - State Reset

### Objective
Verify that closing and reopening the modal resets to smart defaults.

### Steps

1. **Open upload modal**
   - From any denial detail page
   - **Expected:** Date defaults to service_date

2. **Change date to out-of-range value**
   - Change date to `2026-02-01`
   - Warning should appear
   - Click **Cancel** (close modal without uploading)

3. **Reopen modal**
   - Click **"Upload Document"** again
   - **Expected:** Date should reset to service_date (NOT 2026-02-01)
   - **Expected:** No warning visible initially

### ✅ Success Criteria
- [x] Modal state resets on close
- [x] Date returns to smart default (service_date)
- [x] Warning clears when modal reopens
- [x] No stale state from previous open

---

## Console Verification

### Check Browser Console
Throughout all tests, monitor the browser console (F12 → Console tab) for:

- **✅ No JavaScript errors**
- **✅ No React warnings about missing props**
- **✅ No undefined variable errors**
- **✅ API calls complete successfully**

### Backend Logs
Check backend logs for:

```bash
tail -f /private/tmp/claude/-Users-vaatsav-Desktop-claim-appeals-v2/tasks/b0d1fdf.output
```

- **✅ Document upload endpoints succeed**
- **✅ Criteria evaluation finds documents**
- **✅ No date parsing errors**

---

## Summary Checklist

### Wizard Changes
- [ ] Wizard has 6 steps (not 7)
- [ ] No document upload step visible
- [ ] Review step is now step 6
- [ ] Faster submission (no document upload delay)

### Smart Default Dates
- [ ] Document date defaults to service_date
- [ ] Date range hint displays correctly
- [ ] Calculation: (service_date - 90 days) to denial_date

### Validation Warnings
- [ ] Warning appears when date > denial_date
- [ ] Warning appears when date < (service_date - 90 days)
- [ ] Warning is informational (doesn't block upload)
- [ ] Warning text is clear and helpful

### Criteria Evaluation
- [ ] Documents in range are found by evaluation
- [ ] Documents outside range are excluded
- [ ] No "No documents found" error when documents exist in range
- [ ] Fewer false negatives in criteria evaluation

### Edge Cases
- [ ] Fallback to denial_date when no service_date
- [ ] Fallback to today when neither date exists
- [ ] Modal state resets on close/reopen
- [ ] Multiple denials maintain separate date ranges

---

## Expected Improvements

### Before Fix
- Documents defaulted to today's date (2026-01-29)
- For denial with service_date 2025-11-06 and denial_date 2026-01-21:
  - Valid range: 2025-08-08 to 2026-01-21
  - Document date: 2026-01-29 ❌ Out of range
  - Result: "No patient documents found in the required date range"

### After Fix
- Documents default to service_date (2025-11-06)
- Same denial:
  - Valid range: 2025-08-08 to 2026-01-21
  - Document date: 2025-11-06 ✅ In range
  - Result: Documents found, criteria evaluation succeeds

### Impact
- ✅ Higher success rate for criteria evaluation
- ✅ Fewer user errors uploading documents
- ✅ Clearer guidance on valid date ranges
- ✅ Faster denial creation workflow

---

## Troubleshooting

### Issue: Date still defaults to today
**Cause:** Modal not receiving `denial` prop
**Fix:** Check DenialDetail.jsx line 907 - ensure `denial={denial}` is passed

### Issue: Date range hint not showing
**Cause:** Missing service_date or denial_date in denial data
**Fix:** Verify denial has both dates set in step 3 of wizard

### Issue: Warning appears even for valid dates
**Cause:** String comparison instead of date comparison
**Fix:** Check calculateStartDate and isDateOutOfRange functions

### Issue: Upload fails with 500 error
**Cause:** Backend document_routes.py expecting different parameters
**Fix:** Check backend logs, verify documentsAPI.upload signature

---

## Screenshots to Capture

For documentation/bug reports, capture:

1. **Wizard with 6 steps** (progress indicator)
2. **Review step** (no document summary section)
3. **Upload modal with default date** (showing service_date)
4. **Date range hint** (showing calculated range)
5. **Amber warning box** (when date is out of range)
6. **Criteria evaluation success** (documents found in range)

---

## Completion Sign-Off

After completing all tests, confirm:

- [ ] All 8 test scenarios passed
- [ ] No console errors
- [ ] No backend errors
- [ ] Criteria evaluation works correctly
- [ ] User experience is improved
- [ ] Documentation updated (if needed)

**Tested by:** _________________
**Date:** _________________
**Result:** ✅ PASS / ❌ FAIL
**Notes:** _________________
