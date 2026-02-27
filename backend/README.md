# Healthcare Claim Denial Appeal Management - Backend API

## Overview

The backend is a FastAPI-based REST API for managing healthcare claim denials and appeals. It provides endpoints for denial tracking, document management with AI-powered OCR, criteria evaluation using large language models, and automated appeal letter generation. The system integrates Azure Document Intelligence for OCR, Google Gemini for evidence extraction and appeal writing, MongoDB for persistence, and AWS S3 for document storage.

## Tech Stack

### Core Framework
- **FastAPI** 0.109.0 - Modern web framework for building APIs
- **Uvicorn** 0.27.0 - ASGI server
- **Pydantic** 2.5.3 - Data validation and settings management

### Database & Storage
- **Motor** 3.6.0 - Async MongoDB driver
- **PyMongo** 4.9.0 - MongoDB client (with AWS DocumentDB support)
- **boto3** 1.28+ - AWS S3 client

### AI & Document Processing
- **penguin-ai-sdk** - Unified SDK for AI operations
  - Azure Document Intelligence - OCR with bounding boxes
  - Google Gemini Flash - Fast relevancy scoring
  - Google Gemini Pro - Detailed extraction and appeal generation
- **Azure Form Recognizer** 3.3+ - OCR service
- **Google Generative AI** 0.8.0+ - LLM operations
- **PyPDF2** 3.0.0+ - PDF manipulation
- **ReportLab** 4.0.9 - PDF generation
- **pdf2image** 1.16+ - PDF to image conversion
- **Pillow** 10.0+ - Image processing

### Authentication & Security
- **python-jose** 3.3.0 - JWT token handling
- **passlib** 1.7.4 - Password hashing
- **bcrypt** 4.1.2 - Bcrypt hashing algorithm

### Utilities
- **python-multipart** 0.0.6 - File upload support
- **python-dotenv** 1.0.0 - Environment variable management
- **aiofiles** 23.2.1 - Async file operations
- **email-validator** 2.2.0 - Email validation
- **httpx** 0.25+ - HTTP client for external APIs

## Project Structure

```
backend/
├── app.py                    # FastAPI application entry point
├── config.py                 # Configuration and environment variables
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (not in repo)
│
├── models/                   # Pydantic data models
│   ├── user.py              # User, login schemas
│   ├── denial.py            # Denial, claim data models
│   ├── document.py          # Patient document models
│   ├── appeal.py            # Appeal package models
│   └── metrics.py           # Analytics metrics models
│
├── routes/                   # API endpoint handlers
│   ├── auth_routes.py       # Authentication (login, me)
│   ├── denial_routes.py     # Denial CRUD, CSV upload
│   ├── document_routes.py   # Document upload, retrieve, delete
│   ├── medical_policy_routes.py  # Payer policy lookup
│   ├── criteria_evaluation_routes.py  # AI criteria evaluation
│   ├── appeal_routes.py     # Appeal generation, package download
│   └── metrics_routes.py    # Analytics and KPIs
│
├── services/                 # Business logic services
│   └── ai_processor.py      # DocumentProcessor class (AI pipeline)
│
├── utils/                    # Utility modules
│   ├── db_utils.py          # MongoDB connection and collections
│   ├── s3_storage.py        # S3 upload/download utilities
│   └── pdf_merger.py        # PDF merging for appeal packages
│
├── auth.py                   # Authentication utilities
├── jwt_handler.py            # JWT token creation and validation
│
└── seed_comprehensive.py     # Database seeding script

```

## Architecture

### Layered Architecture

The backend follows a layered architecture pattern:

### Error Handling

**Current Approach:** Per-route HTTPException raising without global exception handlers

The application uses FastAPI's built-in HTTPException for error responses:

```python
from fastapi import HTTPException

# Common error patterns:
if not denial:
    raise HTTPException(status_code=404, detail="Denial not found")

if not ObjectId.is_valid(denial_id):
    raise HTTPException(status_code=400, detail="Invalid denial ID")

try:
    result = await some_operation()
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Operation failed: {str(e)}")
```

**Standard HTTP Status Codes Used:**
- **400 Bad Request** - Invalid input, malformed IDs, validation errors
- **401 Unauthorized** - Invalid credentials, missing/expired tokens
- **404 Not Found** - Resource doesn't exist
- **500 Internal Server Error** - Unexpected errors, AI processing failures

**Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Limitations (Future Enhancements):**
- ❌ No global exception handler for consistent error formatting
- ❌ No custom exception classes for domain-specific errors
- ❌ No error logging middleware
- ❌ No request ID tracking for error correlation
- ❌ No validation error customization (uses Pydantic defaults)

**Recommended Improvements:**

```python
# Add to app.py (not currently implemented)
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Layered Architecture (continued)

The backend follows a layered architecture pattern:

```
┌──────────────────────────────────────────────┐
│          API Layer (routes/)                 │
│  - Endpoint handlers                         │
│  - Request validation                        │
│  - Response formatting                       │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│       Service Layer (services/)              │
│  - Business logic                            │
│  - AI processing (DocumentProcessor)         │
│  - Orchestration                             │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│        Data Layer (utils/db_utils.py)        │
│  - MongoDB collections                       │
│  - CRUD operations                           │
│  - Query builders                            │
└──────────────┬───────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────┐
│      Storage Layer (utils/s3_storage.py)     │
│  - S3 document upload                        │
│  - Temporary file downloads                  │
│  - URL generation                            │
└──────────────────────────────────────────────┘
```

### Request Flow Example

```
Client Request (POST /denials)
       ↓
FastAPI Route Handler (denial_routes.py)
       ↓
Validate request body (Pydantic model)
       ↓
Insert into MongoDB (db_utils.denials_collection)
       ↓
Return response (denial_id)
```

### AI Processing Flow

```
Client Request (POST /criteria/evaluate/{denial_id})
       ↓
criteria_evaluation_routes.py
       ↓
DocumentProcessor.evaluate_criteria()
       ├─ Step 1: Filter documents by date range
       ├─ Step 2: OCR all documents (with caching)
       ├─ Step 3: Score document relevancy (Gemini Flash)
       ├─ Step 4: Shortlist top 3 documents
       ├─ Step 5: Extract evidence (Gemini Pro)
       └─ Step 6: Calculate win probability
       ↓
Save to criteria_evaluations collection
       ↓
Return evaluation results with bounding boxes
```

## Database Schema

### MongoDB Collections

| Collection | Purpose | Key Fields |
|-----------|---------|-----------|
| **users** | User authentication and profiles | email, hashed_password, role, created_at |
| **denials** | Healthcare claim denials | claim_number, service_date, amounts, payer_info, patient_info, status |
| **patient_documents** | Medical documents | s3_key, document_type, denial_id, upload_date, full_text |
| **criteria_evaluations** | AI evaluation results | denial_id, criteria[], win_probability, evaluated_at |
| **appeal_packages** | Generated appeals | denial_id, sections[], package_s3_key, created_at |
| **medical_policies** | Payer policies | payer_id, cpt_code, policy_requirements[], criteria[] |
| **ocr_cache** | OCR results cache | document_id, full_text, pages[], bboxes[] |
| **document_relevancy** | Relevancy scores | document_id, evaluation_id, relevancy_score, criteria_matches[] |
| **metrics_cache** | Analytics cache | metric_type, value, calculated_at, expires_at |

### Key Data Models

#### Denial Document

```python
{
  "_id": ObjectId("..."),
  "denial_id": "DN20240115001",
  "claim_number": "CLM123456789",
  "service_date": "2024-01-15",
  "received_date": "2024-02-01",
  "status": "Criteria Evaluated",

  # Financial
  "billed_amount": 2500.00,
  "allowed_amount": 0.00,
  "denied_amount": 2500.00,
  "paid_amount": 0.00,

  # Payer
  "payer_id": "CIGNA29881",
  "payer_name": "Cigna Healthcare",

  # Patient
  "patient_name": "John Smith",
  "patient_dob": "1965-03-15",
  "member_id": "CIG123456789",

  # Provider
  "rendering_npi": "1234567890",
  "rendering_provider_name": "Dr. Sarah Johnson",
  "specialty": "Cardiology",

  # Service
  "cpt_codes": ["93000", "99213"],
  "diagnosis_codes": ["I25.10", "E11.9"],
  "place_of_service": "11",

  # Denial
  "denial_code": "50",
  "denial_reason_description": "Non-covered service",

  # Metadata
  "created_by": "user@example.com",
  "created_at": ISODate("2024-01-15T10:00:00Z")
}
```

#### Patient Document

```python
{
  "_id": ObjectId("..."),
  "document_id": "DOC123",
  "denial_id": "DN20240115001",
  "document_type": "Medical Records",
  "file_name": "patient_chart.pdf",
  "s3_key": "denials/DN20240115001/DOC123_patient_chart.pdf",
  "s3_url": "https://s3.amazonaws.com/...",
  "file_size": 245678,
  "upload_date": ISODate("2024-01-15T11:00:00Z"),
  "full_text": "Patient presents with...",  # From OCR
  "page_count": 5
}
```

#### Criteria Evaluation

```python
{
  "_id": ObjectId("..."),
  "evaluation_id": "EVAL123",
  "denial_id": "DN20240115001",
  "criteria": [
    {
      "id": "medically_necessary",
      "question": "Is the service medically necessary?",
      "answer": "Supporting",  # or "Contradictory" or "Not Mentioned"
      "evidence": "Patient has documented diabetes mellitus type 2...",
      "supporting_documents": [
        {
          "document_id": "DOC123",
          "document_name": "patient_chart.pdf",
          "page_number": 2,
          "bboxes": [
            {
              "page": 2,
              "coordinates": [0.15, 0.30, 0.85, 0.30, 0.85, 0.40, 0.15, 0.40],
              "page_width": 8.5,
              "page_height": 11.0
            }
          ]
        }
      ],
      "explanation": "The medical records clearly document...",
      "confidence": 0.95
    }
  ],
  "win_probability": 0.78,
  "evaluated_at": ISODate("2024-01-15T12:00:00Z")
}
```

#### Appeal Package

```python
{
  "_id": ObjectId("..."),
  "appeal_package_id": "PKG123",
  "denial_id": "DN20240115001",
  "sections": [
    {
      "title": "Claim Information",
      "content": "Claim Number: CLM123456789..."
    },
    {
      "title": "Appeal Argument",
      "content": "The service provided was medically necessary..."
    }
  ],
  "letter_text": "Full letter text...",
  "package_s3_key": "appeals/PKG123/appeal_package.pdf",
  "package_s3_url": "https://s3.amazonaws.com/...",
  "created_at": ISODate("2024-01-15T13:00:00Z")
}
```

### Database Relationships

```
┌──────────┐
│  users   │
└────┬─────┘
     │ created_by
     ▼
┌──────────┐       ┌────────────────────┐
│ denials  │──────▶│ patient_documents  │
└────┬─────┘       └────────────────────┘
     │
     │
     ├──────────▶┌──────────────────────────┐
     │           │ criteria_evaluations     │
     │           └──────────────────────────┘
     │
     └──────────▶┌──────────────────────────┐
                 │ appeal_packages          │
                 └──────────────────────────┘

┌────────────────────┐       ┌──────────────────┐
│ patient_documents  │──────▶│   ocr_cache      │
└────────────────────┘       └──────────────────┘
```

## API Endpoints

### Authentication

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/auth/login` | User login | `{ email, password }` | `{ access_token, user }` |
| GET | `/auth/me` | Get current user | - | `{ email, role }` |

**Example:**
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@penguinai.com", "password": "demo123"}'

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "email": "demo@penguinai.com",
    "role": "admin"
  }
}
```

### Denials Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/denials` | List all denials with filters | Yes |
| GET | `/denials/{denial_id}` | Get denial by ID | Yes |
| POST | `/denials` | Create new denial | Yes |
| PUT | `/denials/{denial_id}` | Update denial | Yes |
| POST | `/denials/upload-csv` | Bulk upload denials | Yes |

**Query Parameters for GET /denials:**
- `status` - Filter by status
- `payer_id` - Filter by payer
- `search` - Search in claim number, patient name
- `date_from` - Service date start
- `date_to` - Service date end

**Example:**
```bash
# Create denial
curl -X POST http://localhost:8000/denials \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_number": "CLM123456",
    "service_date": "2024-01-15",
    "payer_id": "CIGNA29881",
    "patient_name": "John Smith",
    "denied_amount": 2500.00
  }'

# Response
{
  "denial_id": "DN20240115001",
  "message": "Denial created successfully"
}
```

### Document Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/documents/upload` | Upload document and trigger OCR |
| GET | `/documents/denial/{denial_id}` | Get all documents for a denial |
| GET | `/documents/{document_id}` | Get document metadata |
| DELETE | `/documents/{document_id}` | Delete document |

**Example:**
```bash
# Upload document
curl -X POST http://localhost:8000/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@medical_records.pdf" \
  -F "denial_id=DN20240115001" \
  -F "document_type=Medical Records"

# Response
{
  "document_id": "DOC123",
  "s3_url": "https://s3.amazonaws.com/.../medical_records.pdf",
  "ocr_status": "completed"
}
```

### Medical Policies

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/medical-policies` | List all policies |
| GET | `/medical-policies/lookup` | Lookup policy by payer and CPT |

**Example:**
```bash
# Lookup policy
curl -X GET "http://localhost:8000/medical-policies/lookup?payer_id=CIGNA29881&cpt_code=99213" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "payer_id": "CIGNA29881",
  "payer_name": "Cigna Healthcare",
  "cpt_code": "99213",
  "policy_requirements": ["Medical necessity documentation required"],
  "criteria": [
    {
      "id": "medically_necessary",
      "question": "Is the service medically necessary?",
      "required": true
    }
  ]
}
```

### Criteria Evaluation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/criteria/evaluate/{denial_id}` | Evaluate denial using AI |
| GET | `/criteria/evaluation/{denial_id}` | Get existing evaluation |

**Example:**
```bash
# Trigger evaluation
curl -X POST http://localhost:8000/criteria/evaluate/DN20240115001 \
  -H "Authorization: Bearer $TOKEN"

# Response (after AI processing)
{
  "evaluation_id": "EVAL123",
  "denial_id": "DN20240115001",
  "criteria": [
    {
      "id": "medically_necessary",
      "question": "Is the service medically necessary?",
      "answer": "Supporting",
      "evidence": "Patient has documented diabetes...",
      "supporting_documents": [...],
      "confidence": 0.95
    }
  ],
  "win_probability": 0.78
}
```

### Appeal Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/appeals/generate/{denial_id}` | Generate appeal letter and package |
| GET | `/appeals/denial/{denial_id}` | Get appeal for denial |
| GET | `/appeals/{appeal_id}/download` | Download complete PDF package |

**Example:**
```bash
# Generate appeal
curl -X POST http://localhost:8000/appeals/generate/DN20240115001 \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "appeal_package_id": "PKG123",
  "letter_text": "Dear Claims Reviewer...",
  "package_s3_url": "https://s3.amazonaws.com/.../appeal_package.pdf"
}
```

### Metrics & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/metrics/overview` | Get KPI overview |
| GET | `/metrics/trends` | Get trend data for charts |
| GET | `/metrics/payers` | Get payer statistics |

**Example:**
```bash
# Get overview
curl -X GET http://localhost:8000/metrics/overview \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "total_denials": 145,
  "pending_review": 32,
  "average_denied_amount": 1875.50,
  "win_rate": 0.68,
  "active_appeals": 18
}
```

## Core Services

### DocumentProcessor (ai_processor.py)

**Purpose:** Singleton service for AI-powered document processing and criteria evaluation

**Architecture Pattern:** Singleton (initialized once, reused across requests)

#### Initialization

```python
from services.ai_processor import DocumentProcessor

processor = DocumentProcessor()
# Initialized once with:
# - Azure OCR provider
# - Gemini Flash for relevancy scoring
# - Gemini Pro for detailed extraction
```

#### Key Methods

##### 1. process_document_with_cache()

**Purpose:** OCR document with MongoDB caching

```python
async def process_document_with_cache(
    s3_key: str,
    document_id: str
) -> Dict[str, Any]
```

**Flow:**
1. Check `ocr_cache` collection for existing results
2. If cached, return immediately
3. If not cached:
   - Download PDF from S3 to temp file
   - Run Azure OCR
   - Parse pages and bounding boxes
   - Save to cache
   - Return results

**Returns:**
```python
{
  "full_text": "Complete document text...",
  "pages": [
    {
      "page_number": 1,
      "text": "Page 1 text...",
      "bboxes": [
        {
          "text": "diabetes mellitus",
          "coordinates": [0.15, 0.30, 0.85, 0.30, 0.85, 0.40, 0.15, 0.40],
          "page": 1
        }
      ]
    }
  ]
}
```

##### 2. score_document_relevancy()

**Purpose:** Fast relevancy scoring using Gemini Flash

```python
async def score_document_relevancy(
    document_text: str,
    document_id: str,
    document_name: str,
    criteria: List[Dict],
    denial_info: Dict
) -> DocumentRelevancy
```

**Prompt Structure:**
- System: Document scoring expert
- User: Denial details + criteria list + document excerpt
- Asks: Which criteria does this document address?

**Returns:**
```python
{
  "document_id": "DOC123",
  "relevancy_score": 3,  # Number of criteria addressed
  "criteria_matches": [
    {
      "criterion_id": "medically_necessary",
      "relevant": true,
      "confidence": 0.9
    }
  ]
}
```

##### 3. extract_evidence_from_document()

**Purpose:** Detailed evidence extraction with bounding boxes

```python
async def extract_evidence_from_document(
    document_text: str,
    document_id: str,
    document_name: str,
    document_bboxes: List[Dict],
    criteria: List[Dict],
    denial_info: Dict
) -> List[Evidence]
```

**Process:**
1. Send full document text + bounding boxes to Gemini Pro
2. Ask for specific evidence for each criterion
3. Map extracted text to bounding boxes
4. Return evidence with page numbers and coordinates

**Returns:**
```python
[
  {
    "document_id": "DOC123",
    "criterion_id": "medically_necessary",
    "met": true,
    "evidence_text": "Patient has documented diabetes...",
    "page_number": 2,
    "bbox": [0.15, 0.30, 0.85, 0.30, 0.85, 0.40, 0.15, 0.40],
    "explanation": "This text supports medical necessity",
    "confidence": 0.95
  }
]
```

##### 4. evaluate_criteria()

**Purpose:** Complete 6-step evaluation pipeline

```python
async def evaluate_criteria(
    denial_id: str,
    denial_data: Dict,
    documents: List[Dict],
    criteria: List[Dict]
) -> Dict
```

**6-Step Pipeline:**

**Step 1: Filter Documents by Date**
- Include docs from `service_date - 90 days` to `received_date`
- Exclude irrelevant historical documents

**Step 2: OCR All Documents**
- Call `process_document_with_cache()` for each
- Parallel processing with asyncio
- Results cached in MongoDB

**Step 3: Score Document Relevancy**
- Call `score_document_relevancy()` for each document
- Use Gemini Flash (fast, cheap)
- Save scores to `document_relevancy` collection

**Step 4: Shortlist Top 3 Documents**
- Sort by relevancy_score descending
- Take top 3 most relevant documents
- Reduces LLM costs for detailed extraction

**Step 5: Extract Evidence**
- Call `extract_evidence_from_document()` for shortlisted docs
- Use Gemini Pro (accurate, detailed)
- Map evidence to bounding boxes

**Step 6: Calculate Win Probability**
- Count supporting criteria
- Count contradictory criteria
- Formula: `supporting / (supporting + contradictory)`

**Returns:**
```python
{
  "evaluation_id": "EVAL123",
  "denial_id": "DN20240115001",
  "criteria": [
    {
      "id": "medically_necessary",
      "question": "Is the service medically necessary?",
      "answer": "Supporting",
      "evidence": "Patient has documented diabetes...",
      "supporting_documents": [
        {
          "document_id": "DOC123",
          "document_name": "patient_chart.pdf",
          "page_number": 2,
          "bboxes": [...]
        }
      ],
      "confidence": 0.95
    }
  ],
  "win_probability": 0.78,
  "documents_processed": 5,
  "documents_shortlisted": 3
}
```

##### 5. generate_appeal_letter()

**Purpose:** Create professional appeal letter using AI

```python
async def generate_appeal_letter(
    denial_data: Dict,
    criteria_evaluation: Dict
) -> Dict
```

**Prompt Structure:**
- System: Medical appeal letter writing expert
- Context: Denial details, patient info, criteria results
- Task: Write professional, persuasive appeal
- Format: Structured sections with evidence citations

**Generated Sections:**
1. Header with provider letterhead
2. Claim Information summary
3. Patient Details
4. Service Description
5. Denial Reason
6. Appeal Argument (AI-generated based on criteria)
7. Supporting Evidence with document citations
8. Closing and Signature

**Returns:**
```python
{
  "appeal_package_id": "PKG123",
  "sections": [
    {
      "title": "Claim Information",
      "content": "Claim Number: CLM123456..."
    }
  ],
  "letter_text": "Full formatted letter..."
}
```

### S3 Storage Utilities (s3_storage.py)

**Functions:**

```python
def upload_to_s3(file_path: str, s3_key: str) -> str
    """Upload file to S3, return S3 URL"""

def download_to_temp_file(s3_key: str) -> str
    """Download S3 file to temp location, return local path"""

def generate_s3_url(s3_key: str) -> str
    """Generate public S3 URL"""

def delete_from_s3(s3_key: str) -> bool
    """Delete file from S3"""
```

### PDF Merger (pdf_merger.py)

**Purpose:** Merge appeal letter + supporting documents into single PDF package

```python
def merge_appeal_package(
    letter_pdf_path: str,
    document_paths: List[str],
    output_path: str
) -> str
```

**Process:**
1. Generate letter PDF from text using ReportLab
2. Append supporting document PDFs
3. Add page numbers
4. Create table of contents
5. Save merged PDF
6. Upload to S3

## Data Flow Diagrams

### Document Upload + OCR Flow

```
POST /documents/upload
  │
  ├─ Receive multipart/form-data
  │   - file (PDF/image)
  │   - denial_id
  │   - document_type
  │
  ▼
Generate document_id and s3_key
  │
  ▼
Upload file to S3
  s3://appeals-pgn-dev/denials/{denial_id}/{document_id}_{filename}
  │
  ▼
Check ocr_cache for existing OCR results
  │
  ├─ If cached ──────────────────┐
  │                              │
  ├─ If not cached               │
  │   ├─ Download to temp file   │
  │   ├─ Run Azure OCR           │
  │   ├─ Parse bounding boxes    │
  │   └─ Save to ocr_cache       │
  │                              │
  ▼                              ▼
Extract full_text and page_count
  │
  ▼
Save document to patient_documents collection
  - document_id
  - s3_key, s3_url
  - full_text (from OCR)
  - page_count
  - denial_id
  │
  ▼
Return response
  {
    "document_id": "DOC123",
    "s3_url": "https://...",
    "ocr_status": "completed"
  }
```

### Criteria Evaluation Pipeline (6 Steps)

```
POST /criteria/evaluate/{denial_id}
  │
  ▼
Fetch denial details from MongoDB
  │
  ▼
Fetch payer policy criteria
  │
  ▼
Fetch all documents for denial
  │
  ▼
┌─────────────────────────────────────────────┐
│ Step 1: Filter Documents by Date Range      │
│   service_date - 90 days to received_date   │
│   Result: 5 documents → 3 documents         │
└──────────────┬──────────────────────────────┘
               ▼
┌─────────────────────────────────────────────┐
│ Step 2: OCR All Documents (Parallel)        │
│   For each document:                        │
│     - Check ocr_cache                       │
│     - If miss: Azure OCR                    │
│     - Cache result                          │
│   Result: Full text + bboxes for 3 docs    │
└──────────────┬──────────────────────────────┘
               ▼
┌─────────────────────────────────────────────┐
│ Step 3: Score Document Relevancy            │
│   For each document:                        │
│     - Send text + criteria to Gemini Flash  │
│     - Get relevancy score                   │
│   Save to document_relevancy collection     │
│   Result: Doc1=3, Doc2=5, Doc3=1 criteria   │
└──────────────┬──────────────────────────────┘
               ▼
┌─────────────────────────────────────────────┐
│ Step 4: Shortlist Top 3 Documents           │
│   Sort by relevancy_score DESC              │
│   Take top 3                                │
│   Result: [Doc2, Doc1, Doc3]                │
└──────────────┬──────────────────────────────┘
               ▼
┌─────────────────────────────────────────────┐
│ Step 5: Extract Evidence (Detailed)         │
│   For each shortlisted document:            │
│     - Send full text to Gemini Pro          │
│     - Extract evidence for each criterion   │
│     - Map to bounding boxes                 │
│   Result: Evidence with page numbers        │
└──────────────┬──────────────────────────────┘
               ▼
┌─────────────────────────────────────────────┐
│ Step 6: Calculate Win Probability           │
│   Count: Supporting = 4, Contradictory = 1  │
│   Formula: 4 / (4 + 1) = 0.80               │
│   Result: 80% win probability               │
└──────────────┬──────────────────────────────┘
               ▼
Save to criteria_evaluations collection
  │
  ▼
Return evaluation results
```

### Appeal Generation Pipeline

```
POST /appeals/generate/{denial_id}
  │
  ▼
Check if criteria evaluation exists
  │
  ├─ If not exists ────▶ Return error "Evaluate criteria first"
  │
  ▼
Fetch denial details
  │
  ▼
Fetch criteria evaluation
  │
  ▼
Call DocumentProcessor.generate_appeal_letter()
  │
  ├─ Construct prompt with:
  │   - Denial information
  │   - Patient details
  │   - Supporting criteria
  │   - Evidence excerpts
  │
  ├─ Send to Gemini Pro
  │
  ├─ Parse structured response
  │   - Header section
  │   - Claim info
  │   - Appeal argument
  │   - Evidence citations
  │   - Closing
  │
  ▼
Generate PDF using ReportLab
  │
  ├─ Format letter sections
  ├─ Add professional styling
  ├─ Include provider letterhead
  │
  ▼
Fetch supporting documents PDFs from S3
  │
  ▼
Merge PDFs using pdf_merger.py
  │
  ├─ Letter (first)
  ├─ Medical Records
  ├─ Lab Results
  ├─ Imaging Reports
  │
  ▼
Upload merged package to S3
  s3://appeals-pgn-dev/appeals/{package_id}/appeal_package.pdf
  │
  ▼
Save to appeal_packages collection
  - appeal_package_id
  - denial_id
  - sections[]
  - letter_text
  - package_s3_key
  - package_s3_url
  │
  ▼
Return response
  {
    "appeal_package_id": "PKG123",
    "letter_text": "Dear Claims Reviewer...",
    "package_s3_url": "https://s3.amazonaws.com/.../appeal_package.pdf"
  }
```

### Package Download Flow

```
GET /appeals/{appeal_id}/download
  │
  ▼
Fetch appeal package from MongoDB
  │
  ▼
Get package_s3_key
  │
  ▼
Generate pre-signed S3 URL (expires in 1 hour)
  │
  ▼
Redirect to S3 URL
  │
  ▼
Browser downloads PDF
```

## Critical Workflows

### 1. Denial Lifecycle

```
Created (Initial State)
  │
  ├─ User uploads documents
  │
  ▼
Documents Uploaded
  │
  ├─ System runs OCR (cached)
  │ ├─ User triggers criteria evaluation
  │
  ▼
Criteria Evaluated
  │
  ├─ Win probability calculated
  │ ├─ User reviews criteria
  │ ├─ User generates appeal
  │
  ▼
Appeal Generated
  │
  ├─ User downloads package
  │ ├─ User submits to payer
  │
  ▼
Appeal Submitted (Terminal State)
```

**Status Field Values:**
- `Pending Review` - Just created
- `Documents Uploaded` - At least 1 document attached
- `Criteria Evaluated` - AI evaluation completed
- `Appeal Generated` - Letter created
- `Appeal Submitted` - Sent to payer

### 2. Document Processing Workflow

**Upload Phase:**
1. Frontend sends multipart form data
2. Backend validates file type (PDF, JPG, PNG)
3. Generate unique document_id
4. Upload to S3 with key: `denials/{denial_id}/{document_id}_{filename}`
5. Trigger OCR processing

**OCR Phase (with Caching):**
1. Check `ocr_cache` collection by document_id
2. If cached:
   - Return cached `full_text` and `bboxes`
3. If not cached:
   - Download from S3 to temp file
   - Send to Azure Document Intelligence
   - Parse response:
     - Extract full text
     - Parse pages
     - Convert bounding boxes from 4-point (inches) to 8-point normalized
   - Save to `ocr_cache` collection
   - Delete temp file

**Storage Phase:**
1. Save document to `patient_documents` collection with:
   - `document_id`, `denial_id`, `s3_key`
   - `full_text` (from OCR)
   - `page_count`
   - `document_type`, `file_name`, `file_size`
2. Update denial status to "Documents Uploaded"

**Bounding Box Format Conversion:**

Azure returns 4-point format (inches):
```python
# Azure OCR output
{
  "boundingBox": [1.2, 2.3, 4.5, 2.3, 4.5, 2.8, 1.2, 2.8],  # inches
  "page": 1,
  "pageWidth": 8.5,
  "pageHeight": 11.0
}
```

Stored as 8-point normalized (0-1 range):
```python
# MongoDB storage
{
  "coordinates": [0.141, 0.209, 0.529, 0.209, 0.529, 0.255, 0.141, 0.255],  # 0-1
  "page": 1,
  "page_width": 8.5,
  "page_height": 11.0
}

# Formula: normalized = inches / page_dimension
# x = 1.2 / 8.5 = 0.141
# y = 2.3 / 11.0 = 0.209
```

### 3. Criteria Evaluation (Complete 6-Step Flow)

**Prerequisites:**
- Denial must exist
- At least 1 document uploaded
- Payer policy criteria defined

**Step-by-Step Process:**

**Step 1: Filter Documents by Date (90-day window)**
```python
service_date = denial["service_date"]  # 2024-01-15
received_date = denial["received_date"]  # 2024-02-01

start_date = service_date - timedelta(days=90)  # 2023-10-17
end_date = received_date  # 2024-02-01

filtered_docs = [
    doc for doc in documents
    if start_date <= doc["upload_date"] <= end_date
]
```

**Step 2: OCR All Documents (Parallel with Caching)**
```python
tasks = [
    processor.process_document_with_cache(doc["s3_key"], doc["document_id"])
    for doc in filtered_docs
]
ocr_results = await asyncio.gather(*tasks)

# Each result:
{
  "full_text": "Patient presents with diabetes...",
  "pages": [
    {
      "page_number": 1,
      "text": "Page 1 text...",
      "bboxes": [...]
    }
  ]
}
```

**Step 3: Score Relevancy (Gemini Flash)**
```python
for doc in filtered_docs:
    relevancy = await processor.score_document_relevancy(
        document_text=ocr_results[doc["document_id"]]["full_text"],
        document_id=doc["document_id"],
        criteria=policy_criteria,
        denial_info=denial_data
    )
    # Save to document_relevancy collection

# Result:
{
  "document_id": "DOC123",
  "relevancy_score": 5,  # Addresses 5 criteria
  "criteria_matches": [
    {"criterion_id": "medically_necessary", "relevant": true, "confidence": 0.9},
    {"criterion_id": "proper_coding", "relevant": true, "confidence": 0.85}
  ]
}
```

**Step 4: Shortlist Top 3**
```python
sorted_docs = sorted(
    documents_with_relevancy,
    key=lambda x: x["relevancy_score"],
    reverse=True
)
shortlisted = sorted_docs[:3]
```

**Step 5: Extract Evidence (Gemini Pro)**
```python
all_evidence = []
for doc in shortlisted:
    evidence_list = await processor.extract_evidence_from_document(
        document_text=doc["full_text"],
        document_bboxes=doc["bboxes"],
        criteria=policy_criteria,
        denial_info=denial_data
    )
    all_evidence.extend(evidence_list)

# Each evidence item:
{
  "document_id": "DOC123",
  "criterion_id": "medically_necessary",
  "met": true,
  "evidence_text": "Patient has documented diabetes mellitus type 2 with HbA1c of 8.5%",
  "page_number": 2,
  "bbox": [0.15, 0.30, 0.85, 0.30, 0.85, 0.40, 0.15, 0.40],
  "explanation": "This lab result confirms the diagnosis",
  "confidence": 0.95
}
```

**Step 6: Calculate Win Probability**
```python
supporting_count = sum(1 for e in all_evidence if e["met"] == True)
contradictory_count = sum(1 for e in all_evidence if e["met"] == False)

if supporting_count + contradictory_count == 0:
    win_probability = 0.0
else:
    win_probability = supporting_count / (supporting_count + contradictory_count)

# Example: 4 supporting, 1 contradictory
# win_probability = 4 / 5 = 0.80
```

**Final Evaluation Saved:**
```python
evaluation = {
    "evaluation_id": generate_id(),
    "denial_id": denial_id,
    "criteria": [
        {
            "id": criterion["id"],
            "question": criterion["question"],
            "answer": "Supporting" if has_supporting_evidence else "Contradictory",
            "evidence": evidence_text,
            "supporting_documents": [
                {
                    "document_id": evidence["document_id"],
                    "page_number": evidence["page_number"],
                    "bboxes": [evidence["bbox"]]
                }
            ],
            "confidence": evidence["confidence"]
        }
        for criterion in policy_criteria
    ],
    "win_probability": win_probability,
    "evaluated_at": datetime.now()
}
await criteria_evaluations_collection.insert_one(evaluation)
```

### 4. Appeal Generation Workflow

**Prerequisites Check:**
```python
# Must have criteria evaluation
evaluation = await criteria_evaluations_collection.find_one({"denial_id": denial_id})
if not evaluation:
    raise HTTPException(status_code=400, detail="Must evaluate criteria first")
```

**Letter Generation:**
```python
# Construct comprehensive prompt
prompt = f"""
You are a medical appeal letter writing expert. Write a professional appeal letter for:

Claim Number: {denial["claim_number"]}
Patient: {denial["patient_name"]}
Service Date: {denial["service_date"]}
Denied Amount: ${denial["denied_amount"]}
Denial Reason: {denial["denial_reason_description"]}

Supporting Criteria:
{format_supporting_criteria(evaluation["criteria"])}

Requirements:
- Professional medical language
- Cite specific evidence from medical records
- Reference page numbers
- Persuasive but factual
- Follow standard appeal letter format
"""

letter_text = await processor.gemini_pro.generate(prompt)
```

**Package Assembly:**
1. Generate letter PDF with ReportLab
2. Fetch supporting documents from S3
3. Merge PDFs in order:
   - Cover letter
   - Medical records
   - Lab results
   - Imaging reports
4. Upload merged PDF to S3
5. Save appeal_package record

**Example Generated Letter Structure:**
```
[Provider Letterhead]

Date: [Current Date]

To: Claims Review Department
[Payer Name]
[Payer Address]

Re: Appeal for Claim #CLM123456789
Patient: John Smith, DOB: 03/15/1965
Member ID: CIG123456789
Service Date: 01/15/2024

Dear Claims Reviewer,

I am writing to appeal the denial of claim #CLM123456789 for [service description].

CLAIM INFORMATION:
[Detailed claim summary]

DENIAL REASON:
The claim was denied with reason code 50: "Non-covered service"

APPEAL ARGUMENT:
We respectfully disagree with this denial for the following reasons:

1. Medical Necessity: The service provided was medically necessary as evidenced by the patient's documented diabetes mellitus type 2 with HbA1c of 8.5% (See Medical Records, Page 2). This condition requires the specific testing that was performed.

2. Proper Documentation: All required documentation was submitted at the time of service, including prior authorization approval #PA123456 (See Prior Authorization, Page 1).

[Additional evidence points with page citations]

CONCLUSION:
Based on the comprehensive medical evidence provided, we request reconsideration of this denial and payment of the billed amount of $2,500.00.

Supporting documents are enclosed for your review.

Sincerely,

Dr. Sarah Johnson, MD
Rendering Provider
NPI: 1234567890
```

### 5. Package Download

**Flow:**
1. User clicks "Download Package" button in frontend
2. GET /appeals/{appeal_id}/download
3. Backend fetches appeal package record
4. Generates pre-signed S3 URL (expires in 1 hour)
5. Returns redirect response
6. Browser downloads PDF from S3

## AI Integration

### Provider Summary

| Capability | Provider | Model | Purpose |
|------------|----------|-------|---------|
| **OCR** | Azure Document Intelligence | prebuilt-read | Text extraction with bounding boxes |
| **Relevancy Scoring** | Google Gemini | gemini-3-flash-preview | Fast document relevancy assessment |
| **Evidence Extraction** | Google Gemini | gemini-3-flash-preview | Detailed evidence extraction with citations |
| **Appeal Writing** | Google Gemini | gemini-3-flash-preview | Professional letter generation |

### Azure OCR Integration

**Endpoint:** Azure Document Intelligence prebuilt-read model

**Process:**
1. Upload PDF to Azure
2. Poll for completion
3. Parse JSON response
4. Extract pages, lines, words, bounding boxes

**Response Format:**
```json
{
  "pages": [
    {
      "pageNumber": 1,
      "width": 8.5,
      "height": 11.0,
      "lines": [
        {
          "content": "Patient has diabetes mellitus",
          "boundingBox": [1.2, 2.3, 4.5, 2.3, 4.5, 2.8, 1.2, 2.8]
        }
      ]
    }
  ]
}
```

**Bounding Box Conversion:**
- Input: 4-point polygon in inches `[x1, y1, x2, y2, x3, y3, x4, y4]`
- Output: 8-point normalized `[x1/width, y1/height, ...]`
- Normalized to 0-1 range for frontend rendering

### Gemini Integration

**Models Used:**
- **gemini-3-flash-preview** - All LLM operations (fast, cost-effective)

**API Configuration:**
```python
from penguin.llm import create_client

client = create_client("gemini", model="gemini-3-flash-preview")
```

**Common Prompt Pattern:**
```python
response = await client.generate([
    SystemMessage(content="You are a medical expert..."),
    UserMessage(content=f"Analyze this document: {full_text}")
])
```

**Usage Patterns:**

**1. Relevancy Scoring (Fast Pass Filter):**
```python
prompt = f"""
Denial: {denial_info}
Criteria: {criteria_list}
Document: {document_text[:5000]}  # Excerpt for speed

Which criteria does this document address? Return JSON.
"""
# Response: {"criteria_matches": [...]}
```

**2. Evidence Extraction (Detailed):**
```python
prompt = f"""
Full Document: {full_text}  # Complete text
Criteria: {criterion}

Extract evidence that supports or contradicts this criterion.
Include exact quotes and page references.
"""
# Response: Structured evidence with citations
```

**3. Appeal Letter Generation:**
```python
prompt = f"""
Write a professional medical appeal letter.

Claim: {claim_info}
Supporting Evidence: {criteria_evidence}
Denial Reason: {denial_reason}

Format: Professional business letter with citations.
"""
# Response: Complete formatted letter
```

### Bounding Box Workflow

**From OCR to Frontend:**

1. **Azure OCR Output** (inches, 4-point):
```python
{
  "content": "diabetes mellitus",
  "boundingBox": [1.2, 2.3, 4.5, 2.3, 4.5, 2.8, 1.2, 2.8],
  "page": 1,
  "pageWidth": 8.5,
  "pageHeight": 11.0
}
```

2. **Stored in MongoDB** (normalized, 8-point):
```python
{
  "text": "diabetes mellitus",
  "coordinates": [0.141, 0.209, 0.529, 0.209, 0.529, 0.255, 0.141, 0.255],
  "page": 1,
  "page_width": 8.5,
  "page_height": 11.0
}
```

3. **Sent to Frontend** (same normalized format):
```javascript
{
  "text": "diabetes mellitus",
  "bboxes": [
    {
      "page": 1,
      "coordinates": [0.141, 0.209, 0.529, 0.209, 0.529, 0.255, 0.141, 0.255],
      "page_width": 8.5,
      "page_height": 11.0
    }
  ]
}
```

4. **Frontend Rendering:**
```javascript
// PDFViewer converts normalized coords to pixel coordinates
const pixelX = normalizedX * canvasWidth;
const pixelY = normalizedY * canvasHeight;

// Draw bounding box overlay
ctx.strokeRect(pixelX1, pixelY1, pixelX2 - pixelX1, pixelY2 - pixelY1);
```

## Configuration

### Environment Variables

Create a `.env` file in the backend root:

```bash
# Database
MONGODB_URL=mongodb://localhost:27017/
DATABASE_NAME=claim_appeals

# Authentication
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours

# Azure OCR
AZURE_OCR_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OCR_SECRET_KEY=your-azure-ocr-key

# AWS S3
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET=appeals-pgn-dev

# Google Gemini
GEMINI_API_KEY=your-gemini-api-key

# Application
ROOT_PATH=/appeals-dev  # For reverse proxy (empty for local)
LOG_LEVEL=INFO
```

### MongoDB Setup

**Local Development:**
```bash
# Install MongoDB
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community

# Connect
mongosh mongodb://localhost:27017/
```

**AWS DocumentDB (Production):**
```bash
# Connection string with TLS
MONGODB_URL=mongodb://username:password@cluster.docdb.amazonaws.com:27017/?tls=true&tlsCAFile=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false
```

### S3 Setup

**Bucket Configuration:**
- Bucket name: `appeals-pgn-dev` (or your custom bucket)
- Region: `us-east-1` (or match your region)
- Public access: Blocked (use pre-signed URLs)
- CORS: Enabled for frontend domain

**CORS Configuration:**
```json
[
  {
    "AllowedOrigins": ["https://dev-appeals.penguinai.co", "http://localhost:5173"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedHeaders": ["*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

**Folder Structure:**
```
appeals-pgn-dev/
├── denials/
│   └── {denial_id}/
│       ├── {document_id}_filename.pdf
│       └── ...
└── appeals/
    └── {appeal_package_id}/
        └── appeal_package.pdf
```

### AI Provider Setup

**Azure Document Intelligence:**
1. Create Azure resource in portal
2. Get endpoint and API key
3. Add to .env

**Google Gemini:**
1. Get API key from https://makersuite.google.com/app/apikey
2. Add to .env as GEMINI_API_KEY

## Getting Started

### Prerequisites

- **Python** 3.9 or higher
- **MongoDB** (local or DocumentDB)
- **AWS Account** with S3 access
- **Azure Account** with Document Intelligence resource
- **Google AI API Key** for Gemini

### Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Seeding

```bash
# Seed comprehensive sample data
python seed_comprehensive.py

# This creates:
# - Demo user (demo@penguinai.com / demo123)
# - 10 sample denials with varied statuses
# - Medical policies for common payers
# - Sample documents with OCR cache
# - Sample criteria evaluations
```

### Running Locally

```bash
# Start FastAPI server with auto-reload
uvicorn app:app --reload --port 8000

# Server starts on http://localhost:8000

# API documentation available at:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Running with Reverse Proxy

```bash
# Set ROOT_PATH for reverse proxy
export ROOT_PATH=/appeals-dev

# Start server
uvicorn app:app --host 0.0.0.0 --port 8000

# API accessible at:
# https://dev-api.penguinai.co/appeals-dev/docs
```

### Verifying Setup

```bash
# Test health endpoint
curl http://localhost:8000/

# Test login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@penguinai.com", "password": "demo123"}'

# Expected response:
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "email": "demo@penguinai.com",
    "role": "admin"
  }
}
```

## Default Credentials

After running seed script:

```
Email: demo@penguinai.com
Password: demo123
Role: admin
```

## Development Utilities

### Useful Scripts

**Check Database:**
```bash
python diagnose_db.py
# Shows collection counts and sample documents
```

**Test E2E Flow:**
```bash
python test_e2e_flow.py
# Tests complete denial → documents → criteria → appeal flow
```

### MongoDB Queries

**View denials:**
```javascript
db.denials.find().pretty()
```

**View OCR cache:**
```javascript
db.ocr_cache.find({}, {full_text: 0}).pretty()
```

**Check criteria evaluations:**
```javascript
db.criteria_evaluations.find().pretty()
```

**View appeal packages:**
```javascript
db.appeal_packages.find({}, {letter_text: 0}).pretty()
```

## Troubleshooting

### Common Issues

**Issue:** MongoDB connection refused
- **Solution:** Verify MongoDB is running: `brew services list`
- Start MongoDB: `brew services start mongodb-community`

**Issue:** Azure OCR fails with 401 Unauthorized
- **Solution:** Check AZURE_OCR_SECRET_KEY in .env
- Verify endpoint URL is correct

**Issue:** S3 upload fails
- **Solution:** Check AWS credentials
- Verify bucket exists and region matches
- Check IAM permissions for s3:PutObject

**Issue:** Gemini API rate limit exceeded
- **Solution:** Wait and retry
- Consider using caching more aggressively
- Upgrade to paid tier

**Issue:** Bounding boxes not appearing on frontend
- **Solution:** Verify bbox format is 8-point normalized
- Check page_width and page_height are included
- Ensure coordinates are in 0-1 range

**Issue:** OCR cache not working
- **Solution:** Check MongoDB connection
- Verify ocr_cache collection exists
- Check document_id matching

### Logging

**Enable debug logging:**
```bash
export LOG_LEVEL=DEBUG
uvicorn app:app --reload --port 8000
```

**View detailed AI processing logs:**
```python
# In ai_processor.py, logger outputs:
# - OCR cache hits/misses
# - Relevancy scores for each document
# - Evidence extraction results
# - Win probability calculations
```

## Performance Optimization

### Current Optimizations

1. **OCR Caching** - MongoDB cache prevents redundant OCR calls
2. **Document Relevancy Filtering** - Fast Gemini Flash pre-filters documents
3. **Top-3 Shortlisting** - Reduces LLM costs by 60%+
4. **Parallel OCR Processing** - asyncio.gather() for concurrent operations
5. **Pre-signed S3 URLs** - Direct browser downloads, no proxy

### Future Improvements

- [ ] Implement Redis for faster caching
- [ ] Add connection pooling for MongoDB
- [ ] Background job queue for long-running AI tasks
- [ ] Webhook notifications for completion
- [ ] Batch processing for CSV uploads
- [ ] Elasticsearch for full-text search
- [ ] CDN for S3 document delivery

## Error Handling Examples from Routes

### Authentication Errors (auth_routes.py)

```python
# Invalid credentials
if not user or not verify_password(password, user.get("hashed_password", "")):
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Invalid token
if not payload:
    raise HTTPException(status_code=401, detail="Invalid token")

# User not found
if not user:
    raise HTTPException(status_code=401, detail="User not found")
```

**Response:**
```json
{
  "detail": "Invalid credentials"
}
```

### Validation Errors (denial_routes.py)

```python
# Invalid ObjectId format
if not ObjectId.is_valid(denial_id):
    raise HTTPException(status_code=400, detail="Invalid denial ID")

# Missing required data
if not update_data:
    raise HTTPException(status_code=400, detail="No fields to update")

# File type validation
if not file.filename.endswith('.csv'):
    raise HTTPException(status_code=400, detail="File must be CSV format")
```

### Resource Not Found (document_routes.py)

```python
# Document not found
document = await patient_documents_collection.find_one({"document_id": document_id})
if not document:
    raise HTTPException(status_code=404, detail="Document not found")

# PDF file missing from S3
if not os.path.exists(pdf_path):
    raise HTTPException(status_code=404, detail="PDF file not found")
```

### Prerequisite Errors (criteria_evaluation_routes.py)

```python
# Missing required documents
documents = await patient_documents_collection.find({"denial_id": denial_id}).to_list(None)
if not documents:
    raise HTTPException(
        status_code=400,
        detail="No documents uploaded. Please upload documents before evaluation."
    )

# Missing policy criteria
if not policy:
    raise HTTPException(
        status_code=404,
        detail=f"No medical policy found for payer {payer_id} and CPT code {cpt_code}"
    )
```

### AI Processing Errors (appeal_routes.py)

```python
# Criteria evaluation required first
evaluation = await criteria_evaluations_collection.find_one({"denial_id": denial_id})
if not evaluation:
    raise HTTPException(
        status_code=400,
        detail="Criteria evaluation required before generating appeal"
    )

# PDF merge failure
try:
    merger = PdfMerger()
    # ... merge operations
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Failed to merge PDFs: {str(e)}"
    )

# S3 upload failure
try:
    upload_to_s3(package_path, package_s3_key)
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Failed to upload package: {str(e)}"
    )
```

### S3 Errors (document_routes.py)

```python
# File upload to S3 failed
try:
    s3_url = upload_to_s3(temp_file_path, s3_key)
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Failed to upload to S3: {str(e)}"
    )

# Pre-signed URL generation failed
try:
    presigned_url = generate_presigned_url(s3_key)
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail="Failed to generate presigned URL"
    )
```

### Error Response Examples

**400 Bad Request:**
```bash
curl -X POST http://localhost:8000/denials/invalid-id
# Response:
{
  "detail": "Invalid denial ID"
}
```

**401 Unauthorized:**
```bash
curl -X GET http://localhost:8000/auth/me
# Response:
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```bash
curl -X GET http://localhost:8000/denials/DN99999999
# Response:
{
  "detail": "Denial not found"
}
```

**422 Validation Error (Pydantic):**
```bash
curl -X POST http://localhost:8000/denials \
  -H "Content-Type: application/json" \
  -d '{"invalid_field": "value"}'
# Response:
{
  "detail": [
    {
      "loc": ["body", "claim_number"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**500 Internal Server Error:**
```bash
curl -X POST http://localhost:8000/appeals/generate/DN123
# Response (if Gemini API fails):
{
  "detail": "Failed to generate appeal letter: API rate limit exceeded"
}
```

## Security Considerations

### Current Security Measures

- **JWT Authentication** - All endpoints require valid token
- **Password Hashing** - Bcrypt with salt
- **CORS** - Restricted to approved origins
- **S3 Pre-signed URLs** - Time-limited access
- **Input Validation** - Pydantic models validate all inputs

### Security Best Practices

- Rotate JWT_SECRET regularly
- Use environment variables, never hardcode secrets
- Enable S3 bucket encryption
- Monitor AWS CloudWatch for unusual activity
- Implement rate limiting (not currently done)
- Add request logging for audit trails

---

**Last Updated:** January 2026

For frontend documentation, see `frontend/README.md`.
