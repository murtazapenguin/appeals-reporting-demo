"""
Questionnaire Evaluator Service

Evaluates hierarchical questionnaire criteria trees against patient documents.
Reuses the existing ai_processor for OCR + evidence extraction, then applies
tree logic (AND/OR/NOR/AT_LEAST_N) bottom-up to determine overall result.
"""

import logging
import os
import copy
from typing import List, Dict, Tuple
from datetime import datetime

from services.ai_processor import get_processor
from utils.db_utils import questionnaires_collection

logger = logging.getLogger("questionnaire_evaluator")
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def extract_leaf_criteria(node: dict, leaves: list = None) -> list:
    """
    Extract all evaluatable leaf nodes from a criteria tree.
    Returns flat list of dicts with {id, description, question, query, path}.
    """
    if leaves is None:
        leaves = []

    if node.get("evaluatable") and not node.get("subcriteria"):
        leaves.append({
            "id": node.get("question", ""),
            "description": node.get("criteria", ""),
            "question": node.get("question", ""),
            "query": node.get("query", node.get("criteria", "")),
        })
    else:
        for sc in node.get("subcriteria", []):
            extract_leaf_criteria(sc, leaves)

    return leaves


def apply_tree_logic(node: dict, leaf_results: dict) -> dict:
    """
    Apply logic operators bottom-up to determine met/not-met for each node.

    Args:
        node: A criteria tree node (will be mutated with 'met' field)
        leaf_results: Dict mapping question ID -> {met, evidence, explanation}

    Returns:
        The node with 'met' populated at every level.
    """
    # Leaf node — look up result
    if node.get("evaluatable") and not node.get("subcriteria"):
        question_id = node.get("question", "")
        result = leaf_results.get(question_id, {})
        node["met"] = result.get("met", False)
        node["evidence"] = result.get("evidence", [])
        node["explanation"] = result.get("explanation", "")
        return node

    # Recurse into children first
    for sc in node.get("subcriteria", []):
        apply_tree_logic(sc, leaf_results)

    # Apply logic operator
    logic = node.get("logic", "AND").upper()
    children_met = [sc.get("met", False) for sc in node.get("subcriteria", [])]

    if logic == "AND":
        node["met"] = all(children_met)
    elif logic == "OR":
        node["met"] = any(children_met)
    elif logic == "NOR":
        node["met"] = not any(children_met)
    elif logic == "AT_LEAST_N":
        required = node.get("required_count", 1)
        node["met"] = sum(children_met) >= required
    else:
        # Default to AND
        node["met"] = all(children_met)

    return node


def count_tree_results(node: dict) -> Tuple[int, int]:
    """Count (met_leaves, total_leaves) in a resolved tree."""
    if node.get("evaluatable") and not node.get("subcriteria"):
        return (1 if node.get("met") else 0, 1)

    met = 0
    total = 0
    for sc in node.get("subcriteria", []):
        m, t = count_tree_results(sc)
        met += m
        total += t
    return (met, total)


async def find_questionnaire_by_cpt(cpt_code: str) -> dict:
    """Look up a questionnaire by CPT code. Returns None if not found."""
    q = await questionnaires_collection.find_one({"cpt_codes": cpt_code})
    return q


async def evaluate_with_questionnaire(
    denial_id: str,
    denial_data: dict,
    questionnaire: dict,
    documents: list,
) -> dict:
    """
    Evaluate a denial using a hierarchical questionnaire.

    1. Extract leaf criteria from the tree
    2. Use ai_processor.evaluate_criteria() with leaf criteria (flat format)
    3. Map results back into the tree and apply logic operators
    4. Return structured evaluation with both flat criteria and tree

    Args:
        denial_id: Denial ID
        denial_data: Denial document
        questionnaire: Questionnaire document from DB
        documents: Patient documents

    Returns:
        Evaluation dict compatible with CriteriaEvaluationResponse
    """
    guidelines = questionnaire.get("guidelines", {})
    guideline_name = questionnaire.get("guideline_name", "Unknown")
    questionnaire_id = str(questionnaire.get("_id", ""))

    logger.info(f"[Q-EVAL] Starting questionnaire evaluation: {guideline_name}")
    logger.info(f"[Q-EVAL] Questionnaire ID: {questionnaire_id}")

    # Step 1: Extract leaf criteria
    leaves = extract_leaf_criteria(guidelines)
    logger.info(f"[Q-EVAL] Extracted {len(leaves)} evaluatable leaf criteria")

    if not leaves:
        logger.warning(f"[Q-EVAL] No evaluatable criteria found in questionnaire")
        return {
            "denial_id": denial_id,
            "total_criteria": 0,
            "criteria_met": 0,
            "win_probability": 0,
            "criteria": [],
            "criteria_tree": guidelines,
            "guideline_name": guideline_name,
            "questionnaire_id": questionnaire_id,
            "evaluated_at": datetime.utcnow(),
        }

    # Step 2: Run existing flat evaluation on leaf criteria
    processor = get_processor()
    denial_data_str = {**denial_data, "_id": str(denial_data.get("_id", denial_id))}
    docs_str = [{**doc, "_id": str(doc["_id"])} for doc in documents]

    flat_evaluation = await processor.evaluate_criteria(
        denial_id=denial_id,
        denial_data=denial_data_str,
        criteria=leaves,
        documents=docs_str,
    )

    # Step 3: Build leaf_results lookup from flat evaluation
    leaf_results = {}
    flat_criteria = flat_evaluation.get("criteria", [])
    for criterion in flat_criteria:
        leaf_results[criterion["id"]] = {
            "met": criterion.get("met", False),
            "evidence": criterion.get("evidence", []),
            "explanation": criterion.get("explanation", ""),
        }

    # Step 4: Deep copy tree and apply logic
    resolved_tree = copy.deepcopy(guidelines)
    apply_tree_logic(resolved_tree, leaf_results)

    # Step 5: Calculate stats
    met_leaves, total_leaves = count_tree_results(resolved_tree)
    win_probability = int((met_leaves / total_leaves) * 100) if total_leaves > 0 else 0

    logger.info(f"[Q-EVAL] Tree evaluation complete: {met_leaves}/{total_leaves} leaves met")
    logger.info(f"[Q-EVAL] Root node met: {resolved_tree.get('met')}")
    logger.info(f"[Q-EVAL] Win probability: {win_probability}%")

    return {
        "denial_id": denial_id,
        "total_criteria": total_leaves,
        "criteria_met": met_leaves,
        "win_probability": win_probability,
        "criteria": flat_criteria,
        "criteria_tree": resolved_tree,
        "guideline_name": guideline_name,
        "questionnaire_id": questionnaire_id,
        "top_documents": flat_evaluation.get("top_documents", []),
        "evaluated_at": datetime.utcnow(),
    }
