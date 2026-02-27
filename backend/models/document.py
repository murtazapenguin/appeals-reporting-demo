from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime

class PatientDocument(BaseModel):
    id: Optional[str] = None
    denial_id: str
    patient_id: str
    document_name: str
    document_type: str
    document_date: str
    presigned_urls: Dict[str, str]  # page_number -> url
    total_pages: int
    uploaded_at: Optional[datetime] = None

class DocumentPagesResponse(BaseModel):
    document_id: str
    document_name: str
    pages: Dict[str, str]  # page_number -> url
