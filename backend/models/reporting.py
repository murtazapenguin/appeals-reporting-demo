from pydantic import BaseModel
from typing import List, Optional, Dict


class DenialTypeSplit(BaseModel):
    label: str
    count: int
    total_denied: float
    overturn_rate: float


class CodeBreakdown(BaseModel):
    code: str
    description: str
    count: int
    total_denied: float
    overturn_rate: float
    classification: str
    preventability: str


class MonthlyVolume(BaseModel):
    month: str
    administrative: int
    clinical: int
    other: int


class MonthlyRecovery(BaseModel):
    month: str
    recovered_amount: float


class TopItem(BaseModel):
    name: str
    count: int


class ExecutiveSummaryResponse(BaseModel):
    total_denials: int
    overall_overturn_rate: float
    total_recovered: float
    avg_resolution_days: Optional[float]
    preventable_rate: float
    volume_trend: List[MonthlyVolume]
    recovery_trend: List[MonthlyRecovery]
    top_denial_codes: List[TopItem]
    top_payers: List[TopItem]


class ProcedureCodeRow(BaseModel):
    procedure_code: str
    total: int
    medical_necessity: int
    prior_authorization: int
    coding_error: int
    documentation: int
    other: int


class DiagnosisCodeRow(BaseModel):
    code: str
    count: int


class DenialAnalysisResponse(BaseModel):
    admin_split: DenialTypeSplit
    clinical_split: DenialTypeSplit
    other_split: DenialTypeSplit
    code_breakdown: List[CodeBreakdown]
    procedure_matrix: List[ProcedureCodeRow]
    top_diagnosis_codes: List[DiagnosisCodeRow]


class OverturnRow(BaseModel):
    name: str
    total_appeals: int
    overturned: int
    overturn_rate: float
    avg_days_to_decision: Optional[float]
    recovered_amount: float
    extra: Optional[str] = None


class MonthlyOverturn(BaseModel):
    month: str
    overturn_rate: float
    overturned: int
    total_appeals: int


class OverturnRatesResponse(BaseModel):
    overall_overturn_rate: float
    trend: List[MonthlyOverturn]
    rows: List[OverturnRow]


class RecurringPattern(BaseModel):
    code: str
    frequency: int
    trend: str
    common_payer: str
    common_practice: str
    suggested_action: str


class PreventabilityMonth(BaseModel):
    month: str
    high: int
    medium: int
    low: int


class PracticeInsight(BaseModel):
    practice: str
    total_denials: int
    preventable_count: int
    preventable_rate: float
    top_codes: List[str]


class PayerBehavior(BaseModel):
    payer: str
    total_denials: int
    top_codes: List[str]
    overturn_rate: float


class PatternIntelligenceResponse(BaseModel):
    preventability_trend: List[PreventabilityMonth]
    recurring_patterns: List[RecurringPattern]
    practice_insights: List[PracticeInsight]
    payer_behavior: List[PayerBehavior]
    actionable_insights: List[str]


class OperationalKPIsResponse(BaseModel):
    avg_processing_days: Optional[float]
    avg_letter_generation_seconds: Optional[float]
    ai_auto_approval_rate: Optional[float]
    appeals_per_week: Optional[float]
    avg_review_hours: Optional[float]
    fte_capacity_gain: Optional[float]
    processing_trend: List[dict]
    throughput_trend: List[dict]


class PracticeScorecardResponse(BaseModel):
    practice_name: str
    total_denials: int
    total_denied: float
    total_recovered: float
    overturn_rate: float
    preventable_rate: float
    avg_resolution_days: Optional[float]
    admin_split: DenialTypeSplit
    clinical_split: DenialTypeSplit
    top_denial_codes: List[CodeBreakdown]
    top_procedures: List[ProcedureCodeRow]
    payer_breakdown: List[OverturnRow]
    denial_trend: List[MonthlyVolume]
    actionable_insights: List[str]
