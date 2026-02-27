from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL, DATABASE_NAME, MONGODB_TLS, MONGODB_TLS_CA_FILE
import os

# Build connection options
# Always disable retryWrites - harmless for local MongoDB, required for DocumentDB
connection_options = {
    "retryWrites": False,
}

if MONGODB_TLS:
    # DocumentDB/TLS connection settings
    connection_options.update({
        "tls": True,
        "tlsCAFile": MONGODB_TLS_CA_FILE,
        "directConnection": True
    })

client = AsyncIOMotorClient(MONGODB_URL, **connection_options)
db = client[DATABASE_NAME]

# Collections
users_collection = db.users
denials_collection = db.denials
medical_policies_collection = db.medical_policies
patient_documents_collection = db.patient_documents
criteria_evaluations_collection = db.criteria_evaluations
appeal_packages_collection = db.appeal_packages

# Questionnaire collection
questionnaires_collection = db.questionnaires

# Reference data collection
reference_data_collection = db.reference_data

# New collections for AI processing pipeline
ocr_cache_collection = db.ocr_cache
document_relevancy_collection = db.document_relevancy
