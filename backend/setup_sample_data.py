"""
Setup sample data for AI pipeline testing.

Creates:
1. A TKA denial case for patient PT-100000
2. Registers the 10 sample PDFs in patient_documents
3. Ensures medical policy exists for the procedure
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId
import os

# Database connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "claim_appeals")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]


async def setup_sample_data():
    """Set up sample data for AI pipeline testing."""

    patient_id = "PT-100000"
    payer_id = "BCBS"
    procedure_code = "27447"

    print(f"Setting up sample data for patient {patient_id}...")

    # 1. Ensure medical policy exists for TKA
    existing_policy = await db.medical_policies.find_one({
        "payer_id": payer_id,
        "cpt_code": procedure_code
    })

    if not existing_policy:
        policy = {
            "payer_id": payer_id,
            "payer_name": "Blue Cross Blue Shield",
            "cpt_code": procedure_code,
            "cpt_description": "Total Knee Arthroplasty",
            "policy_name": "Total Knee Replacement Medical Policy",
            "criteria": [
                {
                    "id": "C1",
                    "question": "Has the patient tried at least 3 months of conservative therapy (physical therapy, NSAIDs, injections)?",
                    "required": True
                },
                {
                    "id": "C2",
                    "question": "Does imaging (X-ray/MRI) show significant joint degeneration (bone-on-bone contact or severe cartilage loss)?",
                    "required": True
                },
                {
                    "id": "C3",
                    "question": "Is there documented functional impairment affecting daily activities?",
                    "required": True
                },
                {
                    "id": "C4",
                    "question": "Has the patient failed to respond to corticosteroid injections?",
                    "required": True
                },
                {
                    "id": "C5",
                    "question": "Is there documented pain level of 7 or higher on a 10-point scale?",
                    "required": False
                }
            ],
            "created_at": datetime.utcnow()
        }
        await db.medical_policies.insert_one(policy)
        print(f"  Created medical policy for {payer_id} + {procedure_code}")
    else:
        print(f"  Medical policy already exists for {payer_id} + {procedure_code}")

    # 2. Create or update denial for TKA
    existing_denial = await db.denials.find_one({
        "patient_id": patient_id,
        "procedure_code": procedure_code
    })

    denial_id = None
    if existing_denial:
        denial_id = existing_denial["_id"]
        print(f"  Using existing denial: {denial_id}")
    else:
        denial = {
            "claim_number": "CLM-TKA-2024-001",
            "patient_id": patient_id,
            "patient_name": "John Smith",
            "patient_dob": "1958-03-15",
            "provider_id": "PRV-001",
            "provider_name": "Dr. Sarah Wilson",
            "payer_id": payer_id,
            "payer_name": "Blue Cross Blue Shield",
            "procedure_code": procedure_code,
            "procedure_description": "Total Knee Arthroplasty (TKA)",
            "diagnosis_codes": ["M17.11", "M25.561"],
            "claim_amount": 42500.00,
            "service_date": "2024-11-15",  # The surgery date
            "denial_date": "2024-11-25",
            "denial_reason": "Medical necessity not established. Documentation does not demonstrate failure of conservative treatment.",
            "appeal_deadline": "2024-12-25",
            "status": "pending",
            "win_probability": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await db.denials.insert_one(denial)
        denial_id = result.inserted_id
        print(f"  Created new TKA denial: {denial_id}")

    # 3. Register the 10 sample PDFs
    base_path = "/Users/vaatsav/Desktop/claim-appeals-v2/backend/documents/PT-100000/2024/01"

    pdf_documents = [
        {
            "file_name": "progress_note_20240604.pdf",
            "document_name": "Initial Orthopedic Consultation",
            "document_type": "Progress Note",
            "document_date": "2024-06-04",
            "description": "Initial evaluation showing knee pain, ROM limitations, and conservative treatment recommendation"
        },
        {
            "file_name": "xray_report_20240604.pdf",
            "document_name": "Knee X-Ray Report",
            "document_type": "Imaging Report",
            "document_date": "2024-06-04",
            "description": "X-ray findings showing medial compartment narrowing and early osteoarthritis"
        },
        {
            "file_name": "pt_initial_eval_20240619.pdf",
            "document_name": "Physical Therapy Initial Evaluation",
            "document_type": "PT Evaluation",
            "document_date": "2024-06-19",
            "description": "PT evaluation documenting functional deficits and treatment plan"
        },
        {
            "file_name": "pt_discharge_20240814.pdf",
            "document_name": "Physical Therapy Discharge Summary",
            "document_type": "PT Discharge",
            "document_date": "2024-08-14",
            "description": "PT discharge showing minimal improvement after 8 weeks of therapy"
        },
        {
            "file_name": "injection_note_20240823.pdf",
            "document_name": "Corticosteroid Injection Note",
            "document_type": "Procedure Note",
            "document_date": "2024-08-23",
            "description": "Documentation of corticosteroid injection and temporary relief"
        },
        {
            "file_name": "followup_note_20240920.pdf",
            "document_name": "Follow-up Progress Note",
            "document_type": "Progress Note",
            "document_date": "2024-09-20",
            "description": "Follow-up showing injection failure and continued symptoms"
        },
        {
            "file_name": "mri_report_20241002.pdf",
            "document_name": "MRI of Right Knee",
            "document_type": "Imaging Report",
            "document_date": "2024-10-02",
            "description": "MRI showing severe cartilage loss and bone-on-bone contact"
        },
        {
            "file_name": "medication_list_20241012.pdf",
            "document_name": "Current Medication List",
            "document_type": "Medication List",
            "document_date": "2024-10-12",
            "description": "Current medications including failed NSAID trials"
        },
        {
            "file_name": "surgical_recommendation_20241017.pdf",
            "document_name": "Surgical Recommendation Letter",
            "document_type": "Medical Letter",
            "document_date": "2024-10-17",
            "description": "Surgeon's letter recommending TKA after conservative treatment failure"
        },
        {
            "file_name": "preop_clearance_20241101.pdf",
            "document_name": "Pre-operative Medical Clearance",
            "document_type": "Medical Clearance",
            "document_date": "2024-11-01",
            "description": "Medical clearance for surgery documenting patient readiness"
        }
    ]

    # Clear existing sample documents for this patient
    await db.patient_documents.delete_many({
        "patient_id": patient_id,
        "file_path": {"$regex": "^/Users/vaatsav/Desktop/claim-appeals-v2/backend/documents/PT-100000/2024/01"}
    })

    # Insert all PDF documents
    for pdf in pdf_documents:
        doc = {
            "patient_id": patient_id,
            "document_name": pdf["document_name"],
            "document_type": pdf["document_type"],
            "document_date": pdf["document_date"],
            "description": pdf["description"],
            "file_path": f"{base_path}/{pdf['file_name']}",
            "file_name": pdf["file_name"],
            "file_size": os.path.getsize(f"{base_path}/{pdf['file_name']}") if os.path.exists(f"{base_path}/{pdf['file_name']}") else 0,
            "mime_type": "application/pdf",
            "uploaded_at": datetime.utcnow()
        }
        await db.patient_documents.insert_one(doc)

    print(f"  Registered {len(pdf_documents)} PDF documents")

    # 4. Clear any cached OCR/relevancy data for fresh testing
    await db.ocr_cache.delete_many({"patient_id": patient_id})
    await db.document_relevancy.delete_many({})
    print("  Cleared OCR cache and relevancy data for fresh testing")

    print(f"\n✅ Setup complete!")
    print(f"   Denial ID: {denial_id}")
    print(f"   Patient ID: {patient_id}")
    print(f"   Documents: {len(pdf_documents)}")
    print(f"\nTo test the pipeline, run:")
    print(f"   curl -X POST http://localhost:8000/api/criteria-evaluation/evaluate/{denial_id}")

    return str(denial_id)


if __name__ == "__main__":
    result = asyncio.run(setup_sample_data())
    print(f"\nDenial ID for testing: {result}")
