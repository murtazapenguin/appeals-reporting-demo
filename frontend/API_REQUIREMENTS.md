# API Requirements for Claim Appeals Frontend

This document specifies all API endpoints required by the frontend application.

---

## Base URL
```
http://localhost:8000/api
```

---

## Authentication Endpoints

### POST /api/auth/login
Authenticate user and return access token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Response (401):**
```json
{
  "detail": "Invalid credentials"
}
```

---

### GET /api/auth/me
Get current authenticated user.

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200):**
```json
{
  "id": "user123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "appeals_manager"
}
```

---

## Denials Endpoints

### GET /api/denials
Get all denials with optional filters.

**Query Parameters:**
- `status` (optional): "pending" | "in_review" | "appeal_ready" | "submitted" | "approved" | "denied"
- `payer` (optional): Filter by payer name
- `category` (optional): Filter by denial category

**Response (200):**
```json
[
  {
    "id": "denial123",
    "claim_number": "CLM-2024-001",
    "patient_name": "Jane Smith",
    "patient_id": "PT123456",
    "patient_dob": "1985-03-15",
    "provider_name": "Dr. John Wilson",
    "provider_id": "PRV-001",
    "payer_name": "Blue Cross Blue Shield",
    "payer_id": "PAY-001",
    "policy_number": "POL-987654",
    "service_date": "2024-03-15",
    "denial_date": "2024-04-01",
    "denial_code": "MN001",
    "denial_category": "Medical Necessity",
    "denial_reason": "Lack of medical necessity documentation",
    "claim_amount": 15000.00,
    "procedure_code": "99285",
    "diagnosis_codes": "M54.5, M25.511, G89.29",
    "service_description": "Emergency room visit for acute back pain",
    "status": "pending",
    "win_probability": 75,
    "appeal_deadline": "2024-05-01",
    "priority": "high",
    "internal_notes": "Patient has documented chronic condition",
    "created_at": "2024-04-02T10:00:00Z",
    "updated_at": "2024-04-02T10:00:00Z"
  }
]
```

---

### GET /api/denials/{id}
Get single denial by ID.

**Response (200):**
```json
{
  "id": "denial123",
  "claim_number": "CLM-2024-001",
  "patient_name": "Jane Smith",
  "patient_id": "PT123456",
  "patient_dob": "1985-03-15",
  "provider_name": "Dr. John Wilson",
  "provider_id": "PRV-001",
  "payer_name": "Blue Cross Blue Shield",
  "payer_id": "PAY-001",
  "policy_number": "POL-987654",
  "service_date": "2024-03-15",
  "denial_date": "2024-04-01",
  "denial_code": "MN001",
  "denial_category": "Medical Necessity",
  "denial_reason": "Lack of medical necessity documentation",
  "claim_amount": 15000.00,
  "procedure_code": "99285",
  "diagnosis_codes": "M54.5, M25.511, G89.29",
  "service_description": "Emergency room visit for acute back pain",
  "status": "pending",
  "win_probability": 75,
  "appeal_deadline": "2024-05-01",
  "priority": "high",
  "internal_notes": "Patient has documented chronic condition",
  "created_at": "2024-04-02T10:00:00Z",
  "updated_at": "2024-04-02T10:00:00Z"
}
```

---

### POST /api/denials
Create new denial (manual entry).

**Request:**
```json
{
  "claim_number": "CLM-2024-001",
  "patient_name": "Jane Smith",
  "patient_id": "PT123456",
  "patient_dob": "1985-03-15",
  "provider_name": "Dr. John Wilson",
  "provider_id": "PRV-001",
  "payer_name": "Blue Cross Blue Shield",
  "payer_id": "PAY-001",
  "policy_number": "POL-987654",
  "service_date": "2024-03-15",
  "denial_date": "2024-04-01",
  "denial_code": "MN001",
  "denial_category": "Medical Necessity",
  "denial_reason": "Lack of medical necessity documentation",
  "claim_amount": 15000.00,
  "procedure_code": "99285",
  "diagnosis_codes": "M54.5, M25.511, G89.29",
  "service_description": "Emergency room visit for acute back pain",
  "priority": "high",
  "internal_notes": "Patient has documented chronic condition"
}
```

**Response (201):**
```json
{
  "id": "denial123",
  "claim_number": "CLM-2024-001",
  "status": "pending",
  "created_at": "2024-04-02T10:00:00Z"
}
```

---

### PUT /api/denials/{id}
Update existing denial.

**Request:** Same as POST, all fields optional

**Response (200):** Full denial object

---

### POST /api/denials/upload-csv
Bulk upload denials via CSV.

**Request:**
```
Content-Type: multipart/form-data
file: [CSV file]
```

**CSV Headers:**
```
claim_number,patient_name,patient_id,provider_name,provider_id,payer_name,service_date,denial_date,denial_code,denial_category,claim_amount,procedure_code,diagnosis
```

**Response (200):**
```json
{
  "imported_count": 25,
  "failed_count": 2,
  "errors": [
    {
      "row": 5,
      "error": "Missing required field: claim_number"
    }
  ]
}
```

---

## Medical Policies Endpoints

### GET /api/medical-policies
List all medical policies.

**Response (200):**
```json
[
  {
    "id": "policy123",
    "payer_id": "PAY-001",
    "payer_name": "Blue Cross Blue Shield",
    "cpt_code": "99285",
    "policy_number": "MP-2024-001",
    "criteria": [
      {
        "id": "criteria1",
        "question": "Patient has documented chronic pain for >6 months",
        "required": true
      },
      {
        "id": "criteria2",
        "question": "Conservative treatment tried and failed",
        "required": true
      }
    ]
  }
]
```

---

### GET /api/medical-policies/lookup
Lookup policy by payer and CPT code.

**Query Parameters:**
- `payer_id`: Payer identifier
- `cpt_code`: CPT procedure code

**Response (200):**
```json
{
  "id": "policy123",
  "payer_id": "PAY-001",
  "payer_name": "Blue Cross Blue Shield",
  "cpt_code": "99285",
  "policy_number": "MP-2024-001",
  "criteria": [
    {
      "id": "criteria1",
      "question": "Patient has documented chronic pain for >6 months",
      "required": true
    }
  ]
}
```

---

## Documents Endpoints

### GET /api/documents/denial/{denial_id}
Get all documents for a denial.

**Response (200):**
```json
[
  {
    "id": "doc123",
    "denial_id": "denial123",
    "document_name": "progress_note_2024_03_15.pdf",
    "document_type": "progress_note",
    "document_date": "2024-03-15",
    "presigned_urls": {
      "1": "https://storage.example.com/doc123/page1.png",
      "2": "https://storage.example.com/doc123/page2.png",
      "3": "https://storage.example.com/doc123/page3.png"
    },
    "total_pages": 3,
    "uploaded_at": "2024-04-01T10:00:00Z"
  }
]
```

---

### GET /api/documents/denial/{denial_id}/date-range
Get documents within date range.

**Query Parameters:**
- `start_date`: ISO date (e.g., "2024-01-01")
- `end_date`: ISO date (e.g., "2024-03-31")

**Response (200):** Same as above, filtered

---

### GET /api/documents/{document_id}/pages
Get page images for a document.

**Response (200):**
```json
{
  "document_id": "doc123",
  "document_name": "progress_note_2024_03_15.pdf",
  "pages": {
    "1": "https://storage.example.com/doc123/page1.png",
    "2": "https://storage.example.com/doc123/page2.png",
    "3": "https://storage.example.com/doc123/page3.png"
  }
}
```

---

## Criteria Evaluation Endpoints

### POST /api/criteria-evaluation/evaluate/{denial_id}
Evaluate medical necessity criteria for a denial.

**Response (200):**
```json
{
  "denial_id": "denial123",
  "total_criteria": 5,
  "criteria_met": 4,
  "win_probability": 80,
  "criteria": [
    {
      "id": "criteria1",
      "question": "Patient has documented chronic pain for >6 months",
      "met": true,
      "evidence": [
        {
          "document_name": "progress_note_2024_03_15.pdf",
          "page": 2,
          "text": "Patient reports chronic lower back pain ongoing since 2023-09",
          "bbox": [0.1, 0.3, 0.9, 0.3, 0.9, 0.35, 0.1, 0.35],
          "label": "Chronic pain documented",
          "presigned_urls": {
            "2": "https://storage.example.com/doc123/page2.png"
          }
        }
      ]
    },
    {
      "id": "criteria2",
      "question": "MRI shows structural abnormality",
      "met": false,
      "missing_documents": "MRI report from 2024-03-10 required"
    }
  ],
  "evaluated_at": "2024-04-02T11:00:00Z"
}
```

---

### GET /api/criteria-evaluation/{denial_id}
Get existing criteria evaluation results.

**Response (200):** Same as POST response above

**Response (404):**
```json
{
  "detail": "No criteria evaluation found for this denial"
}
```

---

## Appeals Endpoints

### POST /api/appeals/generate/{denial_id}
Generate appeal letter.

**Response (200):**
```json
{
  "denial_id": "denial123",
  "provider_letterhead": {
    "name": "Wilson Medical Center",
    "address": "123 Main St, City, State 12345",
    "phone": "(555) 123-4567"
  },
  "sections": [
    {
      "title": "Introduction",
      "content": "We are writing to appeal the denial of claim CLM-2024-001..."
    },
    {
      "title": "Denied Services",
      "content": "..."
    },
    {
      "title": "Clinical Justification",
      "content": "..."
    }
  ],
  "enclosed_documents": [
    "Progress Notes (2023-09 to 2024-03)",
    "Physical Therapy Records",
    "MRI Report"
  ],
  "signature": {
    "name": "Dr. John Wilson",
    "title": "Chief Medical Officer"
  },
  "generated_at": "2024-04-02T12:00:00Z"
}
```

---

### GET /api/appeals/{denial_id}
Get existing appeal letter.

**Response (200):** Same as POST generate response

**Response (404):**
```json
{
  "detail": "No appeal letter found for this denial"
}
```

---

### GET /api/appeals/{denial_id}/pdf
Download appeal letter as PDF.

**Response (200):**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="appeal_CLM-2024-001.pdf"
[Binary PDF data]
```

---

### POST /api/appeals/{denial_id}/submit
Submit appeal to payer.

**Response (200):**
```json
{
  "denial_id": "denial123",
  "status": "submitted",
  "submitted_at": "2024-04-02T13:00:00Z",
  "confirmation_number": "APPEAL-2024-001"
}
```

---

## Metrics Endpoints

### GET /api/metrics/dashboard
Get dashboard summary metrics.

**Response (200):**
```json
{
  "total_open_denials": 45,
  "total_at_risk": 675000.00,
  "urgent_appeals": 8,
  "high_probability_count": 23,
  "recovered_this_month": 125000.00,
  "recovery_rate_this_month": 72,
  "total_recovered_ytd": 1250000.00,
  "total_claims_recovered": 87
}
```

---

### GET /api/metrics/by-payer
Get success rate by payer.

**Response (200):**
```json
[
  {
    "payer_name": "Blue Cross Blue Shield",
    "total_denials": 25,
    "appeals_submitted": 20,
    "appeals_won": 15,
    "success_rate": 75,
    "recovered_amount": 450000.00
  },
  {
    "payer_name": "United Healthcare",
    "total_denials": 18,
    "appeals_submitted": 15,
    "appeals_won": 10,
    "success_rate": 67,
    "recovered_amount": 320000.00
  }
]
```

---

### GET /api/metrics/by-category
Get performance by denial category.

**Response (200):**
```json
[
  {
    "category": "Medical Necessity",
    "total_denials": 30,
    "appeals_submitted": 25,
    "appeals_won": 18,
    "success_rate": 72,
    "recovered_amount": 550000.00
  },
  {
    "category": "Prior Authorization",
    "total_denials": 15,
    "appeals_submitted": 12,
    "appeals_won": 8,
    "success_rate": 67,
    "recovered_amount": 180000.00
  }
]
```

---

### GET /api/metrics/trends
Get recovery trends over time.

**Query Parameters:**
- `months` (optional, default=12): Number of months to include

**Response (200):**
```json
[
  {
    "month": "2024-01",
    "recovered_amount": 95000.00,
    "submitted_appeals": 12,
    "won_appeals": 8,
    "success_rate": 67
  },
  {
    "month": "2024-02",
    "recovered_amount": 110000.00,
    "submitted_appeals": 15,
    "won_appeals": 11,
    "success_rate": 73
  },
  {
    "month": "2024-03",
    "recovered_amount": 125000.00,
    "submitted_appeals": 18,
    "won_appeals": 13,
    "success_rate": 72
  }
]
```

---

## Status Enums

### Denial Status
- `pending`: Initial state, not yet reviewed
- `in_review`: Being reviewed by staff
- `appeal_ready`: Criteria evaluated, ready to generate appeal
- `submitted`: Appeal letter submitted to payer
- `approved`: Appeal approved, funds recovered
- `denied`: Appeal denied by payer

### Denial Category
- `Medical Necessity`
- `Prior Authorization`
- `Coding Error`
- `Documentation`
- `Other`

### Priority Level
- `low`
- `normal`
- `high`
- `urgent`

---

## Error Responses

All endpoints may return:

**400 Bad Request:**
```json
{
  "detail": "Validation error message"
}
```

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found:**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal server error"
}
```

---

## Bounding Box Format

All bounding boxes use normalized coordinates (0-1 range) in 8-point format:

```json
{
  "bbox": [x1, y1, x2, y2, x3, y3, x4, y4]
}
```

Where:
- (x1, y1) = top-left corner
- (x2, y2) = top-right corner
- (x3, y3) = bottom-right corner
- (x4, y4) = bottom-left corner

Example:
```json
{
  "bbox": [0.1, 0.3, 0.9, 0.3, 0.9, 0.35, 0.1, 0.35]
}
```

---

## Authentication Flow

1. User submits email + password to POST /api/auth/login
2. Backend returns access_token
3. Frontend stores token in localStorage
4. All subsequent requests include header: `Authorization: Bearer {access_token}`
5. Backend validates token on each request
6. On logout, frontend clears localStorage and redirects to /login

---

## Data Validation Requirements

### Required Fields (Create Denial)
- claim_number
- patient_name
- patient_id
- provider_name
- payer_name
- service_date
- denial_date
- denial_category
- claim_amount
- procedure_code
- diagnosis_codes

### Date Formats
All dates should be ISO 8601: `YYYY-MM-DD` or `YYYY-MM-DDTHH:mm:ssZ`

### Currency
All amounts in USD, decimal format: `15000.00`

### Diagnosis Codes
Comma-separated ICD-10 codes: `"M54.5, M25.511, G89.29"`
