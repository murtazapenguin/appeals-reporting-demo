# Button Inventory - Claim Appeals Frontend

## Login Page
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Sign In | Submit login form | POST /api/auth/login | → /dashboard |
| Contact support | Open help | None | External link |

---

## Dashboard
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Add New Denial | Open wizard | None | → /denials/new |
| View All Denials | Open list | None | → /denials |

---

## Layout (Sidebar - All Screens)
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Dashboard | Navigate | None | → /dashboard |
| All Denials | Navigate | None | → /denials |
| New Denial | Navigate | None | → /denials/new |
| Logout | Clear session | None | → /login (clears localStorage) |

---

## Denials List
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Upload CSV | Open file picker | POST /api/denials/upload-csv (on file select) | Stays on page, refreshes list |
| New Denial | Open wizard | None | → /denials/new |
| Table Row (click) | View detail | None | → /denials/:id |
| Search Input | Filter list | None | Local filter |
| Status Filter | Filter list | GET /api/denials?status= | Refreshes list |
| Category Filter | Filter list | GET /api/denials?category= | Refreshes list |

---

## New Denial Wizard
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Next (Steps 1-5) | Advance step | None | Next step (local state) |
| Back | Previous step | None | Previous step (local state) |
| Cancel | Abort wizard | None | → /denials |
| Submit Denial (Step 6) | Create denial | POST /api/denials | → /denials/:id |

---

## Denial Detail - Overview Tab
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Back (arrow) | Return to list | None | → /denials |
| Overview Tab | Switch tab | None | Local state change |
| Criteria Evaluation Tab | Switch tab | None | Local state change |
| Documents Tab | Switch tab | None | Local state change |
| Appeal Letter Tab | Switch tab | None | Local state change |

---

## Denial Detail - Criteria Evaluation Tab
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Evaluate Criteria | Run AI evaluation | POST /api/criteria-evaluation/evaluate/:id | Updates criteriaResults state |
| Generate Appeal | Create appeal letter | POST /api/appeals/generate/:id | Switches to Appeal tab |
| Evidence Link (clickable) | Show source | None | Switches to Documents tab, highlights bbox |

---

## Denial Detail - Documents Tab
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| (No buttons - PDFViewer controlled by evidence clicks) | | | |

---

## Denial Detail - Appeal Letter Tab
| Button | Action | API Call | Navigation |
|--------|--------|----------|------------|
| Generate Appeal Letter | Create letter | POST /api/appeals/generate/:id | Updates appealLetter state |
| Download PDF | Save PDF file | GET /api/appeals/:id/pdf | Browser download |
| Submit Appeal | Send to payer | POST /api/appeals/:id/submit | Updates denial status |

---

## Summary by Component

### LoginPage.jsx
- **Sign In:** authAPI.login() → navigate('/dashboard')
- **Contact support:** Opens external link

### Dashboard.jsx
- **Add New Denial:** navigate('/denials/new')
- **View All Denials:** navigate('/denials')

### Layout.jsx
- **Dashboard (sidebar):** navigate('/dashboard')
- **All Denials (sidebar):** navigate('/denials')
- **New Denial (sidebar):** navigate('/denials/new')
- **Logout (sidebar):** localStorage.removeItem('authToken') → setIsLoggedIn(false) → navigate('/login')

### DenialsList.jsx
- **Upload CSV:** fileInputRef.current.click() → denialsAPI.uploadCSV(file) → loadDenials()
- **New Denial:** navigate('/denials/new')
- **Table Row Click:** navigate(`/denials/${denial.id}`)
- **Search Input:** setSearchTerm() → local filter
- **Status Filter:** setFilters() → denialsAPI.getAll(filters)
- **Category Filter:** setFilters() → denialsAPI.getAll(filters)

### NewDenialWizard.jsx
- **Next (Steps 1-5):** setCurrentStep(currentStep + 1)
- **Back:** setCurrentStep(currentStep - 1)
- **Cancel:** navigate('/denials')
- **Submit Denial:** denialsAPI.create(formData) → navigate(`/denials/${newDenial.id}`)

### DenialDetail.jsx
- **Back Arrow:** navigate('/denials')
- **Tab Buttons (4x):** setActiveTab('overview' | 'criteria' | 'documents' | 'appeal')
- **Evaluate Criteria:** criteriaAPI.evaluate(id) → setCriteriaResults()
- **Generate Appeal:** appealsAPI.generateLetter(id) → setAppealLetter() → setActiveTab('appeal')
- **Evidence Link:** handleEvidenceClick() → setSelectedDocument() → setActiveTab('documents')
- **Download PDF:** appealsAPI.downloadPDF(id) → browser download
- **Submit Appeal:** appealsAPI.submit(id) → alert() → loadDenialData()

---

## Navigation Flow

```
Login → Dashboard → Denials List → Denial Detail (tabs)
                                 → New Denial Wizard → Denial Detail

Denial Detail Tabs:
  - Overview
  - Criteria Evaluation (evidence links → Documents tab)
  - Documents (PDFViewer with bbox highlighting)
  - Appeal Letter (generate → download → submit)
```

---

## Critical User Interactions

### 1. Evidence Click → Document Highlight
**Component:** DenialDetail.jsx → Criteria Evaluation tab
**Trigger:** Click evidence link
**Flow:**
1. handleEvidenceClick(evidence)
2. setSelectedDocument({ documentData, boundingBoxes })
3. setActiveTab('documents')
4. PDFViewer receives boundingBoxes prop
5. Auto-scrolls to page + highlights bbox

**Button:** Evidence link (rendered as clickable p tag)

---

### 2. CSV Upload → Bulk Import
**Component:** DenialsList.jsx
**Trigger:** Click "Upload CSV" button
**Flow:**
1. fileInputRef.current.click()
2. File picker opens
3. User selects CSV
4. handleCSVUpload(e)
5. denialsAPI.uploadCSV(file)
6. loadDenials() refreshes list

**Button:** "Upload CSV" (with ArrowUpTrayIcon)

---

### 3. Wizard Submit → Detail View
**Component:** NewDenialWizard.jsx
**Trigger:** Click "Submit Denial" (Step 6)
**Flow:**
1. handleSubmit()
2. denialsAPI.create(formData)
3. navigate(`/denials/${newDenial.id}`)
4. DenialDetail loads with new ID

**Button:** "Submit Denial" (green gradient, Step 6 only)

---

### 4. Generate Appeal → Download → Submit
**Component:** DenialDetail.jsx → Appeal Letter tab
**Trigger:** Sequential clicks
**Flow:**
1. Click "Generate Appeal" → appealsAPI.generateLetter()
2. Click "Download PDF" → appealsAPI.downloadPDF() → browser download
3. Click "Submit Appeal" → appealsAPI.submit() → status updated

**Buttons:**
- "Generate Appeal" (purple gradient)
- "Download PDF" (white with border, ArrowDownTrayIcon)
- "Submit Appeal" (green gradient, PaperAirplaneIcon)

---

## Error Handling

All buttons with API calls include try/catch:
- **Success:** Update state, navigate, or refresh data
- **Failure:** console.error() + alert() with user-friendly message
- **Loading States:** disabled={isLoading} prevents double-clicks

---

## Accessibility

All buttons include:
- Proper aria labels (icon-only buttons)
- Disabled states (opacity-50 + cursor-not-allowed)
- Keyboard navigation support
- Focus states (ring-2)
