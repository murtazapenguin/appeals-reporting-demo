# Pydantic Models Reference

Complete Pydantic model definitions for FastAPI backends.

## User Models (models/user.py)

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: str = "coder"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserModel(UserBase):
    id: str
    hashed_password: str
    created_at: datetime = datetime.utcnow()
    is_active: bool = True

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
```

## Document Models (models/document.py)

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REVIEW = "needs_review"

class ItemStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"

class BoundingBox(BaseModel):
    page_number: int
    coordinates: List[float]  # [x1, y1, x2, y2, x3, y3, x4, y4]
    label: str
    color: Optional[str] = "#fc459d"

class WorkflowItem(BaseModel):
    """Generic workflow item (ICD code, annotation, etc.)"""
    id: str
    code: Optional[str] = None
    description: str
    status: ItemStatus = ItemStatus.PENDING
    confidence: Optional[float] = None
    evidence: List[str] = []
    bounding_boxes: List[BoundingBox] = []

class DocumentBase(BaseModel):
    name: str
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    document_type: Optional[str] = None

class DocumentCreate(DocumentBase):
    file_path: Optional[str] = None
    pages: Dict[str, str]  # page_number -> image_url

class DocumentUpdate(BaseModel):
    name: Optional[str] = None
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    document_type: Optional[str] = None
    status: Optional[DocumentStatus] = None

class DocumentModel(DocumentBase):
    id: str
    status: DocumentStatus = DocumentStatus.PENDING
    pages: Dict[str, str]
    items: List[WorkflowItem] = []  # Generic workflow items
    assigned_to: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    completed_at: Optional[datetime] = None

class DocumentResponse(DocumentModel):
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int
```

## API Response Models (models/response.py)

```python
from pydantic import BaseModel
from typing import Optional, Any

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
```

## ICD Coding Specific Models (models/icd.py)

```python
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class ICDCodeStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"

class ICDCode(BaseModel):
    id: str
    code: str
    description: str
    category: Optional[str] = None
    status: ICDCodeStatus = ICDCodeStatus.PENDING
    confidence: Optional[float] = None
    evidence: List[str] = []
    page_references: List[int] = []

class ICDCodeUpdate(BaseModel):
    status: ICDCodeStatus

class ICDCodingSession(BaseModel):
    document_id: str
    coder_id: str
    started_at: str
    codes: List[ICDCode]
    notes: Optional[str] = None
```

## File Upload Models (models/upload.py)

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FileUploadResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int
    upload_path: str
    created_at: datetime

class BatchUploadResponse(BaseModel):
    success_count: int
    failed_count: int
    files: List[FileUploadResponse]
    errors: List[str] = []
```
