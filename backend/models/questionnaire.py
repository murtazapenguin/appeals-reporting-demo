from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SubCriterion(BaseModel):
    criteria: str
    question: str
    evaluatable: bool = False
    context: List[str] = []
    logic: Optional[str] = None  # AND, OR, NOR, AT_LEAST_N
    required_count: Optional[int] = None  # For AT_LEAST_N
    subcriteria: List["SubCriterion"] = []
    query: Optional[str] = None  # Only on leaf nodes (evaluatable=True)
    # Evaluation result fields (populated after evaluation)
    met: Optional[bool] = None
    evidence: Optional[List[dict]] = None
    explanation: Optional[str] = None


SubCriterion.model_rebuild()


class QuestionnaireGuidelines(BaseModel):
    criteria: str
    question: str
    evaluatable: bool = False
    context: List[str] = []
    logic: Optional[str] = None
    required_count: Optional[int] = None
    subcriteria: List[SubCriterion] = []
    query: Optional[str] = None


class Questionnaire(BaseModel):
    id: Optional[str] = None
    source_file: str
    guideline_name: str
    line_of_business: List[str] = []
    cpt_codes: List[str] = []
    hcpcs_codes: List[str] = []
    icd_10_codes: List[str] = []
    guidelines: QuestionnaireGuidelines
    total_evaluatable_questions: Optional[int] = None
    max_depth: Optional[int] = None
    imported_at: Optional[datetime] = None


class QuestionnaireResponse(BaseModel):
    id: str
    guideline_name: str
    cpt_codes: List[str] = []
    line_of_business: List[str] = []
    total_evaluatable_questions: Optional[int] = None
    max_depth: Optional[int] = None
