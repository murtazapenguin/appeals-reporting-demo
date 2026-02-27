from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from fastapi.responses import Response, RedirectResponse
from bson import ObjectId
from typing import List, Optional
from datetime import datetime
import os
import tempfile
import logging
import io
from pdf2image import convert_from_path
from models.document import PatientDocument, DocumentPagesResponse
from routes.auth_routes import get_current_user
from jwt_handler import verify_token
from utils.db_utils import patient_documents_collection, denials_collection, users_collection
from utils.s3_storage import (
    upload_to_s3,
    download_from_s3,
    download_to_temp_file,
    generate_presigned_url,
    get_s3_key,
    check_page_image_exists,
    upload_page_image,
    get_page_image_presigned_url
)
from services.ai_processor import get_processor

router = APIRouter(prefix="/api/documents", tags=["Documents"])
logger = logging.getLogger("document_routes")

# Limit concurrent PDF conversions to prevent memory overload
import asyncio
from concurrent.futures import ThreadPoolExecutor

PDF_CONVERSION_SEMAPHORE = asyncio.Semaphore(2)  # Max 2 concurrent conversions
PDF_THREAD_POOL = ThreadPoolExecutor(max_workers=2)  # Thread pool for CPU-bound conversion

async def get_user_from_token_param(token: Optional[str] = Query(None)):
    """Authenticate via query parameter token for image endpoints."""
    if not token:
        return None
    user_id = verify_token(token)
    if not user_id:
        return None
    user = await users_collection.find_one({"_id": ObjectId(user_id)})
    return user

def document_helper(doc) -> dict:
    """Convert MongoDB document to response dict."""
    if not doc:
        return None

    return {
        "id": str(doc["_id"]),
        "denial_id": doc["denial_id"],
        "patient_id": doc.get("patient_id"),
        "document_name": doc["document_name"],
        "document_type": doc["document_type"],
        "document_date": doc["document_date"],
        "presigned_urls": doc.get("presigned_urls", {}),
        "total_pages": doc.get("total_pages", 0),
        "uploaded_at": doc.get("uploaded_at"),
        "s3_key": doc.get("s3_key"),
        "s3_uri": doc.get("s3_uri")
    }

@router.get("/denial/{denial_id}", response_model=List[dict])
async def get_documents_for_denial(denial_id: str, user=Depends(get_current_user)):
    """Get all documents for a denial."""
    documents = await patient_documents_collection.find({"denial_id": denial_id}).to_list(1000)
    return [document_helper(doc) for doc in documents]

@router.get("/denial/{denial_id}/date-range", response_model=List[dict])
async def get_documents_by_date_range(
    denial_id: str,
    start_date: str = Query(...),
    end_date: str = Query(...),
    user=Depends(get_current_user)
):
    """Get documents within date range."""
    documents = await patient_documents_collection.find({
        "denial_id": denial_id,
        "document_date": {
            "$gte": start_date,
            "$lte": end_date
        }
    }).to_list(1000)

    return [document_helper(doc) for doc in documents]

@router.get("/{document_id}/pages", response_model=DocumentPagesResponse)
async def get_document_pages(document_id: str, user=Depends(get_current_user)):
    """Get page images for a document."""
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=400, detail="Invalid document ID")

    doc = await patient_documents_collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentPagesResponse(
        document_id=str(doc["_id"]),
        document_name=doc["document_name"],
        pages=doc.get("presigned_urls", {})
    )


@router.get("/{document_id}/pdf")
async def get_document_pdf(
    document_id: str,
    token: Optional[str] = Query(None)
):
    """
    Get the PDF file directly from S3.
    Returns a presigned URL for the PDF.
    """
    if token:
        user = await get_user_from_token_param(token)
        if not user:
            logger.warning(f"[PDF] Invalid token provided for document {document_id}")

    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=400, detail="Invalid document ID")

    doc = await patient_documents_collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    s3_key = doc.get("s3_key")
    file_path = doc.get("file_path")

    # Try S3 first, fallback to local file
    if s3_key:
        try:
            content = await download_from_s3(s3_key)
            return Response(
                content=content,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f'inline; filename="{doc["document_name"]}"',
                    "Cache-Control": "public, max-age=3600"
                }
            )
        except Exception as e:
            logger.error(f"[PDF ERROR] Failed to get from S3: {str(e)}")

    # Fallback to local file
    if file_path and os.path.exists(file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{doc["document_name"]}"',
                "Cache-Control": "public, max-age=3600"
            }
        )

    raise HTTPException(status_code=404, detail="PDF file not found")


@router.get("/{document_id}/presigned-url")
async def get_presigned_url(document_id: str, user=Depends(get_current_user)):
    """
    Get a presigned URL for direct S3 access to the PDF.
    """
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=400, detail="Invalid document ID")

    doc = await patient_documents_collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    s3_key = doc.get("s3_key")
    if not s3_key:
        raise HTTPException(status_code=404, detail="Document not stored in S3")

    try:
        url = generate_presigned_url(s3_key)
        return {"presigned_url": url, "expires_in": 3600}
    except Exception as e:
        logger.error(f"[PRESIGN ERROR] {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate presigned URL")


@router.get("/{document_id}/page/{page_number}/image")
async def get_document_page_image(
    document_id: str,
    page_number: int,
    token: Optional[str] = Query(None)
):
    """
    Get a specific page of a PDF document as a PNG image.

    Uses S3 caching: checks for cached image first, converts and caches if not found.
    Supports token authentication via query parameter for img tags.
    """
    if token:
        user = await get_user_from_token_param(token)
        if not user:
            logger.warning(f"[PAGE IMAGE] Invalid token provided for document {document_id}")

    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=400, detail="Invalid document ID")

    doc = await patient_documents_collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    patient_id = doc.get("patient_id", "unknown")
    s3_key = doc.get("s3_key")
    file_path = doc.get("file_path")
    temp_file = None

    # Check if cached image exists in S3
    try:
        cache_exists = await check_page_image_exists(patient_id, document_id, page_number)
        if cache_exists:
            logger.info(f"[PAGE IMAGE] Cache hit for {document_id} page {page_number}")
            presigned_url = get_page_image_presigned_url(patient_id, document_id, page_number)
            return RedirectResponse(url=presigned_url, status_code=302)
    except Exception as e:
        logger.warning(f"[PAGE IMAGE] Cache check failed, will convert: {str(e)}")

    # Cache miss - need to convert and cache
    # Use semaphore to limit concurrent conversions (prevent memory overload)
    logger.info(f"[PAGE IMAGE] Cache miss for {document_id} page {page_number}, waiting for semaphore...")

    async with PDF_CONVERSION_SEMAPHORE:
        logger.info(f"[PAGE IMAGE] Converting {document_id} page {page_number}...")
        try:
            # Download PDF from S3
            if s3_key:
                try:
                    temp_file = await download_to_temp_file(s3_key)
                    file_path = temp_file
                except Exception as e:
                    logger.warning(f"[PAGE IMAGE] S3 download failed, trying local: {str(e)}")

            # Check local file
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="PDF file not found")

            # Convert specific page to image (run in thread pool to avoid blocking)
            loop = asyncio.get_event_loop()
            images = await loop.run_in_executor(
                PDF_THREAD_POOL,
                lambda: convert_from_path(
                    file_path,
                    first_page=page_number,
                    last_page=page_number,
                    dpi=100  # Lower DPI for faster conversion
                )
            )

            if not images:
                raise HTTPException(status_code=404, detail=f"Page {page_number} not found")

            # Convert PIL image to PNG bytes
            img_buffer = io.BytesIO()
            images[0].save(img_buffer, format='PNG', optimize=True)
            img_bytes = img_buffer.getvalue()

            # Upload to S3 cache
            try:
                await upload_page_image(img_bytes, patient_id, document_id, page_number)
                logger.info(f"[PAGE IMAGE] Cached {document_id} page {page_number} to S3")
            except Exception as e:
                logger.warning(f"[PAGE IMAGE] Failed to cache to S3: {str(e)}")

            return Response(
                content=img_bytes,
                media_type="image/png",
                headers={
                    "Cache-Control": "public, max-age=31536000"
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"[PAGE IMAGE ERROR] Failed to convert page {page_number} of {document_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to convert page: {str(e)}")
        finally:
            # Clean up temp file from S3 download
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass


@router.get("/{document_id}/page-count")
async def get_document_page_count(document_id: str, user=Depends(get_current_user)):
    """Get the total number of pages in a PDF document."""
    if not ObjectId.is_valid(document_id):
        raise HTTPException(status_code=400, detail="Invalid document ID")

    doc = await patient_documents_collection.find_one({"_id": ObjectId(document_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return cached page count if available
    if doc.get("total_pages"):
        return {"document_id": document_id, "page_count": doc["total_pages"]}

    s3_key = doc.get("s3_key")
    file_path = doc.get("file_path")
    temp_file = None

    try:
        # Try S3 first
        if s3_key:
            try:
                temp_file = await download_to_temp_file(s3_key)
                file_path = temp_file
            except Exception as e:
                logger.warning(f"[PAGE COUNT] S3 download failed: {str(e)}")

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="PDF file not found")

        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        page_count = len(reader.pages)

        # Cache the page count in database
        await patient_documents_collection.update_one(
            {"_id": ObjectId(document_id)},
            {"$set": {"total_pages": page_count}}
        )

        return {"document_id": document_id, "page_count": page_count}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[PAGE COUNT ERROR] Failed to get page count: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get page count")
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


@router.get("/patient/{patient_id}", response_model=List[dict])
async def get_documents_by_patient(patient_id: str, user=Depends(get_current_user)):
    """Get all documents for a patient."""
    documents = await patient_documents_collection.find({"patient_id": patient_id}).to_list(1000)

    result = []
    for doc in documents:
        doc_id = str(doc["_id"])
        s3_key = doc.get("s3_key")
        file_path = doc.get("file_path")
        page_count = doc.get("total_pages", 1)

        # If page count not cached and we have a file, try to get it
        if page_count == 1 and (s3_key or (file_path and os.path.exists(file_path))):
            # Use cached value or default, don't download just to count
            page_count = doc.get("total_pages", 1)

        # Generate presigned_urls pointing to our page image endpoint
        presigned_urls = {}
        for i in range(1, page_count + 1):
            presigned_urls[str(i)] = f"/api/documents/{doc_id}/page/{i}/image"

        result.append({
            "id": doc_id,
            "patient_id": doc.get("patient_id"),
            "document_name": doc.get("document_name"),
            "document_type": doc.get("document_type"),
            "document_date": doc.get("document_date"),
            "file_path": file_path,
            "s3_key": s3_key,
            "s3_uri": doc.get("s3_uri"),
            "total_pages": page_count,
            "presigned_urls": presigned_urls,
            "uploaded_at": doc.get("uploaded_at")
        })

    return result


@router.post("/cache-ocr/{patient_id}")
async def cache_ocr_for_patient(
    patient_id: str,
    user=Depends(get_current_user)
):
    """
    Trigger OCR caching for all documents of a patient.

    Downloads documents from S3 and processes them with OCR.
    """
    logger.info(f"[OCR CACHE] Starting OCR caching for patient {patient_id}")

    documents = await patient_documents_collection.find({"patient_id": patient_id}).to_list(1000)

    if not documents:
        raise HTTPException(status_code=404, detail=f"No documents found for patient {patient_id}")

    processor = get_processor()
    cached_count = 0
    failed_count = 0

    for doc in documents:
        doc_id = str(doc["_id"])
        s3_key = doc.get("s3_key")
        file_path = doc.get("file_path")
        temp_file = None

        try:
            # Try S3 first
            if s3_key:
                temp_file = await download_to_temp_file(s3_key)
                file_path = temp_file
            elif not file_path or not os.path.exists(file_path):
                logger.warning(f"[OCR CACHE] No file found for document {doc_id}")
                failed_count += 1
                continue

            await processor.process_document_with_cache(
                file_path=file_path,
                document_id=doc_id,
                patient_id=patient_id
            )
            cached_count += 1
            logger.info(f"[OCR CACHE] Cached document {doc_id}")

        except Exception as e:
            logger.error(f"[OCR CACHE ERROR] Failed for document {doc_id}: {str(e)}")
            failed_count += 1
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

    return {
        "success": True,
        "patient_id": patient_id,
        "total_documents": len(documents),
        "cached": cached_count,
        "failed": failed_count
    }


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    denial_id: str = Form(...),
    patient_id: str = Form(...),
    document_type: str = Form(...),
    document_date: str = Form(...),
    user=Depends(get_current_user)
):
    """
    Upload and process a patient document.

    Uploads to S3 and processes with OCR using penguin-ai-sdk.
    """
    logger.info(f"[UPLOAD] Uploading document for patient {patient_id}")

    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file content
    file_content = await file.read()
    document_id = str(ObjectId())

    # Upload to S3
    try:
        s3_result = await upload_to_s3(
            file_content=file_content,
            patient_id=patient_id,
            document_id=document_id,
            filename=file.filename
        )
        logger.info(f"[UPLOAD] Uploaded to S3: {s3_result['s3_uri']}")
    except Exception as e:
        logger.error(f"[UPLOAD ERROR] S3 upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")

    # Save to temp file for OCR processing
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_content)
            temp_file = tmp.name

        # Process with OCR
        processor = get_processor()
        ocr_result = await processor.process_document_with_cache(
            file_path=temp_file,
            document_id=document_id,
            patient_id=patient_id
        )

        # Get page count
        from PyPDF2 import PdfReader
        reader = PdfReader(temp_file)
        page_count = len(reader.pages)

        # Create document record
        # Extract lines from all pages
        all_lines = [line for page in ocr_result.get("pages", []) for line in page.get("lines", [])]

        document = {
            "_id": ObjectId(document_id),
            "denial_id": denial_id,
            "patient_id": patient_id,
            "document_name": file.filename,
            "document_type": document_type,
            "document_date": document_date,
            "s3_key": s3_result["s3_key"],
            "s3_uri": s3_result["s3_uri"],
            "s3_bucket": s3_result["bucket"],
            "full_text": ocr_result.get("full_text", ""),
            "lines": all_lines,
            "total_pages": page_count,
            "presigned_urls": {},
            "uploaded_at": datetime.utcnow(),
            "processed_at": ocr_result.get("ocr_timestamp")
        }

        # Save to database
        await patient_documents_collection.insert_one(document)

        logger.info(f"[UPLOAD] Document {document_id} processed and saved to S3")

        # Auto-trigger extraction for EOB documents only
        try:
            if document_type == "eob":
                # Auto-extract denial code + narrative from EOB
                logger.info(f"[AUTO-EXTRACT] Triggering denial extraction for EOB document {document_id}")
                extraction_result = await processor.extract_denial_from_eob(document, ocr_result)

                if extraction_result and extraction_result.get("denial_code"):
                    await denials_collection.update_one(
                        {"_id": ObjectId(denial_id)},
                        {
                            "$set": {
                                "denial_extraction": extraction_result,
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
                    logger.info(f"[AUTO-EXTRACT] Successfully extracted denial info: {extraction_result.get('denial_code')}")
                else:
                    logger.warning(f"[AUTO-EXTRACT] No denial information extracted from EOB {document_id}")

        except Exception as e:
            # Don't block upload on extraction failure - just log warning
            logger.warning(f"[AUTO-EXTRACT] Extraction failed but continuing: {str(e)}")

        return {
            "success": True,
            "document_id": document_id,
            "document_name": file.filename,
            "s3_uri": s3_result["s3_uri"],
            "total_pages": page_count,
            "text_length": len(ocr_result.get("full_text", ""))
        }

    except Exception as e:
        logger.error(f"[UPLOAD ERROR] Failed to process document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)


@router.post("/migrate-to-s3")
async def migrate_documents_to_s3(user=Depends(get_current_user)):
    """
    Migrate existing local documents to S3.

    Finds all documents with file_path but no s3_key and uploads them.
    """
    logger.info("[MIGRATE] Starting migration of local documents to S3")

    # Find documents with local file but no S3 key
    documents = await patient_documents_collection.find({
        "file_path": {"$exists": True, "$ne": None},
        "s3_key": {"$exists": False}
    }).to_list(1000)

    if not documents:
        return {"success": True, "message": "No documents to migrate", "migrated": 0}

    migrated = 0
    failed = 0

    for doc in documents:
        doc_id = str(doc["_id"])
        file_path = doc.get("file_path")
        patient_id = doc.get("patient_id", "unknown")
        filename = doc.get("document_name", os.path.basename(file_path))

        if not file_path or not os.path.exists(file_path):
            logger.warning(f"[MIGRATE] File not found: {file_path}")
            failed += 1
            continue

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            s3_result = await upload_to_s3(
                file_content=file_content,
                patient_id=patient_id,
                document_id=doc_id,
                filename=filename
            )

            # Update document with S3 info
            await patient_documents_collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {
                    "s3_key": s3_result["s3_key"],
                    "s3_uri": s3_result["s3_uri"],
                    "s3_bucket": s3_result["bucket"]
                }}
            )

            migrated += 1
            logger.info(f"[MIGRATE] Migrated {doc_id} to S3")

        except Exception as e:
            logger.error(f"[MIGRATE ERROR] Failed to migrate {doc_id}: {str(e)}")
            failed += 1

    return {
        "success": True,
        "total": len(documents),
        "migrated": migrated,
        "failed": failed
    }
