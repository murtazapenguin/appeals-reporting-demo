"""
Setup clean, properly linked data for the claim appeals application.
Creates denials with matching documents that have real PDF files.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timedelta
import os
import shutil

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["claim_appeals"]

# Test PDF files that exist
TEST_PDFS = [
    "/Users/vaatsav/Desktop/claude-code-agents/test_files/Detailed_Medical_Record_CPT_22630.pdf",
    "/Users/vaatsav/Desktop/claude-code-agents/test_files/Detailed_Medical_Record_OSA.pdf",
    "/Users/vaatsav/Desktop/claude-code-agents/test_files/Banks_christopher 1.pdf",
]

# Document directory
DOC_DIR = "/Users/vaatsav/Desktop/claim-appeals-v2/backend/documents"

async def create_denial_with_documents(
    claim_number: str,
    patient_name: str,
    patient_id: str,
    payer_name: str,
    procedure_code: str,
    diagnosis_codes: str,
    denial_category: str,
    claim_amount: float,
    documents: list
):
    """Create a denial with properly linked documents."""

    denial_id = ObjectId()

    # Create denial
    denial = {
        "_id": denial_id,
        "claim_number": claim_number,
        "patient_name": patient_name,
        "patient_id": patient_id,
        "patient_dob": "1958-03-15",
        "provider_name": "Dr. Sarah Wilson",
        "provider_id": "PRV-001",
        "payer_name": payer_name,
        "payer_id": payer_name.lower().replace(" ", "_"),
        "policy_number": f"POL-{patient_id[-3:]}",
        "service_date": (datetime.now() - timedelta(days=30)).strftime("%Y/%m/%d"),
        "denial_date": (datetime.now() - timedelta(days=7)).strftime("%Y/%m/%d"),
        "denial_code": "M-001",
        "denial_category": denial_category,
        "denial_reason": f"Medical necessity not established for {procedure_code}",
        "claim_amount": claim_amount,
        "procedure_code": procedure_code,
        "diagnosis_codes": diagnosis_codes,
        "service_description": f"Procedure {procedure_code}",
        "priority": "normal",
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "appeal_deadline": (datetime.now() + timedelta(days=30)).strftime("%Y/%m/%d"),
    }

    await db.denials.insert_one(denial)
    print(f"Created denial: {claim_number} ({str(denial_id)})")

    # Create patient document directory
    patient_doc_dir = os.path.join(DOC_DIR, patient_id)
    os.makedirs(patient_doc_dir, exist_ok=True)

    # Create documents
    doc_ids = []
    for i, doc_info in enumerate(documents):
        doc_id = ObjectId()
        doc_ids.append(doc_id)

        # Copy test PDF to patient directory with date prefix
        src_pdf = TEST_PDFS[i % len(TEST_PDFS)]
        # Format: YYYY_MM_DD_document_name.pdf
        date_prefix = doc_info['date'].replace('/', '_')
        dest_filename = f"{date_prefix}_{doc_info['name'].lower().replace(' ', '_')}.pdf"
        dest_path = os.path.join(patient_doc_dir, dest_filename)

        if not os.path.exists(dest_path):
            shutil.copy(src_pdf, dest_path)

        document = {
            "_id": doc_id,
            "denial_id": str(denial_id),
            "patient_id": patient_id,
            "document_name": doc_info["name"],
            "document_type": doc_info["type"],
            "document_date": doc_info["date"],
            "file_path": dest_path,
            "total_pages": 1,
            "presigned_urls": {},
            "uploaded_at": datetime.utcnow(),
        }

        await db.patient_documents.insert_one(document)
        print(f"  Created document: {doc_info['name']} ({str(doc_id)})")

    return str(denial_id), [str(d) for d in doc_ids]


async def main():
    print("Setting up clean test data...")
    print("=" * 50)

    # Case 1: Hip Replacement - Already exists (CLM-TKA-2024-001)
    # We'll add 2 more complete cases

    # Case 2: Lumbar Spine Surgery
    denial_id_2, doc_ids_2 = await create_denial_with_documents(
        claim_number="CLM-SPINE-2024-001",
        patient_name="Robert Martinez",
        patient_id="PT-200001",
        payer_name="Aetna",
        procedure_code="63047",
        diagnosis_codes="M54.5,M51.16",
        denial_category="Medical Necessity",
        claim_amount=45000.00,
        documents=[
            {"name": "Neurology Consultation", "type": "Consultation", "date": "2024/08/15"},
            {"name": "MRI Lumbar Spine Report", "type": "Imaging", "date": "2024/08/20"},
            {"name": "Physical Therapy Records", "type": "Therapy", "date": "2024/09/01"},
            {"name": "Pain Management Notes", "type": "Progress Note", "date": "2024/09/15"},
        ]
    )

    # Case 3: Knee Arthroscopy
    denial_id_3, doc_ids_3 = await create_denial_with_documents(
        claim_number="CLM-KNEE-2024-001",
        patient_name="Emily Thompson",
        patient_id="PT-200002",
        payer_name="Cigna",
        procedure_code="29881",
        diagnosis_codes="M23.21,S83.511A",
        denial_category="Prior Authorization",
        claim_amount=12500.00,
        documents=[
            {"name": "Orthopedic Evaluation", "type": "Consultation", "date": "2024/07/10"},
            {"name": "Knee MRI Report", "type": "Imaging", "date": "2024/07/15"},
            {"name": "Conservative Treatment Summary", "type": "Progress Note", "date": "2024/08/01"},
        ]
    )

    # Case 4: Emergency Department Visit
    denial_id_4, doc_ids_4 = await create_denial_with_documents(
        claim_number="CLM-ED-2024-001",
        patient_name="Michael Chen",
        patient_id="PT-200003",
        payer_name="UnitedHealthcare",
        procedure_code="99285",
        diagnosis_codes="R07.9,I21.3",
        denial_category="Medical Necessity",
        claim_amount=8500.00,
        documents=[
            {"name": "ED Physician Notes", "type": "ED Note", "date": "2024/10/01"},
            {"name": "EKG Report", "type": "Diagnostic", "date": "2024/10/01"},
            {"name": "Cardiac Enzymes Lab Results", "type": "Lab", "date": "2024/10/01"},
        ]
    )

    print("")
    print("=" * 50)
    print("Data setup complete!")
    print("")

    # Print summary
    denial_count = await db.denials.count_documents({})
    doc_count = await db.patient_documents.count_documents({})
    eval_count = await db.criteria_evaluations.count_documents({})

    print(f"Total denials: {denial_count}")
    print(f"Total documents: {doc_count}")
    print(f"Total criteria evaluations: {eval_count}")
    print("")
    print("New denials created:")
    print(f"  1. CLM-SPINE-2024-001 (ID: {denial_id_2}) - PT-200001")
    print(f"  2. CLM-KNEE-2024-001 (ID: {denial_id_3}) - PT-200002")
    print(f"  3. CLM-ED-2024-001 (ID: {denial_id_4}) - PT-200003")


if __name__ == "__main__":
    asyncio.run(main())
