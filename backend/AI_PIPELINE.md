# AI Processing Pipeline Documentation

## Overview

This backend uses **penguin-ai-sdk** for all AI operations:
- **OCR**: Azure Document Intelligence (prebuilt-read model)
- **Relevancy Scoring**: Google Gemini (gemini-2.0-flash-exp)
- **Evidence Extraction**: AWS Bedrock Claude (claude-3-5-sonnet)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI PROCESSING PIPELINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. FILTER DOCUMENTS BY DATE RANGE                              │
│     └─ 90 days before service_date to denial_date               │
│                                                                 │
│  2. OCR WITH CACHING (Azure Document Intelligence)              │
│     ├─ Check ocr_cache collection in MongoDB                    │
│     ├─ If cached: return cached result                          │
│     └─ If not: run OCR and cache result                         │
│                                                                 │
│  3. RELEVANCY SCORING (Google Gemini)                           │
│     ├─ Score each document against criteria (0-N)               │
│     ├─ Cache scores in document_relevancy collection            │
│     └─ Fast, cheap initial filtering                            │
│                                                                 │
│  4. SHORTLIST TOP 3 DOCUMENTS                                   │
│     └─ Sort by relevancy_score descending                       │
│                                                                 │
│  5. EVIDENCE EXTRACTION (AWS Bedrock Claude)                    │
│     ├─ Extract 2-3 key pieces of evidence per document          │
│     ├─ Map evidence text to bounding boxes from OCR cache       │
│     └─ Accurate, detailed analysis                              │
│                                                                 │
│  6. COMPILE RESULTS                                             │
│     ├─ Group evidence by criterion                              │
│     ├─ Calculate win_probability                                │
│     └─ Return structured evaluation with bboxes                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Environment Variables

```bash
# Azure Document Intelligence (OCR)
AZURE_OCR_ENDPOINT=https://penguin-ocr-stage.cognitiveservices.azure.com/
AZURE_OCR_SECRET_KEY=<your-key>

# Google Gemini (Relevancy Scoring)
GEMINI_API_KEY=<your-key>

# AWS Bedrock (Evidence Extraction)
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_SESSION_TOKEN=<optional>
BEDROCK_REGION=us-east-1

# Logging
LOG_LEVEL=INFO
```

## Module Structure

```
backend/
├── penguin/                    # Lightweight penguin-ai-sdk implementation
│   ├── __init__.py
│   ├── ocr.py                 # AzureOCRProvider
│   └── llm.py                 # GeminiClient, BedrockClient
│
├── services/
│   └── ai_processor.py        # DocumentProcessor (main pipeline)
│
├── routes/
│   ├── criteria_evaluation_routes.py  # POST /api/criteria-evaluation/evaluate/{denial_id}
│   └── document_routes.py              # POST /api/documents/cache-ocr/{patient_id}
│
└── utils/
    └── db_utils.py            # MongoDB collections (ocr_cache, document_relevancy)
```

## Key Components

### 1. OCR Provider (penguin.ocr)

```python
from penguin.ocr import AzureOCRProvider

ocr = AzureOCRProvider()
result = await ocr.process_file("document.pdf")

# result.full_text - Complete text (NEVER truncated)
# result.lines - List of OCRLine with:
#   - content: str
#   - page_number: int
#   - bounding_box: List[Dict] - [{"x": 0.1, "y": 0.2}, ...]
#   - confidence: float
```

**Bounding Box Format:**
- Coordinates are normalized (0-1) relative to page dimensions
- 4 points: top-left, top-right, bottom-right, bottom-left
- Converted to 8-point format for PDFViewer: `[x1, y1, x2, y2, x3, y3, x4, y4]`

### 2. LLM Clients (penguin.llm)

```python
from penguin.llm import create_client, UserMessage, SystemMessage

# Gemini for fast relevancy scoring
gemini = create_client("gemini", model="gemini-2.0-flash-exp")

# Bedrock Claude for detailed extraction
claude = create_client("bedrock", model="us.anthropic.claude-3-5-sonnet-20241022-v2:0")

response = await gemini.create(
    messages=[
        SystemMessage("System instruction"),
        UserMessage("User prompt")
    ],
    max_tokens=4096,
    temperature=0.0
)
```

### 3. Document Processor (services/ai_processor.py)

Main class: `DocumentProcessor`

**Methods:**

- `process_document_with_cache()` - OCR with MongoDB caching
- `score_document_relevancy()` - Gemini-based relevancy scoring
- `extract_evidence_from_document()` - Claude-based evidence extraction
- `evaluate_criteria()` - Full pipeline orchestration
- `generate_appeal_letter()` - Appeal letter generation

### 4. MongoDB Collections

**ocr_cache:**
```json
{
  "document_id": "doc123",
  "patient_id": "PT-100000",
  "file_path": "/path/to/doc.pdf",
  "full_text": "Complete document text...",
  "pages": [
    {
      "page_number": 1,
      "text": "Page 1 text",
      "lines": [
        {
          "text": "Line text",
          "bbox": [0.1, 0.2, 0.9, 0.2, 0.9, 0.25, 0.1, 0.25]
        }
      ]
    }
  ],
  "ocr_timestamp": "2024-01-22T10:00:00Z"
}
```

**document_relevancy:**
```json
{
  "document_id": "doc123",
  "document_name": "xray_report.pdf",
  "relevancy_score": 5,
  "criteria_matches": [
    {
      "criterion_id": "CR001",
      "relevant": true,
      "confidence": 0.95
    }
  ]
}
```

## API Endpoints

### Evaluate Criteria

```bash
POST /api/criteria-evaluation/evaluate/{denial_id}
```

**Response:**
```json
{
  "denial_id": "denial123",
  "total_criteria": 8,
  "criteria_met": 6,
  "win_probability": 75,
  "criteria": [
    {
      "id": "CR001",
      "question": "Does patient have chronic pain?",
      "met": true,
      "evidence": [
        {
          "document_id": "doc123",
          "document_name": "progress_note.pdf",
          "page": 1,
          "text": "Patient reports chronic knee pain for 8 months",
          "bbox": [0.1, 0.2, 0.9, 0.2, 0.9, 0.25, 0.1, 0.25],
          "confidence": 0.9
        }
      ],
      "explanation": "Evidence found in progress note dated 06/04/2024"
    }
  ],
  "top_documents": [
    {
      "document_id": "doc123",
      "document_name": "progress_note.pdf",
      "relevancy_score": 5
    }
  ]
}
```

### Cache OCR for Patient

```bash
POST /api/documents/cache-ocr/{patient_id}
```

Pre-processes all documents for a patient and caches OCR results.

## Critical Rules

### NEVER Truncate Text

```python
# ❌ WRONG - Never do this
full_text[:8000]
text[:5000]

# ✅ CORRECT - Always use full text
full_text  # Pass complete text to LLM

# ✅ If text is too long
# - Increase max_tokens parameter
# - Use models with larger context (Claude 200k, Gemini 1M)
# - Process in parts and combine results
```

### Use Only penguin-ai-sdk

```python
# ❌ FORBIDDEN
import pytesseract
import openai
import anthropic
from langchain import ...

# ✅ REQUIRED
from penguin.ocr import AzureOCRProvider
from penguin.llm import create_client
```

## Testing

Run the pipeline test:

```bash
source venv/bin/activate
python test_pipeline.py
```

Expected output:
```
[STEP 1] OCR Processing
✓ xray_report_20240604.pdf: 880 chars, 27 lines
✓ progress_note_20240604.pdf: 1899 chars, 41 lines

[STEP 2] Document Relevancy Scoring (Gemini)
✓ xray_report_20240604.pdf: relevancy_score=2
  - CR001: RELEVANT (confidence: 0.9)
  - CR002: RELEVANT (confidence: 1.0)

✓ Azure OCR: Working
✓ Gemini LLM: Working
✓ Bounding boxes: Mapped
✓ Full text extraction: NEVER truncated
```

## Performance

- **OCR**: ~3-5 seconds per page
- **Relevancy Scoring**: ~1-2 seconds per document (Gemini)
- **Evidence Extraction**: ~3-5 seconds per document (Claude)
- **Caching**: Reduces repeat OCR to <100ms

## Sample Documents

Test files located at:
```
backend/documents/PT-100000/2024/01/
├── xray_report_20240604.pdf
├── progress_note_20240604.pdf
├── mri_report_20241002.pdf
├── surgical_recommendation_20241017.pdf
└── ... (10 total PDFs)
```

## Next Steps

1. Start backend: `uvicorn main:app --reload`
2. Test OCR caching: `POST /api/documents/cache-ocr/PT-100000`
3. Test criteria evaluation: `POST /api/criteria-evaluation/evaluate/{denial_id}`
4. Verify bounding boxes render correctly in PDFViewer

## Troubleshooting

### Import Errors

```bash
# Activate venv first
source venv/bin/activate

# Verify installations
python -c "from penguin.ocr import AzureOCRProvider; print('OK')"
python -c "from penguin.llm import create_client; print('OK')"
```

### Azure OCR Errors

- Check `AZURE_OCR_ENDPOINT` and `AZURE_OCR_SECRET_KEY` in `.env`
- Verify endpoint is accessible
- Check Azure quota limits

### Gemini API Errors

- Check `GEMINI_API_KEY` in `.env`
- Verify API key is active
- Check rate limits

### Bedrock Errors

- Check AWS credentials (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
- Verify Bedrock model access in AWS console
- Check `BEDROCK_REGION` matches your model region

## Support

For issues or questions, check:
1. `test_pipeline.py` for example usage
2. `services/ai_processor.py` for implementation details
3. Logs with `LOG_LEVEL=DEBUG`
