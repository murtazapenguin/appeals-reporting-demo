from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from bson import ObjectId
from typing import List, Optional
from datetime import datetime, timedelta
from models.denial import DenialCreate, DenialUpdate, DenialResponse, CSVUploadResponse
from routes.auth_routes import get_current_user
from utils.db_utils import denials_collection
import csv
import io
import logging

router = APIRouter(prefix="/api/denials", tags=["Denials"])
logger = logging.getLogger("denial_routes")

def denial_helper(denial) -> dict:
    """Convert MongoDB denial to response dict."""
    if not denial:
        return None

    return {
        "id": str(denial["_id"]),
        "claim_number": denial["claim_number"],
        "patient_name": denial["patient_name"],
        "patient_id": denial["patient_id"],
        "patient_dob": denial.get("patient_dob"),
        "provider_name": denial["provider_name"],
        "provider_id": denial.get("provider_id"),
        "provider_npi": denial.get("provider_npi"),
        "provider_address": denial.get("provider_address"),
        "provider_phone": denial.get("provider_phone"),
        "provider_tax_id": denial.get("provider_tax_id"),
        "provider_practice_name": denial.get("provider_practice_name"),
        "payer_name": denial["payer_name"],
        "payer_id": denial.get("payer_id"),
        "policy_number": denial.get("policy_number"),
        "group_number": denial.get("group_number"),
        "service_date": denial["service_date"],
        "denial_date": denial["denial_date"],
        "denial_code": denial.get("denial_code"),
        "denial_category": denial.get("denial_category", "medical_necessity"),
        "denial_reason": denial.get("denial_reason"),
        "claim_amount": denial.get("claim_amount", 0),
        "paid_amount": denial.get("paid_amount", 0),
        "denied_amount": denial.get("denied_amount", 0),
        "procedure_code": denial.get("procedure_code"),
        "diagnosis_codes": denial.get("diagnosis_codes", []),
        "service_description": denial.get("service_description"),
        "status": denial.get("status", "pending"),
        "win_probability": denial.get("win_probability"),
        "appeal_deadline": denial.get("appeal_deadline"),
        "priority": denial.get("priority", "normal"),
        "internal_notes": denial.get("internal_notes"),
        "submitted_at": denial.get("submitted_at"),
        "created_at": denial.get("created_at"),
        "updated_at": denial.get("updated_at"),
        "denial_extraction": denial.get("denial_extraction"),
        "provider_extraction": denial.get("provider_extraction")
    }

def calculate_appeal_deadline(denial_date: str) -> str:
    """Calculate appeal deadline (30 days from denial date)."""
    try:
        denial_dt = datetime.fromisoformat(denial_date.replace("Z", ""))
        deadline = denial_dt + timedelta(days=30)
        return deadline.isoformat()
    except:
        return None

@router.get("", response_model=List[DenialResponse])
async def get_denials(
    status: Optional[str] = None,
    payer: Optional[str] = None,
    category: Optional[str] = None,
    user=Depends(get_current_user)
):
    """Get all denials with optional filters."""
    query = {}

    if status:
        # Support comma-separated status values for multi-status filtering
        if "," in status:
            query["status"] = {"$in": status.split(",")}
        else:
            query["status"] = status
    if payer:
        query["payer_name"] = payer
    if category:
        query["denial_category"] = category

    denials = await denials_collection.find(query).to_list(1000)
    return [denial_helper(denial) for denial in denials]

@router.get("/{denial_id}", response_model=DenialResponse)
async def get_denial(denial_id: str, user=Depends(get_current_user)):
    """Get single denial by ID."""
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
    if not denial:
        raise HTTPException(status_code=404, detail="Denial not found")

    return denial_helper(denial)

@router.post("", response_model=dict)
async def create_denial(denial: DenialCreate, user=Depends(get_current_user)):
    """Create new denial (manual entry)."""
    logger.info(f"[CREATE DENIAL] Starting - Patient: {denial.patient_name}, Claim: {denial.claim_number}")

    denial_dict = denial.model_dump()
    denial_dict["status"] = "pending"
    denial_dict["created_at"] = datetime.utcnow()
    denial_dict["updated_at"] = datetime.utcnow()
    denial_dict["appeal_deadline"] = calculate_appeal_deadline(denial.denial_date)

    logger.info(f"[CREATE DENIAL] Inserting into database...")
    result = await denials_collection.insert_one(denial_dict)
    logger.info(f"[CREATE DENIAL] ✓ Inserted with ID: {result.inserted_id}")

    # Verify it was saved
    verify = await denials_collection.find_one({"_id": result.inserted_id})
    if verify:
        logger.info(f"[CREATE DENIAL] ✓ Verified denial exists in database")
    else:
        logger.error(f"[CREATE DENIAL] ✗ ERROR: Denial not found after insert!")

    return {
        "id": str(result.inserted_id),
        "claim_number": denial.claim_number,
        "status": "pending",
        "created_at": denial_dict["created_at"]
    }

@router.put("/{denial_id}", response_model=DenialResponse)
async def update_denial(
    denial_id: str,
    denial_update: DenialUpdate,
    user=Depends(get_current_user)
):
    """Update existing denial."""
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    update_data = {k: v for k, v in denial_update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.utcnow()

    result = await denials_collection.update_one(
        {"_id": ObjectId(denial_id)},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Denial not found")

    denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
    return denial_helper(denial)

@router.post("/upload-csv", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...), user=Depends(get_current_user)):
    """Bulk upload denials via CSV."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")

    content = await file.read()
    csv_data = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_data)

    imported_count = 0
    failed_count = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            # Validate required fields
            required_fields = [
                'claim_number', 'patient_name', 'patient_id', 'provider_name',
                'payer_name', 'service_date', 'denial_date', 'denial_category',
                'claim_amount', 'procedure_code', 'diagnosis_codes'
            ]

            missing_fields = [f for f in required_fields if not row.get(f)]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            denial_dict = {
                "claim_number": row['claim_number'],
                "patient_name": row['patient_name'],
                "patient_id": row['patient_id'],
                "patient_dob": row.get('patient_dob'),
                "provider_name": row['provider_name'],
                "provider_id": row.get('provider_id'),
                "payer_name": row['payer_name'],
                "payer_id": row.get('payer_id'),
                "policy_number": row.get('policy_number'),
                "group_number": row.get('group_number'),
                "service_date": row['service_date'],
                "denial_date": row['denial_date'],
                "denial_code": row.get('denial_code'),
                "denial_category": row['denial_category'],
                "denial_reason": row.get('denial_reason'),
                "claim_amount": float(row['claim_amount']),
                "paid_amount": float(row.get('paid_amount', 0)),
                "denied_amount": float(row.get('denied_amount', 0)),
                "procedure_code": row['procedure_code'],
                "diagnosis_codes": row['diagnosis_codes'],
                "service_description": row.get('service_description'),
                "priority": row.get('priority', 'normal'),
                "internal_notes": row.get('internal_notes'),
                "status": "pending",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "appeal_deadline": calculate_appeal_deadline(row['denial_date'])
            }

            await denials_collection.insert_one(denial_dict)
            imported_count += 1

        except Exception as e:
            failed_count += 1
            errors.append({
                "row": row_num,
                "error": str(e)
            })

    return CSVUploadResponse(
        imported_count=imported_count,
        failed_count=failed_count,
        errors=errors
    )


@router.post("/{denial_id}/extract-denial-info")
async def extract_denial_info(denial_id: str, user=Depends(get_current_user)):
    """
    Extract denial code and narrative from EOB documents.

    1. Find document_type='eob' for this denial
    2. Get OCR cache
    3. Run extraction
    4. Update denial record with denial_extraction field
    """
    from utils.db_utils import patient_documents_collection, ocr_cache_collection
    from services.ai_processor import get_processor

    try:
        # Get denial
        denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
        if not denial:
            raise HTTPException(status_code=404, detail="Denial not found")

        # Find EOB document for this denial
        eob_document = await patient_documents_collection.find_one({
            "denial_id": denial_id,
            "document_type": "eob"
        })

        if not eob_document:
            raise HTTPException(status_code=404, detail="No EOB document found for this denial")

        # Get OCR cache
        doc_id = str(eob_document["_id"])
        ocr_data = await ocr_cache_collection.find_one({"document_id": doc_id})

        if not ocr_data:
            raise HTTPException(status_code=404, detail="OCR data not available for EOB document")

        # Run extraction
        processor = get_processor()
        extraction_result = await processor.extract_denial_from_eob(eob_document, ocr_data)

        if not extraction_result:
            return {
                "success": False,
                "message": "No denial information could be extracted from the EOB document"
            }

        # Update denial record
        await denials_collection.update_one(
            {"_id": ObjectId(denial_id)},
            {
                "$set": {
                    "denial_extraction": extraction_result,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        logger.info(f"[EXTRACTION] Updated denial {denial_id} with denial extraction")

        return {
            "success": True,
            "extraction": extraction_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[EXTRACTION ERROR] Failed to extract denial info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


