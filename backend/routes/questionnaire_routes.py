from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from typing import Optional, List
from routes.auth_routes import get_current_user
from utils.db_utils import questionnaires_collection

router = APIRouter(prefix="/api/questionnaires", tags=["Questionnaires"])


def questionnaire_helper(q) -> dict:
    """Convert MongoDB questionnaire document to response dict."""
    if not q:
        return None
    return {
        "id": str(q["_id"]),
        "source_file": q.get("source_file", ""),
        "guideline_name": q.get("guideline_name", ""),
        "line_of_business": q.get("line_of_business", []),
        "cpt_codes": q.get("cpt_codes", []),
        "hcpcs_codes": q.get("hcpcs_codes", []),
        "icd_10_codes": q.get("icd_10_codes", []),
        "total_evaluatable_questions": q.get("total_evaluatable_questions"),
        "max_depth": q.get("max_depth"),
        "guidelines": q.get("guidelines"),
    }


@router.get("")
async def list_questionnaires(
    cpt_code: Optional[str] = Query(None, description="Filter by CPT code"),
    user=Depends(get_current_user),
):
    """List all questionnaires, optionally filtered by CPT code."""
    query = {}
    if cpt_code:
        query["cpt_codes"] = cpt_code

    questionnaires = await questionnaires_collection.find(query).to_list(100)
    return [questionnaire_helper(q) for q in questionnaires]


@router.get("/lookup")
async def lookup_questionnaire(
    cpt_code: str = Query(..., description="CPT code to look up"),
    user=Depends(get_current_user),
):
    """Find questionnaire(s) matching a CPT code."""
    questionnaires = await questionnaires_collection.find(
        {"cpt_codes": cpt_code}
    ).to_list(10)

    if not questionnaires:
        raise HTTPException(
            status_code=404,
            detail=f"No questionnaire found for CPT code {cpt_code}",
        )

    return [questionnaire_helper(q) for q in questionnaires]


@router.get("/{questionnaire_id}")
async def get_questionnaire(
    questionnaire_id: str,
    user=Depends(get_current_user),
):
    """Get a questionnaire by ID."""
    if not ObjectId.is_valid(questionnaire_id):
        raise HTTPException(status_code=400, detail="Invalid questionnaire ID")

    q = await questionnaires_collection.find_one({"_id": ObjectId(questionnaire_id)})
    if not q:
        raise HTTPException(status_code=404, detail="Questionnaire not found")

    return questionnaire_helper(q)
