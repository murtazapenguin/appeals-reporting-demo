from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class Evidence(BaseModel):
    document_id: Optional[str] = None
    document_name: str
    page: int
    text: str
    bbox: List[float]  # [x1, y1, x2, y2, x3, y3, x4, y4]
    label: Optional[str] = None  # Optional - used for display label
    presigned_urls: Optional[Dict[str, str]] = None  # page_number -> url (optional, for S3 storage)
    confidence: Optional[float] = None  # Confidence score for the evidence

class CriteriaResult(BaseModel):
    id: str
    description: str
    met: bool
    evidence: Optional[List[Evidence]] = []
    missing_documents: Optional[str] = None

class CriteriaEvaluationResponse(BaseModel):
    denial_id: str
    total_criteria: int
    criteria_met: int
    win_probability: int
    criteria: List[CriteriaResult]
    evaluated_at: datetime
    # Questionnaire-specific fields (optional, for hierarchical evaluations)
    criteria_tree: Optional[Dict] = None
    guideline_name: Optional[str] = None
    questionnaire_id: Optional[str] = None
