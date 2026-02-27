from pydantic import BaseModel
from typing import List, Optional

class CriteriaQuestion(BaseModel):
    id: str
    category: Optional[str] = None
    description: str
    required: bool = True
    weight: Optional[float] = 1.0
    evidence_keywords: Optional[List[str]] = []
    document_types_expected: Optional[List[str]] = []

class MedicalPolicy(BaseModel):
    id: Optional[str] = None
    payer_id: str
    payer_name: str
    cpt_code: str
    policy_number: Optional[str] = None
    criteria: List[CriteriaQuestion]

class MedicalPolicyResponse(BaseModel):
    id: str
    payer_id: str
    payer_name: str
    cpt_code: str
    procedure_name: Optional[str] = None
    policy_number: Optional[str] = None
    criteria: List[CriteriaQuestion]
