from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from typing import List, Optional
from models.medical_policy import MedicalPolicyResponse
from routes.auth_routes import get_current_user
from utils.db_utils import medical_policies_collection

router = APIRouter(prefix="/api/medical-policies", tags=["Medical Policies"])

def policy_helper(policy) -> dict:
    """Convert MongoDB policy to response dict."""
    if not policy:
        return None

    # Normalize criteria: map 'question' -> 'description' if needed
    criteria = []
    for c in policy.get("criteria", []):
        c = dict(c)
        if "question" in c and "description" not in c:
            c["description"] = c.pop("question")
        criteria.append(c)

    return {
        "id": str(policy["_id"]),
        "payer_id": policy["payer_id"],
        "payer_name": policy["payer_name"],
        "cpt_code": policy["cpt_code"],
        "procedure_name": policy.get("procedure_name"),
        "policy_number": policy.get("policy_number"),
        "criteria": criteria
    }

@router.get("", response_model=List[MedicalPolicyResponse])
async def get_medical_policies(user=Depends(get_current_user)):
    """List all medical policies."""
    policies = await medical_policies_collection.find({}).to_list(1000)
    return [policy_helper(policy) for policy in policies]

@router.get("/lookup", response_model=MedicalPolicyResponse)
async def lookup_policy(
    payer_id: str = Query(...),
    cpt_code: str = Query(...),
    user=Depends(get_current_user)
):
    """Lookup policy by payer and CPT code."""
    policy = await medical_policies_collection.find_one({
        "payer_id": payer_id,
        "cpt_code": cpt_code
    })

    if not policy:
        raise HTTPException(
            status_code=404,
            detail=f"No policy found for payer {payer_id} and CPT {cpt_code}"
        )

    return policy_helper(policy)
