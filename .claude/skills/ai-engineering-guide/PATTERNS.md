# AI-architect Code Patterns

This document contains detailed code patterns for document processing using the penguin-ai-sdk.

---

## Table of Contents

1. [OCR Patterns](#ocr-patterns)
2. [LLM Patterns](#llm-patterns)
3. [Tool Definition Patterns](#tool-definition-patterns)
4. [Bounding Box Patterns](#bounding-box-patterns)
5. [Error Handling Patterns](#error-handling-patterns)
6. [Async Patterns](#async-patterns)

---

## OCR Patterns

### AWS Textract (Recommended)

```python
import asyncio
from penguin.ocr import AWSTextractProvider, OCRResult

class TextractProcessor:
    """AWS Textract OCR processor with automatic PDF handling."""

    def __init__(
        self,
        region_name: str = "us-east-1",
        s3_bucket: str = None,
        extract_tables: bool = True,
        extract_forms: bool = True
    ):
        self.ocr = AWSTextractProvider(
            region_name=region_name,
            s3_bucket=s3_bucket,
            extract_tables=extract_tables,
            extract_forms=extract_forms,
            use_async_for_large_files=True,
            size_threshold_mb=10
        )

    async def process_single(self, file_path: str) -> OCRResult:
        """Process a single document."""
        return await self.ocr.process_file(file_path)

    async def process_batch(
        self,
        file_paths: list,
        max_concurrency: int = 5
    ) -> list:
        """Process multiple documents in parallel."""
        return await self.ocr.process_batch(
            file_paths,
            max_concurrency=max_concurrency
        )

    def extract_text_by_page(self, result: OCRResult) -> dict:
        """Group extracted text by page number."""
        pages = {}
        for line in result.lines:
            page = line.page_number
            if page not in pages:
                pages[page] = []
            pages[page].append({
                "text": line.content,
                "confidence": line.confidence,
                "bbox": line.bounding_box
            })
        return pages
```

### Azure Document Intelligence

```python
from penguin.ocr import AzureOCRProvider

class AzureProcessor:
    """Azure Document Intelligence processor."""

    def __init__(
        self,
        endpoint: str = None,
        key: str = None,
        model_id: str = "prebuilt-read"
    ):
        import os
        self.ocr = AzureOCRProvider(
            endpoint=endpoint or os.getenv("AZURE_OCR_ENDPOINT"),
            key=key or os.getenv("AZURE_OCR_SECRET_KEY"),
            model_id=model_id
        )

    async def process(self, file_path: str) -> dict:
        result = await self.ocr.process_file(file_path)
        return {
            "text": result.full_text,
            "lines": [
                {
                    "content": line.content,
                    "page": line.page_number,
                    "bbox": line.bounding_box,
                    "confidence": line.confidence
                }
                for line in result.lines
            ],
            "provider": result.provider
        }
```

### Google Document AI

```python
from penguin.ocr.providers.google import GoogleDocumentAIProvider

class GoogleProcessor:
    """Google Document AI processor."""

    def __init__(
        self,
        project_id: str,
        location: str = "us",
        processor_id: str = None
    ):
        self.ocr = GoogleDocumentAIProvider(
            project_id=project_id,
            location=location,
            processor_id=processor_id
        )

    async def process(self, file_path: str) -> dict:
        result = await self.ocr.process_file(file_path)
        return {
            "text": result.full_text,
            "lines": result.lines,
            "metadata": result.metadata
        }
```

---

## LLM Patterns

### Basic Completion

```python
from penguin.llm import create_client, UserMessage, SystemMessage

async def simple_extraction(text: str, prompt: str) -> str:
    """Simple text-to-text extraction."""
    client = create_client("bedrock", model="claude-sonnet-4-5")

    result = await client.create([
        SystemMessage(prompt),
        UserMessage(text)
    ])

    return result.content
```

### Structured Output with Pydantic

```python
from penguin.llm import create_client, UserMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MedicalFinding(BaseModel):
    """Structured medical finding from document."""
    finding: str = Field(description="Description of the finding")
    location: str = Field(description="Body location or system")
    severity: Severity = Field(description="Clinical severity")
    icd_code: Optional[str] = Field(description="Related ICD-10 code")
    confidence: float = Field(ge=0, le=1, description="Confidence 0-1")
    source_text: str = Field(description="Original text from document")

class ExtractionResult(BaseModel):
    """Complete extraction result."""
    findings: List[MedicalFinding]
    summary: str
    document_type: str

async def extract_structured(text: str) -> ExtractionResult:
    """Extract structured data from medical text."""
    client = create_client("bedrock", model="claude-sonnet-4-5")

    result = await client.create(
        messages=[
            SystemMessage("""You are a medical document analyzer.
            Extract all medical findings with ICD-10 codes when applicable.
            Be precise with source_text - use exact quotes."""),
            UserMessage(f"Analyze this document:\n\n{text}")
        ],
        output_format=ExtractionResult
    )

    return result.content
```

### Multi-turn Conversation

```python
from penguin.llm import ChatSession, create_client

class ConversationalExtractor:
    """Multi-turn extraction with context."""

    def __init__(self, system_prompt: str):
        client = create_client("bedrock", model="claude-sonnet-4-5")
        self.session = ChatSession(client, system_instruction=system_prompt)

    async def extract_with_followup(self, text: str) -> dict:
        # Initial extraction
        response1 = await self.session.send(
            f"Analyze this document and identify key entities:\n\n{text}"
        )

        # Follow-up for clarification
        response2 = await self.session.send(
            "Now provide ICD-10 codes for each identified condition."
        )

        # Final summary
        response3 = await self.session.send(
            "Summarize the findings in a structured format."
        )

        return {
            "entities": response1.content,
            "codes": response2.content,
            "summary": response3.content
        }
```

### Streaming Response

```python
from penguin.llm import create_client, UserMessage

async def stream_extraction(text: str):
    """Stream extraction results."""
    client = create_client("bedrock", model="claude-sonnet-4-5")

    async for chunk in client.create_stream([
        UserMessage(f"Extract key information:\n\n{text}")
    ]):
        if chunk.delta_content:
            yield chunk.delta_content
```

### Extended Thinking (Claude Sonnet 4.5)

```python
from penguin.llm import create_client, UserMessage, SystemMessage

async def extract_with_reasoning(text: str) -> dict:
    """Extract with visible reasoning chain."""
    client = create_client("bedrock", model="claude-sonnet-4-5")

    result = await client.create(
        messages=[
            SystemMessage("Analyze the medical document step by step."),
            UserMessage(text)
        ],
        thinking=True  # Enable extended thinking
    )

    return {
        "reasoning": result.thinking,  # Internal reasoning
        "answer": result.content       # Final answer
    }
```

---

## Tool Definition Patterns

### Simple Tool

```python
from penguin.tools import tool

@tool
def lookup_icd_code(description: str) -> dict:
    """Look up ICD-10 code from description.

    Args:
        description: Medical condition description
    """
    # Mock implementation
    return {
        "code": "J06.9",
        "description": "Acute upper respiratory infection, unspecified",
        "category": "Diseases of the respiratory system"
    }
```

### Tool with Complex Types

```python
from penguin.tools import tool
from typing import List, Optional
from pydantic import BaseModel

class SearchResult(BaseModel):
    code: str
    description: str
    score: float

@tool
def search_medical_codes(
    query: str,
    code_system: str = "ICD-10",
    limit: int = 10,
    min_score: float = 0.5
) -> List[SearchResult]:
    """Search medical coding database.

    Args:
        query: Search query text
        code_system: Coding system (ICD-10, CPT, SNOMED)
        limit: Maximum results
        min_score: Minimum relevance score
    """
    # Implementation
    return [
        SearchResult(code="J06.9", description="...", score=0.95)
    ]
```

### Tool Execution

```python
from penguin.tools import ToolExecutor, tool
from penguin.llm import create_client, UserMessage

@tool
def get_patient_history(patient_id: str) -> dict:
    """Get patient medical history."""
    return {"conditions": [...], "medications": [...]}

@tool
def validate_diagnosis(code: str, symptoms: List[str]) -> bool:
    """Validate if diagnosis code matches symptoms."""
    return True

async def agent_with_tools(query: str):
    # Create executor with tools
    executor = ToolExecutor([get_patient_history, validate_diagnosis])

    # Create client
    client = create_client("bedrock", model="claude-sonnet-4-5")

    # First call with tools
    result = await client.create(
        messages=[UserMessage(query)],
        tools=executor.to_provider_format("bedrock")
    )

    # Handle tool calls
    if result.has_tool_calls:
        tool_results = await executor.execute_parallel(result.tool_calls)

        # Continue conversation with tool results
        messages = [
            UserMessage(query),
            result.to_message(),  # Assistant message with tool calls
        ]

        # Add tool results
        for tc, tr in zip(result.tool_calls, tool_results):
            messages.append(tr.to_message(tc.call_id))

        # Get final response
        final = await client.create(messages=messages)
        return final.content

    return result.content
```

---

## Bounding Box Patterns

### Convert OCR Bbox to PDFViewer Format

```python
def ocr_bbox_to_pdf_viewer(bbox: list) -> list:
    """Convert OCR bounding box to PDFViewer 8-point format.

    Input: [{x, y}, {x, y}, {x, y}, {x, y}] (4 corners)
    Output: [x1, y1, x2, y2, x3, y3, x4, y4] (8 values)
    """
    if len(bbox) != 4:
        raise ValueError("Expected 4 corner points")

    return [
        bbox[0]["x"], bbox[0]["y"],  # Top-left
        bbox[1]["x"], bbox[1]["y"],  # Top-right
        bbox[2]["x"], bbox[2]["y"],  # Bottom-right
        bbox[3]["x"], bbox[3]["y"]   # Bottom-left
    ]
```

### Map Extracted Text to Bounding Boxes

```python
from difflib import SequenceMatcher

def find_text_bbox(search_text: str, ocr_lines: list, threshold: float = 0.8) -> list:
    """Find bounding box for extracted text.

    Args:
        search_text: Text to find
        ocr_lines: List of OCRLine objects
        threshold: Similarity threshold

    Returns:
        List of matching bboxes with page numbers
    """
    matches = []
    search_lower = search_text.lower().strip()

    for line in ocr_lines:
        line_lower = line.content.lower().strip()

        # Check for exact substring match
        if search_lower in line_lower:
            matches.append({
                "coords": ocr_bbox_to_pdf_viewer(line.bounding_box),
                "page": line.page_number,
                "confidence": 1.0
            })
            continue

        # Check for fuzzy match
        ratio = SequenceMatcher(None, search_lower, line_lower).ratio()
        if ratio >= threshold:
            matches.append({
                "coords": ocr_bbox_to_pdf_viewer(line.bounding_box),
                "page": line.page_number,
                "confidence": ratio
            })

    return matches
```

### Merge Adjacent Bounding Boxes

```python
def merge_bboxes(bboxes: list, page: int) -> dict:
    """Merge multiple bboxes on same page into one.

    Useful when extracted text spans multiple OCR lines.
    """
    if not bboxes:
        return None

    same_page = [b for b in bboxes if b.get("page") == page]
    if not same_page:
        return None

    # Find bounding rectangle
    all_coords = [b["coords"] for b in same_page]

    min_x = min(c[0] for c in all_coords)  # Left
    min_y = min(c[1] for c in all_coords)  # Top
    max_x = max(c[2] for c in all_coords)  # Right
    max_y = max(c[5] for c in all_coords)  # Bottom

    return {
        "coords": [min_x, min_y, max_x, min_y, max_x, max_y, min_x, max_y],
        "page": page
    }
```

### Create PDFViewer BoundingBox Object

```python
def create_pdf_viewer_bbox(
    bboxes: list,
    document_name: str,
    labels: list = None,
    colors: list = None
) -> dict:
    """Create bounding box object for PDFViewer component.

    Args:
        bboxes: List of {"coords": [...], "page": int}
        document_name: PDF filename
        labels: Optional labels for each bbox
        colors: Optional colors for each bbox
    """
    # Group by page
    by_page = {}
    for i, bbox in enumerate(bboxes):
        page = bbox["page"]
        if page not in by_page:
            by_page[page] = {
                "bbox": [],
                "label": [],
                "color": []
            }

        by_page[page]["bbox"].append(bbox["coords"])
        by_page[page]["label"].append(labels[i] if labels else f"Evidence {i+1}")
        by_page[page]["color"].append(colors[i] if colors else "#fc459d")

    # Convert to PDFViewer format
    result = []
    for page, data in by_page.items():
        result.append({
            "page_number": page,
            "document_name": document_name,
            "bbox": data["bbox"],
            "label": data["label"],
            "color": data["color"]
        })

    return result
```

---

## Error Handling Patterns

### Retry with Exponential Backoff

```python
import asyncio
from functools import wraps

def retry_async(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for async retry with exponential backoff."""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        await asyncio.sleep(delay)

            raise last_error

        return wrapper
    return decorator

# Usage
@retry_async(max_retries=3)
async def process_with_retry(file_path: str):
    return await ocr.process_file(file_path)
```

### Graceful Degradation

```python
class RobustProcessor:
    """Processor with fallback options."""

    def __init__(self):
        self.primary_ocr = AWSTextractProvider()
        self.fallback_ocr = AzureOCRProvider()

    async def process(self, file_path: str) -> dict:
        # Try primary
        try:
            result = await self.primary_ocr.process_file(file_path)
            return {"success": True, "data": result, "provider": "aws"}
        except Exception as e:
            print(f"Primary OCR failed: {e}")

        # Try fallback
        try:
            result = await self.fallback_ocr.process_file(file_path)
            return {"success": True, "data": result, "provider": "azure"}
        except Exception as e:
            print(f"Fallback OCR failed: {e}")

        return {"success": False, "error": "All OCR providers failed"}
```

### Validation and Error Reporting

```python
from pydantic import BaseModel, ValidationError
from typing import List, Union

class ProcessingError(BaseModel):
    stage: str
    message: str
    details: dict = {}

class ProcessingResult(BaseModel):
    success: bool
    data: dict = None
    errors: List[ProcessingError] = []

async def validated_process(file_path: str) -> ProcessingResult:
    errors = []

    # Validate input
    if not file_path.endswith(('.pdf', '.png', '.jpg')):
        errors.append(ProcessingError(
            stage="validation",
            message="Unsupported file type",
            details={"file": file_path}
        ))
        return ProcessingResult(success=False, errors=errors)

    # OCR
    try:
        ocr_result = await ocr.process_file(file_path)
    except Exception as e:
        errors.append(ProcessingError(
            stage="ocr",
            message=str(e),
            details={"file": file_path}
        ))
        return ProcessingResult(success=False, errors=errors)

    # LLM
    try:
        extraction = await extract_codes(ocr_result.full_text)
    except Exception as e:
        errors.append(ProcessingError(
            stage="llm",
            message=str(e)
        ))
        return ProcessingResult(success=False, errors=errors)

    return ProcessingResult(
        success=True,
        data={"ocr": ocr_result, "extraction": extraction}
    )
```

---

## Async Patterns

### Concurrent Processing

```python
import asyncio
from typing import List

async def process_documents_concurrent(
    file_paths: List[str],
    max_concurrent: int = 5
) -> List[dict]:
    """Process multiple documents with controlled concurrency."""

    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_one(path: str) -> dict:
        async with semaphore:
            return await process_document(path)

    tasks = [process_one(path) for path in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [
        {"success": True, "data": r} if not isinstance(r, Exception)
        else {"success": False, "error": str(r)}
        for r in results
    ]
```

### Timeout Handling

```python
import asyncio

async def process_with_timeout(file_path: str, timeout: float = 60.0) -> dict:
    """Process with timeout."""
    try:
        result = await asyncio.wait_for(
            process_document(file_path),
            timeout=timeout
        )
        return {"success": True, "data": result}
    except asyncio.TimeoutError:
        return {"success": False, "error": f"Processing timed out after {timeout}s"}
```

### Progress Tracking

```python
from typing import AsyncIterator, Tuple

async def process_with_progress(
    file_paths: List[str]
) -> AsyncIterator[Tuple[int, int, dict]]:
    """Process documents with progress updates.

    Yields: (current, total, result)
    """
    total = len(file_paths)

    for i, path in enumerate(file_paths):
        result = await process_document(path)
        yield (i + 1, total, result)

# Usage
async def main():
    async for current, total, result in process_with_progress(files):
        print(f"Progress: {current}/{total}")
        print(f"Result: {result}")
```

---

## Complete Example: ICD Code Extraction Pipeline

```python
"""Complete ICD-10 code extraction pipeline."""

import asyncio
from penguin.ocr import AWSTextractProvider
from penguin.llm import create_client, UserMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import List, Optional

# Data Models
class BoundingBox(BaseModel):
    coords: List[float] = Field(description="8-point bbox [x1,y1,...,x4,y4]")
    page: int

class ICDCode(BaseModel):
    id: str
    question_number: str
    criteria: str
    answer: bool
    confidence: int = Field(ge=0, le=100)
    status: str = "pending"
    reason: List[str]
    supporting_sentence: List[str]
    bboxes: List[BoundingBox] = []

class ProcessedDocument(BaseModel):
    id: str
    intake_id: str
    patient_name: str
    full_text: str
    codes: List[ICDCode]
    pages: dict

# Pipeline
class ICDExtractionPipeline:
    SYSTEM_PROMPT = """You are a medical coding expert.
    Extract ICD-10 relevant criteria from medical documents.

    For each finding:
    1. Identify the medical criteria being evaluated
    2. Determine if the criteria is met (True/False)
    3. Provide confidence (0-100)
    4. List reasoning steps
    5. Quote exact supporting text from the document

    Be precise and use exact quotes for supporting_sentence.
    """

    def __init__(self):
        self.ocr = AWSTextractProvider(
            extract_tables=True,
            use_async_for_large_files=True
        )
        self.llm = create_client("bedrock", model="claude-sonnet-4-5")

    async def process(self, file_path: str, document_id: str) -> ProcessedDocument:
        # Step 1: OCR
        ocr_result = await self.ocr.process_file(file_path)

        # Step 2: Extract codes
        codes = await self._extract_codes(ocr_result.full_text)

        # Step 3: Map bounding boxes
        codes_with_bboxes = self._map_bboxes(codes, ocr_result.lines)

        # Step 4: Generate page URLs (placeholder)
        pages = self._generate_pages(file_path, len(set(l.page_number for l in ocr_result.lines)))

        return ProcessedDocument(
            id=f"doc_{document_id}",
            intake_id=document_id,
            patient_name="Patient",  # Extract from text
            full_text=ocr_result.full_text,
            codes=codes_with_bboxes,
            pages=pages
        )

    async def _extract_codes(self, text: str) -> List[ICDCode]:
        result = await self.llm.create(
            messages=[
                SystemMessage(self.SYSTEM_PROMPT),
                UserMessage(f"Document:\n\n{text}")
            ],
            output_format=List[ICDCode]
        )
        return result.content

    def _map_bboxes(self, codes: List[ICDCode], lines: list) -> List[ICDCode]:
        for code in codes:
            bboxes = []
            for sentence in code.supporting_sentence:
                for line in lines:
                    if sentence.lower()[:50] in line.content.lower():
                        bboxes.append(BoundingBox(
                            coords=self._to_8point(line.bounding_box),
                            page=line.page_number
                        ))
            code.bboxes = bboxes
        return codes

    def _to_8point(self, bbox: list) -> List[float]:
        return [
            bbox[0]["x"], bbox[0]["y"],
            bbox[1]["x"], bbox[1]["y"],
            bbox[2]["x"], bbox[2]["y"],
            bbox[3]["x"], bbox[3]["y"]
        ]

    def _generate_pages(self, file_path: str, num_pages: int) -> dict:
        # In production, generate presigned S3 URLs
        base = file_path.replace(".pdf", "")
        return {
            str(i): f"{base}_page_{i}.png"
            for i in range(1, num_pages + 1)
        }

# Usage
async def main():
    pipeline = ICDExtractionPipeline()
    result = await pipeline.process("medical_record.pdf", "9701")
    print(result.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(main())
```
