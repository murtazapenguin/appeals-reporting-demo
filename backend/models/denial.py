from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict
from datetime import datetime
from enum import Enum

class DenialStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPEAL_READY = "appeal_ready"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DENIED = "denied"

class DenialCategory(str, Enum):
    MEDICAL_NECESSITY = "Medical Necessity"
    PRIOR_AUTHORIZATION = "Prior Authorization"
    CODING_ERROR = "Coding Error"
    DOCUMENTATION = "Documentation"
    OTHER = "Other"

class PriorityLevel(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class DenialExtraction(BaseModel):
    """Extracted denial information from EOB/Remittance Letter"""
    denial_code: Optional[str] = None  # e.g., "CO-45"
    denial_narrative: Optional[str] = None  # Full text explanation
    extracted_from_document_id: Optional[str] = None
    extraction_confidence: Optional[float] = None
    extracted_at: Optional[datetime] = None

class ProviderExtraction(BaseModel):
    """Extracted provider information from PA Approval Letter"""
    provider_name: Optional[str] = None
    npi: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    tax_id: Optional[str] = None
    practice_name: Optional[str] = None
    extracted_from_document_id: Optional[str] = None
    extraction_confidence: Optional[float] = None
    extracted_at: Optional[datetime] = None

class DenialBase(BaseModel):
    claim_number: str
    patient_name: str
    patient_id: str
    patient_dob: Optional[str] = None
    provider_name: str
    provider_id: Optional[str] = None
    provider_npi: Optional[str] = None
    provider_address: Optional[str] = None
    provider_phone: Optional[str] = None
    provider_tax_id: Optional[str] = None
    provider_practice_name: Optional[str] = None
    payer_name: str
    payer_id: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    service_date: str
    denial_date: str
    denial_code: Optional[str] = None
    denial_category: str
    denial_reason: Optional[str] = None
    claim_amount: float
    paid_amount: Optional[float] = 0
    denied_amount: Optional[float] = 0
    procedure_code: str
    diagnosis_codes: Union[str, List[str]]
    service_description: Optional[str] = None
    priority: str = "normal"
    internal_notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    denial_extraction: Optional[DenialExtraction] = None
    provider_extraction: Optional[ProviderExtraction] = None

class DenialCreate(DenialBase):
    pass

class DenialUpdate(BaseModel):
    claim_number: Optional[str] = None
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    patient_dob: Optional[str] = None
    provider_name: Optional[str] = None
    provider_id: Optional[str] = None
    provider_npi: Optional[str] = None
    provider_address: Optional[str] = None
    provider_phone: Optional[str] = None
    provider_tax_id: Optional[str] = None
    provider_practice_name: Optional[str] = None
    payer_name: Optional[str] = None
    payer_id: Optional[str] = None
    policy_number: Optional[str] = None
    group_number: Optional[str] = None
    service_date: Optional[str] = None
    denial_date: Optional[str] = None
    denial_code: Optional[str] = None
    denial_category: Optional[str] = None
    denial_reason: Optional[str] = None
    claim_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    denied_amount: Optional[float] = None
    procedure_code: Optional[str] = None
    diagnosis_codes: Optional[Union[str, List[str]]] = None
    service_description: Optional[str] = None
    priority: Optional[str] = None
    internal_notes: Optional[str] = None
    status: Optional[str] = None
    denial_extraction: Optional[DenialExtraction] = None
    provider_extraction: Optional[ProviderExtraction] = None

class DenialResponse(DenialBase):
    id: str
    status: str = "pending"
    win_probability: Optional[int] = None
    appeal_deadline: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class CSVUploadResponse(BaseModel):
    imported_count: int
    failed_count: int
    errors: list
