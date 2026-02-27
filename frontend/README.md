# Healthcare Claim Denial Appeal Management - Frontend

## Overview

The frontend is a React-based web application for managing healthcare claim denials and appeals. It provides healthcare providers with tools to track denied claims, upload supporting documentation, evaluate appeal criteria using AI, and generate professional appeal letters. The application features a multi-step wizard for creating denials, integrated PDF viewing with bounding box highlighting, and real-time analytics dashboards.

## Tech Stack

### Core Framework
- **React** 19.1.0 - UI framework
- **Vite** 7.0.4 - Build tool and dev server
- **React Router DOM** 7.7.0 - Client-side routing

### UI Libraries
- **Tailwind CSS** 3.4.17 - Utility-first CSS framework
- **Material-UI** 7.3.7 - Component library
- **Emotion** 11.14.0 - CSS-in-JS styling
- **Lucide React** 0.562.0 - Icon library
- **Heroicons** 2.1.5 - Additional icons

### Visualization & Display
- **Recharts** 3.7.0 - Chart library for analytics
- **React Markdown** 10.1.0 - Markdown rendering
- **PDF.js** (via custom PDFViewer component) - PDF rendering

### Development Tools
- **ESLint** 9.31.0 - Code linting
- **Autoprefixer** 10.4.21 - CSS vendor prefixing
- **PostCSS** 8.5.4 - CSS processing

## Project Structure

```
frontend/
├── public/                    # Static assets
├── src/
│   ├── App.jsx               # Root component with routing
│   ├── main.jsx              # Application entry point
│   ├── index.css             # Global styles
│   ├── components/           # React components
│   │   ├── LoginPage.jsx     # Authentication screen
│   │   ├── Layout.jsx        # App shell with sidebar
│   │   ├── Dashboard.jsx     # Analytics dashboard
│   │   ├── DenialsList.jsx   # Browse and filter denials
│   │   ├── NewDenialWizard.jsx  # 7-step denial creation
│   │   ├── DenialDetail.jsx  # Complete denial view (largest component)
│   │   ├── DocumentUploadModal.jsx  # File upload interface
│   │   ├── DocumentChecklist.jsx    # Document progress tracker
│   │   └── PDFViewer.jsx     # PDF display wrapper
│   ├── services/
│   │   └── api.js            # API client with all endpoints
│   └── lib/
│       └── pdf-viewer/       # PDF viewing library
│           └── src/
│               ├── components/
│               │   ├── PDFViewer.jsx      # Core PDF viewer
│               │   ├── PDFPageRenderer.jsx
│               │   ├── PDFToolbar.jsx
│               │   ├── NERViewer.jsx      # Bounding box viewer
│               │   ├── NERPDFPageRenderer.jsx
│               │   ├── AnnotationCanvas.jsx
│               │   └── NERTagsSidebar.jsx
│               └── ...
├── .env                      # Environment variables
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind configuration
└── package.json              # Dependencies

```

## Architecture

### Routing Structure

| Route | Component | Protection | Description |
|-------|-----------|------------|-------------|
| `/login` | LoginPage | Public | User authentication |
| `/dashboard` | Dashboard | Protected | Analytics and metrics overview |
| `/denials` | DenialsList | Protected | Browse all denials with filters |
| `/denials/new` | NewDenialWizard | Protected | Create new denial (7-step wizard) |
| `/denials/:id` | DenialDetail | Protected | Comprehensive denial management |

### State Management

The application uses **React local state** (useState, useEffect) without global state management libraries like Redux. State is managed at the component level with props drilling for parent-child communication.

**Authentication State:**
- Stored in `localStorage.authToken`
- Managed in App.jsx via `isLoggedIn` state
- Protected routes redirect to `/login` if not authenticated

**Data Fetching:**
- API calls made directly in components using `useEffect`
- Loading states managed with local `useState`
- No caching or query management library

### Component Hierarchy

```
App
├── LoginPage (unauthenticated)
└── Layout (authenticated wrapper)
    ├── Sidebar (navigation)
    └── Main Content
        ├── Dashboard
        │   ├── MetricCards (5 KPI cards)
        │   └── Charts (Recharts visualizations)
        ├── DenialsList
        │   ├── Filters (status, payer, date range)
        │   └── DenialCards (grid layout)
        ├── NewDenialWizard
        │   ├── Step 1: Basic Info
        │   ├── Step 2: Payer Selection
        │   ├── Step 3: Patient Details
        │   ├── Step 4: Provider Info
        │   ├── Step 5: Service Details
        │   ├── Step 6: Denial Reason
        │   └── Step 7: Review & Submit
        └── DenialDetail
            ├── Header (claim info, status badge)
            ├── Tabs (Overview, Documents, Criteria, Appeal)
            ├── DocumentUploadModal
            ├── DocumentChecklist
            ├── CriteriaEvaluation
            ├── AppealLetterViewer
            └── PDFViewer (with bounding boxes)
```

## Key Components

### Dashboard
**Location:** `src/components/Dashboard.jsx`

**Purpose:** Analytics and key performance indicators

**Features:**
- 5 metric cards (Total Denials, Pending Review, Average Denied Amount, Win Rate, Active Appeals)
- Denial trends chart (line graph using Recharts)
- Status distribution chart (pie chart)
- Top payers by denials (bar chart)
- Quick action buttons (New Denial, Upload CSV)

**Data Loading:**
```javascript
useEffect(() => {
  const fetchData = async () => {
    const [denials, metrics] = await Promise.all([
      denialsAPI.getAll(),
      metricsAPI.getOverview()
    ]);
    // Process and set state
  };
}, []);
```

### DenialsList
**Location:** `src/components/DenialsList.jsx`

**Purpose:** Browse, filter, and search denials

**Features:**
- Search by claim number, patient name
- Filter by status (Pending Review, Documents Uploaded, Criteria Evaluated, Appeal Generated)
- Filter by payer
- Date range filtering
- Grid layout with denial cards
- Click to navigate to detail view

**State Management:**
```javascript
const [filters, setFilters] = useState({
  status: '',
  payer_id: '',
  search: '',
  date_from: '',
  date_to: ''
});
```

### NewDenialWizard
**Location:** `src/components/NewDenialWizard.jsx`

**Purpose:** Multi-step guided denial creation

**7-Step Workflow:**

1. **Basic Info** - Claim number, service date, status
2. **Payer Selection** - Insurance payer with policy lookup
3. **Patient Details** - Name, DOB, member ID
4. **Provider Info** - NPI, name, specialty, location
5. **Service Details** - CPT codes, diagnosis codes, place of service
6. **Denial Reason** - Denial code and description
7. **Review & Submit** - Summary with edit capability

**Step Navigation:**
```javascript
const [currentStep, setCurrentStep] = useState(1);
const [formData, setFormData] = useState({...});

const nextStep = () => setCurrentStep(prev => Math.min(prev + 1, 7));
const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 1));
```

**Submission:**
```javascript
const handleSubmit = async () => {
  const result = await denialsAPI.create(formData);
  navigate(`/denials/${result.denial_id}`);
};
```

### DenialDetail
**Location:** `src/components/DenialDetail.jsx`

**Purpose:** Comprehensive denial management hub (largest component)

**Tabbed Interface:**

**1. Overview Tab**
- Full denial information display
- Edit capability
- Status management
- Key dates and amounts

**2. Documents Tab**
- Upload documents button → DocumentUploadModal
- Document checklist with progress tracking
- Document cards with metadata
- View PDF button → Opens PDFViewer

**3. Criteria Evaluation Tab**
- Evaluate criteria button (triggers AI processing)
- Loading states with progress indicators
- Results display:
  - Win probability percentage
  - Supporting criteria cards (green)
  - Contradictory criteria cards (red)
  - Each card shows:
    - Question and answer
    - Evidence text
    - Supporting documents with bounding box links
- Click evidence → scrolls to highlighted text in PDF

**4. Appeal Letter Tab**
- Generate appeal button (triggers AI)
- Letter preview with professional formatting
- Download appeal package (PDF with merged documents)
- Edit and regenerate capability

**Component Size:** ~1200 lines (most complex component)

### DocumentUploadModal
**Location:** `src/components/DocumentUploadModal.jsx`

**Purpose:** File upload interface

**Features:**
- Drag-and-drop file zone
- File type validation (PDF, images)
- Document type selection dropdown
- Upload progress indicator
- Multi-file support

**Upload Flow:**
```javascript
const handleUpload = async (files) => {
  for (const file of files) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', selectedType);
    await documentsAPI.upload(denialId, formData);
  }
  onUploadComplete();
};
```

### DocumentChecklist
**Location:** `src/components/DocumentChecklist.jsx`

**Purpose:** Track required document collection

**Features:**
- Displays required document types
- Shows completion status (uploaded vs missing)
- Visual progress bar
- Link to upload modal

**Document Types:**
- Medical Records
- Lab Results
- Imaging Reports
- Prior Authorization
- Denial Letter
- Provider Notes

### PDFViewer with Bounding Boxes
**Location:** `src/lib/pdf-viewer/src/components/NERViewer.jsx`

**Purpose:** Display PDFs with AI-extracted text highlighting

**Features:**
- Multi-page PDF rendering
- Zoom controls (fit-width, fit-page, custom zoom)
- Page navigation
- Bounding box overlays highlighting extracted evidence
- Click bounding box → shows extracted text tooltip
- Scroll to page from evidence click
- Color-coded highlights by entity type

**Data Format Expected:**
```javascript
{
  document_url: "https://s3.../document.pdf",
  entities: [
    {
      text: "Patient has diabetes mellitus",
      bboxes: [
        {
          page: 1,
          coordinates: [x1, y1, x2, y2, x3, y3, x4, y4], // Normalized 0-1
          page_width: 8.5,
          page_height: 11
        }
      ],
      entity_type: "CONDITION"
    }
  ]
}
```

## API Integration

### Service Layer Structure
**Location:** `src/services/api.js`

**Base Configuration:**
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://dev-api.penguinai.co/appeals-dev';

const getHeaders = () => ({
  'Content-Type': 'application/json',
  ...(localStorage.getItem('authToken') && {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  })
});
```

**API Modules:**

| Module | Endpoints | Purpose |
|--------|-----------|---------|
| `authAPI` | login, getMe | Authentication |
| `denialsAPI` | getAll, getById, create, update, uploadCSV | Denial CRUD |
| `medicalPoliciesAPI` | getAll, lookup | Payer policy lookup |
| `documentsAPI` | upload, getByDenialId, delete | Document management |
| `criteriaAPI` | evaluate | AI criteria evaluation |
| `appealsAPI` | generate, getByDenialId, download | Appeal generation |
| `metricsAPI` | getOverview, getTrends | Analytics data |

### Authentication Flow

```
┌─────────────┐
│ LoginPage   │
│             │
│ Enter email │
│ & password  │
└──────┬──────┘
       │
       │ POST /auth/login
       ▼
┌─────────────────┐
│   Backend API   │
│                 │
│ Validate creds  │
│ Generate JWT    │
└──────┬──────────┘
       │
       │ Return { access_token, user }
       ▼
┌──────────────────┐
│   Frontend       │
│                  │
│ Store token in   │
│ localStorage     │
│ Set isLoggedIn   │
│ Navigate to      │
│ /dashboard       │
└──────────────────┘
```

**Token Storage:**
```javascript
// On login
localStorage.setItem('authToken', data.access_token);

// On every API request
headers: {
  'Authorization': `Bearer ${localStorage.getItem('authToken')}`
}

// On logout
localStorage.removeItem('authToken');
```

### Error Handling

**Pattern:**
```javascript
try {
  const data = await denialsAPI.getById(id);
  setDenial(data);
} catch (error) {
  console.error('Failed to load denial:', error);
  // Show error notification (varies by component)
}
```

**No Global Error Handler** - Errors managed per-component

## Data Flow Diagrams

### Creating a New Denial

```
User clicks "New Denial" on Dashboard
         ↓
Navigate to /denials/new
         ↓
NewDenialWizard renders (Step 1)
         ↓
User fills Basic Info → Next
         ↓
User selects Payer (Step 2)
  ├─ Dropdown changed → medicalPoliciesAPI.lookup(payer_id, cpt_code)
  └─ Display policy requirements
         ↓
User fills Patient, Provider, Service details (Steps 3-5)
         ↓
User enters Denial Reason (Step 6)
         ↓
Review & Submit (Step 7)
         ↓
User clicks Submit
         ↓
POST /denials with formData
         ↓
Backend creates denial, returns { denial_id }
         ↓
Navigate to /denials/{denial_id}
         ↓
DenialDetail loads with new denial
```

### Document Upload Workflow

```
User on DenialDetail → Documents tab
         ↓
Click "Upload Documents" button
         ↓
DocumentUploadModal opens
         ↓
User drags files or clicks to browse
         ↓
User selects document type
         ↓
Click "Upload"
         ↓
For each file:
  POST /documents/upload
  ├─ FormData with file + metadata
  └─ Returns document_id
         ↓
Modal closes
         ↓
DenialDetail refetches documents
         ↓
DocumentChecklist updates progress
```

### Appeal Generation Workflow

```
User on DenialDetail → Appeal tab
         ↓
Click "Generate Appeal Letter" button
         ↓
POST /appeals/generate/{denial_id}
         ↓
Backend AI Processing:
  1. Fetch denial details
  2. Load criteria evaluation
  3. Generate letter using Gemini
  4. Assemble PDF package
  5. Upload to S3
         ↓
Loading spinner on frontend (polling or waiting)
         ↓
Response: { appeal_package_id, letter_text, package_s3_url }
         ↓
Display letter in preview
         ↓
User clicks "Download Package"
         ↓
GET /appeals/{appeal_id}/download
         ↓
Browser downloads PDF package
```

### Criteria Evaluation with Bounding Boxes

```
User on DenialDetail → Criteria tab
         ↓
Click "Evaluate Criteria" button
         ↓
POST /criteria/evaluate/{denial_id}
         ↓
Backend AI Pipeline:
  1. Filter documents by date
  2. OCR all documents (cached)
  3. Score relevancy (Gemini Flash)
  4. Shortlist top 3 documents
  5. Extract evidence (Gemini Pro)
  6. Map bounding boxes
  7. Calculate win probability
         ↓
Loading indicator on frontend
         ↓
Response: {
  criteria: [
    {
      question: "Is the service medically necessary?",
      answer: "Supporting",
      evidence: "Patient has documented diabetes...",
      supporting_documents: [
        {
          document_id: "doc123",
          bboxes: [{page: 1, coordinates: [...]}]
        }
      ]
    }
  ],
  win_probability: 0.78
}
         ↓
Display criteria cards with evidence
         ↓
User clicks evidence text
         ↓
Frontend extracts bboxes from clicked criterion
         ↓
Pass to NERViewer component:
  - Load PDF from document S3 URL
  - Overlay bounding boxes on correct pages
  - Scroll to first bbox
  - Highlight in green/red based on support type
```

## Critical Workflows

### 1. Creating a New Denial (7-Step Wizard)

**Entry Point:** Dashboard or DenialsList → "New Denial" button

**Step-by-Step:**

| Step | Fields | Validation | API Calls |
|------|--------|------------|-----------|
| 1. Basic Info | claim_number, service_date, received_date, status | Required fields | None |
| 2. Payer | payer_id, payer_name | Must select payer | `medicalPoliciesAPI.lookup()` on CPT change |
| 3. Patient | patient_name, patient_dob, member_id | DOB format validation | None |
| 4. Provider | rendering_npi, rendering_provider_name, specialty, location | NPI format | None |
| 5. Service | cpt_codes[], diagnosis_codes[], place_of_service | At least 1 CPT required | None |
| 6. Denial | denial_code, denial_reason_description | Required | None |
| 7. Review | Display all entered data | Final validation | `denialsAPI.create()` |

**Navigation:**
- Next/Previous buttons
- Step indicator (visual progress bar)
- Can't skip steps (sequential)
- Form data persists across steps

**Submission:**
```javascript
const formData = {
  claim_number: "CLM123456",
  service_date: "2024-01-15",
  payer_id: "CIGNA29881",
  patient_name: "John Doe",
  cpt_codes: ["99213", "80053"],
  // ... all fields
};

const result = await denialsAPI.create(formData);
// Navigate to /denials/{result.denial_id}
```

### 2. Generating an Appeal Letter

**Prerequisites:**
- Denial must have documents uploaded
- Criteria must be evaluated (win_probability calculated)

**Flow:**
1. Navigate to DenialDetail → Appeal tab
2. System checks if criteria evaluated
   - If not: Show "Evaluate Criteria First" message
   - If yes: Show "Generate Appeal" button
3. User clicks "Generate Appeal Letter"
4. Frontend makes POST /appeals/generate/{denial_id}
5. Loading state shows progress
6. Backend AI generates professional letter
7. Response includes letter_text and package_s3_url
8. Frontend displays letter preview with formatting
9. User can download complete package (PDF)

**Generated Letter Sections:**
- Header (provider letterhead)
- Claim information summary
- Patient details
- Service description
- Denial reason
- Appeal argument (AI-generated based on criteria)
- Supporting evidence references
- Closing and signature

### 3. Document Management

**Upload Flow:**
1. DenialDetail → Documents tab
2. Click "Upload Documents"
3. DocumentUploadModal opens
4. Select document type from dropdown
5. Drag files or browse
6. Files uploaded to S3 via backend
7. Backend triggers OCR processing
8. Documents saved to MongoDB with metadata
9. Modal closes, documents list refreshes
10. DocumentChecklist updates progress

**Document Types:**
- Medical Records
- Lab Results
- Imaging Reports
- Prior Authorization
- Denial Letter
- Provider Notes
- Other

**Delete Flow:**
1. User clicks delete icon on document card
2. Confirmation prompt
3. DELETE /documents/{document_id}
4. Document removed from S3 and MongoDB
5. List refreshes

## Styling & UI

### Tailwind CSS Approach

**Utility-First Pattern:**
```jsx
<div className="bg-white/80 backdrop-blur-sm rounded-lg shadow-lg p-6">
  <h2 className="text-2xl font-bold text-gray-800 mb-4">
    Claim Denials
  </h2>
</div>
```

### PenguinAI Branding

**Primary Color:** `#fc459d` (pink)

**Color Palette:**
```css
Primary: #fc459d
Purple: #9333ea
Pink: #ec4899
Gray Scale: gray-50 to gray-900
```

**Gradient Patterns:**
```jsx
className="bg-gradient-to-r from-[#fc459d] via-purple-600 to-pink-600"
className="bg-gradient-to-br from-purple-600 to-pink-600"
```

**Glass Effect:**
```jsx
className="bg-white/80 backdrop-blur-sm"
```

### Design System Elements

**Cards:**
```jsx
<div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
```

**Buttons:**
```jsx
// Primary
<button className="bg-gradient-to-r from-[#fc459d] to-purple-600 text-white px-6 py-2 rounded-lg">

// Secondary
<button className="border border-purple-600 text-purple-600 px-6 py-2 rounded-lg hover:bg-purple-50">
```

**Status Badges:**
```jsx
// Success
<span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">

// Warning
<span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">

// Danger
<span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
```

**Icons:**
- Material-UI icons for actions
- Lucide React for navigation
- Heroicons for UI elements

## Getting Started

### Prerequisites

- **Node.js** 18.0.0 or higher
- **npm** 9.0.0 or higher (or yarn/pnpm)
- Backend API running (see backend README)

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Running Locally

```bash
# Start development server
npm run dev

# Opens on http://localhost:5173
```

The Vite dev server includes:
- Hot module replacement (HMR)
- Fast refresh for React components
- Automatic port detection (uses 5174 if 5173 is busy)

### Building for Production

```bash
# Production build
npm run build

# Preview production build
npm run preview

# Development build (useful for debugging)
npm run build:dev
```

Build output goes to `dist/` directory.

### Environment Variables

Create a `.env` file in the frontend root:

```env
# API Base URL
VITE_API_BASE_URL=https://dev-api.penguinai.co/appeals-dev

# For local backend development
# VITE_API_BASE_URL=http://localhost:8000
```

**Note:** Vite requires `VITE_` prefix for environment variables to be exposed to the client.

### Default Credentials

```
Email: demo@penguinai.com
Password: demo123
```

## Configuration Files

### vite.config.js
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
```

### tailwind.config.js
```javascript
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        'penguin-pink': '#fc459d'
      }
    }
  },
  plugins: []
}
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

**PDF.js Requirements:** Modern browsers with Canvas API support

## Performance Considerations

### Optimization Strategies

1. **Code Splitting** - React Router lazy loading (not currently implemented)
2. **Image Optimization** - Use optimized assets
3. **PDF Rendering** - Lazy load pages, render viewport only
4. **API Calls** - Debounce search inputs
5. **Bundle Size** - Vite tree-shaking removes unused code

### Current Limitations

- No API response caching
- No infinite scroll pagination (loads all denials)
- No optimistic UI updates
- No service worker for offline support

## Common Development Tasks

### Adding a New Route

1. Create component in `src/components/`
2. Add route to `App.jsx`:
```jsx
<Route path="/new-route" element={
  <ProtectedRoute>
    <Layout><NewComponent /></Layout>
  </ProtectedRoute>
} />
```
3. Add navigation link in `Layout.jsx` sidebar

### Adding a New API Endpoint

1. Open `src/services/api.js`
2. Add to appropriate module:
```javascript
export const denialsAPI = {
  // ... existing methods
  newMethod: async (params) => {
    const response = await fetch(`${BASE_URL}/new-endpoint`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(params)
    });
    if (!response.ok) throw new Error('Failed');
    return response.json();
  }
};
```

### Adding a New Component

```jsx
// src/components/NewComponent.jsx
import { useState, useEffect } from 'react';
import { denialsAPI } from '../services/api';

export default function NewComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await denialsAPI.getAll();
        setData(result);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="p-6">
      {/* Component content */}
    </div>
  );
}
```

## Troubleshooting

### Common Issues

**Issue:** Cannot connect to backend API
- **Solution:** Check VITE_API_BASE_URL in .env
- Verify backend is running
- Check CORS configuration on backend

**Issue:** Authentication token expired
- **Solution:** Log out and log back in
- Token lifetime is 24 hours (1440 minutes)

**Issue:** PDF not rendering
- **Solution:** Check document S3 URL is accessible
- Verify CORS on S3 bucket
- Check browser console for errors

**Issue:** Bounding boxes not appearing
- **Solution:** Verify bbox format is normalized (0-1 range)
- Check page dimensions are included
- Ensure OCR was successful

**Issue:** Hot reload not working
- **Solution:** Restart Vite dev server
- Clear browser cache
- Check for syntax errors

## Architecture Decisions

### Why No Redux/State Management Library?

- Application state is mostly server-side
- Components fetch their own data
- Limited state sharing between routes
- Simplicity preferred over complexity

### Why Tailwind CSS?

- Rapid UI development
- Consistent design system
- Small bundle size with purging
- No CSS naming conflicts

### Why Material-UI with Tailwind?

- MUI provides complex components (modals, dialogs)
- Tailwind handles layout and custom styling
- Emotion allows CSS-in-JS when needed

### Why Custom PDF Viewer?

- Need bounding box highlighting
- Custom annotation requirements
- Scroll-to-bbox functionality
- Entity color coding

## Future Enhancements

Potential improvements (not currently implemented):

- [ ] Implement React Query for caching and state management
- [ ] Add lazy loading for routes and components
- [ ] Implement infinite scroll pagination
- [ ] Add optimistic UI updates
- [ ] Implement WebSocket for real-time updates
- [ ] Add offline support with service workers
- [ ] Implement comprehensive error boundaries
- [ ] Add unit and integration tests
- [ ] Implement accessibility improvements (ARIA labels)
- [ ] Add dark mode support
- [ ] Implement advanced search with Elasticsearch

---

**Last Updated:** January 2026

For backend documentation, see `backend/README.md`.
