import asyncio
from datetime import datetime, timedelta
import random
from auth import hash_password
from utils.db_utils import (
    users_collection,
    denials_collection,
    medical_policies_collection,
    patient_documents_collection,
    criteria_evaluations_collection,
    appeal_packages_collection
)

async def seed_comprehensive():
    """Seed the database with comprehensive data for demo."""
    print("=" * 60)
    print("COMPREHENSIVE DATABASE SEEDING")
    print("=" * 60)

    # Clear existing data
    await users_collection.delete_many({})
    await denials_collection.delete_many({})
    await medical_policies_collection.delete_many({})
    await patient_documents_collection.delete_many({})
    await criteria_evaluations_collection.delete_many({})
    await appeal_packages_collection.delete_many({})
    print("\n[1/6] Cleared existing data")

    # ================================================================
    # 1. USERS
    # ================================================================
    users = [
        {
            "email": "demo@penguinai.com",
            "password": hash_password("demo123"),
            "name": "Demo User",
            "role": "appeals_manager"
        },
        {
            "email": "admin@penguinai.com",
            "password": hash_password("admin123"),
            "name": "Admin User",
            "role": "admin"
        },
        {
            "email": "reviewer@penguinai.com",
            "password": hash_password("review123"),
            "name": "Claims Reviewer",
            "role": "reviewer"
        }
    ]

    for user in users:
        await users_collection.insert_one(user)
    print(f"[2/6] Created {len(users)} users")

    # ================================================================
    # 2. MEDICAL POLICIES (Payer + CPT Code combinations)
    # ================================================================
    policies = [
        # Blue Cross Blue Shield Policies
        {
            "payer_id": "PAY-BCBS",
            "payer_name": "Blue Cross Blue Shield",
            "cpt_code": "27447",
            "cpt_description": "Total Knee Arthroplasty",
            "denial_category": "Medical Necessity",
            "policy_name": "Total Joint Replacement Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "TKA-1",
                    "category": "Conservative Treatment",
                    "question": "Has the patient completed at least 6 months of conservative treatment (physical therapy, NSAIDs, injections)?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["physical therapy", "PT", "NSAID", "injection", "cortisone", "conservative", "6 months"],
                    "document_types_expected": ["Physical Therapy Records", "Progress Notes", "Medication List"],
                    "response_type": "boolean"
                },
                {
                    "id": "TKA-2",
                    "category": "Diagnostic Evidence",
                    "question": "Does imaging show bone-on-bone contact or Grade IV cartilage loss (Kellgren-Lawrence Grade 4)?",
                    "required": True,
                    "weight": 2.5,
                    "evidence_keywords": ["bone-on-bone", "Grade IV", "Grade 4", "severe", "cartilage loss", "Kellgren-Lawrence"],
                    "document_types_expected": ["X-Ray Report", "MRI Report", "Radiology Report"],
                    "response_type": "boolean"
                },
                {
                    "id": "TKA-3",
                    "category": "Functional Limitation",
                    "question": "Is there documented significant functional limitation affecting daily activities (walking, stairs, ADLs)?",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["functional limitation", "walking", "stairs", "ADL", "daily activities", "mobility", "disability"],
                    "document_types_expected": ["Progress Notes", "Functional Assessment", "History & Physical"],
                    "response_type": "boolean"
                },
                {
                    "id": "TKA-4",
                    "category": "Treatment Failure",
                    "question": "Has the patient's condition failed to improve despite conservative measures?",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["failed", "no improvement", "worsening", "unsuccessful", "refractory"],
                    "document_types_expected": ["Progress Notes", "Physical Therapy Notes"],
                    "response_type": "boolean"
                },
                {
                    "id": "TKA-5",
                    "category": "BMI Documentation",
                    "question": "Is BMI documented as < 40 or with bariatric clearance if BMI >= 40?",
                    "required": True,
                    "weight": 1.0,
                    "evidence_keywords": ["BMI", "weight", "bariatric", "obesity", "clearance"],
                    "document_types_expected": ["Pre-operative Assessment", "History & Physical"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["AAOS Guidelines 2023", "CMS LCD L33724"],
            "historical_overturn_rate": 0.72,
            "average_processing_days": 21
        },
        {
            "payer_id": "PAY-BCBS",
            "payer_name": "Blue Cross Blue Shield",
            "cpt_code": "27130",
            "cpt_description": "Total Hip Arthroplasty",
            "denial_category": "Medical Necessity",
            "policy_name": "Total Joint Replacement Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "THA-1",
                    "category": "Conservative Treatment",
                    "question": "Has the patient tried conservative treatment for at least 3 months?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["physical therapy", "PT", "conservative", "3 months", "NSAID"],
                    "document_types_expected": ["Physical Therapy Records", "Progress Notes"],
                    "response_type": "boolean"
                },
                {
                    "id": "THA-2",
                    "category": "Imaging Evidence",
                    "question": "Does X-ray or MRI show severe hip joint deterioration?",
                    "required": True,
                    "weight": 2.5,
                    "evidence_keywords": ["avascular necrosis", "severe arthritis", "joint space narrowing", "osteonecrosis"],
                    "document_types_expected": ["X-Ray Report", "MRI Report"],
                    "response_type": "boolean"
                },
                {
                    "id": "THA-3",
                    "category": "Pain and Function",
                    "question": "Is there documented chronic hip pain limiting ambulation?",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["hip pain", "chronic", "ambulation", "walking difficulty", "limp"],
                    "document_types_expected": ["Progress Notes", "Orthopedic Consult"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["AAOS Guidelines 2023"],
            "historical_overturn_rate": 0.68,
            "average_processing_days": 18
        },
        # United Healthcare Policies
        {
            "payer_id": "PAY-UHC",
            "payer_name": "United Healthcare",
            "cpt_code": "99285",
            "cpt_description": "Emergency Department Visit - Level 5",
            "denial_category": "Coding Error",
            "policy_name": "ED Visit Medical Necessity",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "ED5-1",
                    "category": "Severity",
                    "question": "Does documentation show immediate threat to life or physiologic function?",
                    "required": True,
                    "weight": 2.5,
                    "evidence_keywords": ["life-threatening", "critical", "severe", "acute", "emergency", "unstable"],
                    "document_types_expected": ["Emergency Room Record", "Triage Notes"],
                    "response_type": "boolean"
                },
                {
                    "id": "ED5-2",
                    "category": "Medical Decision Making",
                    "question": "Is high complexity medical decision making documented (multiple diagnoses, high-risk medications)?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["high complexity", "MDM", "differential diagnosis", "multiple diagnoses", "high risk"],
                    "document_types_expected": ["Emergency Room Record", "Physician Notes"],
                    "response_type": "boolean"
                },
                {
                    "id": "ED5-3",
                    "category": "Time Documentation",
                    "question": "Is total time spent documented and consistent with Level 5 requirements (>60 minutes)?",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["60 minutes", "time", "duration", "prolonged", "extended"],
                    "document_types_expected": ["Emergency Room Record", "Time Log"],
                    "response_type": "boolean"
                },
                {
                    "id": "ED5-4",
                    "category": "Services Rendered",
                    "question": "Were extensive services and monitoring required (IV, multiple tests, procedures)?",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["IV", "monitoring", "laboratory", "imaging", "procedure", "continuous"],
                    "document_types_expected": ["Emergency Room Record", "Nursing Notes", "Lab Results"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["AMA E/M Guidelines 2023", "ACEP Guidelines"],
            "historical_overturn_rate": 0.78,
            "average_processing_days": 14
        },
        {
            "payer_id": "PAY-UHC",
            "payer_name": "United Healthcare",
            "cpt_code": "99284",
            "cpt_description": "Emergency Department Visit - Level 4",
            "denial_category": "Coding Error",
            "policy_name": "ED Visit Medical Necessity",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "ED4-1",
                    "category": "Severity",
                    "question": "Does documentation show urgent condition requiring prompt attention?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["urgent", "acute", "prompt", "timely"],
                    "document_types_expected": ["Emergency Room Record"],
                    "response_type": "boolean"
                },
                {
                    "id": "ED4-2",
                    "category": "Medical Decision Making",
                    "question": "Is moderate complexity medical decision making documented?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["moderate complexity", "MDM", "diagnosis", "treatment plan"],
                    "document_types_expected": ["Emergency Room Record"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["AMA E/M Guidelines 2023"],
            "historical_overturn_rate": 0.82,
            "average_processing_days": 12
        },
        # Aetna Policies
        {
            "payer_id": "PAY-AETNA",
            "payer_name": "Aetna",
            "cpt_code": "72148",
            "cpt_description": "MRI Lumbar Spine Without Contrast",
            "denial_category": "Prior Authorization",
            "policy_name": "Advanced Imaging Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "MRI-1",
                    "category": "Clinical Indication",
                    "question": "Are neurological symptoms (radiculopathy, weakness, numbness) documented?",
                    "required": True,
                    "weight": 2.5,
                    "evidence_keywords": ["radiculopathy", "weakness", "numbness", "neurological", "nerve", "tingling"],
                    "document_types_expected": ["Progress Notes", "Neurology Consult"],
                    "response_type": "boolean"
                },
                {
                    "id": "MRI-2",
                    "category": "Conservative Treatment",
                    "question": "Has patient failed 4-6 weeks of conservative treatment?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["4 weeks", "6 weeks", "conservative", "failed", "physical therapy", "medication"],
                    "document_types_expected": ["Progress Notes", "Physical Therapy Records"],
                    "response_type": "boolean"
                },
                {
                    "id": "MRI-3",
                    "category": "Red Flags",
                    "question": "Are there red flag symptoms (cauda equina, progressive neurological deficit, cancer history)?",
                    "required": False,
                    "weight": 3.0,
                    "evidence_keywords": ["cauda equina", "bladder", "bowel", "progressive", "cancer", "malignancy", "red flag"],
                    "document_types_expected": ["Progress Notes", "History & Physical"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["ACR Appropriateness Criteria", "Choosing Wisely"],
            "historical_overturn_rate": 0.65,
            "average_processing_days": 10
        },
        {
            "payer_id": "PAY-AETNA",
            "payer_name": "Aetna",
            "cpt_code": "72141",
            "cpt_description": "MRI Cervical Spine Without Contrast",
            "denial_category": "Prior Authorization",
            "policy_name": "Advanced Imaging Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "CMRI-1",
                    "category": "Clinical Indication",
                    "question": "Are cervical radiculopathy symptoms documented?",
                    "required": True,
                    "weight": 2.5,
                    "evidence_keywords": ["cervical radiculopathy", "arm pain", "neck pain", "numbness", "weakness"],
                    "document_types_expected": ["Progress Notes", "Neurology Consult"],
                    "response_type": "boolean"
                },
                {
                    "id": "CMRI-2",
                    "category": "Conservative Treatment",
                    "question": "Has patient completed conservative treatment trial?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["conservative", "physical therapy", "NSAIDs", "failed"],
                    "document_types_expected": ["Progress Notes", "Physical Therapy Records"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["ACR Appropriateness Criteria"],
            "historical_overturn_rate": 0.70,
            "average_processing_days": 10
        },
        # Cigna Policies
        {
            "payer_id": "PAY-CIGNA",
            "payer_name": "Cigna",
            "cpt_code": "29881",
            "cpt_description": "Knee Arthroscopy with Meniscectomy",
            "denial_category": "Medical Necessity",
            "policy_name": "Knee Surgery Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "ARTH-1",
                    "category": "Conservative Treatment",
                    "question": "Has patient failed 6 weeks of conservative treatment?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["6 weeks", "conservative", "physical therapy", "failed", "RICE"],
                    "document_types_expected": ["Progress Notes", "Physical Therapy Records"],
                    "response_type": "boolean"
                },
                {
                    "id": "ARTH-2",
                    "category": "Imaging Evidence",
                    "question": "Does MRI show meniscal tear requiring surgical intervention?",
                    "required": True,
                    "weight": 2.5,
                    "evidence_keywords": ["meniscal tear", "MRI", "surgical", "bucket handle", "complex tear"],
                    "document_types_expected": ["MRI Report", "Radiology Report"],
                    "response_type": "boolean"
                },
                {
                    "id": "ARTH-3",
                    "category": "Mechanical Symptoms",
                    "question": "Are mechanical symptoms (locking, catching, giving way) documented?",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["locking", "catching", "giving way", "mechanical", "instability"],
                    "document_types_expected": ["Progress Notes", "Orthopedic Consult"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["AAOS Guidelines"],
            "historical_overturn_rate": 0.75,
            "average_processing_days": 15
        },
        # Humana Policies
        {
            "payer_id": "PAY-HUMANA",
            "payer_name": "Humana",
            "cpt_code": "63047",
            "cpt_description": "Lumbar Laminectomy",
            "denial_category": "Medical Necessity",
            "policy_name": "Spine Surgery Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {
                    "id": "LAMI-1",
                    "category": "Conservative Treatment",
                    "question": "Has patient failed 12 weeks of conservative treatment including PT and injections?",
                    "required": True,
                    "weight": 2.0,
                    "evidence_keywords": ["12 weeks", "conservative", "physical therapy", "injection", "epidural", "failed"],
                    "document_types_expected": ["Progress Notes", "Physical Therapy Records", "Procedure Notes"],
                    "response_type": "boolean"
                },
                {
                    "id": "LAMI-2",
                    "category": "Imaging Correlation",
                    "question": "Does imaging correlate with clinical presentation (stenosis at symptomatic level)?",
                    "required": True,
                    "weight": 2.5,
                    "evidence_keywords": ["stenosis", "correlation", "symptomatic level", "compression", "MRI"],
                    "document_types_expected": ["MRI Report", "Progress Notes"],
                    "response_type": "boolean"
                },
                {
                    "id": "LAMI-3",
                    "category": "Neurological Deficit",
                    "question": "Is progressive neurological deficit documented?",
                    "required": False,
                    "weight": 3.0,
                    "evidence_keywords": ["neurological deficit", "progressive", "weakness", "motor deficit"],
                    "document_types_expected": ["Neurology Consult", "Progress Notes"],
                    "response_type": "boolean"
                },
                {
                    "id": "LAMI-4",
                    "category": "Functional Impact",
                    "question": "Is significant functional impairment documented (unable to walk >2 blocks)?",
                    "required": True,
                    "weight": 1.5,
                    "evidence_keywords": ["functional", "walking", "ambulation", "limited", "disability"],
                    "document_types_expected": ["Progress Notes", "Functional Assessment"],
                    "response_type": "boolean"
                }
            ],
            "clinical_guidelines": ["NASS Guidelines", "CMS LCD"],
            "historical_overturn_rate": 0.60,
            "average_processing_days": 25
        }
    ]

    for policy in policies:
        await medical_policies_collection.insert_one(policy)
    print(f"[3/6] Created {len(policies)} medical policies")

    # ================================================================
    # 3. DENIALS (15 comprehensive denials)
    # ================================================================
    today = datetime.utcnow()

    patient_names = [
        "Margaret Johnson", "Robert Chen", "Linda Martinez", "James Anderson",
        "Patricia Brown", "William Taylor", "Susan White", "David Lee",
        "Jennifer Garcia", "Michael Williams", "Elizabeth Jones", "Thomas Davis",
        "Barbara Miller", "Richard Wilson", "Nancy Moore"
    ]

    providers = [
        ("Dr. Sarah Wilson", "PRV-001", "Wilson Orthopedic Center", "123 Medical Plaza, Suite 400, Austin, TX 78701", "(512) 555-0100"),
        ("Dr. Michael Torres", "PRV-002", "Torres Emergency Medicine", "456 Hospital Blvd, Houston, TX 77001", "(713) 555-0200"),
        ("Dr. Emily Parker", "PRV-003", "Parker Spine Institute", "789 Spine Way, Dallas, TX 75201", "(214) 555-0300"),
        ("Dr. John Smith", "PRV-004", "Smith Surgical Associates", "321 Surgical Center, San Antonio, TX 78201", "(210) 555-0400"),
        ("Dr. Lisa Chen", "PRV-005", "Chen Neurology Group", "555 Neuro Drive, Fort Worth, TX 76101", "(817) 555-0500")
    ]

    payers = [
        ("Blue Cross Blue Shield", "PAY-BCBS"),
        ("United Healthcare", "PAY-UHC"),
        ("Aetna", "PAY-AETNA"),
        ("Cigna", "PAY-CIGNA"),
        ("Humana", "PAY-HUMANA")
    ]

    statuses = ["pending", "in_review", "appeal_ready", "submitted", "approved", "denied"]
    priorities = ["low", "normal", "high", "urgent"]
    categories = ["Medical Necessity", "Prior Authorization", "Coding Error", "Documentation"]

    procedures = [
        ("27447", "Total Knee Arthroplasty", "M17.11", 45000),
        ("27130", "Total Hip Arthroplasty", "M16.11", 48000),
        ("99285", "ED Visit Level 5", "I21.3", 2500),
        ("99284", "ED Visit Level 4", "R07.9", 1800),
        ("72148", "MRI Lumbar Spine", "M54.5", 1950),
        ("72141", "MRI Cervical Spine", "M54.2", 1850),
        ("29881", "Knee Arthroscopy", "S83.211A", 8500),
        ("63047", "Lumbar Laminectomy", "M48.06", 35000)
    ]

    denials = []
    for i in range(15):
        patient_id = f"PT-{100000 + i}"
        payer = random.choice(payers)
        provider = random.choice(providers)
        procedure = random.choice(procedures)
        status = statuses[i % len(statuses)] if i < len(statuses) else random.choice(statuses)

        service_offset = random.randint(30, 120)
        denial_offset = service_offset - random.randint(10, 25)
        deadline_offset = denial_offset - 30  # 30 days from denial

        win_prob = random.randint(45, 95) if status not in ["pending"] else None

        denial = {
            "claim_number": f"CLM-2024-{str(i+1).zfill(3)}",
            "patient_name": patient_names[i],
            "patient_id": patient_id,
            "patient_dob": f"{random.randint(1950, 1990)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "provider_name": provider[0],
            "provider_id": provider[1],
            "provider_practice": provider[2],
            "provider_address": provider[3],
            "provider_phone": provider[4],
            "payer_name": payer[0],
            "payer_id": payer[1],
            "policy_number": f"POL-{random.randint(100000, 999999)}",
            "group_number": f"GRP-{random.randint(1000, 9999)}",
            "service_date": (today - timedelta(days=service_offset)).strftime("%Y-%m-%d"),
            "denial_date": (today - timedelta(days=denial_offset)).strftime("%Y-%m-%d"),
            "denial_code": f"{categories[i % len(categories)][:2].upper()}{str(i+1).zfill(3)}",
            "denial_category": categories[i % len(categories)],
            "denial_reason": f"Insufficient documentation for {procedure[1]}",
            "claim_amount": procedure[3] + random.randint(-500, 500),
            "procedure_code": procedure[0],
            "procedure_description": procedure[1],
            "diagnosis_codes": procedure[2],
            "service_description": procedure[1],
            "status": status,
            "win_probability": win_prob,
            "priority": priorities[i % len(priorities)],
            "appeal_deadline": (today - timedelta(days=deadline_offset)).strftime("%Y-%m-%d"),
            "internal_notes": f"Case #{i+1} - Review required",
            "created_at": today - timedelta(days=denial_offset),
            "updated_at": today - timedelta(days=random.randint(0, 10))
        }
        denials.append(denial)
        await denials_collection.insert_one(denial)

    print(f"[4/6] Created {len(denials)} denials")

    # ================================================================
    # 4. PATIENT DOCUMENTS
    # ================================================================
    document_types = [
        "Progress Notes", "Physical Therapy Records", "MRI Report", "X-Ray Report",
        "Operative Report", "Discharge Summary", "Lab Results", "History & Physical",
        "Orthopedic Consult", "Neurology Consult", "Pre-operative Assessment"
    ]

    documents = []
    for denial in denials[:10]:  # Create documents for first 10 denials
        num_docs = random.randint(2, 5)
        for j in range(num_docs):
            doc_type = random.choice(document_types)
            doc_date = datetime.strptime(denial["service_date"], "%Y-%m-%d") - timedelta(days=random.randint(1, 60))

            doc = {
                "denial_id": denial["claim_number"],
                "patient_id": denial["patient_id"],
                "document_name": f"{doc_type.lower().replace(' ', '_')}_{doc_date.strftime('%Y%m%d')}.pdf",
                "document_type": doc_type.lower().replace(" ", "_"),
                "document_date": doc_date.strftime("%Y-%m-%d"),
                "file_path": f"/documents/{denial['patient_id']}/{doc_date.strftime('%Y/%m/%d')}/{doc_type.lower().replace(' ', '_')}.pdf",
                "total_pages": random.randint(2, 8),
                "presigned_urls": {
                    str(p): f"https://storage.example.com/{denial['patient_id']}/page{p}.png"
                    for p in range(1, random.randint(3, 6))
                },
                "ocr_text": f"Sample OCR text for {doc_type}. Patient {denial['patient_name']} presented with symptoms...",
                "uploaded_at": datetime.utcnow()
            }
            documents.append(doc)
            await patient_documents_collection.insert_one(doc)

    print(f"[5/6] Created {len(documents)} patient documents")

    # ================================================================
    # 5. SAMPLE CRITERIA EVALUATIONS
    # ================================================================
    evaluations = []
    for denial in denials[:5]:  # Create evaluations for first 5 denials
        criteria_count = random.randint(3, 5)
        criteria_met = random.randint(2, criteria_count)

        criteria = []
        for c in range(criteria_count):
            is_met = c < criteria_met
            criterion = {
                "id": f"criterion_{c+1}",
                "question": f"Sample criterion question {c+1}",
                "met": is_met,
            }
            if is_met:
                criterion["evidence"] = [{
                    "document_id": f"doc_{c}",
                    "document_name": f"sample_document_{c}.pdf",
                    "page": random.randint(1, 5),
                    "text": "Sample evidence text extracted from document...",
                    "bbox": [0.1, 0.2 + c*0.1, 0.9, 0.2 + c*0.1, 0.9, 0.25 + c*0.1, 0.1, 0.25 + c*0.1]
                }]
            else:
                criterion["missing_documents"] = "Required documentation not found"
            criteria.append(criterion)

        evaluation = {
            "denial_id": denial["claim_number"],
            "total_criteria": criteria_count,
            "criteria_met": criteria_met,
            "win_probability": int((criteria_met / criteria_count) * 100),
            "criteria": criteria,
            "evaluated_at": datetime.utcnow()
        }
        evaluations.append(evaluation)
        await criteria_evaluations_collection.insert_one(evaluation)

    print(f"[6/6] Created {len(evaluations)} criteria evaluations")

    # ================================================================
    # SUMMARY
    # ================================================================
    print("\n" + "=" * 60)
    print("DATABASE SEEDING COMPLETE")
    print("=" * 60)

    print(f"\n{'Collection':<30} {'Count':>10}")
    print("-" * 42)
    print(f"{'users':<30} {len(users):>10}")
    print(f"{'medical_policies':<30} {len(policies):>10}")
    print(f"{'denials':<30} {len(denials):>10}")
    print(f"{'patient_documents':<30} {len(documents):>10}")
    print(f"{'criteria_evaluations':<30} {len(evaluations):>10}")

    print(f"\n{'Status':<20} {'Count':>10}")
    print("-" * 32)
    status_counts = {}
    for d in denials:
        s = d["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
    for status, count in sorted(status_counts.items()):
        print(f"{status:<20} {count:>10}")

    print(f"\n{'Payer':<30} {'Count':>10}")
    print("-" * 42)
    payer_counts = {}
    for d in denials:
        p = d["payer_name"]
        payer_counts[p] = payer_counts.get(p, 0) + 1
    for payer, count in sorted(payer_counts.items()):
        print(f"{payer:<30} {count:>10}")

    print("\n" + "=" * 60)
    print("TEST CREDENTIALS")
    print("=" * 60)
    print(f"  Email:    demo@penguinai.com")
    print(f"  Password: demo123")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(seed_comprehensive())
