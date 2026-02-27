from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime
from typing import Optional
from models.criteria_evaluation import CriteriaEvaluationResponse, CriteriaResult, Evidence
from routes.auth_routes import get_current_user
from utils.db_utils import (
    criteria_evaluations_collection,
    denials_collection,
    medical_policies_collection,
    patient_documents_collection
)
from services.ai_processor import get_processor
from services.questionnaire_evaluator import find_questionnaire_by_cpt, evaluate_with_questionnaire
import asyncio
import logging

router = APIRouter(prefix="/api/criteria-evaluation", tags=["Criteria Evaluation"])
logger = logging.getLogger("criteria_evaluation_routes")

# Document types that contain clinical/medical evidence for criteria evaluation.
# Excludes administrative docs (EOBs, claim forms, denial letters, etc.)
CLINICAL_DOC_TYPES = {
    "medical_records", "prior_visit_notes", "diagnostic_tests",
    "clinical_guidelines", "peer_reviewed",
}

# CPT codes that should use flat medical-policy criteria instead of questionnaires
FLAT_CRITERIA_CPT_CODES = {"27447"}

def evaluation_helper(evaluation) -> dict:
    """Convert MongoDB evaluation to response dict."""
    if not evaluation:
        return None

    # Transform criteria to ensure 'description' field exists
    # Handle backward compatibility with old 'question' field
    criteria = []
    for criterion in evaluation.get("criteria", []):
        # Create a copy to avoid modifying original
        c = dict(criterion)

        # Map 'question' to 'description' if needed
        if "question" in c and "description" not in c:
            c["description"] = c.pop("question")
        elif "question" in c and "description" in c:
            # Both exist, remove question
            c.pop("question", None)

        criteria.append(c)

    result = {
        "denial_id": evaluation["denial_id"],
        "total_criteria": evaluation["total_criteria"],
        "criteria_met": evaluation["criteria_met"],
        "win_probability": evaluation["win_probability"],
        "criteria": criteria,
        "evaluated_at": evaluation["evaluated_at"],
    }

    # Include questionnaire-specific fields if present
    if evaluation.get("criteria_tree"):
        result["criteria_tree"] = evaluation["criteria_tree"]
    if evaluation.get("guideline_name"):
        result["guideline_name"] = evaluation["guideline_name"]
    if evaluation.get("questionnaire_id"):
        result["questionnaire_id"] = evaluation["questionnaire_id"]

    return result

async def _run_evaluation_background(denial_id: str, denial: dict, documents: list, questionnaire: dict, procedure_code: str):
    """Run criteria evaluation as a background task."""
    try:
        eval_start = datetime.utcnow()
        await denials_collection.update_one(
            {"_id": ObjectId(denial_id)},
            {"$set": {
                "evaluation_status": "processing",
                "evaluation_error": None,
                "processing_timestamps.review_started_at": eval_start,
            }}
        )

        if questionnaire:
            logger.info(f"[EVAL] Found questionnaire: {questionnaire.get('guideline_name')} for CPT {procedure_code}")

            if not documents:
                from services.questionnaire_evaluator import extract_leaf_criteria
                leaves = extract_leaf_criteria(questionnaire.get("guidelines", {}))
                evaluation = {
                    "denial_id": denial_id,
                    "total_criteria": len(leaves),
                    "criteria_met": 0,
                    "win_probability": 0,
                    "criteria": [
                        {
                            "id": c["id"],
                            "description": c["description"],
                            "met": False,
                            "evidence": [],
                            "missing_documents": "No clinical documents found for evidence review"
                        }
                        for c in leaves
                    ],
                    "criteria_tree": questionnaire.get("guidelines"),
                    "guideline_name": questionnaire.get("guideline_name"),
                    "questionnaire_id": str(questionnaire["_id"]),
                    "evaluated_at": datetime.utcnow(),
                }
            else:
                evaluation = await evaluate_with_questionnaire(
                    denial_id=denial_id,
                    denial_data=denial,
                    questionnaire=questionnaire,
                    documents=documents,
                )
        else:
            logger.info(f"[EVAL] Using flat medical policy criteria for CPT {procedure_code}")
            policy = await medical_policies_collection.find_one({
                "payer_id": denial.get("payer_id"),
                "cpt_code": procedure_code
            })

            if not policy:
                await denials_collection.update_one(
                    {"_id": ObjectId(denial_id)},
                    {"$set": {
                        "evaluation_status": "failed",
                        "evaluation_error": f"No medical policy or questionnaire found for CPT {procedure_code}"
                    }}
                )
                return

            criteria = policy.get("criteria", [])
            logger.info(f"[EVAL] Found {len(criteria)} flat criteria to evaluate")

            if not documents:
                evaluation = {
                    "denial_id": denial_id,
                    "total_criteria": len(criteria),
                    "criteria_met": 0,
                    "win_probability": 0,
                    "criteria": [
                        {
                            "id": c["id"],
                            "description": c.get("description") or c.get("question", ""),
                            "met": False,
                            "evidence": [],
                            "missing_documents": "No clinical documents found for evidence review"
                        }
                        for c in criteria
                    ],
                    "evaluated_at": datetime.utcnow()
                }
            else:
                processor = get_processor()
                denial_data = {**denial, "_id": str(denial["_id"])}

                evaluation = await processor.evaluate_criteria(
                    denial_id=denial_id,
                    denial_data=denial_data,
                    criteria=criteria,
                    documents=[{**doc, "_id": str(doc["_id"])} for doc in documents]
                )

        # Save evaluation to database
        await criteria_evaluations_collection.update_one(
            {"denial_id": denial_id},
            {"$set": evaluation},
            upsert=True
        )

        eval_end = datetime.utcnow()
        await denials_collection.update_one(
            {"_id": ObjectId(denial_id)},
            {
                "$set": {
                    "win_probability": evaluation["win_probability"],
                    "status": "in_review",
                    "evaluation_status": "completed",
                    "updated_at": eval_end,
                    "processing_timestamps.review_completed_at": eval_end,
                }
            }
        )

        logger.info(f"[EVAL] Completed for denial {denial_id}, win_probability={evaluation['win_probability']}%")

    except Exception as e:
        logger.error(f"[EVAL ERROR] Background evaluation failed for {denial_id}: {str(e)}")
        await denials_collection.update_one(
            {"_id": ObjectId(denial_id)},
            {"$set": {
                "evaluation_status": "failed",
                "evaluation_error": str(e)
            }}
        )


@router.post("/evaluate/{denial_id}")
async def evaluate_criteria(denial_id: str, user=Depends(get_current_user)):
    """
    Kick off criteria evaluation as a background task.

    Returns immediately with status "processing". Frontend should poll
    GET /criteria-evaluation/{denial_id} until results appear.
    """
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    logger.info(f"[EVAL] Starting evaluation for denial {denial_id}")

    # 1. Get denial details
    denial = await denials_collection.find_one({"_id": ObjectId(denial_id)})
    if not denial:
        raise HTTPException(status_code=404, detail="Denial not found")

    # 2. Get patient documents for this denial
    documents = await patient_documents_collection.find({
        "denial_id": denial_id
    }).to_list(1000)

    if not documents:
        documents = await patient_documents_collection.find({
            "patient_id": denial.get("patient_id")
        }).to_list(1000)

    logger.info(f"[EVAL] Found {len(documents)} total documents for denial {denial_id}")

    # 2b. Filter to clinical/medical documents only (exclude EOBs, claim forms, etc.)
    clinical_documents = [
        doc for doc in documents
        if doc.get("document_type") in CLINICAL_DOC_TYPES
    ]
    logger.info(f"[EVAL] {len(clinical_documents)} clinical documents after filtering (excluded {len(documents) - len(clinical_documents)} non-clinical)")

    # 3. Find questionnaire by CPT code (skip for CPTs that prefer flat criteria)
    procedure_code = denial.get("procedure_code")
    if procedure_code and procedure_code not in FLAT_CRITERIA_CPT_CODES:
        questionnaire = await find_questionnaire_by_cpt(procedure_code)
    else:
        questionnaire = None
        if procedure_code in FLAT_CRITERIA_CPT_CODES:
            logger.info(f"[EVAL] CPT {procedure_code} uses flat criteria — skipping questionnaire lookup")

    # 4. Validate that we have either a questionnaire or a medical policy
    if not questionnaire:
        policy = await medical_policies_collection.find_one({
            "payer_id": denial.get("payer_id"),
            "cpt_code": procedure_code
        })
        if not policy:
            raise HTTPException(
                status_code=404,
                detail=f"No medical policy or questionnaire found for CPT {procedure_code}"
            )

    # 5. Guard against concurrent evaluations
    if denial.get("evaluation_status") == "processing":
        return {"status": "processing", "denial_id": denial_id}

    # 6. Mark as processing and launch background task
    await denials_collection.update_one(
        {"_id": ObjectId(denial_id)},
        {"$set": {"evaluation_status": "processing", "evaluation_error": None}}
    )

    asyncio.create_task(
        _run_evaluation_background(denial_id, denial, clinical_documents, questionnaire, procedure_code)
    )

    return {"status": "processing", "denial_id": denial_id}


@router.get("/status/{denial_id}")
async def get_evaluation_status(denial_id: str, user=Depends(get_current_user)):
    """Get current evaluation status for a denial."""
    if not ObjectId.is_valid(denial_id):
        raise HTTPException(status_code=400, detail="Invalid denial ID")

    denial = await denials_collection.find_one(
        {"_id": ObjectId(denial_id)},
        {"evaluation_status": 1, "evaluation_error": 1}
    )
    if not denial:
        raise HTTPException(status_code=404, detail="Denial not found")

    return {
        "denial_id": denial_id,
        "status": denial.get("evaluation_status", "idle"),
        "error": denial.get("evaluation_error")
    }

@router.get("/{denial_id}", response_model=Optional[CriteriaEvaluationResponse])
async def get_criteria_evaluation(denial_id: str, user=Depends(get_current_user)):
    """Get existing criteria evaluation results."""
    evaluation = await criteria_evaluations_collection.find_one({"denial_id": denial_id})

    if not evaluation:
        return None

    return evaluation_helper(evaluation)
