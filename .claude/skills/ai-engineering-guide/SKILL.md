---
name: ai-engineering-guide
description: Build AI applications using PenguinAI SDK - provider-agnostic library for AWS Bedrock, OpenAI, Gemini, Azure. Use for LLM clients, OCR, embeddings, vector search, or document processing. Triggers on penguin, penguinai, LLM, OCR, document AI, or AI pipelines.
---

# AI Architect

Provider-agnostic AI orchestration library for building production AI applications.

---

## ⛔ CRITICAL REQUIREMENTS - MANDATORY

> **ABSOLUTE RULE - NO EXCEPTIONS:**
>
> **NEVER TRUNCATE OCR/DOCUMENT TEXT:**
> - ❌ `full_text[:8000]` - NEVER do this
> - ❌ `text[:5000]` - NEVER arbitrarily cut text
> - ✅ Pass the FULL document text to LLM
> - ✅ If too long, increase `max_tokens` parameter
> - ✅ If still too long, use continuation (process in parts, combine results)
> - ✅ Use models with larger context windows (Claude 200k, Gemini 1M)
>
> ALL AI functionality MUST use `penguin-ai-sdk`. This includes:
> - LLM calls (chat, extraction, agents)
> - OCR (Optical Character Recognition)
> - PDF text extraction
> - Document classification
> - Entity extraction
> - Embeddings and vector search
>
> **FORBIDDEN LIBRARIES - DO NOT USE:**
> | ❌ Forbidden | ✅ Use Instead |
> |--------------|----------------|
> | `pytesseract` | `penguin.ocr` |
> | `openai` | `penguin.llm` |
> | `anthropic` | `penguin.llm` |
> | `google.generativeai` | `penguin.llm` |
> | `boto3` for Bedrock | `penguin.llm` |
> | `azure.ai.formrecognizer` | `penguin.ocr` |
> | `langchain` | `penguin.llm` + `penguin.tools` |
> | Direct API calls | `penguin.*` modules |
>
> The `penguin-ai-sdk` is the **ONLY** approved library for AI operations.

---

## Overview

PenguinAI SDK abstracts away provider differences, giving you a unified interface for:

- **LLM** - Multi-provider chat (Bedrock, OpenAI, Gemini, Azure)
- **Tools** - Function calling with `@tool` decorator
- **Agents** - Automated tool-calling loops
- **Middleware** - Security guardrails (prompt injection, output safety)
- **OCR** - Document text extraction (Azure, AWS Textract, Google)
- **Embeddings** - Text vectors (Bedrock Titan, sentence-transformers)
- **Vector DB** - Semantic search (S3 Vectors)
- **Redaction** - PII detection and removal
- **Evals** - LLM-as-judge evaluation

---

## Quick Start

```python
import asyncio
from penguin.llm import create_client, UserMessage

async def main():
    client = create_client("bedrock", model="claude-sonnet-4-5")
    result = await client.create([UserMessage("Hello")])
    print(result.content)

asyncio.run(main())
```

---

## Installation

```bash
# CPU (Mac/Laptops)
pip install torch --index-url https://download.pytorch.org/whl/cpu
aws s3 cp s3://penguin-library/packages/penguin_ai_sdk-0.1.3-py3-none-any.whl /tmp/
pip install "/tmp/penguin_ai_sdk-0.1.3-py3-none-any.whl[cpu]"
```

---

## Key Imports

```python
# LLM
from penguin.llm import create_client, UserMessage, SystemMessage

# Tools & Agents
from penguin.tools import tool, ToolExecutor
from penguin.agents import chat_with_tools, Agent

# OCR & Embeddings
from penguin.ocr import AzureOCRProvider, AWSTextractProvider
from penguin.embeddings import create_embedding_client

# Vector DB
from penguin.vector_db import create_vector_client

# Utilities
from penguin.redaction import PenguinPIIRedactor
from penguin.data_assets import load_asset
```

---

## Default Providers

| Capability | Default Provider | Model |
|------------|------------------|-------|
| **OCR** | Azure Document Intelligence | prebuilt-read |
| **LLM** | Google Gemini | gemini-2.0-flash |

### Environment Variables (Default)

```bash
# Azure Document Intelligence (OCR)
AZURE_OCR_ENDPOINT=https://penguin-ocr-stage.cognitiveservices.azure.com/
AZURE_OCR_SECRET_KEY=your-azure-key

# Google Gemini (LLM)
GEMINI_API_KEY=your-gemini-api-key
```

---

## Document Processing Pipeline

For document AI workflows (OCR → LLM → Structured Output):

### Basic Pipeline (Azure OCR + Gemini LLM)

```python
from penguin.ocr import AzureOCRProvider
from penguin.llm import create_client, UserMessage, SystemMessage
from pydantic import BaseModel
from typing import List

class ICDCode(BaseModel):
    code: str
    description: str
    confidence: float
    supporting_text: str

class DocumentProcessor:
    def __init__(self):
        self.ocr = AzureOCRProvider()  # Azure Document Intelligence
        self.llm = create_client("gemini", model="gemini-2.0-flash")  # Google Gemini

    async def process(self, file_path: str) -> List[ICDCode]:
        # Step 1: OCR with Azure
        ocr_result = await self.ocr.process_file(file_path)

        # Step 2: LLM Extraction with Gemini
        result = await self.llm.create(
            messages=[
                SystemMessage("Extract ICD-10 codes from the document."),
                UserMessage(ocr_result.full_text)
            ],
            output_format=List[ICDCode]
        )

        return result.content
```

### OCR Result Format

All OCR providers return normalized results:

```python
class OCRResult:
    file_path: str           # Original file path
    full_text: str           # Complete extracted text
    provider: str            # "aws_textract" | "azure_document_intelligence" | "google_document_ai"
    lines: List[OCRLine]     # Line-by-line results
    metadata: Dict           # Provider-specific data

class OCRLine:
    content: str             # Text content
    page_number: int         # 1-indexed page number
    bounding_box: List[Dict] # [{x, y}, {x, y}, {x, y}, {x, y}]
    confidence: float        # 0.0 - 1.0
```

### Bounding Box Format

Coordinates are normalized (0-1) relative to page dimensions:

```python
# Convert to 8-point format for PDFViewer
def to_pdf_viewer_format(bbox):
    return [
        bbox[0]["x"], bbox[0]["y"],  # x1, y1
        bbox[1]["x"], bbox[1]["y"],  # x2, y2
        bbox[2]["x"], bbox[2]["y"],  # x3, y3
        bbox[3]["x"], bbox[3]["y"]   # x4, y4
    ]
```

---

## Logging (Required for Debugging)

Add logging to all AI operations:

```python
import logging
logger = logging.getLogger("ai_processor")

# Log at key points:
logger.info(f"[OCR] Starting for {document_id}")
logger.info(f"[LLM] Extracting codes, text length: {len(text)}")
logger.error(f"[ERROR] Failed: {str(e)}")
```

Use `LOG_LEVEL=DEBUG` in `.env` for verbose output.

---

## Reference Documentation

For complete API documentation and examples, see:

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Comprehensive SDK documentation with all modules
- **[PATTERNS.md](PATTERNS.md)** - Detailed code patterns for document processing
- **[templates/](templates/)** - Ready-to-use templates:
  - `ocr_processor.py` - Multi-provider OCR processor
  - `llm_extractor.py` - LLM extraction with structured output
  - `document_pipeline.py` - Full end-to-end document pipeline
