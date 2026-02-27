# Quick Test Checklist - Document Date Fix

## 🚀 Quick Start
```
✅ Backend running: http://localhost:8000
✅ Frontend running: http://localhost:5174
📧 Login: demo@penguinai.com / demo123
```

---

## ✅ Test 1: New Wizard Has 6 Steps (2 min)

**Navigate:** http://localhost:5174 → Click "+ New Denial"

**Check Progress Bar:**
```
1️⃣ Basic Info  →  2️⃣ Payer  →  3️⃣ Denial Details  →  4️⃣ Clinical & Financial  →  5️⃣ Notes  →  6️⃣ Review
```

❌ **Should NOT see:** "Upload Documents" step

**Quick Form Fill:**
- Step 1: `CLM-001` | `John Smith` | `PAT-123` | Select Dr. Wilson
- Step 2: Select `Blue Cross Blue Shield`
- Step 3: Service `2025-11-06` | Denial `2026-01-21` | Category `Medical Necessity`
- Step 4: Claim `25000` | CPT `27447 - Total Knee`
- Step 5: Notes `Test` | Priority `Normal`
- Step 6: Review → **Submit**

✅ **Expected:** Fast redirect to denial detail page (no upload delay)

---

## ✅ Test 2: Smart Default Date (1 min)

**From denial detail page → Click "Upload Document"**

**Check Date Field:**
```
Document Date: [2025-11-06] ← Should be service_date (NOT today)

Below date picker:
ℹ️  Valid range for evaluation: 2025-08-08 to 2026-01-21
```

✅ **Expected:**
- Default date = `2025-11-06` (service_date from step 3)
- Date range hint visible
- NO warning box (date is in range)

**Upload:**
- Select any PDF
- Type: `Medical Records`
- Click **Upload Document**

✅ **Expected:** Upload succeeds, document appears in list

---

## ✅ Test 3: Validation Warning (1 min)

**Click "Upload Document" again**

**Change date to future:**
```
Document Date: [2026-01-29] ← Change to today (after denial_date)
```

✅ **Expected:**
```
⚠️  Warning: This date is outside the evaluation range.
    Documents may not be included in criteria evaluation.
```

**Amber warning box should appear**

**Still upload:**
- Select PDF
- Type: `Lab Results`
- Click **Upload Document**

✅ **Expected:** Upload still works (warning doesn't block)

---

## ✅ Test 4: Criteria Evaluation Works (1 min)

**From denial detail page:**
- Click **"Evidence"** tab
- Click **"Evaluate Criteria"** button
- Wait for evaluation to complete

✅ **Expected:**
```
✓ Found 1 document in date range (Medical Records from Test 2)
✓ Criteria show evidence
✓ NO error: "No patient documents found in the required date range"
```

❌ **Should NOT see:** Error about no documents (the bug we fixed!)

---

## ✅ Test 5: Browser Console Check (30 sec)

**Press F12 → Console tab**

✅ **Expected:**
- No red errors
- No warnings about missing props
- No undefined variable errors

---

## 📊 Quick Results Table

| Test | What to Check | Expected Result | Pass/Fail |
|------|---------------|-----------------|-----------|
| 1 | Wizard steps | 6 steps, no upload step | [ ] |
| 2 | Default date | `2025-11-06` (service_date) | [ ] |
| 3 | Date hint | Shows valid range | [ ] |
| 4 | Warning | Appears when date out of range | [ ] |
| 5 | Evaluation | Finds documents, no error | [ ] |
| 6 | Console | No errors | [ ] |

---

## 🐛 Common Issues & Fixes

### Issue: Date still shows today (2026-01-29)
**Cause:** Modal not receiving `denial` prop
**Check:** DenialDetail.jsx line 907 → should have `denial={denial}`

### Issue: No date range hint visible
**Cause:** Missing service_date or denial_date
**Check:** Step 3 of wizard → ensure dates are filled

### Issue: Warning shows for valid dates
**Cause:** Date calculation error
**Check:** Browser console for JavaScript errors

### Issue: "No documents found" still happening
**Cause:** Document uploaded with wrong date in Test 3
**Fix:** Only Test 2 document (2025-11-06) should be in range

---

## 📸 Screenshots to Capture

For documentation/reporting:

1. **Wizard progress bar** showing 6 steps
2. **Upload modal** with default date `2025-11-06`
3. **Date range hint** text
4. **Amber warning box** when date is out of range
5. **Criteria evaluation results** showing documents found

---

## ⏱️ Total Test Time: ~5 minutes

**Priority:** Run Tests 1, 2, and 4 minimum
**Full test:** All 5 tests for complete verification

---

## 🎯 Success Criteria Summary

**✅ PASS if:**
- Wizard has 6 steps (not 7)
- Document date defaults to service_date (not today)
- Date range hint shows below date picker
- Warning appears for out-of-range dates
- Criteria evaluation finds documents
- No console errors

**❌ FAIL if:**
- Wizard still has 7 steps
- Date defaults to today (2026-01-29)
- No date range hint
- No warning for bad dates
- "No documents found" error still appears

---

## 📝 Quick Report Template

After testing, fill out:

```
Date Tested: __________
Tester: __________

Test Results:
[ ] Test 1: Wizard (6 steps) - PASS / FAIL
[ ] Test 2: Smart default - PASS / FAIL
[ ] Test 3: Validation warning - PASS / FAIL
[ ] Test 4: Criteria evaluation - PASS / FAIL
[ ] Test 5: Console check - PASS / FAIL

Issues Found:
1. ______________________
2. ______________________

Overall Status: ✅ PASS / ❌ FAIL

Notes:
_______________________
_______________________
```

---

## 🔗 Full Documentation

- **Detailed Tests:** `TESTING_GUIDE.md` (8 comprehensive scenarios)
- **Visual Diagrams:** `WORKFLOW_DIAGRAM.md` (before/after workflows)
- **Implementation:** `IMPLEMENTATION_SUMMARY.md` (technical details)

---

**Ready to Test:** Open http://localhost:5174 and start with Test 1! 🚀
