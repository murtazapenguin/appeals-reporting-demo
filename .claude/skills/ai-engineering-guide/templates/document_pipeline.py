"""
Document Processing Pipeline Template using penguin-ai-sdk

Complete end-to-end pipeline for processing documents:
PDF → OCR → LLM Extraction → Structured Output with Bounding Boxes
"""

import asyncio
import os
import uuid
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

# penguin-ai-sdk imports
from penguin.ocr import AWSTextractProvider, OCRResult
from penguin.llm import create_client, UserMessage, SystemMessage

# Optional: pdf2image for manual PDF conversion
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False


# ============================================
# Data Models
# ============================================

class BoundingBox(BaseModel):
    """Bounding box in 8-point format for PDFViewer."""
    coords: List[float] = Field(description="8 values: [x1,y1,x2,y2,x3,y3,x4,y4]")
    page: int


class ExtractedCode(BaseModel):
    """Extracted ICD/medical code with evidence."""
    id: str = Field(default_factory=lambda: f"code_{uuid.uuid4().hex[:8]}")
    question_number: str
    criteria: str
    answer: bool
    confidence: int = Field(ge=0, le=100)
    status: str = "pending"
    reason: List[str]
    supporting_sentence: List[str]
    bboxes: List[BoundingBox] = []


class ProcessedDocument(BaseModel):
    """Complete processed document ready for frontend."""
    id: str
    intake_id: str
    patient_name: str
    date_of_birth: Optional[str] = None
    procedure: str = ""
    guideline: str = ""
    status: str = "pending"
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    full_text: str
    codes: List[ExtractedCode]
    pages: Dict[str, str]  # page_num -> image_url


# ============================================
# Pipeline Configuration
# ============================================

@dataclass
class PipelineConfig:
    """Configuration for document processing pipeline."""
    # OCR settings
    ocr_provider: str = "aws"
    aws_region: str = "us-east-1"
    aws_s3_bucket: Optional[str] = None
    extract_tables: bool = True
    extract_forms: bool = True

    # LLM settings
    llm_provider: str = "bedrock"
    llm_model: str = "claude-sonnet-4-5"
    temperature: float = 0.0
    max_tokens: int = 30000

    # Output settings
    output_dir: str = "/tmp/processed_docs"
    image_format: str = "png"
    image_dpi: int = 200


# ============================================
# Document Pipeline
# ============================================

class DocumentPipeline:
    """
    End-to-end document processing pipeline.

    Stages:
    1. OCR - Extract text and bounding boxes
    2. Image Generation - Convert PDF pages to images
    3. LLM Extraction - Extract structured data
    4. Bbox Mapping - Map extractions to bounding boxes
    5. Output - Generate final structured output

    Usage:
        pipeline = DocumentPipeline()
        result = await pipeline.process("document.pdf", "12345")
    """

    EXTRACTION_PROMPT = """You are a medical document analyzer specializing in ICD-10 coding criteria.

    For each medical finding in the document, provide:
    1. question_number: A sequential identifier (Q1, Q2, etc.)
    2. criteria: The medical criteria being evaluated
    3. answer: True if the criteria is met based on documentation, False otherwise
    4. confidence: Your confidence level (0-100)
    5. reason: List of reasoning steps that led to your conclusion
    6. supporting_sentence: Exact quotes from the document that support the finding

    IMPORTANT:
    - Use EXACT quotes for supporting_sentence - these will be used to find bounding boxes
    - Be thorough - identify all relevant medical findings
    - Only mark answer as True when there is clear documentation support
    """

    def __init__(self, config: PipelineConfig = None):
        self.config = config or PipelineConfig()

        # Initialize OCR
        self.ocr = AWSTextractProvider(
            region_name=self.config.aws_region,
            s3_bucket=self.config.aws_s3_bucket,
            extract_tables=self.config.extract_tables,
            extract_forms=self.config.extract_forms,
            use_async_for_large_files=True
        )

        # Initialize LLM
        self.llm = create_client(
            self.config.llm_provider,
            model=self.config.llm_model
        )

        # Ensure output directory exists
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

    async def process(
        self,
        file_path: str,
        document_id: str,
        patient_name: str = "Unknown Patient"
    ) -> ProcessedDocument:
        """
        Process a document through the complete pipeline.

        Args:
            file_path: Path to PDF or image file
            document_id: Unique identifier for the document
            patient_name: Patient name for the document

        Returns:
            ProcessedDocument ready for frontend consumption
        """
        # Stage 1: OCR
        print(f"[1/5] Running OCR on {file_path}...")
        ocr_result = await self._run_ocr(file_path)

        # Stage 2: Generate page images
        print("[2/5] Generating page images...")
        pages = await self._generate_pages(file_path, document_id, ocr_result)

        # Stage 3: LLM extraction
        print("[3/5] Extracting structured data with LLM...")
        raw_codes = await self._extract_codes(ocr_result.full_text)

        # Stage 4: Map bounding boxes
        print("[4/5] Mapping bounding boxes...")
        codes = self._map_bboxes(raw_codes, ocr_result.lines)

        # Stage 5: Build output
        print("[5/5] Building final output...")
        return ProcessedDocument(
            id=f"doc_{document_id}",
            intake_id=document_id,
            patient_name=patient_name,
            procedure=self._extract_procedure(ocr_result.full_text),
            status="pending",
            full_text=ocr_result.full_text,
            codes=codes,
            pages=pages
        )

    async def _run_ocr(self, file_path: str) -> OCRResult:
        """Run OCR on the document."""
        return await self.ocr.process_file(file_path)

    async def _generate_pages(
        self,
        file_path: str,
        document_id: str,
        ocr_result: OCRResult
    ) -> Dict[str, str]:
        """Generate page images from PDF."""
        pages = {}

        # Get unique page numbers from OCR
        page_numbers = sorted(set(line.page_number for line in ocr_result.lines))

        if file_path.lower().endswith('.pdf') and PDF2IMAGE_AVAILABLE:
            # Convert PDF to images
            images = convert_from_path(
                file_path,
                dpi=self.config.image_dpi
            )

            for i, image in enumerate(images):
                page_num = i + 1
                output_path = os.path.join(
                    self.config.output_dir,
                    f"{document_id}_page_{page_num}.{self.config.image_format}"
                )
                image.save(output_path, self.config.image_format.upper())
                pages[str(page_num)] = output_path
        else:
            # For images or when pdf2image unavailable, use placeholder URLs
            for page_num in page_numbers:
                pages[str(page_num)] = f"/test-images/{document_id}.pdf_page_{page_num}.png"

        return pages

    async def _extract_codes(self, text: str) -> List[ExtractedCode]:
        """Extract ICD codes using LLM."""
        result = await self.llm.create(
            messages=[
                SystemMessage(self.EXTRACTION_PROMPT),
                UserMessage(f"Analyze this medical document:\n\n{text}")
            ],
            output_format=List[ExtractedCode],
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )

        return result.content

    def _map_bboxes(
        self,
        codes: List[ExtractedCode],
        ocr_lines: List
    ) -> List[ExtractedCode]:
        """Map extracted codes to OCR bounding boxes."""
        for code in codes:
            bboxes = []

            for sentence in code.supporting_sentence:
                # Find matching OCR lines
                matches = self._find_text_in_lines(sentence, ocr_lines)
                bboxes.extend(matches)

            code.bboxes = bboxes

        return codes

    def _find_text_in_lines(
        self,
        search_text: str,
        ocr_lines: List,
        threshold: float = 0.6
    ) -> List[BoundingBox]:
        """Find text in OCR lines and return bounding boxes."""
        from difflib import SequenceMatcher

        matches = []
        search_lower = search_text.lower().strip()

        # Split search text into words for partial matching
        search_words = search_lower.split()

        for line in ocr_lines:
            line_lower = line.content.lower().strip()

            # Check for exact substring match
            if search_lower[:50] in line_lower:
                matches.append(BoundingBox(
                    coords=self._to_8point(line.bounding_box),
                    page=line.page_number
                ))
                continue

            # Check for word overlap
            line_words = line_lower.split()
            overlap = len(set(search_words) & set(line_words))
            if overlap >= len(search_words) * threshold:
                matches.append(BoundingBox(
                    coords=self._to_8point(line.bounding_box),
                    page=line.page_number
                ))
                continue

            # Fuzzy match for shorter texts
            if len(search_lower) < 100:
                ratio = SequenceMatcher(None, search_lower, line_lower).ratio()
                if ratio >= threshold:
                    matches.append(BoundingBox(
                        coords=self._to_8point(line.bounding_box),
                        page=line.page_number
                    ))

        return matches

    def _to_8point(self, bbox: List[Dict]) -> List[float]:
        """Convert 4-corner bbox to 8-point format."""
        if not bbox or len(bbox) != 4:
            return [0, 0, 0, 0, 0, 0, 0, 0]

        return [
            bbox[0].get("x", 0), bbox[0].get("y", 0),
            bbox[1].get("x", 0), bbox[1].get("y", 0),
            bbox[2].get("x", 0), bbox[2].get("y", 0),
            bbox[3].get("x", 0), bbox[3].get("y", 0)
        ]

    def _extract_procedure(self, text: str) -> str:
        """Extract procedure name from document (simple heuristic)."""
        lines = text.split('\n')[:20]  # Check first 20 lines
        for line in lines:
            lower = line.lower()
            if 'procedure' in lower or 'surgery' in lower or 'operation' in lower:
                return line.strip()
        return "Medical Document Review"


# ============================================
# Convenience Functions
# ============================================

async def process_document(
    file_path: str,
    document_id: str = None,
    patient_name: str = "Unknown Patient",
    config: PipelineConfig = None
) -> ProcessedDocument:
    """
    Quick function to process a document.

    Args:
        file_path: Path to PDF or image
        document_id: Optional document ID (auto-generated if not provided)
        patient_name: Patient name
        config: Optional pipeline configuration

    Returns:
        ProcessedDocument ready for frontend
    """
    if document_id is None:
        document_id = uuid.uuid4().hex[:8]

    pipeline = DocumentPipeline(config)
    return await pipeline.process(file_path, document_id, patient_name)


async def process_batch(
    file_paths: List[str],
    max_concurrency: int = 3,
    config: PipelineConfig = None
) -> List[ProcessedDocument]:
    """
    Process multiple documents in parallel.

    Args:
        file_paths: List of file paths
        max_concurrency: Maximum concurrent operations
        config: Optional pipeline configuration

    Returns:
        List of ProcessedDocument objects
    """
    pipeline = DocumentPipeline(config)
    semaphore = asyncio.Semaphore(max_concurrency)

    async def process_one(path: str) -> ProcessedDocument:
        async with semaphore:
            doc_id = Path(path).stem
            return await pipeline.process(path, doc_id)

    return await asyncio.gather(*[process_one(p) for p in file_paths])


# ============================================
# CLI Interface
# ============================================

if __name__ == "__main__":
    import sys
    import json

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python document_pipeline.py <file_path> [document_id]")
            print("\nExample:")
            print("  python document_pipeline.py medical_record.pdf 12345")
            sys.exit(1)

        file_path = sys.argv[1]
        document_id = sys.argv[2] if len(sys.argv) > 2 else None

        print(f"Processing: {file_path}")
        print("-" * 50)

        result = await process_document(file_path, document_id)

        print("\n=== Processing Complete ===")
        print(f"Document ID: {result.id}")
        print(f"Patient: {result.patient_name}")
        print(f"Pages: {len(result.pages)}")
        print(f"Codes extracted: {len(result.codes)}")

        print("\n=== Extracted Codes ===")
        for code in result.codes:
            print(f"\n{code.question_number}: {code.criteria[:60]}...")
            print(f"  Answer: {code.answer} ({code.confidence}% confidence)")
            print(f"  Evidence locations: {len(code.bboxes)} bounding boxes")

        # Save to JSON
        output_file = f"{result.intake_id}_processed.json"
        with open(output_file, 'w') as f:
            json.dump(result.model_dump(), f, indent=2)
        print(f"\nSaved to: {output_file}")

    asyncio.run(main())
