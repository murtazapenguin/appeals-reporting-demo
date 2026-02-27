"""
PDF Merger Utility for Appeal Package Generation

Merges multiple PDFs into a single package for appeal submission.
"""

from PyPDF2 import PdfReader, PdfWriter
import io
import logging
from typing import List

logger = logging.getLogger("pdf_merger")


async def merge_pdfs(pdf_files: List[io.BytesIO]) -> io.BytesIO:
    """
    Merge multiple PDFs into one.

    Args:
        pdf_files: List of BytesIO objects containing PDF data

    Returns:
        BytesIO containing the merged PDF
    """
    writer = PdfWriter()

    for idx, pdf_file in enumerate(pdf_files):
        try:
            pdf_file.seek(0)
            reader = PdfReader(pdf_file)
            for page in reader.pages:
                writer.add_page(page)
            logger.info(f"[PDF MERGE] Added PDF {idx + 1} ({len(reader.pages)} pages)")
        except Exception as e:
            logger.error(f"[PDF MERGE ERROR] Failed to add PDF {idx + 1}: {str(e)}")
            raise

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)

    logger.info(f"[PDF MERGE] Successfully merged {len(pdf_files)} PDFs")
    return output


async def merge_pdf_bytes(pdf_bytes_list: List[bytes]) -> bytes:
    """
    Merge multiple PDFs from raw bytes.

    Args:
        pdf_bytes_list: List of PDF file contents as bytes

    Returns:
        Merged PDF content as bytes
    """
    pdf_files = [io.BytesIO(pdf_bytes) for pdf_bytes in pdf_bytes_list]
    merged = await merge_pdfs(pdf_files)
    return merged.getvalue()
