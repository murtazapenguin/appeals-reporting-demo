---
name: backend-guide
description: FastAPI backend patterns with MongoDB using platform-starter-kit conventions. Includes JWT authentication, Motor async driver, and Pydantic models. Triggers on backend APIs, FastAPI, MongoDB, or authentication.
---

# FastAPI Backend Patterns

Patterns for building FastAPI backends with MongoDB that integrate with React frontends.

---

## Source Library: platform-starter-kit (CRITICAL - REUSE THIS)

**Location:** `../claude-code-agents/platform-starter-kit/`

A comprehensive FastAPI backend with authentication, RBAC, multi-tenant support, and utilities.

### Key Modules to Reuse

| Module | Purpose | Copy Command |
|--------|---------|--------------|
| `app.py` | FastAPI with middleware stack | Base template |
| `login.py` | JWT + SSO authentication | `cp platform-starter-kit/login.py backend/` |
| `jwt_handler.py` | Token management | `cp platform-starter-kit/jwt_handler.py backend/` |
| `auth.py` | Auth decorators | `cp platform-starter-kit/auth.py backend/` |

### Reusable Utilities

```bash
# Copy utilities directory
cp -r ../claude-code-agents/platform-starter-kit/utils backend/

# Individual utilities:
# - utils/ocr_utils.py      - Azure Form Recognizer OCR
# - utils/evidence_bbox_utils.py - Bounding box extraction
# - utils/bucket_utils.py   - Multi-cloud storage (S3, Azure Blob)
# - utils/email_service.py  - Email notifications
# - utils/db_utils.py       - MongoDB connection helpers
```

### WebSocket Support
```bash
cp -r ../claude-code-agents/platform-starter-kit/websocket backend/
```

### Storage Abstraction (AWS S3 / Azure Blob)
```bash
cp -r ../claude-code-agents/platform-starter-kit/storage backend/
```

### Complete Backend Setup
```bash
# Copy entire starter kit as base
cp -r ../claude-code-agents/platform-starter-kit/* backend/

# Then customize for your specific needs
```

---

## Quick Start

```bash
mkdir -p my-backend/{models,routes,repositories,services,utils}
cd my-backend
pip install fastapi uvicorn motor pydantic python-jose bcrypt python-multipart python-dotenv
```

---

## Project Structure

```
my-backend/
├── app.py                    # FastAPI entry point
├── config.py                 # Configuration
├── auth.py                   # Password hashing
├── jwt_handler.py            # JWT tokens
├── requirements.txt
├── .env
├── models/
│   ├── user.py
│   └── document.py
├── routes/
│   ├── auth_routes.py
│   └── document_routes.py
├── repositories/
│   └── base_repository.py
└── services/
    └── ai_processor.py       # AI processing (via AI-architect)
```

---

## Core Configuration

```python
# config.py
import os
from dotenv import load_dotenv
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "penguin_app")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
```

```python
# utils/db_utils.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL, DATABASE_NAME

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]
```

---

## Authentication

### JWT Handler

```python
# jwt_handler.py
from datetime import datetime, timedelta
from jose import jwt
from config import JWT_SECRET, JWT_ALGORITHM

def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except:
        return None
```

### Password Hashing

```python
# auth.py
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### Auth Routes

```python
# routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/login")
async def login(credentials: LoginRequest):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(str(user["_id"]))
    return {"access_token": token, "user": {"email": user["email"]}}

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    user_id = verify_token(creds.credentials)
    if not user_id:
        raise HTTPException(401, "Invalid token")
    return await db.users.find_one({"_id": ObjectId(user_id)})
```

---

## Standard Status Enums

```python
# models/document.py
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class CodeStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    DENIED = "denied"
```

---

## Standard API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/register` | Register |
| GET | `/api/auth/me` | Current user |
| GET | `/api/documents/queue` | List documents |
| GET | `/api/documents/{id}` | Get document |
| POST | `/api/documents/` | Create document |
| PUT | `/api/documents/{id}/start-coding` | Start workflow |
| PUT | `/api/documents/{id}/codes/{code_id}` | Update code |
| PUT | `/api/documents/{id}/complete` | Complete workflow |

---

## Queue Endpoint Pattern

```python
@router.get("/queue")
async def get_queue(status: str | None = None, user=Depends(get_current_user)):
    query = {}
    if status:
        query["status"] = status

    documents = await db.documents.find(query).to_list(100)

    # Calculate stats
    all_docs = await db.documents.find({}).to_list(1000)
    stats = {
        "total": len(all_docs),
        "pending": sum(1 for d in all_docs if d["status"] == "pending"),
        "in_progress": sum(1 for d in all_docs if d["status"] == "in_progress"),
        "completed": sum(1 for d in all_docs if d["status"] == "completed")
    }

    return {"documents": documents, "stats": stats}
```

---

## App Entry Point

```python
# app.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.auth_routes import router as auth_router
from routes.document_routes import router as document_router

app = FastAPI(title="PenguinAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(document_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

---

## Response Shapes (must match frontend)

```python
# Queue response
{
    "documents": [
        {
            "id": "...",
            "episode_id": "...",      # snake_case for JSON
            "patient_name": "...",
            "status": "pending",
            "codes": [...]
        }
    ],
    "stats": { "total": 10, "pending": 5, "in_progress": 3, "completed": 2 }
}
```

---

## Logging (Required for Debugging)

Add logging to all routes and services:

```python
import logging
logger = logging.getLogger("api")

# Log at key points:
logger.info(f"[AUTH] Login attempt for {email}")
logger.info(f"[UPLOAD] Processing {filename}")
logger.error(f"[ERROR] Failed: {str(e)}")
```

Use `LOG_LEVEL=DEBUG` in `.env` for verbose output.

---

## Running the Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
# API docs at http://localhost:8000/docs
```

---

## Progressive Disclosure

For detailed patterns, see:
- `templates/MODELS.md` - Complete Pydantic model definitions
- `templates/ROUTES.md` - Full route implementations
- `templates/PATTERNS.md` - Advanced patterns
- `scripts/scaffold_backend.py` - Scaffolding script
