# PDF Viewer/NER Annotation Tool - Complete Implementation Documentation

# Using Across Multiple Projects - Git Submodule

git submodule add https://github.com/Penguin-AI-Corp/data-labelling-library.git src/lib/pdf-viewer

# Then import normally
import { PDFViewer, NERViewer } from './lib/pdf-viewer';

## Install dependencies:

npm install @mui/material @emotion/react @emotion/styled @mui/icons-material lucide-react

## Import and use:

jsx// src/App.js
```jsx
import React, { useState } from 'react';
import { PDFViewer, NERViewer } from './lib/pdf-viewer';

function App() {
  const [viewMode, setViewMode] = useState('pdf'); // 'pdf' or 'ner'
  const [searchResults, setSearchResults] = useState(null);

  const documentData = {
    files: ['document1.pdf'],
    presigned_urls: {
      'document1.pdf': {
        '1': '/sample-page1.png',
        '2': '/sample-page2.png',
      }
    }
  };

  const boundingBoxData = {
    supporting_sentence_in_document: "",
    document_name: "document1.pdf",
    section_name: "Unknown",
    page_number: "2",
    bbox: [
        [
        0.055248618784530384, 0.18784604095790808, 0.47513812154696133,
        0.18784604095790808, 0.47513812154696133, 0.21986525248482422,
        0.055248618784530384, 0.21986525248482422,
        ],
    ],
   };

  const nerData = [
    {
      filename: "document1.pdf",
      data: {
        "1": [
          {
            word: "John",
            entity: "John Doe",
            entity_type: "PERSON",
            code: "P001",
            bbox: [0.1, 0.1, 0.2, 0.15],
            tags: ["medical", "patient"]
          }
        ],
        "2": [
          {
            word: "Hospital",
            entity: "General Hospital",
            entity_type: "ORGANIZATION", 
            code: "ORG001",
            bbox: [0.3, 0.2, 0.5, 0.25],
            tags: ["medical", "facility"]
          }
        ]
      }
    }
  ];

  return (
    <div style={{ height: '100vh' }}>
      {/* Mode Toggle */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setViewMode('pdf')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'pdf'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            PDF Viewer
          </button>
          <button
            onClick={() => setViewMode('ner')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'ner'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            NER Viewer
          </button>
        </div>
      </div>

      {/* Viewer Component */}
      {viewMode === 'ner' ? (
        <NERViewer
          documentData={documentData}
          nerData={nerData}
          userInterfaces={{
            docNavigation: true,
            zoom: true,
            download: true,
            keyboardShortcuts: true,
            showFilename: true,
          }}
        />
      ) : (
        <PDFViewer
          documentData={documentData}
          boundingBoxes={boundingBoxData}  
          searchResults={searchResults}
          setSearchResults={setSearchResults}
          userInterfaces={{
            docNavigation: true,
            zoom: true,
            download: true,
          }}
        />
      )}
    </div>
  );
}

export default App;
```

## Overview

A comprehensive React PDF viewer with annotation capabilities, search functionality, Named Entity Recognition (NER) highlighting, and document navigation. This documentation covers both PDFViewer and NERViewer components with all props, handlers, and data structures.

## Table of Contents

1. [Component Props](#component-props)
2. [Data Structures](#data-structures)
3. [Event Handlers](#event-handlers)
4. [User Interface Configuration](#user-interface-configuration)
5. [Complete Usage Examples](#complete-usage-examples)
6. [API Integration](#api-integration)
7. [Versions & Tags](#versions--tags)

---

## Component Props

### PDFViewer Props Reference

```jsx
<PDFViewer
  documentData={DocumentData}           // Required: Document files and URLs
  boundingBoxes={BoundingBoxData}       // Optional: Highlight regions
  searchResults={SearchResults}         // Optional: Search results with highlights
  userInterfaces={UserInterfaces}       // Optional: UI feature toggles
  onDocumentChange={Function}           // Optional: Document change callback
  onPageChange={Function}               // Optional: Page change callback
  onAnnotationAdd={Function}            // Optional: New annotation callback
  onSearchPerformed={Function}          // Optional: Search execution callback
  setSearchResults={Function}           // Optional: Search results setter
/>
```

### NERViewer Props Reference

```jsx
<NERViewer
  documentData={DocumentData}           // Required: Document files and URLs
  nerData={NERData}                     // Required: NER entity data
  userInterfaces={NERUserInterfaces}    // Optional: UI feature toggles
  onDocumentChange={Function}           // Optional: Document change callback
  onPageChange={Function}               // Optional: Page change callback
  className={string}                    // Optional: CSS class name
/>
```

### Prop Details

#### PDFViewer Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `documentData` | `DocumentData` | ✅ | - | Contains file names and page URLs |
| `boundingBoxes` | `BoundingBox \| null` | ❌ | `null` | Regions to highlight on pages |
| `searchResults` | `SearchResults \| null` | ❌ | `null` | Search results with highlighting |
| `userInterfaces` | `UserInterfaces` | ❌ | `{}` | UI feature configuration |
| `onDocumentChange` | `(documentName: string) => void` | ❌ | - | Called when user switches documents |
| `onPageChange` | `(pageNumber: number) => void` | ❌ | - | Called when user navigates pages |
| `onAnnotationAdd` | `(annotation: Annotation) => void` | ❌ | - | Called when user adds annotation |
| `onSearchPerformed` | `(searchQuery: string) => void` | ❌ | - | Called when user performs search |
| `setSearchResults` | `(results: SearchResults \| null) => void` | ❌ | - | Function to update search results |

#### NERViewer Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `documentData` | `DocumentData` | ✅ | - | Contains file names and page URLs |
| `nerData` | `NERData` | ✅ | - | Named entity recognition data |
| `userInterfaces` | `NERUserInterfaces` | ❌ | `{}` | UI feature configuration |
| `onDocumentChange` | `(documentName: string) => void` | ❌ | - | Called when user switches documents |
| `onPageChange` | `(pageNumber: number) => void` | ❌ | - | Called when user navigates pages |
| `className` | `string` | ❌ | `""` | CSS class name for styling |

---

## Data Structures

### DocumentData

**Purpose:** Defines the documents and their page URLs (Used by both PDFViewer and NERViewer)

```typescript
interface DocumentData {
  files: string[];                    // Array of document names
  presigned_urls: {
    [documentName: string]: {
      [pageNumber: string]: string;   // Page number to image URL mapping
    };
  };
}
```

**Example:**
```javascript
const samplePDFData = {
  files: ['Annual_Report_2023.pdf', 'User_Manual.pdf', 'Technical_Specs.pdf'],
  presigned_urls: {
    'Annual_Report_2023.pdf': {
      '1': 'https://example.com/annual-report-page1.png',
      '2': 'https://example.com/annual-report-page2.png',
      '3': 'https://example.com/annual-report-page3.png',
    },
    'User_Manual.pdf': {
      '1': 'https://example.com/manual-page1.png',
      '2': 'https://example.com/manual-page2.png',
    },
    'Technical_Specs.pdf': {
      '1': 'https://example.com/specs-page1.png',
    }
  }
};
```

### BoundingBox (PDFViewer)

**Purpose:** Defines regions to highlight on specific pages

```typescript
interface BoundingBox {
  document_name: string;              // Document containing the highlight
  page_number: string;                // Page number (as string)
  bbox: number[][];                   // Array of coordinate arrays
  supporting_sentence_in_document?: string; // Optional tooltip text
}
```

**Coordinate Format:** Each bbox item is `[x1, y1, x2, y2, x3, y3, x4, y4]` representing four corners
- Coordinates are normalized (0.0 to 1.0)
- `(0,0)` is top-left, `(1,1)` is bottom-right

**Example:**
```javascript
const sampleBoundingBoxes = {
  document_name: 'Annual_Report_2023.pdf',
  page_number: '1',
  bbox: [
    [0.1, 0.1, 0.5, 0.1, 0.5, 0.2, 0.1, 0.2], // First highlight region
    [0.2, 0.3, 0.8, 0.3, 0.8, 0.4, 0.2, 0.4], // Second highlight region
  ],
  supporting_sentence_in_document: 'Key financial metrics for Q4 2023'
};
```

### NERData (NERViewer)

**Purpose:** Contains named entity recognition data for highlighting entities

```typescript
interface NERData {
  filename: string;                   // Document filename
  data: {
    [pageNumber: string]: NEREntity[]; // Page number to entities mapping
  };
}

interface NEREntity {
  word: string;                       // Detected word/phrase
  entity: string;                     // Full entity name
  entity_type: string;                // Entity classification (PERSON, ORG, etc.)
  code: string;                       // Entity code/identifier
  bbox: number[];                     // [x_min, y_min, x_max, y_max] normalized coordinates
  tags?: string[];                    // Optional tags for categorization
}
```

**Example:**
```javascript
const sampleNERData = [
  {
    filename: 'Medical_Report.pdf',
    data: {
      '1': [
        {
          word: 'John Doe',
          entity: 'John Doe',
          entity_type: 'PERSON',
          code: 'PATIENT_001',
          bbox: [0.1, 0.15, 0.25, 0.18],
          tags: ['patient', 'primary']
        },
        {
          word: 'diabetes',
          entity: 'Type 2 Diabetes',
          entity_type: 'CONDITION',
          code: 'ICD10_E11',
          bbox: [0.3, 0.45, 0.42, 0.48],
          tags: ['diagnosis', 'chronic']
        }
      ],
      '2': [
        {
          word: 'General Hospital',
          entity: 'General Hospital',
          entity_type: 'ORGANIZATION',
          code: 'FACILITY_001',
          bbox: [0.2, 0.1, 0.45, 0.13],
          tags: ['medical', 'facility']
        }
      ]
    }
  }
];
```

### SearchResults (PDFViewer)

**Purpose:** Contains search matches with highlighting information

```typescript
interface SearchResults {
  results: SearchResult[];            // Array of individual search matches
  total_matches: number;              // Total number of matches found
}

interface SearchResult {
  document_name: string;              // Document containing the match
  page_number: string;                // Page number (as string)
  text_snippet: string;               // Matching text excerpt
  match_score: number;                // Relevance score (0.0 to 1.0)
  bbox: number[][];                   // Coordinates of matching text
}
```

### UserInterfaces (PDFViewer)

**Purpose:** Controls which UI features are displayed in PDFViewer

```typescript
interface UserInterfaces {
  docNavigation?: boolean;            // Show document navigation controls
  zoom?: boolean;                     // Show zoom controls
  download?: boolean;                 // Show download button
}
```

### NERUserInterfaces (NERViewer)

**Purpose:** Controls which UI features are displayed in NERViewer

```typescript
interface NERUserInterfaces {
  docNavigation?: boolean;            // Show document navigation controls
  zoom?: boolean;                     // Show zoom controls
  download?: boolean;                 // Show download button
  keyboardShortcuts?: boolean;        // Show keyboard shortcuts help
  showFilename?: boolean;             // Show filename indicator
}
```

**Example:**
```javascript
const nerUserInterfaces = {
  docNavigation: true,       // Shows prev/next document buttons
  zoom: true,               // Shows zoom in/out controls
  download: false,          // Hides download button
  keyboardShortcuts: true,  // Shows keyboard shortcuts overlay
  showFilename: true,       // Shows filename in top-left corner
};
```

---

## Event Handlers

### NERViewer Event Handlers

#### onDocumentChange (NERViewer)

**Purpose:** Called when user switches to a different document in NER viewer

```javascript
const handleNERDocumentChange = (documentName) => {
  console.log("NER Viewer - User switched to document:", documentName);
  
  // Common use cases:
  // 1. Load NER data for new document
  loadNERDataForDocument(documentName);
  
  // 2. Reset entity type visibility
  resetEntityTypeFilters();
  
  // 3. Update URL/routing
  window.history.pushState({}, '', `/ner-documents/${documentName}`);
  
  // 4. Analytics tracking
  analytics.track('ner_document_viewed', { 
    document: documentName,
    entity_types_count: getUniqueEntityTypes(nerData).length
  });
};
```

#### onPageChange (NERViewer)

**Purpose:** Called when user navigates to a different page in NER viewer

```javascript
const handleNERPageChange = (pageNumber) => {
  console.log("NER Viewer - User navigated to page:", pageNumber);
  
  // Common use cases:
  // 1. Update entity counts for current page
  updateEntityCountsDisplay(pageNumber);
  
  // 2. Preload entities for adjacent pages
  preloadEntitiesForPage(pageNumber + 1);
  preloadEntitiesForPage(pageNumber - 1);
  
  // 3. Analytics
  const pageEntities = getCurrentPageEntities(currentDocument, pageNumber);
  analytics.track('ner_page_viewed', { 
    page: pageNumber,
    entities_count: pageEntities.length,
    entity_types: [...new Set(pageEntities.map(e => e.entity_type))]
  });
  
  // 4. Auto-scroll tags sidebar to show current page entities
  scrollTagsToCurrentPage(pageNumber);
};
```

### PDFViewer Event Handlers

[Previous PDFViewer event handlers remain the same as in original documentation]

---

## User Interface Configuration

### NERViewer Features

#### keyboardShortcuts: boolean

**When `true`:** Shows keyboard shortcuts overlay
- Displays keyboard navigation help
- Shows entity interaction shortcuts
- Includes scrolling and zoom shortcuts

**Keyboard Shortcuts:**
```
↑↓ Scroll • Shift+↑↓ Page • Ctrl+↑↓ Top/Bottom
PgUp/PgDn Page • Home/End Document
Ctrl+T Toggle Tags Sidebar
Click entities to view details
```

#### showFilename: boolean

**When `true`:** Shows filename indicator
- Displays current document name in top-left corner
- Useful for multi-document workflows
- Automatically truncates long filenames

**UI Elements:**
```
📄 Medical_Report.pdf
```

### NERViewer Unique Features

#### Entity Type Filtering
- **Color-coded entity types**: Each entity type gets a unique color
- **Toggle visibility**: Click entity type buttons to show/hide
- **Current page indicators**: Shows count of entities on current page
- **Dynamic colors**: Entity colors match bounding box highlights

#### Tags Sidebar
- **Expandable tags**: Click to expand and view entities
- **Scrollable content**: Handles large numbers of entities
- **Color-coded entities**: Matches entity type colors
- **Entity details**: Shows entity name, code, and type

#### Entity Details Popup
- **Click interaction**: Click any entity to view details
- **Comprehensive info**: Shows word, entity name, code, and type
- **Copy functionality**: Copy entity details with one click
- **Search integration**: Direct Google search for entity codes

---

## Complete Usage Examples

### Basic NER Setup

```javascript
import React, { useState } from 'react';
import { NERViewer } from './components/NERViewer';

function BasicNERViewer() {
  const documentData = {
    files: ['medical_report.pdf'],
    presigned_urls: {
      'medical_report.pdf': {
        '1': '/images/medical-page1.png',
        '2': '/images/medical-page2.png',
      }
    }
  };

  const nerData = [
    {
      filename: 'medical_report.pdf',
      data: {
        '1': [
          {
            word: 'Patient',
            entity: 'John Smith',
            entity_type: 'PERSON',
            code: 'P001',
            bbox: [0.1, 0.2, 0.3, 0.25],
            tags: ['patient', 'primary']
          },
          {
            word: 'Hypertension',
            entity: 'Essential Hypertension',
            entity_type: 'CONDITION',
            code: 'I10',
            bbox: [0.4, 0.5, 0.6, 0.55],
            tags: ['diagnosis', 'cardiovascular']
          }
        ]
      }
    }
  ];

  return (
    <div style={{ height: '100vh' }}>
      <NERViewer
        documentData={documentData}
        nerData={nerData}
        userInterfaces={{
          docNavigation: false,
          zoom: true,
          download: true,
          keyboardShortcuts: true,
          showFilename: true,
        }}
        onDocumentChange={(doc) => console.log('Document changed:', doc)}
        onPageChange={(page) => console.log('Page changed:', page)}
      />
    </div>
  );
}
```

### Advanced Multi-Mode Setup

```javascript
import React, { useState, useEffect } from 'react';
import { PDFViewer, NERViewer } from './components';

function MultiModeViewer() {
  const [viewMode, setViewMode] = useState('ner');
  const [searchResults, setSearchResults] = useState(null);
  const [currentDocument, setCurrentDocument] = useState('');
  const [currentPage, setCurrentPage] = useState(1);

  const documentData = {
    files: ['medical_report.pdf', 'lab_results.pdf'],
    presigned_urls: {
      'medical_report.pdf': {
        '1': 'https://cdn.example.com/medical-page1.png',
        '2': 'https://cdn.example.com/medical-page2.png',
      },
      'lab_results.pdf': {
        '1': 'https://cdn.example.com/lab-page1.png',
      }
    }
  };

  const nerData = [
    {
      filename: 'medical_report.pdf',
      data: {
        '1': [
          {
            word: 'John Doe',
            entity: 'John Doe',
            entity_type: 'PERSON',
            code: 'PATIENT_001',
            bbox: [0.15, 0.1, 0.35, 0.15],
            tags: ['patient', 'demographics']
          },
          {
            word: 'Type 2 Diabetes',
            entity: 'Diabetes Mellitus Type 2',
            entity_type: 'CONDITION',
            code: 'E11.9',
            bbox: [0.2, 0.4, 0.5, 0.45],
            tags: ['diagnosis', 'endocrine']
          }
        ],
        '2': [
          {
            word: 'Metformin',
            entity: 'Metformin Hydrochloride',
            entity_type: 'MEDICATION',
            code: 'RX001',
            bbox: [0.3, 0.3, 0.5, 0.35],
            tags: ['prescription', 'diabetes']
          }
        ]
      }
    },
    {
      filename: 'lab_results.pdf',
      data: {
        '1': [
          {
            word: 'Glucose',
            entity: 'Blood Glucose',
            entity_type: 'LAB_TEST',
            code: 'LAB_GLU',
            bbox: [0.1, 0.2, 0.25, 0.25],
            tags: ['laboratory', 'diabetes']
          }
        ]
      }
    }
  ];

  const boundingBoxes = {
    document_name: 'medical_report.pdf',
    page_number: '1',
    bbox: [[0.1, 0.6, 0.9, 0.6, 0.9, 0.8, 0.1, 0.8]],
    supporting_sentence_in_document: 'Key clinical findings'
  };

  const handleModeChange = (mode) => {
    setViewMode(mode);
    setCurrentPage(1);
    
    // Analytics
    analytics.track('viewer_mode_changed', {
      new_mode: mode,
      document: currentDocument
    });
  };

  const handleDocumentChange = (documentName) => {
    setCurrentDocument(documentName);
    setCurrentPage(1);
    
    // Load mode-specific data
    if (viewMode === 'ner') {
      loadNERDataForDocument(documentName);
    } else {
      loadAnnotationsForDocument(documentName);
    }
  };

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
    
    // Mode-specific page change handling
    if (viewMode === 'ner') {
      // Update entity counts, preload entity data
      updateNERPageData(pageNumber);
    } else {
      // Load annotations, preload adjacent pages
      updatePDFPageData(pageNumber);
    }
  };

  const handleSearchPerformed = async (searchQuery) => {
    try {
      const endpoint = viewMode === 'ner' ? 
        '/api/ner-search' : '/api/documents/search';
        
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          documents: documentData.files,
          mode: viewMode
        })
      });

      if (response.ok) {
        const results = await response.json();
        setSearchResults(results);
      }
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults(null);
    }
  };

  return (
    <div style={{ height: '100vh' }}>
      {/* Mode Toggle */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              onClick={() => handleModeChange('pdf')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                viewMode === 'pdf'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              PDF Viewer
            </button>
            <button
              onClick={() => handleModeChange('ner')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                viewMode === 'ner'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              NER Viewer
            </button>
          </div>
          
          <div className="text-sm text-gray-600">
            Current: {currentDocument || 'No document selected'} - Page {currentPage}
          </div>
        </div>
      </div>

      {/* Viewer Component */}
      {viewMode === 'ner' ? (
        <NERViewer
          documentData={documentData}
          nerData={nerData}
          userInterfaces={{
            docNavigation: true,
            zoom: true,
            download: true,
            keyboardShortcuts: true,
            showFilename: true,
          }}
          onDocumentChange={handleDocumentChange}
          onPageChange={handlePageChange}
          className="ner-viewer-container"
        />
      ) : (
        <PDFViewer
          documentData={documentData}
          boundingBoxes={boundingBoxes}
          searchResults={searchResults}
          userInterfaces={{
            docNavigation: true,
            zoom: true,
            download: true,
          }}
          onDocumentChange={handleDocumentChange}
          onPageChange={handlePageChange}
          onSearchPerformed={handleSearchPerformed}
          setSearchResults={setSearchResults}
          className="pdf-viewer-container"
        />
      )}
    </div>
  );
}
```

---

## API Integration

### NER API Example

```javascript
// Backend API endpoint for NER data
app.get('/api/ner-data/:documentName', async (req, res) => {
  const { documentName } = req.params;
  
  try {
    // Your NER service implementation
    const nerResults = await nerService.getEntitiesForDocument(documentName);
    
    // Format response to match NERData interface
    const formattedNERData = {
      filename: documentName,
      data: {}
    };
    
    // Group entities by page
    nerResults.entities.forEach(entity => {
      const pageNum = entity.page_number.toString();
      if (!formattedNERData.data[pageNum]) {
        formattedNERData.data[pageNum] = [];
      }
      
      formattedNERData.data[pageNum].push({
        word: entity.detected_word,
        entity: entity.full_entity_name,
        entity_type: entity.classification,
        code: entity.entity_code,
        bbox: entity.bounding_box,
        tags: entity.tags || []
      });
    });
    
    res.json([formattedNERData]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load NER data' });
  }
});

// NER Search API endpoint
app.post('/api/ner-search', async (req, res) => {
  const { query, documents, entity_types } = req.body;
  
  try {
    const searchResults = await nerService.searchEntities({
      query,
      documents,
      entity_types,
      include_context: true
    });
    
    const formattedResults = {
      results: searchResults.matches.map(match => ({
        document_name: match.document,
        page_number: match.page.toString(),
        text_snippet: match.context_snippet,
        match_score: match.confidence_score,
        bbox: [match.bounding_box],
        entity_info: {
          type: match.entity_type,
          code: match.entity_code,
          tags: match.tags
        }
      })),
      total_matches: searchResults.total_count,
      entity_type_breakdown: searchResults.type_counts
    };
    
    res.json(formattedResults);
  } catch (error) {
    res.status(500).json({ error: 'NER search failed' });
  }
});
```

### Entity Management API

```javascript
// Get unique entity types
app.get('/api/entity-types/:documentName', async (req, res) => {
  try {
    const entityTypes = await nerService.getUniqueEntityTypes(req.params.documentName);
    res.json(entityTypes);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load entity types' });
  }
});

// Get entities by tag
app.get('/api/entities/by-tag/:tag', async (req, res) => {
  const { tag } = req.params;
  const { document_name } = req.query;
  
  try {
    const entities = await nerService.getEntitiesByTag(tag, document_name);
    res.json(entities);
  } catch (error) {
    res.status(500).json({ error: 'Failed to load tagged entities' });
  }
});
```

---

## Keyboard Shortcuts

### PDFViewer Shortcuts
[Previous PDF shortcuts remain the same]

### NERViewer Shortcuts

The NER Viewer includes additional keyboard shortcuts:

| Shortcut | Action |
|----------|--------|
| `↑` / `↓` | Smooth scroll up/down |
| `Shift + ↑` / `Shift + ↓` | Page scroll |
| `Ctrl/Cmd + ↑` / `Ctrl/Cmd + ↓` | Jump to top/bottom |
| `Page Up` / `Page Down` | Navigate pages |
| `Home` / `End` | Jump to first/last page |
| `←` / `→` | Navigate pages |
| `Ctrl/Cmd + T` | Toggle tags sidebar |
| `Ctrl/Cmd + +` | Zoom in |
| `Ctrl/Cmd + -` | Zoom out |
| `Escape` | Close entity details popup |
| `Click` | View entity details |

---

## Versions & Tags

### Version Management

This project uses Git tags for version management. You can work with different versions using the following commands:

```bash
# Navigate to the PDF/NER viewer directory
cd src/lib/pdf-viewer

# List all available versions/tags
git tag

# Fetch latest tags from remote repository
git fetch --tags

# Switch to a specific version
git checkout V2.0.0

# Switch to latest version
git checkout $(git describe --tags --abbrev=0)

# Switch back to main development branch
git checkout main
```

### Available Versions

| Version | Release Date | Features | Status |
|---------|--------------|----------|---------|
| **V2.0.0** | Latest | NER Viewer, Entity highlighting, Tags sidebar, Entity details popup | ✅ Stable |
| **V1.0.0** | Previous | Advanced keyboard navigation, image preloading, smooth scrolling (PDF only) | ✅ Stable |

### Version Features

#### V2.0.0 (Latest) - NER Support
- ✅ **NERViewer Component**: Complete NER document viewing
- ✅ **Entity Highlighting**: Color-coded entity detection
- ✅ **Tags Sidebar**: Categorized entity browsing
- ✅ **Entity Details Popup**: Comprehensive entity information
- ✅ **Dynamic Colors**: Entity type color coordination
- ✅ **Keyboard Navigation**: Enhanced scrolling and navigation
- ✅ **Mobile Responsive**: Touch-friendly interface

#### V1.0.0 - PDF Foundation
- ✅ **PDFViewer Component**: Core PDF viewing functionality
- ✅ **Search Integration**: Full-text search with highlighting
- ✅ **Annotation Support**: Drawing and highlighting tools
- ✅ **Bounding Box Highlighting**: Custom region highlighting

### Compatibility Notes

- **V2.0.0+**: Compatible with React 16+, Material-UI 4+, Lucide React icons
- **V1.0.0+**: Compatible with React 16+ and Material-UI 4+

---

## Migration Guide

### Upgrading from V1.0.0 to V2.0.0

1. **Install new dependencies:**
```bash
npm install lucide-react
```

2. **Update imports:**
```javascript
// Old (V1.0.0)
import { PDFViewer } from './lib/pdf-viewer';

// New (V2.0.0)
import { PDFViewer, NERViewer } from './lib/pdf-viewer';
```

3. **Add NER data structure:**
```javascript
// New in V2.0.0
const nerData = [
  {
    filename: "document.pdf",
    data: {
      "1": [/* entities for page 1 */],
      "2": [/* entities for page 2 */]
    }
  }
];
```

4. **Use NER interfaces:**
```javascript
// New NER-specific user interfaces
const nerUserInterfaces = {
  docNavigation: true,
  zoom: true,
  download: true,
  keyboardShortcuts: true,  // New in V2.0.0
  showFilename: true,       // New in V2.0.0
};
```

---

This comprehensive documentation covers both PDF viewing and NER (Named Entity Recognition) functionality, providing everything you need to implement and customize both viewers in your applications!