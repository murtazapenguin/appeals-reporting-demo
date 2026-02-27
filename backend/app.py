# Claim Appeals API
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from routes.auth_routes import router as auth_router
from routes.denial_routes import router as denial_router
from routes.medical_policy_routes import router as medical_policy_router
from routes.document_routes import router as document_router
from routes.criteria_evaluation_routes import router as criteria_evaluation_router
from routes.appeal_routes import router as appeal_router
from routes.metrics_routes import router as metrics_router
from routes.questionnaire_routes import router as questionnaire_router
from routes.reference_data_routes import router as reference_data_router
from routes.reporting_routes import router as reporting_router
import os

# Configure root_path for reverse proxy deployment
# In production, this is set via environment variable
ROOT_PATH = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title="Healthcare Claim Denial Appeal Management API",
    description="Backend API for managing healthcare claim denials and appeals",
    version="1.0.0",
    root_path=ROOT_PATH,  # Important for docs to work behind reverse proxy
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Custom OpenAPI schema to handle reverse proxy
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add servers for reverse proxy support
    openapi_schema["servers"] = [
        {"url": ROOT_PATH or "/", "description": "Current environment"}
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware - allow all origins for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://appeals-dev.penguinai.co",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(denial_router)
app.include_router(medical_policy_router)
app.include_router(document_router)
app.include_router(criteria_evaluation_router)
app.include_router(appeal_router)
app.include_router(metrics_router)
app.include_router(questionnaire_router)
app.include_router(reference_data_router)
app.include_router(reporting_router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    # Deployment trigger - force redeploy 2026-02-13
    return {"status": "ok", "service": "claim-appeals-api"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Healthcare Claim Denial Appeal Management API",
        "docs": "/docs",
        "health": "/health"
    }
