---
name: frontend-guide
description: React UI patterns for PDF processing and document annotation workflows. Includes PDFViewer component, Tailwind CSS v4, React Router, and PenguinAI branding. Triggers on React, PDF viewers, frontend UI, or Tailwind.
---

# React UI Patterns

Patterns for building React applications with PDF viewing and document annotation capabilities.

---

## Source Libraries (CRITICAL - REUSE THESE)

### Standard UI Template
Base scaffold for new React applications with PenguinAI branding.

**Location:** `../claude-code-agents/Standard_UI_Template/`

**Copy these components for new projects:**
```bash
# Copy complete template as starting point
cp -r ../claude-code-agents/Standard_UI_Template/* my-app/

# Or copy specific components
cp Standard_UI_Template/src/components/LoginPage.jsx my-app/src/components/
cp Standard_UI_Template/src/components/Dashboard.jsx my-app/src/components/
cp Standard_UI_Template/public/penguin-logo.svg my-app/public/
cp Standard_UI_Template/public/Penguinai-name.png my-app/public/
```

**Key Files:**
- `src/components/LoginPage.jsx` - Authentication UI with PenguinAI branding
- `src/components/Dashboard.jsx` - Dashboard layout pattern
- `public/penguin-logo.svg` - Logo icon
- `public/Penguinai-name.png` - Full brand name image
- `tailwind.config.js` - Preconfigured Tailwind v4

### data-labelling-library (PDF Viewer)
Production PDF viewer with annotations and bounding boxes.

**Location:** `../claude-code-agents/data-labelling-library/`

**Exports:** `PDFViewer` (default), `NERViewer`

**Features:** Multi-page PDF, zoom, search, annotation, entity highlighting

---

## PDFViewer Component (CRITICAL)

> **ALWAYS use `data-labelling-library` for PDF/document viewing.**
> **NEVER use:** pdf.js, react-pdf, pdfjs-dist, or custom viewers.

### Installation

```bash
# Copy library to your project
cp -r ../claude-code-agents/data-labelling-library src/lib/pdf-viewer

# Required dependencies
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material lucide-react
```

### Basic Usage

```jsx
import { PDFViewer } from '../lib/pdf-viewer';

<PDFViewer
  documentData={documentData}
  boundingBoxes={boundingBoxes}
  className="h-full"
  userInterfaces={{ enableToolbar: false, zoom: true }}
/>
```

### documentData Format

```javascript
const documentData = {
  files: ["document.pdf"],
  presigned_urls: {
    "document.pdf": {
      "1": "https://url-to-page-1.png",
      "2": "https://url-to-page-2.png"
    }
  }
};
```

### boundingBoxes Format (8-point normalized coordinates)

```javascript
const boundingBoxes = [{
  page_number: 1,
  document_name: "document.pdf",
  bbox: [[0.1, 0.2, 0.3, 0.2, 0.3, 0.25, 0.1, 0.25]],  // x1,y1,...,x4,y4
  label: ["Evidence 1"],
  color: ["#fc459d"]
}];
```

### Height Constraints (CRITICAL)

PDFViewer requires explicit height for proper scrolling:

```jsx
// CORRECT: Explicit height chain
<div className="h-screen flex">
  <div className="w-3/5 h-full">
    <PDFViewer documentData={data} className="h-full" />
  </div>
</div>

// WRONG: No height constraint
<div>
  <PDFViewer documentData={data} />  // Pages expand instead of scroll
</div>
```

### Evidence Click → Auto-Scroll

```jsx
const [boundingBoxes, setBoundingBoxes] = useState([]);

const handleEvidenceClick = (evidence) => {
  setBoundingBoxes([{
    page_number: evidence.page,
    document_name: evidence.documentName,
    bbox: [evidence.coords],
    label: [evidence.label],
    color: ['#fc459d']
  }]);
  // PDFViewer auto-scrolls when boundingBoxes changes
};
```

---

## Project Setup

### 1. Create Project

```bash
npm create vite@latest my-app -- --template react
cd my-app
npm install react-router-dom @heroicons/react lucide-react
npm install @mui/material @emotion/react @emotion/styled @mui/icons-material
npm install -D tailwindcss @tailwindcss/postcss
```

### 2. Tailwind CSS v4 Configuration

```javascript
// postcss.config.js
export default {
  plugins: { '@tailwindcss/postcss': {} }
}
```

```css
/* src/index.css */
@import "tailwindcss";

@theme {
  --animate-gradient: gradient 8s linear infinite;
  --animate-float: float 6s ease-in-out infinite;
}

@layer components {
  .gradient-bg {
    background: linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
  }
  .glass-effect {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
  }
}
```

### 3. Project Structure

```
my-app/
├── public/
│   ├── penguin-logo.svg
│   └── Penguinai-name.png
├── src/
│   ├── App.jsx
│   ├── index.css
│   ├── lib/pdf-viewer/
│   ├── components/
│   ├── context/
│   ├── hooks/
│   └── services/api.js
└── .env.development
```

---

## PenguinAI Branding

```jsx
// Colors
const PRIMARY = "#fc459d";
const GRADIENTS = "from-[#fc459d] via-purple-600 to-pink-600";

// Glass Card
<div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-gray-200/50">

// Logo Usage
<img src="/penguin-logo.svg" alt="PenguinAI" className="h-8 w-8" />
<img src="/Penguinai-name.png" alt="PenguinAI" className="h-6" />
```

---

## React Router Setup

```jsx
// App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/queue" element={
          <ProtectedRoute><QueuePage /></ProtectedRoute>
        } />
        <Route path="/coding/:id" element={
          <ProtectedRoute><CodingPage /></ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('authToken');
  return token ? children : <Navigate to="/login" />;
}
```

---

## API Service Layer

```javascript
// src/services/api.js
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const getHeaders = () => ({
  'Content-Type': 'application/json',
  ...(localStorage.getItem('authToken') && {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  })
});

export const authAPI = {
  login: (email, password) =>
    fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ email, password })
    }).then(r => r.json()),

  getMe: () =>
    fetch(`${BASE_URL}/auth/me`, { headers: getHeaders() })
      .then(r => r.json())
};

export const documentsAPI = {
  getQueue: (status) =>
    fetch(`${BASE_URL}/documents/queue${status ? `?status=${status}` : ''}`, {
      headers: getHeaders()
    }).then(r => r.json()),

  getById: (id) =>
    fetch(`${BASE_URL}/documents/${id}`, { headers: getHeaders() })
      .then(r => r.json())
};
```

---

## Common UI Patterns

### Split Panel Layout (60/40)

```jsx
<div className="h-screen flex">
  <div className="w-3/5 h-full border-r">
    <PDFViewer documentData={data} className="h-full" />
  </div>
  <div className="w-2/5 h-full overflow-y-auto p-4">
    {/* Sidebar content */}
  </div>
</div>
```

### Loading State

```jsx
const [isLoading, setIsLoading] = useState(false);

<button disabled={isLoading} onClick={handleSubmit}>
  {isLoading ? (
    <><Spinner className="animate-spin mr-2" /> Loading...</>
  ) : 'Submit'}
</button>
```

### Status Badge

```jsx
const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800'
};

<span className={`px-2 py-1 rounded-full text-xs ${STATUS_COLORS[status]}`}>
  {status}
</span>
```

---

## Progressive Disclosure

For detailed patterns, see:
- `templates/api-contract.md` - API contract specification
- `templates/project-structure.md` - Full project structure
- `templates/api-hooks.js` - React hooks for API calls
- `templates/auth-context.jsx` - Authentication context
- `templates/transformers.js` - Data transformation utilities
