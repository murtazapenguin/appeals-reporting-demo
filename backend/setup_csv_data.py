"""
Setup documents for CSV import cases.
Creates documents for patients that will be imported via CSV.
These patients will have documents ready so criteria evaluation can be triggered after CSV import.
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
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


async def create_documents_for_patient(patient_id: str, documents: list):
    """Create documents for a patient before denial is imported via CSV."""

    # Create patient document directory
    patient_doc_dir = os.path.join(DOC_DIR, patient_id)
    os.makedirs(patient_doc_dir, exist_ok=True)

    print(f"\nCreating documents for patient: {patient_id}")

    for i, doc_info in enumerate(documents):
        doc_id = ObjectId()

        # Copy test PDF to patient directory with date prefix
        src_pdf = TEST_PDFS[i % len(TEST_PDFS)]
        date_prefix = doc_info['date'].replace('/', '_')
        dest_filename = f"{date_prefix}_{doc_info['name'].lower().replace(' ', '_')}.pdf"
        dest_path = os.path.join(patient_doc_dir, dest_filename)

        if not os.path.exists(dest_path):
            shutil.copy(src_pdf, dest_path)

        document = {
            "_id": doc_id,
            "denial_id": None,  # Will be linked after CSV import
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

    return patient_id


async def main():
    print("Setting up documents for CSV import cases...")
    print("=" * 50)

    # Case 1: PT-300001 - Hip Replacement (will match blue_cross_blue_shield + 27130)
    await create_documents_for_patient(
        patient_id="PT-300001",
        documents=[
            {"name": "Orthopedic Consultation", "type": "Consultation", "date": "2024/08/01"},
            {"name": "Hip X-Ray Report", "type": "Imaging", "date": "2024/08/05"},
            {"name": "Physical Therapy Progress Notes", "type": "Therapy", "date": "2024/08/15"},
            {"name": "Pain Management Evaluation", "type": "Progress Note", "date": "2024/09/01"},
        ]
    )

    # Case 2: PT-300002 - Spine Surgery (will match aetna + 63047)
    await create_documents_for_patient(
        patient_id="PT-300002",
        documents=[
            {"name": "Neurosurgery Consultation", "type": "Consultation", "date": "2024/07/15"},
            {"name": "Lumbar MRI Report", "type": "Imaging", "date": "2024/07/20"},
            {"name": "Conservative Treatment Summary", "type": "Progress Note", "date": "2024/08/01"},
            {"name": "EMG Study Results", "type": "Diagnostic", "date": "2024/08/10"},
        ]
    )

    # Case 3: PT-300003 - Knee Arthroscopy (will match cigna + 29881)
    await create_documents_for_patient(
        patient_id="PT-300003",
        documents=[
            {"name": "Sports Medicine Evaluation", "type": "Consultation", "date": "2024/08/01"},
            {"name": "Knee MRI Report", "type": "Imaging", "date": "2024/08/05"},
            {"name": "Physical Therapy Records", "type": "Therapy", "date": "2024/08/20"},
        ]
    )

    print("")
    print("=" * 50)
    print("Document setup complete!")
    print("")

    # Print summary
    doc_count = await db.patient_documents.count_documents({})
    print(f"Total documents in database: {doc_count}")
    print("")
    print("Documents created for:")
    print("  - PT-300001 (James Wilson - Hip Replacement)")
    print("  - PT-300002 (Patricia Davis - Spine Surgery)")
    print("  - PT-300003 (William Brown - Knee Arthroscopy)")
    print("")
    print("Next steps:")
    print("  1. Upload sample_denials.csv via the UI")
    print("  2. Click on a denial to view details")
    print("  3. Click 'Start Evaluation' to trigger criteria evaluation")


if __name__ == "__main__":
    asyncio.run(main())
