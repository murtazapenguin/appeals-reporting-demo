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
    appeal_packages_collection,
    reference_data_collection,
    questionnaires_collection,
)

random.seed(42)

PAYERS = [
    ("Blue Cross Blue Shield", "PAY-BCBS"),
    ("United Healthcare", "PAY-UHC"),
    ("Aetna", "PAY-AETNA"),
    ("Cigna", "PAY-CIGNA"),
    ("Humana", "PAY-HUMANA"),
]

PRACTICES = [
    {
        "provider_name": "Dr. Sarah Wilson",
        "provider_id": "PRV-001",
        "provider_npi": "1234567890",
        "provider_practice_name": "Wilson Orthopedic Center",
        "provider_address": "123 Medical Plaza, Suite 400, Austin, TX 78701",
        "provider_phone": "(512) 555-0100",
        "provider_tax_id": "74-1234567",
    },
    {
        "provider_name": "Dr. Michael Torres",
        "provider_id": "PRV-002",
        "provider_npi": "2345678901",
        "provider_practice_name": "Torres Emergency Medicine",
        "provider_address": "456 Hospital Blvd, Houston, TX 77001",
        "provider_phone": "(713) 555-0200",
        "provider_tax_id": "74-2345678",
    },
    {
        "provider_name": "Dr. Emily Parker",
        "provider_id": "PRV-003",
        "provider_npi": "3456789012",
        "provider_practice_name": "Parker Spine Institute",
        "provider_address": "789 Spine Way, Dallas, TX 75201",
        "provider_phone": "(214) 555-0300",
        "provider_tax_id": "74-3456789",
    },
    {
        "provider_name": "Dr. Harvey Dent",
        "provider_id": "PRV-004",
        "provider_npi": "4567890123",
        "provider_practice_name": "Dent Reconstructive Surgery",
        "provider_address": "321 Surgical Center, San Antonio, TX 78201",
        "provider_phone": "(210) 555-0400",
        "provider_tax_id": "74-4567890",
    },
    {
        "provider_name": "Dr. Leslie Thompkins",
        "provider_id": "PRV-005",
        "provider_npi": "5678901234",
        "provider_practice_name": "Thompkins Family Medicine",
        "provider_address": "555 Primary Care Dr, Fort Worth, TX 76101",
        "provider_phone": "(817) 555-0500",
        "provider_tax_id": "74-5678901",
    },
    {
        "provider_name": "Dr. Thomas Elliot",
        "provider_id": "PRV-006",
        "provider_npi": "6789012345",
        "provider_practice_name": "Elliot Neurosurgery Group",
        "provider_address": "900 Brain & Spine Blvd, Austin, TX 78702",
        "provider_phone": "(512) 555-0600",
        "provider_tax_id": "74-6789012",
    },
]

PROCEDURES = [
    {"code": "27447", "desc": "Total Knee Arthroplasty", "icd": "M17.11", "charge": 45000},
    {"code": "27130", "desc": "Total Hip Arthroplasty", "icd": "M16.11", "charge": 48000},
    {"code": "99285", "desc": "ED Visit Level 5", "icd": "I21.3", "charge": 2500},
    {"code": "99284", "desc": "ED Visit Level 4", "icd": "R07.9", "charge": 1800},
    {"code": "72148", "desc": "MRI Lumbar Spine Without Contrast", "icd": "M54.5", "charge": 1950},
    {"code": "72141", "desc": "MRI Cervical Spine Without Contrast", "icd": "M54.2", "charge": 1850},
    {"code": "29881", "desc": "Knee Arthroscopy with Meniscectomy", "icd": "S83.211A", "charge": 8500},
    {"code": "63047", "desc": "Lumbar Laminectomy", "icd": "M48.06", "charge": 35000},
    {"code": "22551", "desc": "Anterior Cervical Discectomy & Fusion", "icd": "M50.12", "charge": 52000},
    {"code": "43239", "desc": "Upper GI Endoscopy with Biopsy", "icd": "K21.0", "charge": 3200},
    {"code": "99291", "desc": "Critical Care First Hour", "icd": "R65.20", "charge": 4800},
    {"code": "70553", "desc": "MRI Brain With & Without Contrast", "icd": "G43.909", "charge": 2800},
]

DENIAL_CODES = {
    "CO-45":  "Charges exceed fee schedule/contracted amount",
    "CO-50":  "Non-covered service per benefit plan",
    "CO-96":  "Non-covered charge(s)",
    "CO-97":  "Payment adjusted — already adjudicated",
    "CO-16":  "Claim lacks information or has submission errors",
    "CO-18":  "Duplicate claim/service",
    "CO-29":  "Time limit for filing has expired",
    "CO-197": "Precertification/authorization/notification absent",
    "CO-204": "Service not covered when performed by this provider",
    "CO-167": "Diagnosis is not covered",
    "CO-11":  "Diagnosis inconsistent with procedure",
    "CO-4":   "Procedure code inconsistent with modifier",
    "CO-222": "Exceeds number of services allowed",
    "CO-236": "Procedure/service not paid separately",
    "PR-1":   "Deductible amount",
    "PR-2":   "Coinsurance amount",
}

DENIAL_CATEGORY_MAP = {
    "CO-45": "Coding Error",
    "CO-50": "Medical Necessity",
    "CO-96": "Medical Necessity",
    "CO-97": "Coding Error",
    "CO-16": "Documentation",
    "CO-18": "Coding Error",
    "CO-29": "Prior Authorization",
    "CO-197": "Prior Authorization",
    "CO-204": "Prior Authorization",
    "CO-167": "Medical Necessity",
    "CO-11": "Coding Error",
    "CO-4": "Coding Error",
    "CO-222": "Medical Necessity",
    "CO-236": "Coding Error",
    "PR-1": "Documentation",
    "PR-2": "Documentation",
}

PATIENT_FIRST = [
    "Margaret", "Robert", "Linda", "James", "Patricia", "William",
    "Susan", "David", "Jennifer", "Michael", "Elizabeth", "Thomas",
    "Barbara", "Richard", "Nancy", "Charles", "Karen", "Joseph",
    "Dorothy", "Daniel", "Helen", "Paul", "Sandra", "Mark",
    "Carol", "Steven", "Betty", "Andrew", "Maria", "George",
    "Ruth", "Kenneth", "Sharon", "Edward", "Donna", "Ronald",
    "Laura", "Timothy", "Deborah", "Jason", "Cynthia", "Brian",
    "Angela", "Frank", "Kathleen", "Scott", "Diane", "Raymond",
    "Pamela", "Gregory",
]

PATIENT_LAST = [
    "Johnson", "Chen", "Martinez", "Anderson", "Brown", "Taylor",
    "White", "Lee", "Garcia", "Williams", "Jones", "Davis",
    "Miller", "Wilson", "Moore", "Thompson", "Clark", "Lewis",
    "Walker", "Hall", "Allen", "Young", "King", "Wright",
    "Lopez", "Hill", "Scott", "Green", "Adams", "Baker",
    "Nelson", "Carter", "Mitchell", "Perez", "Roberts", "Turner",
    "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
    "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook",
    "Morgan", "Bell",
]


def _rand_dob():
    year = random.randint(1945, 1990)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


def _rand_policy():
    return f"POL-{random.randint(100000, 999999)}"


def _rand_group():
    return f"GRP-{random.randint(1000, 9999)}"


def _build_denial(
    idx: int,
    today: datetime,
    status: str,
    denial_age_days: int,
    denial_code: str,
    procedure: dict,
    payer: tuple,
    practice: dict,
    priority: str,
    win_prob,
):
    first = PATIENT_FIRST[idx % len(PATIENT_FIRST)]
    last = PATIENT_LAST[idx % len(PATIENT_LAST)]
    patient_name = f"{first} {last}"
    patient_id = f"PT-{200000 + idx}"

    service_date = today - timedelta(days=denial_age_days + random.randint(10, 30))
    denial_date = today - timedelta(days=denial_age_days)
    appeal_deadline = denial_date + timedelta(days=60)

    charge = procedure["charge"] + random.randint(-300, 300)
    denied_amount = charge
    paid_amount = 0.0

    if status == "approved":
        paid_amount = denied_amount
        denied_amount = 0.0
    elif status == "denied":
        paid_amount = 0.0

    created_at = denial_date + timedelta(days=random.randint(0, 3))

    submitted_at = None
    if status in ("submitted", "approved", "denied"):
        submitted_at = created_at + timedelta(days=random.randint(3, 14))

    if status in ("approved", "denied"):
        updated_at = submitted_at + timedelta(days=random.randint(7, 45)) if submitted_at else today
    elif status == "submitted":
        updated_at = submitted_at if submitted_at else today
    else:
        updated_at = created_at + timedelta(days=random.randint(0, 5))

    processing_timestamps = None
    if submitted_at:
        review_started = created_at + timedelta(hours=random.randint(2, 48))
        review_completed = review_started + timedelta(hours=random.randint(1, 12))
        processing_timestamps = {
            "review_started_at": review_started,
            "review_completed_at": review_completed,
            "letter_generation_seconds": random.randint(15, 90),
        }

    diagnosis_extra = random.choice(["", ", G89.29", ", M25.561", ", Z96.641", ", M79.3", ", R26.2"])
    diag = procedure["icd"] + diagnosis_extra

    denial_reason_templates = {
        "Medical Necessity": [
            f"Medical necessity not established for {procedure['desc']}",
            f"Documentation does not support medical necessity for {procedure['desc']}",
            f"The submitted records do not demonstrate that {procedure['desc']} was medically necessary",
            f"Conservative treatment alternatives not exhausted prior to {procedure['desc']}",
            f"Clinical criteria not met per payer guidelines for {procedure['desc']}",
        ],
        "Prior Authorization": [
            f"Prior authorization was not obtained for {procedure['desc']}",
            f"Service {procedure['code']} requires precertification which was not on file",
            f"Notification/authorization absent for {procedure['desc']}",
            f"Retroactive authorization request denied for {procedure['desc']}",
        ],
        "Coding Error": [
            f"Procedure code {procedure['code']} inconsistent with submitted diagnosis",
            f"Charges for {procedure['desc']} exceed contracted rate",
            f"Duplicate submission for {procedure['desc']} on service date",
            f"Modifier required for procedure {procedure['code']} when billed with this diagnosis",
            f"Service {procedure['code']} not separately payable with primary procedure",
        ],
        "Documentation": [
            f"Claim for {procedure['desc']} lacks required supporting documentation",
            f"Insufficient documentation to process claim for {procedure['desc']}",
            f"Missing operative report for {procedure['desc']}",
            f"Incomplete records submitted for {procedure['desc']}",
        ],
    }

    category = DENIAL_CATEGORY_MAP.get(denial_code, "Medical Necessity")
    reason_options = denial_reason_templates.get(category, denial_reason_templates["Medical Necessity"])
    denial_reason = random.choice(reason_options)

    notes_by_status = {
        "pending": "New denial — awaiting initial review",
        "in_review": "Under review — gathering supporting documentation",
        "appeal_ready": "Appeal letter drafted — ready for submission",
        "submitted": f"Appeal submitted on {submitted_at.strftime('%Y-%m-%d') if submitted_at else 'N/A'}",
        "approved": "OVERTURNED — payer approved the appeal",
        "denied": "Appeal REJECTED by payer — consider second-level appeal",
    }

    return {
        "claim_number": f"CLM-2025-{str(idx + 1).zfill(4)}",
        "patient_name": patient_name,
        "patient_id": patient_id,
        "patient_dob": _rand_dob(),
        "provider_name": practice["provider_name"],
        "provider_id": practice["provider_id"],
        "provider_npi": practice["provider_npi"],
        "provider_practice_name": practice["provider_practice_name"],
        "provider_address": practice["provider_address"],
        "provider_phone": practice["provider_phone"],
        "provider_tax_id": practice["provider_tax_id"],
        "payer_name": payer[0],
        "payer_id": payer[1],
        "policy_number": _rand_policy(),
        "group_number": _rand_group(),
        "service_date": service_date.strftime("%Y-%m-%d"),
        "denial_date": denial_date.strftime("%Y-%m-%d"),
        "denial_code": denial_code,
        "denial_category": category,
        "denial_reason": denial_reason,
        "claim_amount": charge,
        "denied_amount": denied_amount,
        "paid_amount": paid_amount,
        "procedure_code": procedure["code"],
        "procedure_description": procedure["desc"],
        "diagnosis_codes": diag,
        "service_description": procedure["desc"],
        "status": status,
        "win_probability": win_prob,
        "priority": priority,
        "appeal_deadline": appeal_deadline.strftime("%Y-%m-%d"),
        "internal_notes": notes_by_status.get(status, ""),
        "submitted_at": submitted_at,
        "created_at": created_at,
        "updated_at": updated_at,
        "processing_timestamps": processing_timestamps,
    }


DENIAL_SPECS = [
    # ──── REJECTED / DENIED APPEALS (the main ask) ────────────────
    {"status": "denied", "age": 20,  "code": "CO-50",  "proc_idx": 0, "payer_idx": 0, "prac_idx": 0, "pri": "high",   "wp": 62},
    {"status": "denied", "age": 35,  "code": "CO-197", "proc_idx": 2, "payer_idx": 1, "prac_idx": 1, "pri": "urgent", "wp": 45},
    {"status": "denied", "age": 50,  "code": "CO-50",  "proc_idx": 1, "payer_idx": 2, "prac_idx": 0, "pri": "high",   "wp": 55},
    {"status": "denied", "age": 65,  "code": "CO-45",  "proc_idx": 3, "payer_idx": 1, "prac_idx": 1, "pri": "normal", "wp": 38},
    {"status": "denied", "age": 80,  "code": "CO-167", "proc_idx": 4, "payer_idx": 2, "prac_idx": 2, "pri": "normal", "wp": 42},
    {"status": "denied", "age": 95,  "code": "CO-16",  "proc_idx": 5, "payer_idx": 3, "prac_idx": 2, "pri": "low",    "wp": 30},
    {"status": "denied", "age": 110, "code": "CO-50",  "proc_idx": 7, "payer_idx": 4, "prac_idx": 5, "pri": "high",   "wp": 58},
    {"status": "denied", "age": 130, "code": "CO-197", "proc_idx": 8, "payer_idx": 0, "prac_idx": 5, "pri": "urgent", "wp": 35},
    {"status": "denied", "age": 150, "code": "CO-96",  "proc_idx": 6, "payer_idx": 3, "prac_idx": 3, "pri": "normal", "wp": 48},
    {"status": "denied", "age": 170, "code": "CO-45",  "proc_idx": 9, "payer_idx": 1, "prac_idx": 4, "pri": "low",    "wp": 25},
    {"status": "denied", "age": 200, "code": "CO-11",  "proc_idx": 10, "payer_idx": 2, "prac_idx": 1, "pri": "normal", "wp": 40},
    {"status": "denied", "age": 220, "code": "CO-204", "proc_idx": 0, "payer_idx": 4, "prac_idx": 3, "pri": "high",   "wp": 50},
    {"status": "denied", "age": 240, "code": "CO-222", "proc_idx": 11, "payer_idx": 0, "prac_idx": 2, "pri": "normal", "wp": 33},
    {"status": "denied", "age": 260, "code": "CO-29",  "proc_idx": 1, "payer_idx": 3, "prac_idx": 0, "pri": "low",    "wp": 15},
    {"status": "denied", "age": 280, "code": "CO-97",  "proc_idx": 2, "payer_idx": 1, "prac_idx": 1, "pri": "normal", "wp": 28},

    # ──── APPROVED / OVERTURNED APPEALS ───────────────────────────
    {"status": "approved", "age": 25,  "code": "CO-50",  "proc_idx": 0, "payer_idx": 0, "prac_idx": 0, "pri": "high",   "wp": 85},
    {"status": "approved", "age": 40,  "code": "CO-197", "proc_idx": 7, "payer_idx": 1, "prac_idx": 5, "pri": "urgent", "wp": 78},
    {"status": "approved", "age": 60,  "code": "CO-45",  "proc_idx": 2, "payer_idx": 2, "prac_idx": 1, "pri": "normal", "wp": 82},
    {"status": "approved", "age": 75,  "code": "CO-16",  "proc_idx": 4, "payer_idx": 0, "prac_idx": 2, "pri": "normal", "wp": 72},
    {"status": "approved", "age": 90,  "code": "CO-167", "proc_idx": 1, "payer_idx": 3, "prac_idx": 0, "pri": "high",   "wp": 88},
    {"status": "approved", "age": 120, "code": "CO-50",  "proc_idx": 8, "payer_idx": 4, "prac_idx": 5, "pri": "high",   "wp": 90},
    {"status": "approved", "age": 140, "code": "CO-11",  "proc_idx": 3, "payer_idx": 1, "prac_idx": 4, "pri": "normal", "wp": 75},
    {"status": "approved", "age": 180, "code": "CO-96",  "proc_idx": 6, "payer_idx": 2, "prac_idx": 3, "pri": "normal", "wp": 80},
    {"status": "approved", "age": 210, "code": "CO-197", "proc_idx": 5, "payer_idx": 0, "prac_idx": 2, "pri": "high",   "wp": 70},
    {"status": "approved", "age": 250, "code": "CO-4",   "proc_idx": 9, "payer_idx": 3, "prac_idx": 4, "pri": "normal", "wp": 65},
    {"status": "approved", "age": 300, "code": "CO-45",  "proc_idx": 10, "payer_idx": 4, "prac_idx": 1, "pri": "low",   "wp": 60},

    # ──── SUBMITTED (awaiting payer decision) ─────────────────────
    {"status": "submitted", "age": 12, "code": "CO-50",  "proc_idx": 0, "payer_idx": 0, "prac_idx": 0, "pri": "urgent", "wp": 78},
    {"status": "submitted", "age": 18, "code": "CO-197", "proc_idx": 7, "payer_idx": 1, "prac_idx": 5, "pri": "high",   "wp": 65},
    {"status": "submitted", "age": 22, "code": "CO-16",  "proc_idx": 2, "payer_idx": 2, "prac_idx": 1, "pri": "normal", "wp": 72},
    {"status": "submitted", "age": 30, "code": "CO-167", "proc_idx": 8, "payer_idx": 3, "prac_idx": 3, "pri": "high",   "wp": 55},
    {"status": "submitted", "age": 45, "code": "CO-45",  "proc_idx": 6, "payer_idx": 4, "prac_idx": 2, "pri": "normal", "wp": 60},

    # ──── APPEAL READY (letter drafted, not yet sent) ─────────────
    {"status": "appeal_ready", "age": 8,  "code": "CO-50",  "proc_idx": 1, "payer_idx": 0, "prac_idx": 0, "pri": "urgent", "wp": 82},
    {"status": "appeal_ready", "age": 14, "code": "CO-197", "proc_idx": 4, "payer_idx": 1, "prac_idx": 2, "pri": "high",   "wp": 70},
    {"status": "appeal_ready", "age": 20, "code": "CO-96",  "proc_idx": 10, "payer_idx": 2, "prac_idx": 5, "pri": "normal", "wp": 58},
    {"status": "appeal_ready", "age": 28, "code": "CO-11",  "proc_idx": 9, "payer_idx": 4, "prac_idx": 4, "pri": "normal", "wp": 63},

    # ──── IN REVIEW (criteria evaluation in progress) ─────────────
    {"status": "in_review", "age": 5,  "code": "CO-50",  "proc_idx": 0, "payer_idx": 2, "prac_idx": 0, "pri": "urgent", "wp": 75},
    {"status": "in_review", "age": 10, "code": "CO-167", "proc_idx": 7, "payer_idx": 0, "prac_idx": 5, "pri": "high",   "wp": 68},
    {"status": "in_review", "age": 15, "code": "CO-45",  "proc_idx": 3, "payer_idx": 3, "prac_idx": 1, "pri": "normal", "wp": 55},
    {"status": "in_review", "age": 25, "code": "CO-16",  "proc_idx": 5, "payer_idx": 1, "prac_idx": 4, "pri": "normal", "wp": 50},

    # ──── PENDING (new, unworked) ─────────────────────────────────
    {"status": "pending", "age": 2,  "code": "CO-50",  "proc_idx": 0, "payer_idx": 0, "prac_idx": 0, "pri": "urgent", "wp": None},
    {"status": "pending", "age": 3,  "code": "CO-197", "proc_idx": 8, "payer_idx": 1, "prac_idx": 5, "pri": "high",   "wp": None},
    {"status": "pending", "age": 5,  "code": "CO-45",  "proc_idx": 2, "payer_idx": 2, "prac_idx": 1, "pri": "normal", "wp": None},
    {"status": "pending", "age": 7,  "code": "CO-16",  "proc_idx": 4, "payer_idx": 3, "prac_idx": 2, "pri": "normal", "wp": None},
    {"status": "pending", "age": 9,  "code": "CO-96",  "proc_idx": 6, "payer_idx": 4, "prac_idx": 3, "pri": "high",   "wp": None},
    {"status": "pending", "age": 12, "code": "CO-167", "proc_idx": 1, "payer_idx": 0, "prac_idx": 4, "pri": "normal", "wp": None},
]


def _build_appeal_letter(denial: dict) -> dict:
    provider = denial["provider_name"]
    practice = denial["provider_practice_name"]
    patient = denial["patient_name"]
    procedure_desc = denial.get("procedure_description", denial.get("service_description", ""))
    payer = denial["payer_name"]
    claim_number = denial["claim_number"]
    denial_code = denial.get("denial_code", "")
    denial_reason = denial.get("denial_reason", "")
    service_date = denial["service_date"]

    return {
        "denial_id": denial["_id_str"],
        "provider_letterhead": {
            "name": f"{practice}\n{provider}",
            "address": denial.get("provider_address", ""),
            "phone": denial.get("provider_phone", ""),
        },
        "sections": [
            {
                "title": "RE: Appeal of Claim Denial",
                "content": (
                    f"Dear {payer} Appeals Department,\n\n"
                    f"I am writing to formally appeal the denial of claim {claim_number} "
                    f"for patient {patient}, date of service {service_date}. "
                    f"The claim for {procedure_desc} was denied under code {denial_code} "
                    f"with the stated reason: \"{denial_reason}\"\n\n"
                    f"We respectfully disagree with this determination and submit the following "
                    f"evidence in support of medical necessity and appropriateness of this service."
                ),
            },
            {
                "title": "Clinical Summary",
                "content": (
                    f"{patient} presented with significant and progressive symptoms that "
                    f"warranted {procedure_desc}. The patient had undergone extensive "
                    f"conservative treatment including physical therapy, pharmacological "
                    f"management, and activity modification without adequate relief. "
                    f"Clinical examination and diagnostic imaging confirmed the need for "
                    f"surgical intervention."
                ),
            },
            {
                "title": "Supporting Evidence",
                "content": (
                    f"The enclosed medical records demonstrate:\n"
                    f"• Documented failure of conservative treatment over multiple months\n"
                    f"• Diagnostic imaging confirming the clinical diagnosis\n"
                    f"• Functional limitations impacting activities of daily living\n"
                    f"• Specialist recommendation for the procedure\n"
                    f"• Compliance with applicable clinical guidelines and payer policy criteria"
                ),
            },
            {
                "title": "Conclusion",
                "content": (
                    f"Based on the comprehensive clinical evidence, we believe {procedure_desc} "
                    f"was medically necessary and appropriate for {patient}. We respectfully "
                    f"request that {payer} reverse the denial and provide coverage for this claim.\n\n"
                    f"Thank you for your prompt attention to this matter."
                ),
            },
        ],
        "enclosed_documents": [
            "Medical Records",
            "Diagnostic Test Results",
            "Progress Notes",
            "Physical Therapy Records",
            "Specialist Consultation Report",
        ],
        "signature": {
            "name": provider,
            "title": f"Attending Physician, {practice}",
        },
        "generated_at": denial.get("submitted_at") or denial.get("updated_at") or datetime.utcnow(),
    }


async def seed_comprehensive():
    print("=" * 60)
    print("COMPREHENSIVE DATABASE SEEDING")
    print("=" * 60)

    await users_collection.delete_many({})
    await denials_collection.delete_many({})
    await medical_policies_collection.delete_many({})
    await patient_documents_collection.delete_many({})
    await criteria_evaluations_collection.delete_many({})
    await appeal_packages_collection.delete_many({})
    await reference_data_collection.delete_many({})
    print("\n[1/8] Cleared existing data")

    # ── Users ─────────────────────────────────────────────────────
    users = [
        {"email": "demo@penguinai.com", "password": hash_password("demo123"), "name": "Demo User", "role": "appeals_manager"},
        {"email": "admin@penguinai.com", "password": hash_password("admin123"), "name": "Admin User", "role": "admin"},
        {"email": "reviewer@penguinai.com", "password": hash_password("review123"), "name": "Claims Reviewer", "role": "reviewer"},
    ]
    for u in users:
        await users_collection.insert_one(u)
    print(f"[2/8] Created {len(users)} users")

    # ── Reference Data ────────────────────────────────────────────
    await reference_data_collection.update_one(
        {"type": "payers"},
        {"$set": {"type": "payers", "values": [p[0] for p in PAYERS]}},
        upsert=True,
    )
    await reference_data_collection.update_one(
        {"type": "providers"},
        {"$set": {"type": "providers", "values": [
            {"name": p["provider_name"], "practice": p["provider_practice_name"]}
            for p in PRACTICES
        ]}},
        upsert=True,
    )
    print(f"[3/8] Seeded reference data ({len(PAYERS)} payers, {len(PRACTICES)} providers)")

    # ── Medical Policies ──────────────────────────────────────────
    policies = [
        {
            "payer_id": "PAY-BCBS", "payer_name": "Blue Cross Blue Shield",
            "cpt_code": "27447", "cpt_description": "Total Knee Arthroplasty",
            "denial_category": "Medical Necessity",
            "policy_name": "Total Joint Replacement Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {"id": "TKA-1", "category": "Conservative Treatment", "question": "Has the patient completed at least 6 months of conservative treatment?", "required": True, "weight": 2.0, "evidence_keywords": ["physical therapy", "PT", "NSAID", "injection", "conservative", "6 months"], "document_types_expected": ["Physical Therapy Records", "Progress Notes"], "response_type": "boolean"},
                {"id": "TKA-2", "category": "Diagnostic Evidence", "question": "Does imaging show bone-on-bone contact or Grade IV cartilage loss?", "required": True, "weight": 2.5, "evidence_keywords": ["bone-on-bone", "Grade IV", "Grade 4", "severe", "cartilage loss", "Kellgren-Lawrence"], "document_types_expected": ["X-Ray Report", "MRI Report"], "response_type": "boolean"},
                {"id": "TKA-3", "category": "Functional Limitation", "question": "Is there documented significant functional limitation affecting daily activities?", "required": True, "weight": 1.5, "evidence_keywords": ["functional limitation", "walking", "stairs", "ADL", "daily activities"], "document_types_expected": ["Progress Notes", "Functional Assessment"], "response_type": "boolean"},
                {"id": "TKA-4", "category": "Treatment Failure", "question": "Has the patient's condition failed to improve despite conservative measures?", "required": True, "weight": 1.5, "evidence_keywords": ["failed", "no improvement", "worsening", "unsuccessful"], "document_types_expected": ["Progress Notes"], "response_type": "boolean"},
                {"id": "TKA-5", "category": "BMI Documentation", "question": "Is BMI < 40 or bariatric clearance documented?", "required": True, "weight": 1.0, "evidence_keywords": ["BMI", "weight", "bariatric", "clearance"], "document_types_expected": ["Pre-operative Assessment"], "response_type": "boolean"},
            ],
            "clinical_guidelines": ["AAOS Guidelines 2023", "CMS LCD L33724"],
            "historical_overturn_rate": 0.72, "average_processing_days": 21,
        },
        {
            "payer_id": "PAY-UHC", "payer_name": "United Healthcare",
            "cpt_code": "99285", "cpt_description": "Emergency Department Visit - Level 5",
            "denial_category": "Coding Error",
            "policy_name": "ED Visit Medical Necessity",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {"id": "ED5-1", "category": "Severity", "question": "Does documentation show immediate threat to life or physiologic function?", "required": True, "weight": 2.5, "evidence_keywords": ["life-threatening", "critical", "severe", "emergency"], "document_types_expected": ["Emergency Room Record"], "response_type": "boolean"},
                {"id": "ED5-2", "category": "Medical Decision Making", "question": "Is high complexity medical decision making documented?", "required": True, "weight": 2.0, "evidence_keywords": ["high complexity", "MDM", "differential diagnosis"], "document_types_expected": ["Emergency Room Record"], "response_type": "boolean"},
                {"id": "ED5-3", "category": "Time Documentation", "question": "Is total time > 60 minutes documented?", "required": True, "weight": 1.5, "evidence_keywords": ["60 minutes", "time", "duration", "prolonged"], "document_types_expected": ["Emergency Room Record"], "response_type": "boolean"},
            ],
            "clinical_guidelines": ["AMA E/M Guidelines 2023", "ACEP Guidelines"],
            "historical_overturn_rate": 0.78, "average_processing_days": 14,
        },
        {
            "payer_id": "PAY-AETNA", "payer_name": "Aetna",
            "cpt_code": "72148", "cpt_description": "MRI Lumbar Spine Without Contrast",
            "denial_category": "Prior Authorization",
            "policy_name": "Advanced Imaging Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {"id": "MRI-1", "category": "Clinical Indication", "question": "Are neurological symptoms documented?", "required": True, "weight": 2.5, "evidence_keywords": ["radiculopathy", "weakness", "numbness", "neurological"], "document_types_expected": ["Progress Notes"], "response_type": "boolean"},
                {"id": "MRI-2", "category": "Conservative Treatment", "question": "Has patient failed 4-6 weeks of conservative treatment?", "required": True, "weight": 2.0, "evidence_keywords": ["4 weeks", "6 weeks", "conservative", "failed"], "document_types_expected": ["Progress Notes", "Physical Therapy Records"], "response_type": "boolean"},
            ],
            "clinical_guidelines": ["ACR Appropriateness Criteria"],
            "historical_overturn_rate": 0.65, "average_processing_days": 10,
        },
        {
            "payer_id": "PAY-CIGNA", "payer_name": "Cigna",
            "cpt_code": "29881", "cpt_description": "Knee Arthroscopy with Meniscectomy",
            "denial_category": "Medical Necessity",
            "policy_name": "Knee Surgery Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {"id": "ARTH-1", "category": "Conservative Treatment", "question": "Has patient failed 6 weeks of conservative treatment?", "required": True, "weight": 2.0, "evidence_keywords": ["6 weeks", "conservative", "physical therapy", "failed"], "document_types_expected": ["Progress Notes", "Physical Therapy Records"], "response_type": "boolean"},
                {"id": "ARTH-2", "category": "Imaging Evidence", "question": "Does MRI show meniscal tear requiring surgical intervention?", "required": True, "weight": 2.5, "evidence_keywords": ["meniscal tear", "MRI", "bucket handle", "complex tear"], "document_types_expected": ["MRI Report"], "response_type": "boolean"},
            ],
            "clinical_guidelines": ["AAOS Guidelines"],
            "historical_overturn_rate": 0.75, "average_processing_days": 15,
        },
        {
            "payer_id": "PAY-HUMANA", "payer_name": "Humana",
            "cpt_code": "63047", "cpt_description": "Lumbar Laminectomy",
            "denial_category": "Medical Necessity",
            "policy_name": "Spine Surgery Policy",
            "effective_date": "2024-01-01",
            "criteria_questions": [
                {"id": "LAMI-1", "category": "Conservative Treatment", "question": "Has patient failed 12 weeks of conservative treatment including PT and injections?", "required": True, "weight": 2.0, "evidence_keywords": ["12 weeks", "conservative", "physical therapy", "injection", "epidural", "failed"], "document_types_expected": ["Progress Notes", "Physical Therapy Records"], "response_type": "boolean"},
                {"id": "LAMI-2", "category": "Imaging Correlation", "question": "Does imaging correlate with clinical presentation?", "required": True, "weight": 2.5, "evidence_keywords": ["stenosis", "correlation", "symptomatic level", "compression", "MRI"], "document_types_expected": ["MRI Report", "Progress Notes"], "response_type": "boolean"},
            ],
            "clinical_guidelines": ["NASS Guidelines", "CMS LCD"],
            "historical_overturn_rate": 0.60, "average_processing_days": 25,
        },
    ]
    for p in policies:
        await medical_policies_collection.insert_one(p)
    print(f"[4/8] Created {len(policies)} medical policies")

    # ── Denials ───────────────────────────────────────────────────
    today = datetime.utcnow()
    denial_records = []
    for idx, spec in enumerate(DENIAL_SPECS):
        d = _build_denial(
            idx=idx,
            today=today,
            status=spec["status"],
            denial_age_days=spec["age"],
            denial_code=spec["code"],
            procedure=PROCEDURES[spec["proc_idx"]],
            payer=PAYERS[spec["payer_idx"]],
            practice=PRACTICES[spec["prac_idx"]],
            priority=spec["pri"],
            win_prob=spec["wp"],
        )
        result = await denials_collection.insert_one(d)
        d["_id_str"] = str(result.inserted_id)
        denial_records.append(d)
    print(f"[5/8] Created {len(denial_records)} denials")

    # ── Documents ─────────────────────────────────────────────────
    doc_types = [
        "medical_records", "prior_visit_notes", "diagnostic_tests",
        "physical_therapy_notes", "operative_report", "discharge_summary",
        "radiology_report", "lab_results", "claim_form", "eob",
    ]
    doc_count = 0
    for denial in denial_records:
        num = random.randint(2, 5)
        for j in range(num):
            dt = doc_types[j % len(doc_types)]
            doc_date = datetime.strptime(denial["service_date"], "%Y-%m-%d") - timedelta(days=random.randint(1, 60))
            pages = random.randint(2, 8)
            doc = {
                "denial_id": denial["_id_str"],
                "patient_id": denial["patient_id"],
                "document_name": f"{dt}_{doc_date.strftime('%Y%m%d')}.pdf",
                "document_type": dt,
                "document_date": doc_date.strftime("%Y-%m-%d"),
                "file_path": f"/documents/{denial['patient_id']}/{doc_date.strftime('%Y/%m/%d')}/{dt}.pdf",
                "total_pages": pages,
                "presigned_urls": {str(p): f"https://storage.example.com/{denial['patient_id']}/{dt}/page{p}.png" for p in range(1, pages + 1)},
                "uploaded_at": denial["created_at"],
            }
            await patient_documents_collection.insert_one(doc)
            doc_count += 1
    print(f"[6/8] Created {doc_count} patient documents")

    # ── Criteria Evaluations ──────────────────────────────────────
    eval_count = 0
    for denial in denial_records:
        if denial["status"] in ("pending",):
            continue
        criteria_total = random.randint(3, 5)
        if denial["status"] == "approved":
            criteria_met = criteria_total - random.randint(0, 1)
        elif denial["status"] == "denied":
            criteria_met = random.randint(1, criteria_total - 1)
        else:
            criteria_met = random.randint(2, criteria_total)

        criteria_list = []
        for c in range(criteria_total):
            is_met = c < criteria_met
            criterion = {
                "id": f"criterion_{c + 1}",
                "question": f"Does documentation support criterion {c + 1}?",
                "met": is_met,
            }
            if is_met:
                criterion["evidence"] = [{
                    "document_id": f"doc_{c}",
                    "document_name": f"supporting_document_{c}.pdf",
                    "page": random.randint(1, 5),
                    "text": f"Evidence found supporting criterion {c + 1} in patient records.",
                    "bbox": [0.1, 0.2 + c * 0.1, 0.9, 0.2 + c * 0.1, 0.9, 0.25 + c * 0.1, 0.1, 0.25 + c * 0.1],
                }]
            else:
                criterion["missing_documents"] = "Required documentation not found in submitted records"
            criteria_list.append(criterion)

        wp = denial.get("win_probability") or int((criteria_met / criteria_total) * 100)
        evaluation = {
            "denial_id": denial["_id_str"],
            "total_criteria": criteria_total,
            "criteria_met": criteria_met,
            "win_probability": wp,
            "criteria": criteria_list,
            "evaluated_at": denial["created_at"] + timedelta(hours=random.randint(1, 24)),
        }
        await criteria_evaluations_collection.insert_one(evaluation)
        eval_count += 1
    print(f"[7/8] Created {eval_count} criteria evaluations")

    # ── Appeal Letters ────────────────────────────────────────────
    letter_count = 0
    for denial in denial_records:
        if denial["status"] in ("pending", "in_review"):
            continue
        letter = _build_appeal_letter(denial)
        await appeal_packages_collection.insert_one(letter)
        letter_count += 1
    print(f"[8/8] Created {letter_count} appeal letters")

    # ── Summary ───────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("DATABASE SEEDING COMPLETE")
    print("=" * 60)

    status_counts = {}
    total_denied_amt = 0.0
    total_recovered = 0.0
    for d in denial_records:
        s = d["status"]
        status_counts[s] = status_counts.get(s, 0) + 1
        total_denied_amt += d.get("denied_amount", 0)
        if s == "approved":
            total_recovered += d.get("claim_amount", 0)

    print(f"\n{'Collection':<30} {'Count':>10}")
    print("-" * 42)
    print(f"{'users':<30} {len(users):>10}")
    print(f"{'medical_policies':<30} {len(policies):>10}")
    print(f"{'denials':<30} {len(denial_records):>10}")
    print(f"{'patient_documents':<30} {doc_count:>10}")
    print(f"{'criteria_evaluations':<30} {eval_count:>10}")
    print(f"{'appeal_letters':<30} {letter_count:>10}")

    print(f"\n{'Status':<20} {'Count':>10}")
    print("-" * 32)
    for status, count in sorted(status_counts.items()):
        print(f"  {status:<18} {count:>10}")

    payer_counts = {}
    for d in denial_records:
        p = d["payer_name"]
        payer_counts[p] = payer_counts.get(p, 0) + 1
    print(f"\n{'Payer':<30} {'Count':>10}")
    print("-" * 42)
    for payer, count in sorted(payer_counts.items()):
        print(f"  {payer:<28} {count:>10}")

    practice_counts = {}
    for d in denial_records:
        p = d["provider_practice_name"]
        practice_counts[p] = practice_counts.get(p, 0) + 1
    print(f"\n{'Practice':<35} {'Count':>10}")
    print("-" * 47)
    for practice, count in sorted(practice_counts.items()):
        print(f"  {practice:<33} {count:>10}")

    print(f"\n  Total denied amount:   ${total_denied_amt:>12,.2f}")
    print(f"  Total recovered:       ${total_recovered:>12,.2f}")

    print("\n" + "=" * 60)
    print("CREDENTIALS")
    print("=" * 60)
    print("  Email:    demo@penguinai.com")
    print("  Password: demo123")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(seed_comprehensive())
