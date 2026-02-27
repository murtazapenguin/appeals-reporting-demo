from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from bson import ObjectId
from datetime import datetime
from typing import Optional
from models.appeal import AppealLetter, AppealSubmitResponse, AppealSection, ProviderLetterhead, AppealSignature
from routes.auth_routes import get_current_user
from utils.db_utils import (
    appeal_packages_collection,
    denials_collection,
    criteria_evaluations_collection,
    patient_documents_collection
)
from utils.pdf_merger import merge_pdf_bytes
from utils.s3_storage import (
    download_from_s3,
    upload_to_s3,
    generate_presigned_url
)
from services.ai_processor import get_processor
import asyncio
import io
import logging
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Document type priority for package ordering
DOCUMENT_TYPE_ORDER = [
    'medical_records',
    'prior_visit_notes',
    'diagnostic_tests',
    'claim_form',
    'eob',
    'payer_policy',
    'clinical_guidelines',
    'prior_auth',
    'peer_reviewed',
    'denial_letter',
    'other'
]

router = APIRouter(prefix="/api/appeals", tags=["Appeals"])
logger = logging.getLogger("appeal_routes")

def appeal_helper(appeal) -> dict:
    """Convert MongoDB appeal to response dict."""
    if not appeal:
        return None

    return {
        "denial_id": appeal["denial_id"],
        "provider_letterhead": appeal["provider_letterhead"],
        "sections": appeal["sections"],
        "enclosed_documents": appeal["enclosed_documents"],
        "signature": appeal["signature"],
        "generated_at": appeal["generated_at"]
    }

async def _run_appeal_generation_background(denial_id: str, denial: dict, criteria_evaluation: dict, documents: list):
    """Run appeal letter generation as a background task."""
    try:
        gen_start = datetime.utcnow()
        await denials_collection.update_one(
            {"_id": ObjectId(denial_id)},
            {"$set": {
                "appeal_status": "processing",
                "appeal_error": None,
                "processing_timestamps.letter_generation_started_at": gen_start,
            }}
        )

        processor = get_processor()

        denial_data = {**denial, "_id": str(denial["_id"])}
        documents_data = [{**doc, "_id": str(doc["_id"])} for doc in documents]

        appeal_letter = await processor.generate_appeal_letter(
            denial_data=denial_data,
            criteria_evaluation=criteria_evaluation,
            documents=documents_data
        )

        # Save appeal letter
        await appeal_packages_collection.update_one(
            {"denial_id": denial_id},
            {"$set": appeal_letter},
            upsert=True
        )

        gen_end = datetime.utcnow()
        gen_seconds = (gen_end - gen_start).total_seconds()
        await denials_collection.update_one(
            {"_id": ObjectId(denial_id)},
            {
                "$set": {
                    "status": "appeal_ready",
                    "appeal_status": "completed",
                    "updated_at": gen_end,
                    "processing_timestamps.letter_generated_at": gen_end,
                    "processing_timestamps.letter_generation_seconds": gen_seconds,
                }
            }
        )

        logger.info(f"[APPEAL] Letter generated in {gen_seconds:.1f}s for denial {denial_id}")

    except Exception as e:
        logger.error(f"[APPEAL ERROR] Background generation failed for {denial_id}: {str(e)}")
        await denials_collection.update_one(
            {"_id": ObjectId(denial_id)},
            {"$set": {
                "appeal_status": "failed",
                "appeal_error": str(e)
            }}
        )


@router.post("/generate/{denial_id}")
async def generate_appeal_letter(denial_id: str, user=Depends(get_current_user)):
    """
    Kick off appeal letter generation as a background task.

    Returns immediately with status "processing". Frontend should poll
    GET /appeals/{denial_id} until results appear.
    """
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    logger.info(f"[APPEAL] Generating letter for denial {denial_id}")

    # 1. Get denial details
    denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
    if not denial:
        raise HTTPException(status_code=404, detail="Denial not found")

    # 2. Get criteria evaluation (must be done first)
    criteria_evaluation = await criteria_evaluations_collection.find_one({"denial_id": denial_id})
    if not criteria_evaluation:
        raise HTTPException(
            status_code=400,
            detail="Criteria evaluation not found. Please evaluate criteria first."
        )

    # 3. Get patient documents
    documents = await patient_documents_collection.find({
        "patient_id": denial.get("patient_id")
    }).to_list(1000)

    if not documents:
        logger.warning(f"[APPEAL] No documents found for patient {denial.get('patient_id')}")

    # 4. Guard against concurrent generations
    if denial.get("appeal_status") == "processing":
        return {"status": "processing", "denial_id": denial_id}

    # 5. Mark as processing and launch background task
    await denials_collection.update_one(
        {"_id": ObjectId(denial_id)},
        {"$set": {"appeal_status": "processing", "appeal_error": None}}
    )

    asyncio.create_task(
        _run_appeal_generation_background(denial_id, denial, criteria_evaluation, documents)
    )

    return {"status": "processing", "denial_id": denial_id}


@router.get("/status/{denial_id}")
async def get_appeal_status(denial_id: str, user=Depends(get_current_user)):
    """Get current appeal generation status for a denial."""
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    denial = await denials_collection.find_one(
        {"_id": ObjectId(denial_id)},
        {"appeal_status": 1, "appeal_error": 1}
    )
    if not denial:
        raise HTTPException(status_code=404, detail="Denial not found")

    return {
        "denial_id": denial_id,
        "status": denial.get("appeal_status", "idle"),
        "error": denial.get("appeal_error")
    }

@router.get("/{denial_id}", response_model=Optional[AppealLetter])
async def get_appeal_letter(denial_id: str, user=Depends(get_current_user)):
    """Get existing appeal letter."""
    appeal = await appeal_packages_collection.find_one({"denial_id": denial_id})

    if not appeal:
        return None

    return appeal_helper(appeal)

@router.get("/{denial_id}/pdf")
async def download_appeal_pdf(denial_id: str, user=Depends(get_current_user)):
    """Download appeal letter as PDF."""
    appeal = await appeal_packages_collection.find_one({"denial_id": denial_id})

    if not appeal:
        raise HTTPException(
            status_code=404,
            detail="No appeal letter found for this denial"
        )

    denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})

    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Add letterhead
    y = 750
    p.drawString(100, y, appeal["provider_letterhead"]["name"])
    y -= 20
    p.drawString(100, y, appeal["provider_letterhead"]["address"])
    y -= 20
    p.drawString(100, y, appeal["provider_letterhead"]["phone"])
    y -= 40

    # Add date
    p.drawString(100, y, datetime.now().strftime("%B %d, %Y"))
    y -= 40

    # Add RE: line
    p.drawString(100, y, f"RE: Appeal for Claim {denial['claim_number']}")
    y -= 20
    p.drawString(100, y, f"Patient: {denial['patient_name']}")
    y -= 40

    # Add sections
    for section in appeal["sections"]:
        if y < 100:
            p.showPage()
            y = 750

        p.drawString(100, y, section["title"])
        y -= 20

        # Wrap text
        words = section["content"].split()
        line = ""
        for word in words:
            if len(line + word) < 80:
                line += word + " "
            else:
                p.drawString(120, y, line)
                y -= 15
                line = word + " "
                if y < 100:
                    p.showPage()
                    y = 750
        if line:
            p.drawString(120, y, line)
            y -= 30

    # Add enclosed documents
    if y < 150:
        p.showPage()
        y = 750

    p.drawString(100, y, "Enclosed Documents:")
    y -= 20
    for doc in appeal["enclosed_documents"]:
        p.drawString(120, y, f"- {doc}")
        y -= 15

    # Add signature
    y -= 30
    p.drawString(100, y, "Sincerely,")
    y -= 40
    p.drawString(100, y, appeal["signature"]["name"])
    y -= 15
    p.drawString(100, y, appeal["signature"]["title"])

    p.save()
    buffer.seek(0)

    filename = f"appeal_{denial['claim_number']}.pdf"

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/{denial_id}/submit", response_model=AppealSubmitResponse)
async def submit_appeal(denial_id: str, user=Depends(get_current_user)):
    """Submit appeal to payer."""
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
    if not denial:
        raise HTTPException(status_code=404, detail="Denial not found")

    appeal = await appeal_packages_collection.find_one({"denial_id": denial_id})
    if not appeal:
        raise HTTPException(
            status_code=404,
            detail="No appeal letter found. Generate appeal first."
        )

    # Update denial status
    submitted_at = datetime.utcnow()
    confirmation_number = f"APPEAL-{datetime.now().strftime('%Y%m%d')}-{denial_id[:8].upper()}"

    await denials_collection.update_one(
        {"_id": ObjectId(denial_id)},
        {
            "$set": {
                "status": "submitted",
                "submitted_at": submitted_at,
                "updated_at": submitted_at
            }
        }
    )

    return AppealSubmitResponse(
        denial_id=denial_id,
        status="submitted",
        submitted_at=submitted_at,
        confirmation_number=confirmation_number
    )


@router.post("/{denial_id}/generate-package")
async def generate_appeal_package(denial_id: str, user=Depends(get_current_user)):
    """
    Generate final appeal package.

    Merges appeal letter PDF with all supporting documents in order:
    1. Appeal Letter (generated)
    2. Medical Records
    3. Prior Visit Notes
    4. Diagnostic Tests
    5. Claim Form (CMS-1500/UB-04)
    6. EOB/Remittance
    7. Payer Policy
    8. Clinical Guidelines
    9. Prior Authorization
    10. Peer-Reviewed Literature
    11. Other Documents
    """
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    logger.info(f"[PACKAGE] Generating package for denial {denial_id}")

    # 1. Get denial details
    denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
    if not denial:
        raise HTTPException(status_code=404, detail="Denial not found")

    # 2. Get appeal letter
    appeal = await appeal_packages_collection.find_one({"denial_id": denial_id})
    if not appeal:
        raise HTTPException(
            status_code=400,
            detail="No appeal letter found. Generate appeal letter first."
        )

    # 3. Generate appeal letter PDF
    letter_buffer = io.BytesIO()
    p = canvas.Canvas(letter_buffer, pagesize=letter)

    # Add letterhead
    y = 750
    p.drawString(100, y, appeal["provider_letterhead"]["name"])
    y -= 20
    p.drawString(100, y, appeal["provider_letterhead"]["address"])
    y -= 20
    p.drawString(100, y, appeal["provider_letterhead"]["phone"])
    y -= 40

    # Add date
    p.drawString(100, y, datetime.now().strftime("%B %d, %Y"))
    y -= 40

    # Add RE: line
    p.drawString(100, y, f"RE: Appeal for Claim {denial['claim_number']}")
    y -= 20
    p.drawString(100, y, f"Patient: {denial['patient_name']}")
    y -= 40

    # Add sections
    for section in appeal["sections"]:
        if y < 100:
            p.showPage()
            y = 750

        p.drawString(100, y, section["title"])
        y -= 20

        # Wrap text
        words = section["content"].split()
        line = ""
        for word in words:
            if len(line + word) < 80:
                line += word + " "
            else:
                p.drawString(120, y, line)
                y -= 15
                line = word + " "
                if y < 100:
                    p.showPage()
                    y = 750
        if line:
            p.drawString(120, y, line)
            y -= 30

    # Add enclosed documents
    if y < 150:
        p.showPage()
        y = 750

    p.drawString(100, y, "Enclosed Documents:")
    y -= 20
    for doc in appeal.get("enclosed_documents", []):
        p.drawString(120, y, f"- {doc}")
        y -= 15

    # Add signature
    y -= 30
    p.drawString(100, y, "Sincerely,")
    y -= 40
    p.drawString(100, y, appeal["signature"]["name"])
    y -= 15
    p.drawString(100, y, appeal["signature"]["title"])

    p.save()
    letter_buffer.seek(0)
    letter_pdf_bytes = letter_buffer.getvalue()

    # 4. Get all patient documents
    documents = await patient_documents_collection.find({
        "patient_id": denial.get("patient_id")
    }).to_list(1000)

    # 5. Sort documents by type order
    def get_doc_order(doc):
        doc_type = doc.get("document_type", "other")
        try:
            return DOCUMENT_TYPE_ORDER.index(doc_type)
        except ValueError:
            return len(DOCUMENT_TYPE_ORDER)

    sorted_docs = sorted(documents, key=get_doc_order)

    # 6. Collect all PDF bytes
    pdf_bytes_list = [letter_pdf_bytes]

    for doc in sorted_docs:
        s3_key = doc.get("s3_key")
        if s3_key:
            try:
                pdf_bytes = await download_from_s3(s3_key)
                pdf_bytes_list.append(pdf_bytes)
                logger.info(f"[PACKAGE] Added document: {doc.get('document_name')}")
            except Exception as e:
                logger.warning(f"[PACKAGE] Failed to download {doc.get('document_name')}: {str(e)}")

    # 7. Merge all PDFs
    try:
        merged_pdf = await merge_pdf_bytes(pdf_bytes_list)
        logger.info(f"[PACKAGE] Merged {len(pdf_bytes_list)} PDFs")
    except Exception as e:
        logger.error(f"[PACKAGE ERROR] Failed to merge PDFs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to merge PDFs: {str(e)}")

    # 8. Upload merged PDF to S3
    patient_id = denial.get("patient_id", "unknown")
    package_filename = f"appeal_package_{denial['claim_number']}.pdf"

    try:
        s3_result = await upload_to_s3(
            file_content=merged_pdf,
            patient_id=patient_id,
            document_id=f"package_{denial_id}",
            filename=package_filename
        )
        logger.info(f"[PACKAGE] Uploaded to S3: {s3_result['s3_uri']}")
    except Exception as e:
        logger.error(f"[PACKAGE ERROR] S3 upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload package: {str(e)}")

    # 9. Save package info to appeal record
    await appeal_packages_collection.update_one(
        {"denial_id": denial_id},
        {"$set": {
            "package_s3_key": s3_result["s3_key"],
            "package_s3_uri": s3_result["s3_uri"],
            "package_generated_at": datetime.utcnow(),
            "package_document_count": len(pdf_bytes_list)
        }}
    )

    # 10. Generate presigned URL for preview
    presigned_url = generate_presigned_url(s3_result["s3_key"])

    return {
        "success": True,
        "denial_id": denial_id,
        "package_url": presigned_url,
        "document_count": len(pdf_bytes_list),
        "s3_uri": s3_result["s3_uri"]
    }


@router.get("/{denial_id}/package")
async def get_appeal_package(
    denial_id: str,
    token: Optional[str] = Query(None),
    user=Depends(get_current_user)
):
    """
    Get the generated appeal package.

    Returns a presigned URL for the merged PDF package.
    """
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    appeal = await appeal_packages_collection.find_one({"denial_id": denial_id})

    if not appeal:
        raise HTTPException(
            status_code=404,
            detail="No appeal found for this denial"
        )

    package_s3_key = appeal.get("package_s3_key")
    if not package_s3_key:
        raise HTTPException(
            status_code=404,
            detail="No package generated. Generate package first."
        )

    presigned_url = generate_presigned_url(package_s3_key)

    return {
        "denial_id": denial_id,
        "package_url": presigned_url,
        "document_count": appeal.get("package_document_count", 0),
        "generated_at": appeal.get("package_generated_at")
    }


@router.get("/{denial_id}/package/download")
async def download_appeal_package(denial_id: str, user=Depends(get_current_user)):
    """
    Download the appeal package PDF directly.
    """
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    appeal = await appeal_packages_collection.find_one({"denial_id": denial_id})

    if not appeal:
        raise HTTPException(status_code=404, detail="No appeal found")

    package_s3_key = appeal.get("package_s3_key")
    if not package_s3_key:
        raise HTTPException(status_code=404, detail="No package generated")

    try:
        pdf_bytes = await download_from_s3(package_s3_key)
        denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
        filename = f"appeal_package_{denial['claim_number']}.pdf"

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"[PACKAGE ERROR] Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download package")
