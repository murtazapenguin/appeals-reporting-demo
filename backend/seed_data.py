import asyncio
from datetime import datetime, timedelta
from auth import hash_password
from utils.db_utils import (
    users_collection,
    denials_collection,
    medical_policies_collection,
    patient_documents_collection
)

async def seed_database():
    """Seed the database with initial data."""
    print("Starting database seeding...")

    # Clear existing data
    await users_collection.delete_many({})
    await denials_collection.delete_many({})
    await medical_policies_collection.delete_many({})
    await patient_documents_collection.delete_many({})

    # 1. Create demo user
    demo_user = {
        "email": "demo@penguinai.com",
        "password": hash_password("demo123"),
        "name": "Demo User",
        "role": "appeals_manager"
    }
    user_result = await users_collection.insert_one(demo_user)
    print(f"Created demo user: {demo_user['email']}")

    # 2. Create medical policies
    policies = [
        {
            "payer_id": "PAY-001",
            "payer_name": "Blue Cross Blue Shield",
            "cpt_code": "27447",
            "policy_number": "MP-BCBS-27447",
            "criteria": [
                {
                    "id": "criteria1",
                    "category": "Medical Necessity",
                    "question": "Patient has documented chronic joint pain for >6 months",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["chronic pain", "joint pain", "6 months", "ongoing"],
                    "document_types_expected": ["progress_note", "history_physical"]
                },
                {
                    "id": "criteria2",
                    "category": "Conservative Treatment",
                    "question": "Conservative treatment (PT, medications) tried and failed",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["physical therapy", "PT", "medication", "failed", "unsuccessful"],
                    "document_types_expected": ["physical_therapy_notes", "medication_records"]
                },
                {
                    "id": "criteria3",
                    "category": "Imaging",
                    "question": "Imaging (X-ray or MRI) shows severe joint degeneration",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["X-ray", "MRI", "degeneration", "severe", "bone-on-bone"],
                    "document_types_expected": ["radiology_report", "imaging"]
                },
                {
                    "id": "criteria4",
                    "category": "Functional Impact",
                    "question": "Documented functional impairment affecting daily activities",
                    "required": True,
                    "weight": 1.0,
                    "evidence_keywords": ["functional impairment", "daily activities", "mobility", "walking"],
                    "document_types_expected": ["progress_note", "functional_assessment"]
                },
                {
                    "id": "criteria5",
                    "category": "Specialist Recommendation",
                    "question": "Orthopedic surgeon recommendation for total knee replacement",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["orthopedic", "surgeon", "recommendation", "arthroplasty", "replacement"],
                    "document_types_expected": ["orthopedic_consult", "surgical_clearance"]
                }
            ]
        },
        {
            "payer_id": "PAY-002",
            "payer_name": "United Healthcare",
            "cpt_code": "99285",
            "policy_number": "MP-UHC-99285",
            "criteria": [
                {
                    "id": "criteria1",
                    "category": "Severity",
                    "question": "Immediate threat to life or physiologic function",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["emergency", "severe", "critical", "life-threatening"],
                    "document_types_expected": ["emergency_room_record"]
                },
                {
                    "id": "criteria2",
                    "category": "Documentation",
                    "question": "High complexity medical decision making documented",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["complex", "decision making", "differential diagnosis"],
                    "document_types_expected": ["emergency_room_record"]
                },
                {
                    "id": "criteria3",
                    "category": "Services Provided",
                    "question": "Extended ER services and monitoring required",
                    "required": True,
                    "weight": 1.0,
                    "evidence_keywords": ["monitoring", "extended", "observation", "continuous"],
                    "document_types_expected": ["emergency_room_record", "nursing_notes"]
                },
                {
                    "id": "criteria4",
                    "category": "Time",
                    "question": "Visit duration and complexity justify Level 5 coding",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["duration", "time", "prolonged", "extensive"],
                    "document_types_expected": ["emergency_room_record"]
                }
            ]
        },
        {
            "payer_id": "PAY-003",
            "payer_name": "Aetna",
            "cpt_code": "72148",
            "policy_number": "MP-AETNA-72148",
            "criteria": [
                {
                    "id": "criteria1",
                    "category": "Clinical Indication",
                    "question": "Clinical symptoms warrant MRI imaging (vs X-ray)",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["radiculopathy", "neurologic", "severe pain", "MRI indicated"],
                    "document_types_expected": ["progress_note", "referral"]
                },
                {
                    "id": "criteria2",
                    "category": "Prior Imaging",
                    "question": "X-ray or other imaging inconclusive or insufficient",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["X-ray", "inconclusive", "insufficient", "additional imaging"],
                    "document_types_expected": ["radiology_report"]
                },
                {
                    "id": "criteria3",
                    "category": "Treatment Planning",
                    "question": "MRI results will alter treatment plan",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["treatment plan", "surgical", "intervention", "management"],
                    "document_types_expected": ["progress_note", "treatment_plan"]
                }
            ]
        }
    ]

    for policy in policies:
        await medical_policies_collection.insert_one(policy)
    print(f"Created {len(policies)} medical policies")

    # 3. Create sample denials
    today = datetime.utcnow()

    denials = [
        {
            "claim_number": "CLM-2024-001",
            "patient_name": "Margaret Johnson",
            "patient_id": "PT-001234",
            "patient_dob": "1958-03-15",
            "provider_name": "Dr. Sarah Wilson",
            "provider_id": "PRV-001",
            "payer_name": "Blue Cross Blue Shield",
            "payer_id": "PAY-001",
            "policy_number": "POL-987654",
            "service_date": (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=30)).strftime("%Y-%m-%d"),
            "denial_code": "MN001",
            "denial_category": "Medical Necessity",
            "denial_reason": "Lack of medical necessity documentation for total knee arthroplasty",
            "claim_amount": 45000.00,
            "procedure_code": "27447",
            "diagnosis_codes": "M17.11, M25.561, G89.29",
            "service_description": "Total knee arthroplasty",
            "status": "pending",
            "priority": "high",
            "internal_notes": "Patient has 18-month documented chronic pain history",
            "created_at": today - timedelta(days=30),
            "updated_at": today - timedelta(days=30),
            "appeal_deadline": (today).strftime("%Y-%m-%d")
        },
        {
            "claim_number": "CLM-2024-002",
            "patient_name": "Robert Chen",
            "patient_id": "PT-001235",
            "patient_dob": "1972-07-22",
            "provider_name": "Dr. Michael Torres",
            "provider_id": "PRV-002",
            "payer_name": "United Healthcare",
            "payer_id": "PAY-002",
            "policy_number": "POL-123456",
            "service_date": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=45)).strftime("%Y-%m-%d"),
            "denial_code": "CC001",
            "denial_category": "Coding Error",
            "denial_reason": "Level 5 ER visit not supported by documentation",
            "claim_amount": 2500.00,
            "procedure_code": "99285",
            "diagnosis_codes": "I21.3, I50.9",
            "service_description": "Emergency room visit - Level 5",
            "status": "in_review",
            "win_probability": 85,
            "priority": "normal",
            "internal_notes": "Strong documentation of high complexity decision making",
            "created_at": today - timedelta(days=45),
            "updated_at": today - timedelta(days=20),
            "appeal_deadline": (today - timedelta(days=15)).strftime("%Y-%m-%d")
        },
        {
            "claim_number": "CLM-2024-003",
            "patient_name": "Linda Martinez",
            "patient_id": "PT-001236",
            "patient_dob": "1965-11-08",
            "provider_name": "Dr. Emily Parker",
            "provider_id": "PRV-003",
            "payer_name": "Aetna",
            "payer_id": "PAY-003",
            "policy_number": "POL-555777",
            "service_date": (today - timedelta(days=75)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=60)).strftime("%Y-%m-%d"),
            "denial_code": "PA001",
            "denial_category": "Prior Authorization",
            "denial_reason": "MRI lumbar spine not pre-authorized",
            "claim_amount": 1800.00,
            "procedure_code": "72148",
            "diagnosis_codes": "M54.5, M51.26",
            "service_description": "MRI lumbar spine without contrast",
            "status": "appeal_ready",
            "win_probability": 70,
            "priority": "normal",
            "internal_notes": "Emergency circumstances - prior auth not feasible",
            "created_at": today - timedelta(days=60),
            "updated_at": today - timedelta(days=10),
            "appeal_deadline": (today - timedelta(days=30)).strftime("%Y-%m-%d")
        },
        {
            "claim_number": "CLM-2024-004",
            "patient_name": "James Anderson",
            "patient_id": "PT-001237",
            "patient_dob": "1950-05-20",
            "provider_name": "Dr. Sarah Wilson",
            "provider_id": "PRV-001",
            "payer_name": "Blue Cross Blue Shield",
            "payer_id": "PAY-001",
            "policy_number": "POL-888999",
            "service_date": (today - timedelta(days=90)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=75)).strftime("%Y-%m-%d"),
            "denial_code": "MN001",
            "denial_category": "Medical Necessity",
            "denial_reason": "Insufficient documentation of conservative treatment failure",
            "claim_amount": 48000.00,
            "procedure_code": "27447",
            "diagnosis_codes": "M17.0, M25.562",
            "service_description": "Total knee arthroplasty",
            "status": "submitted",
            "win_probability": 75,
            "priority": "high",
            "internal_notes": "Strong case - extensive PT records available",
            "created_at": today - timedelta(days=75),
            "updated_at": today - timedelta(days=5),
            "appeal_deadline": (today - timedelta(days=45)).strftime("%Y-%m-%d")
        },
        {
            "claim_number": "CLM-2024-005",
            "patient_name": "Patricia Brown",
            "patient_id": "PT-001238",
            "patient_dob": "1980-09-12",
            "provider_name": "Dr. Michael Torres",
            "provider_id": "PRV-002",
            "payer_name": "United Healthcare",
            "payer_id": "PAY-002",
            "policy_number": "POL-333444",
            "service_date": (today - timedelta(days=100)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=85)).strftime("%Y-%m-%d"),
            "denial_code": "DOC001",
            "denial_category": "Documentation",
            "denial_reason": "Missing required documentation",
            "claim_amount": 3200.00,
            "procedure_code": "99285",
            "diagnosis_codes": "J96.00, R06.03",
            "service_description": "Emergency room visit - respiratory distress",
            "status": "approved",
            "win_probability": 90,
            "priority": "urgent",
            "internal_notes": "Additional documentation submitted - APPROVED",
            "created_at": today - timedelta(days=85),
            "updated_at": today - timedelta(days=3),
            "appeal_deadline": (today - timedelta(days=55)).strftime("%Y-%m-%d")
        },
        {
            "claim_number": "CLM-2024-006",
            "patient_name": "William Taylor",
            "patient_id": "PT-001239",
            "patient_dob": "1968-02-28",
            "provider_name": "Dr. Emily Parker",
            "provider_id": "PRV-003",
            "payer_name": "Aetna",
            "payer_id": "PAY-003",
            "policy_number": "POL-666888",
            "service_date": (today - timedelta(days=50)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=35)).strftime("%Y-%m-%d"),
            "denial_code": "MN001",
            "denial_category": "Medical Necessity",
            "denial_reason": "X-ray sufficient, MRI not medically necessary",
            "claim_amount": 1950.00,
            "procedure_code": "72148",
            "diagnosis_codes": "M54.5, M48.06",
            "service_description": "MRI lumbar spine with contrast",
            "status": "denied",
            "win_probability": 45,
            "priority": "low",
            "internal_notes": "Weak case - X-ray was recent and clear",
            "created_at": today - timedelta(days=35),
            "updated_at": today - timedelta(days=2),
            "appeal_deadline": (today - timedelta(days=5)).strftime("%Y-%m-%d")
        },
        {
            "claim_number": "CLM-2024-007",
            "patient_name": "Susan White",
            "patient_id": "PT-001240",
            "patient_dob": "1955-12-03",
            "provider_name": "Dr. Sarah Wilson",
            "provider_id": "PRV-001",
            "payer_name": "Blue Cross Blue Shield",
            "payer_id": "PAY-001",
            "policy_number": "POL-111222",
            "service_date": (today - timedelta(days=25)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=10)).strftime("%Y-%m-%d"),
            "denial_code": "MN001",
            "denial_category": "Medical Necessity",
            "denial_reason": "Conservative treatment duration insufficient",
            "claim_amount": 46500.00,
            "procedure_code": "27447",
            "diagnosis_codes": "M17.12, M25.562, M79.3",
            "service_description": "Total knee arthroplasty - bilateral",
            "status": "pending",
            "priority": "urgent",
            "internal_notes": "NEW - requires immediate review",
            "created_at": today - timedelta(days=10),
            "updated_at": today - timedelta(days=10),
            "appeal_deadline": (today + timedelta(days=20)).strftime("%Y-%m-%d")
        }
    ]

    # Insert denials and collect their IDs
    denial_ids = []
    for denial in denials:
        result = await denials_collection.insert_one(denial)
        denial_ids.append(str(result.inserted_id))
    print(f"Created {len(denials)} sample denials")

    # 4. Create sample documents for the first denial (Margaret Johnson - Total Knee Arthroplasty)
    # Using document types that match REQUIRED_DOCUMENTS in frontend
    sample_documents = [
        {
            "denial_id": denial_ids[0],
            "patient_id": "PT-001234",
            "document_name": "medical_records_2024_01.pdf",
            "document_type": "medical_records",
            "document_date": "2024-01-15",
            "presigned_urls": {
                "1": "https://example.com/doc1/page1.png",
                "2": "https://example.com/doc1/page2.png",
                "3": "https://example.com/doc1/page3.png"
            },
            "total_pages": 3,
            "uploaded_at": datetime.utcnow()
        },
        {
            "denial_id": denial_ids[0],
            "patient_id": "PT-001234",
            "document_name": "prior_visit_notes_2023.pdf",
            "document_type": "prior_visit_notes",
            "document_date": "2023-09-15",
            "presigned_urls": {
                "1": "https://example.com/doc2/page1.png",
                "2": "https://example.com/doc2/page2.png"
            },
            "total_pages": 2,
            "uploaded_at": datetime.utcnow()
        },
        {
            "denial_id": denial_ids[0],
            "patient_id": "PT-001234",
            "document_name": "mri_lumbar_spine_report.pdf",
            "document_type": "diagnostic_tests",
            "document_date": "2024-01-10",
            "presigned_urls": {
                "1": "https://example.com/doc3/page1.png",
                "2": "https://example.com/doc3/page2.png"
            },
            "total_pages": 2,
            "uploaded_at": datetime.utcnow()
        },
        {
            "denial_id": denial_ids[0],
            "patient_id": "PT-001234",
            "document_name": "cms1500_claim_form.pdf",
            "document_type": "claim_form",
            "document_date": "2024-01-20",
            "presigned_urls": {
                "1": "https://example.com/doc4/page1.png"
            },
            "total_pages": 1,
            "uploaded_at": datetime.utcnow()
        },
        {
            "denial_id": denial_ids[0],
            "patient_id": "PT-001234",
            "document_name": "eob_denial_notice.pdf",
            "document_type": "eob",
            "document_date": "2024-01-25",
            "presigned_urls": {
                "1": "https://example.com/doc5/page1.png",
                "2": "https://example.com/doc5/page2.png"
            },
            "total_pages": 2,
            "uploaded_at": datetime.utcnow()
        },
        # Add a few documents for the second denial (Robert Chen - ER Visit)
        {
            "denial_id": denial_ids[1],
            "patient_id": "PT-001235",
            "document_name": "er_medical_records.pdf",
            "document_type": "medical_records",
            "document_date": "2024-01-05",
            "presigned_urls": {
                "1": "https://example.com/doc6/page1.png",
                "2": "https://example.com/doc6/page2.png"
            },
            "total_pages": 2,
            "uploaded_at": datetime.utcnow()
        },
        {
            "denial_id": denial_ids[1],
            "patient_id": "PT-001235",
            "document_name": "claim_form_99285.pdf",
            "document_type": "claim_form",
            "document_date": "2024-01-10",
            "presigned_urls": {
                "1": "https://example.com/doc7/page1.png"
            },
            "total_pages": 1,
            "uploaded_at": datetime.utcnow()
        },
        {
            "denial_id": denial_ids[1],
            "patient_id": "PT-001235",
            "document_name": "eob_remittance.pdf",
            "document_type": "eob",
            "document_date": "2024-01-15",
            "presigned_urls": {
                "1": "https://example.com/doc8/page1.png"
            },
            "total_pages": 1,
            "uploaded_at": datetime.utcnow()
        }
    ]

    for doc in sample_documents:
        await patient_documents_collection.insert_one(doc)
    print(f"Created {len(sample_documents)} sample documents")

    print("\n" + "="*50)
    print("Database seeding completed!")
    print("="*50)
    print(f"\nDemo Credentials:")
    print(f"  Email: {demo_user['email']}")
    print(f"  Password: demo123")
    print(f"\nCreated:")
    print(f"  - 1 user")
    print(f"  - {len(policies)} medical policies")
    print(f"  - {len(denials)} denials")
    print(f"  - {len(sample_documents)} documents")
    print(f"\nStatus breakdown:")
    status_counts = {}
    for d in denials:
        status = d["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    for status, count in status_counts.items():
        print(f"  - {status}: {count}")

if __name__ == "__main__":
    asyncio.run(seed_database())
