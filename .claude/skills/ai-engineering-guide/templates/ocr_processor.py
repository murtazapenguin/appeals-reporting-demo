"""
OCR Processor Template using penguin-ai-sdk

This template provides a ready-to-use OCR processor with support for
multiple providers (AWS Textract, Azure, Google).
"""

import asyncio
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# penguin-ai-sdk imports
from penguin.ocr import AWSTextractProvider, AzureOCRProvider, OCRResult, OCRLine


@dataclass
class ProcessedLine:
    """Processed OCR line with normalized bounding box."""
    content: str
    page_number: int
    confidence: float
    bbox_8point: List[float]  # [x1, y1, x2, y2, x3, y3, x4, y4]


@dataclass
class OCROutput:
    """Standardized OCR output."""
    full_text: str
    lines: List[ProcessedLine]
    page_count: int
    provider: str
    metadata: Dict[str, Any]


class OCRProcessor:
    """
    Multi-provider OCR processor using penguin-ai-sdk.

    Supports:
    - AWS Textract (default, best for PDFs)
    - Azure Document Intelligence
    - Google Document AI

    Usage:
        processor = OCRProcessor(provider="aws")
        result = await processor.process("document.pdf")
    """

    def __init__(
        self,
        provider: str = "aws",
        # AWS options
        aws_region: str = "us-east-1",
        aws_s3_bucket: Optional[str] = None,
        extract_tables: bool = True,
        extract_forms: bool = True,
        # Azure options
        azure_endpoint: Optional[str] = None,
        azure_key: Optional[str] = None,
        # Google options
        google_project_id: Optional[str] = None,
        google_processor_id: Optional[str] = None
    ):
        self.provider_name = provider

        if provider == "aws":
            self.ocr = AWSTextractProvider(
                region_name=aws_region,
                s3_bucket=aws_s3_bucket,
                extract_tables=extract_tables,
                extract_forms=extract_forms,
                use_async_for_large_files=True,
                size_threshold_mb=10
            )
        elif provider == "azure":
            self.ocr = AzureOCRProvider(
                endpoint=azure_endpoint or os.getenv("AZURE_OCR_ENDPOINT"),
                key=azure_key or os.getenv("AZURE_OCR_SECRET_KEY"),
                model_id="prebuilt-read"
            )
        elif provider == "google":
            from penguin.ocr.providers.google import GoogleDocumentAIProvider
            self.ocr = GoogleDocumentAIProvider(
                project_id=google_project_id or os.getenv("GOOGLE_PROJECT_ID"),
                processor_id=google_processor_id
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def process(self, file_path: str) -> OCROutput:
        """
        Process a document and return standardized output.

        Args:
            file_path: Path to PDF or image file

        Returns:
            OCROutput with full text, lines with bboxes, and metadata
        """
        result = await self.ocr.process_file(file_path)
        return self._normalize_result(result)

    async def process_batch(
        self,
        file_paths: List[str],
        max_concurrency: int = 5
    ) -> List[OCROutput]:
        """
        Process multiple documents in parallel.

        Args:
            file_paths: List of file paths
            max_concurrency: Maximum concurrent operations

        Returns:
            List of OCROutput objects
        """
        results = await self.ocr.process_batch(
            file_paths,
            max_concurrency=max_concurrency
        )
        return [self._normalize_result(r) for r in results]

    def _normalize_result(self, result: OCRResult) -> OCROutput:
        """Convert OCRResult to standardized OCROutput."""
        lines = []
        page_numbers = set()

        for line in result.lines:
            page_numbers.add(line.page_number)
            lines.append(ProcessedLine(
                content=line.content,
                page_number=line.page_number,
                confidence=line.confidence or 0.0,
                bbox_8point=self._to_8point(line.bounding_box)
            ))

        return OCROutput(
            full_text=result.full_text,
            lines=lines,
            page_count=len(page_numbers),
            provider=result.provider,
            metadata=result.metadata
        )

    def _to_8point(self, bbox: List[Dict]) -> List[float]:
        """
        Convert 4-corner bbox to 8-point format.

        Input: [{x, y}, {x, y}, {x, y}, {x, y}]
        Output: [x1, y1, x2, y2, x3, y3, x4, y4]
        """
        if not bbox or len(bbox) != 4:
            return [0, 0, 0, 0, 0, 0, 0, 0]

        return [
            bbox[0].get("x", 0), bbox[0].get("y", 0),
            bbox[1].get("x", 0), bbox[1].get("y", 0),
            bbox[2].get("x", 0), bbox[2].get("y", 0),
            bbox[3].get("x", 0), bbox[3].get("y", 0)
        ]

    def get_text_by_page(self, output: OCROutput) -> Dict[int, str]:
        """Group full text by page number."""
        pages = {}
        for line in output.lines:
            page = line.page_number
            if page not in pages:
                pages[page] = []
            pages[page].append(line.content)

        return {page: "\n".join(lines) for page, lines in pages.items()}

    def find_text_location(
        self,
        output: OCROutput,
        search_text: str,
        fuzzy_threshold: float = 0.8
    ) -> List[Dict]:
        """
        Find bounding box for text in OCR output.

        Args:
            output: OCR output to search
            search_text: Text to find
            fuzzy_threshold: Similarity threshold for fuzzy matching

        Returns:
            List of matches with bbox and page
        """
        from difflib import SequenceMatcher

        matches = []
        search_lower = search_text.lower().strip()

        for line in output.lines:
            line_lower = line.content.lower().strip()

            # Exact substring match
            if search_lower in line_lower:
                matches.append({
                    "coords": line.bbox_8point,
                    "page": line.page_number,
                    "confidence": 1.0,
                    "matched_text": line.content
                })
                continue

            # Fuzzy match
            ratio = SequenceMatcher(None, search_lower, line_lower).ratio()
            if ratio >= fuzzy_threshold:
                matches.append({
                    "coords": line.bbox_8point,
                    "page": line.page_number,
                    "confidence": ratio,
                    "matched_text": line.content
                })

        return matches


# Convenience function
async def process_document(
    file_path: str,
    provider: str = "aws"
) -> OCROutput:
    """
    Quick function to process a document.

    Args:
        file_path: Path to document
        provider: OCR provider ("aws", "azure", "google")

    Returns:
        OCROutput with text and bounding boxes
    """
    processor = OCRProcessor(provider=provider)
    return await processor.process(file_path)


# CLI usage
if __name__ == "__main__":
    import sys

    async def main():
        if len(sys.argv) < 2:
            print("Usage: python ocr_processor.py <file_path> [provider]")
            sys.exit(1)

        file_path = sys.argv[1]
        provider = sys.argv[2] if len(sys.argv) > 2 else "aws"

        print(f"Processing {file_path} with {provider}...")
        result = await process_document(file_path, provider)

        print(f"\n=== OCR Result ===")
        print(f"Provider: {result.provider}")
        print(f"Pages: {result.page_count}")
        print(f"Lines: {len(result.lines)}")
        print(f"\n=== Full Text ===\n{result.full_text[:500]}...")

    asyncio.run(main())
