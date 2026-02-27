from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

class AppealSection(BaseModel):
    title: str
    content: str

class AppealSignature(BaseModel):
    name: str
    title: str

class ProviderLetterhead(BaseModel):
    name: str
    address: str
    phone: str

class AppealLetter(BaseModel):
    denial_id: str
    provider_letterhead: ProviderLetterhead
    sections: List[AppealSection]
    enclosed_documents: List[str]
    signature: AppealSignature
    generated_at: datetime

class AppealSubmitResponse(BaseModel):
    denial_id: str
    status: str
    submitted_at: datetime
    confirmation_number: str
