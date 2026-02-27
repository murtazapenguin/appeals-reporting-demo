---
name: ui-testing-guide
description: Reviews and fixes React UI applications. MANDATORY browser testing with Claude in Chrome to verify all buttons work and user workflows complete. Includes code review checklists, common fixes, and workflow verification. Triggers on requests to test UI, review UI, fix UI issues, or quality assurance.
---

# UI Testing Guide

This skill reviews React applications, identifies issues, and automatically fixes them.

**IMPORTANT:** This skill includes MANDATORY browser-based testing using Claude in Chrome to verify all UI elements work correctly and user workflows are complete.

---

## CRITICAL: USE UI-ARCHITECT OUTPUTS FOR TESTING

**Before testing, you MUST reference UI-architect's workflow documentation to know WHAT to test.**

### Required Inputs from UI-architect

1. **Screen Inventory** - All screens with routes, entry/exit points
2. **User Journeys** - Step-by-step paths users take
3. **State Transitions** - What buttons lead where
4. **Button Inventory** - All buttons per screen with expected actions
5. **API Requirements** - What API calls each action makes

### Test Against the Design, Not Just the Code

```
UI-architect says:          You verify:
─────────────────────────────────────────────────
Login → Queue on success    Click login, ends at /queue
Queue → Coding on Start     Click Start Coding, ends at /coding/:id
Coding → Queue on Complete  Click Complete, ends at /queue
Queue → Login on Logout     Click Logout, ends at /login
```

---

## REVIEW PROCESS

### Phase 1: Project Structure Review

1. **Verify project structure** - Ensure all required files exist:
   ```
   - package.json (with correct dependencies)
   - vite.config.js / tailwind.config.js
   - src/App.jsx (with proper routing)
   - src/components/ (all required components)
   - public/ (logos and assets)
   ```

2. **Check imports** - Verify all imports resolve correctly

### Phase 2: UI/UX Review

#### Layout Issues
- [ ] **Overflow problems** - Content exceeding container bounds
- [ ] **Overlapping elements** - Z-index conflicts, absolute positioning
- [ ] **Scroll issues** - Missing `overflow-y-auto` on scrollable containers
- [ ] **Height constraints** - PDFViewer needs explicit height (`h-screen`, `h-full`)
- [ ] **Flexbox issues** - Missing `flex-shrink-0` on headers/footers

#### Visual Consistency
- [ ] **Color scheme** - Using PenguinAI brand colors (`#fc459d`, gradients)
- [ ] **Spacing** - Consistent padding/margin (use Tailwind scale)
- [ ] **Border radius** - Consistent rounding (`rounded-xl`, `rounded-2xl`)

### Phase 3: Code Quality Review

#### React Best Practices
- [ ] **useMemo/useCallback** - Memoize expensive computations
- [ ] **Key props** - Unique keys for list items
- [ ] **Event handlers** - Proper `stopPropagation` where needed
- [ ] **Cleanup** - useEffect cleanup functions for subscriptions/timers

### Phase 4: Functional Review

#### Navigation
- [ ] **Route protection** - Auth guards on protected routes
- [ ] **Redirects** - Proper redirect logic after login/logout

#### Forms
- [ ] **Validation** - Required fields enforced
- [ ] **Error states** - Error messages displayed properly
- [ ] **Loading states** - Buttons disabled during submission

---

## PHASE 5: BROWSER TESTING WITH CLAUDE IN CHROME (MANDATORY)

**This phase is REQUIRED and must be performed for every UI review.**

### 5.1 Setup Browser Testing

1. **Start the development server:**
   ```bash
   cd [app-directory]
   npm run dev &
   ```
   Wait for server to start (http://localhost:5173)

2. **Initialize Chrome context:**
   - Use `mcp__claude-in-chrome__tabs_context_mcp` to get current tabs
   - Create a new tab with `mcp__claude-in-chrome__tabs_create_mcp`
   - Navigate to the application URL

### 5.2 Test All Buttons and Interactive Elements

#### Login Page Testing
- [ ] Navigate to login page
- [ ] Take screenshot to verify layout
- [ ] Test username/password input fields
- [ ] Test login button (click and verify navigation)
- [ ] Verify redirect to main page after login

#### Navigation Testing
- [ ] Test all sidebar/navbar links
- [ ] Verify each link navigates to correct page
- [ ] Test logout button
- [ ] Test back buttons where applicable

#### Page-Specific Button Testing
- [ ] Use `mcp__claude-in-chrome__find` to locate all buttons
- [ ] Click each button and verify expected behavior
- [ ] Take screenshots before and after clicks
- [ ] Document any buttons that don't respond

### 5.3 User Workflow Verification

**CRITICAL:** Test workflows defined by UI-architect, not just common patterns.

#### Test Each Journey Step-by-Step

```markdown
### Journey 1: First-time User (from UI-architect)
- [ ] Step 1: Navigate to /login → Login page displays
- [ ] Step 2: Enter demo@penguinai.com / demo123 → No errors
- [ ] Step 3: Click Sign In → Redirects to /queue
- [ ] Step 4: Queue shows documents → Documents visible
- [ ] Step 5: Click Start Coding → Navigates to /coding/:id
- [ ] Step 6: See PDF and codes → Both panels render
- [ ] Step 7: Click Accept on a code → Status changes
- [ ] Step 8: Click Complete → Redirects to /queue
- [ ] Step 9: Click Logout → Redirects to /login
```

#### Test State Transitions Table

| From | Action | Expected To | Actual | Pass? |
|------|--------|-------------|--------|-------|
| /login | Submit (success) | /queue | | |
| /queue | Start Coding | /coding/:id | | |
| /queue | Logout | /login | | |
| /coding | Complete | /queue | | |
| /coding | Back | /queue | | |

#### Test Button Inventory

| Button | Expected Action | Tested | Works? |
|--------|-----------------|--------|--------|
| Sign In | Submit form, redirect to /queue | | |
| Start Coding | Navigate to /coding/:id | | |
| Accept | Update code status | | |
| Complete | Mark doc complete, go to /queue | | |
| Logout | Clear token, go to /login | | |

### 5.4 Browser Testing Commands

```javascript
// Get tab context
mcp__claude-in-chrome__tabs_context_mcp({ createIfEmpty: true })

// Create new tab
mcp__claude-in-chrome__tabs_create_mcp()

// Navigate to URL
mcp__claude-in-chrome__navigate({ url: "http://localhost:5173", tabId: TAB_ID })

// Take screenshot
mcp__claude-in-chrome__computer({ action: "screenshot", tabId: TAB_ID })

// Find elements
mcp__claude-in-chrome__find({ query: "login button", tabId: TAB_ID })

// Click element by coordinates
mcp__claude-in-chrome__computer({ action: "left_click", coordinate: [x, y], tabId: TAB_ID })

// Type text
mcp__claude-in-chrome__computer({ action: "type", text: "username", tabId: TAB_ID })

// Read page structure
mcp__claude-in-chrome__read_page({ tabId: TAB_ID, filter: "interactive" })

// Read console for errors
mcp__claude-in-chrome__read_console_messages({ tabId: TAB_ID, onlyErrors: true })
```

### 5.5 Document Browser Test Results

```markdown
## Browser Test Results

### Environment
- URL: http://localhost:5173
- Browser: Chrome (via Claude in Chrome)

### Buttons Tested
| Button | Location | Action | Result |
|--------|----------|--------|--------|
| Login | LoginPage | Click | ✅ Navigates to Queue |
| Logout | Sidebar | Click | ✅ Redirects to Login |

### Workflows Tested
| Workflow | Steps | Status | Issues |
|----------|-------|--------|--------|
| Login Flow | 3 | ✅ Pass | None |

### Console Errors
- [List any JavaScript errors found]
```

---

## PHASE 6: DELEGATE MISSING FEATURES

If browser testing reveals missing functionality:

1. **Document the issue** with current state, expected state, user impact
2. **Invoke UI-architect skill** with detailed requirements
3. **Re-test** after UI-architect makes changes

---

## COMMON FIXES

### Fix 1: PDFViewer Height Issues
```jsx
// WRONG
<div><PDFViewer documentData={data} /></div>

// CORRECT
<div className="h-screen flex">
  <div className="w-3/5 h-full">
    <PDFViewer documentData={data} className="h-full" />
  </div>
</div>
```

### Fix 2: Z-index Hierarchy
```jsx
<header className="... z-50">  {/* Highest */}
<aside className="... z-40">   {/* Sidebar */}
<main className="... z-10">    {/* Content */}
```

### Fix 3: Scrollable Container
```jsx
<div className="h-full flex flex-col overflow-hidden">
  <header className="flex-shrink-0">...</header>
  <main className="flex-1 overflow-y-auto">{content}</main>
</div>
```

### Fix 4: Click Event Bubbling
```jsx
<button onClick={(e) => {
  e.stopPropagation()
  handleButtonClick()
}}>
```

### Fix 5: Loading States
```jsx
const [isLoading, setIsLoading] = useState(false)

<button disabled={isLoading}>
  {isLoading ? 'Loading...' : 'Submit'}
</button>
```

See `templates/common-fixes.md` for more patterns.

---

## EXECUTION STEPS

### Step 1: Code Review
1. Identify the application directory
2. Read all components (.jsx/.js files)
3. Run the checklist - go through each review category
4. Document issues found
5. Apply fixes using Edit tool
6. Verify build with `npm run build`

### Step 2: Browser Testing (MANDATORY)
7. Start dev server: `npm run dev &`
8. Open browser with Claude in Chrome
9. Test all buttons - click every button and verify
10. Test all workflows - complete each user journey
11. Check console for errors
12. Document results

### Step 3: Handle Missing Features
13. List missing workflows/functionality
14. Delegate to UI-architect with specifications
15. Re-test after changes

### Step 4: Final Report
16. Summarize changes and fixes applied
17. Report browser test outcomes
18. Clean up (stop dev server)

---

## PRIORITY ORDER FOR FIXES

1. **Critical** - Build errors, broken functionality
2. **High** - UI layout issues, overflow problems, non-working buttons
3. **Medium** - Missing loading states, validation
4. **Low** - Code style, minor optimizations

---

## BROWSER TESTING FAILURE HANDLING

### Non-working Button
1. Take screenshot showing the button
2. Check console for errors
3. Read the component code
4. Fix the onClick handler or navigation logic
5. Re-test in browser

### Broken Workflow
1. Document which step fails
2. Identify the component responsible
3. If minor: Apply fix directly
4. If major: Delegate to UI-architect

---

## IMPORTANT NOTES

- **Browser testing is MANDATORY** - Never skip Phase 5
- **Test EVERY button** - Not just the main ones
- **Complete workflows** - Don't stop at individual button clicks
- **Test against UI-architect's design** - Not just what you see
- **Re-test after fixes** - Always verify changes work in browser
- **Clean up** - Stop dev server when done

---

## Progressive Disclosure

For detailed patterns, see:
- `templates/review-checklist.md` - Full review checklist
- `templates/common-fixes.md` - Extended fix patterns
