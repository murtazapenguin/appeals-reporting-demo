# PenguinAI Full-Stack Development Pipeline

This workspace uses **skills for knowledge** and **subagents for execution** to build full-stack applications.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    SKILLS (Knowledge - Auto-loaded)              │
├─────────────────────────────────────────────────────────────────┤
│  frontend-guide       │ React, PDFViewer, Tailwind v4           │
│  backend-guide        │ FastAPI, MongoDB, JWT authentication    │
│  ai-engineering-guide │ penguin-ai-sdk, OCR, LLM extraction     │
│  ui-testing-guide     │ Claude in Chrome browser testing, QA    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                 SUBAGENTS (Execution - Spawned)                  │
├─────────────────────────────────────────────────────────────────┤
│  ui-builder      │ Phase 1 - Build React frontend               │
│  api-builder     │ Phase 2 - Build FastAPI backend              │
│  ai-integrator   │ Phase 2.5 - Add document processing          │
│  quality-tester  │ Phase 3 - Test complete application          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Sequential Workflow (4 Phases)

When building full-stack applications, execute these phases IN ORDER:

### Phase 1: ui-builder
- **Spawns with:** frontend-guide skill
- **Creates:** React UI + USER_WORKFLOW.md + API_REQUIREMENTS.md
- **Output:** Working frontend at http://localhost:5173

### Phase 2: api-builder
- **Spawns with:** backend-guide, ai-engineering-guide skills
- **Reads:** API_REQUIREMENTS.md from Phase 1
- **Creates:** FastAPI backend + MongoDB + seed data
- **Output:** Working API at http://localhost:8000
- **MUST invoke ai-integrator** if document processing needed

### Phase 2.5: ai-integrator (conditional)
- **Spawns with:** ai-engineering-guide skill
- **Adds:** OCR, LLM extraction, bounding box mapping
- **Output:** /services/ai_processor.py integrated with upload route

### Phase 3: quality-tester
- **Spawns with:** ui-testing-guide, frontend-guide, backend-guide skills
- **Tests:** Complete integrated application (UI + API + E2E)
- **MANDATORY:** Browser testing with Claude in Chrome
- **Verifies:** All buttons, workflows, API responses, and E2E flows
- **Output:** Test report + fixes applied

---

## When to Use Each Subagent

| User Request | Subagent | Condition |
|--------------|----------|-----------|
| "Build an app" | ui-builder → api-builder → quality-tester | Start full pipeline |
| "Create UI for..." | ui-builder | Frontend only |
| "Create backend for..." | api-builder | Backend only |
| "Add document processing" | ai-integrator | AI capabilities |
| "Test the app" | quality-tester | Testing only |

---

## Pre-Build Clarification Questions

**IMPORTANT:** Before spawning any subagent, gather clarity on requirements. Ask relevant questions based on what's being built.

### Frontend (ui-builder) Clarifications

| Category | Questions to Ask |
|----------|------------------|
| **Screens** | What screens/pages are needed? (Login, Dashboard, List, Detail, Form?) |
| **User Roles** | Who are the users? Different roles with different views? |
| **Key Workflows** | What are the main user journeys? (e.g., Login → View List → Select Item → Process → Complete) |
| **Data Display** | What data needs to be displayed? Tables, cards, charts? |
| **Document Viewing** | Need PDF viewer? Document annotations? Bounding box highlights? |
| **Forms** | What forms are needed? What fields? Validation rules? |
| **Navigation** | Sidebar? Top nav? Breadcrumbs? Back buttons? |
| **Branding** | Use PenguinAI branding or custom colors/logos? |

### Backend (api-builder) Clarifications

| Category | Questions to Ask |
|----------|------------------|
| **Authentication** | JWT tokens? SSO? Session-based? Guest access? |
| **Data Models** | What entities? (Users, Documents, Items?) What fields on each? |
| **Relationships** | How do entities relate? (User has many Documents?) |
| **Endpoints** | CRUD operations needed? Any special business logic endpoints? |
| **File Uploads** | Need file upload? What types? (PDF, images?) Max size? |
| **Storage** | Local filesystem? S3? Azure Blob? |
| **Permissions** | Role-based access? Who can see/edit what? |
| **Seed Data** | What demo data should be pre-populated? |

### AI Processing (ai-integrator) Clarifications

| Category | Questions to Ask |
|----------|------------------|
| **Document Type** | What documents? (Medical records, invoices, contracts, forms?) |
| **OCR Needs** | Need text extraction? Table extraction? Handwriting? |
| **Extraction Goals** | What to extract? (Codes, dates, names, amounts, entities?) |
| **Output Format** | Structured JSON? What fields in the output schema? |
| **Bounding Boxes** | Need to highlight source text in document? Click-to-scroll? |
| **Confidence Scores** | Show confidence? Threshold for auto-accept? |
| **Human Review** | Accept/Deny workflow? Edit extracted values? |
| **Providers** | Use defaults (Azure OCR + Bedrock Claude) or specific providers? |

### Example Clarification Flow

```
User: "Build me a medical coding app"

Before building, ask:
1. What screens? → Login, Queue, Coding Screen, Upload
2. User workflow? → Login → See queue → Select document → Review codes → Accept/Deny → Complete
3. What documents? → Medical records (PDFs)
4. What to extract? → ICD-10 codes with supporting text
5. Need bounding boxes? → Yes, click code to highlight source in PDF
6. Auth method? → JWT with email/password
7. Seed data? → 5 sample documents with pre-extracted codes
```

---

## Resource Locations

| Resource | Path |
|----------|------|
| Skills | `.claude/skills/` |
| Subagents | `.claude/agents/` |
| Standard UI Template | `/Users/vaatsav/Desktop/claude-code-agents/Standard_UI_Template/` |
| PDF Viewer Library | `/Users/vaatsav/Desktop/claude-code-agents/data-labelling-library/` |
| Platform Starter Kit | `/Users/vaatsav/Desktop/claude-code-agents/platform-starter-kit/` |
| Test Files | `/Users/vaatsav/Desktop/claude-code-agents/test_files/` |

---

## Library Usage Guidelines

### Frontend Libraries (Copy to Project)

| Library | Usage | Command |
|---------|-------|---------|
| **Standard_UI_Template** | Base scaffold for React apps | `cp -r Standard_UI_Template/* my-app/` |
| **data-labelling-library** | PDFViewer component (MANDATORY for PDF viewing) | `cp -r data-labelling-library my-app/src/lib/pdf-viewer` |

### Backend Libraries (Copy to Project)

| Library | Usage | Command |
|---------|-------|---------|
| **platform-starter-kit** | FastAPI foundation with auth, RBAC, utilities | `cp -r platform-starter-kit/* backend/` |
| **platform-starter-kit/utils** | OCR, bbox, storage utilities | `cp -r platform-starter-kit/utils backend/` |

### SDK Libraries (Install via pip)

### Test Data

| Library | Usage | Path |
|---------|-------|------|
| **test_files** | Sample PDFs, images, bounding boxes | `/Users/vaatsav/Desktop/claude-code-agents/test_files/` |

> **CRITICAL:** Always COPY libraries to projects. Never reference paths outside the project directory at runtime.

---

## Branding

- **Primary Color:** `#fc459d`
- **Gradients:** `from-[#fc459d] via-purple-600 to-pink-600`
- **Glass Effect:** `bg-white/80 backdrop-blur-sm`
- **Logo Files:** `penguin-logo.svg`, `Penguinai-name.png`

---

## MongoDB

- **Connection:** `mongodb://localhost:27017/`
- **Default Database:** `penguin_app`

---

## Default AI Providers

| Capability | Provider |
|------------|----------|
| **OCR** | Azure Document Intelligence |
| **LLM** | BEDOCK CLAUDE |

---

## Data Flow

```
┌───────────┐    ┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│ ui-builder│───▶│ api-builder │───▶│ai-integrator │───▶│quality-tester │
└───────────┘    └─────────────┘    └──────────────┘    └───────────────┘
      │                │                   │                    │
      ▼                ▼                   ▼                    ▼
  React App       FastAPI App       AI Processing        Test Report
  USER_WORKFLOW   All Endpoints     OCR + LLM            All Verified
  API_REQUIREMENTS Seed Data        Bounding Boxes       Production Ready
```

---

## Final Output Format

After all phases complete:

```markdown
## Full-Stack Application Ready

### Frontend (ui-builder)
- URL: http://localhost:5173
- Build: Passing

### Backend (api-builder)
- URL: http://localhost:8000
- API Docs: http://localhost:8000/docs

### AI Processing (ai-integrator)
- OCR: Working
- LLM Extraction: Working
- Bounding Boxes: Mapped

### Tests (quality-tester)
- Browser Tests: All passing
- API Integration: Verified
- E2E Workflows: Complete

### Credentials
- Email: demo@penguinai.com
- Password: demo123
```

---

## Post-Task Cleanup

**After completing any task, clean up unnecessary files:**

### Remove These Files
- ❌ Auto-generated README.md files (unless explicitly requested)
- ❌ CHANGELOG.md (unless requested)
- ❌ CONTRIBUTING.md
- ❌ Duplicate documentation files
- ❌ Empty or placeholder markdown files
- ❌ `.md` files created during development that aren't needed

### Keep These Files
- ✅ `USER_WORKFLOW.md` - Required for testing phase
- ✅ `API_REQUIREMENTS.md` - Required for backend phase
- ✅ `.env.example` - Environment template
- ✅ Project's main README if explicitly requested

### Cleanup Command
```bash
# Review and remove unnecessary markdown files
find . -name "README.md" -path "*/src/*" -delete
find . -name "*.md" -empty -delete
```