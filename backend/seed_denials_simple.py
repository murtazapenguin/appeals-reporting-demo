#!/usr/bin/env python3
"""Simple seed script to add denial cases without auth dependencies."""

import asyncio
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['penguin_app']
denials_collection = db['denials']

def calculate_appeal_deadline(denial_date):
    """Calculate appeal deadline (30 days from denial date)."""
    deadline = denial_date + timedelta(days=30)
    return deadline

# Sample denial cases
denial_cases = [
    {
        "claim_number": "CLM-2025-001",
        "patient_name": "Sarah Martinez",
        "patient_id": "PAT-001234",
        "patient_dob": "1975-03-15",
        "provider_name": "Dr. Emily Parker",
        "provider_id": "PRV-003",
        "payer_name": "Blue Cross Blue Shield",
        "payer_id": "PAY-BCBS",
        "policy_number": "POL-BCBS-789012",
        "service_date": "2025-01-15",
        "denial_date": "2025-01-20",
        "denial_code": "CO-50",
        "denial_category": "Medical Necessity",
        "denial_reason": "Services not medically necessary per policy guidelines",
        "claim_amount": 8500.00,
        "paid_amount": 0.00,
        "denied_amount": 8500.00,
        "procedure_code": "63047",
        "diagnosis_codes": ["M54.5", "M51.16", "M48.06"],
        "service_description": "Lumbar Laminectomy",
        "status": "pending",
        "priority": "high",
        "internal_notes": "Patient has chronic lower back pain with documented conservative treatment failure"
    },
    {
        "claim_number": "CLM-2025-002",
        "patient_name": "Michael Johnson",
        "patient_id": "PAT-005678",
        "patient_dob": "1968-07-22",
        "provider_name": "Dr. Sarah Wilson",
        "provider_id": "PRV-001",
        "payer_name": "United Healthcare",
        "payer_id": "PAY-UHC",
        "policy_number": "POL-UHC-456789",
        "service_date": "2025-01-10",
        "denial_date": "2025-01-18",
        "denial_code": "CO-197",
        "denial_category": "Prior Authorization",
        "denial_reason": "Procedure required prior authorization which was not obtained",
        "claim_amount": 12500.00,
        "paid_amount": 0.00,
        "denied_amount": 12500.00,
        "procedure_code": "27447",
        "diagnosis_codes": ["M17.11", "M25.561"],
        "service_description": "Total Knee Arthroplasty",
        "status": "pending",
        "priority": "urgent",
        "internal_notes": "Emergency procedure due to severe pain and mobility issues"
    },
    {
        "claim_number": "CLM-2025-003",
        "patient_name": "Jennifer Davis",
        "patient_id": "PAT-009012",
        "patient_dob": "1982-11-30",
        "provider_name": "Dr. Michael Torres",
        "provider_id": "PRV-002",
        "payer_name": "Aetna",
        "payer_id": "PAY-AETNA",
        "policy_number": "POL-AETNA-123456",
        "service_date": "2025-01-12",
        "denial_date": "2025-01-19",
        "denial_code": "CO-50",
        "denial_category": "Medical Necessity",
        "denial_reason": "MRI not medically necessary - requires conservative treatment first",
        "claim_amount": 2800.00,
        "paid_amount": 0.00,
        "denied_amount": 2800.00,
        "procedure_code": "72148",
        "diagnosis_codes": ["M54.5", "M54.2"],
        "service_description": "MRI Lumbar Spine Without Contrast",
        "status": "pending",
        "priority": "normal",
        "internal_notes": "Patient has failed 6 weeks of physical therapy and medication"
    },
    {
        "claim_number": "CLM-2025-004",
        "patient_name": "Robert Chen",
        "patient_id": "PAT-003456",
        "patient_dob": "1955-04-18",
        "provider_name": "Dr. Lisa Chen",
        "provider_id": "PRV-005",
        "payer_name": "Cigna",
        "payer_id": "PAY-CIGNA",
        "policy_number": "POL-CIGNA-789123",
        "service_date": "2025-01-08",
        "denial_date": "2025-01-16",
        "denial_code": "CO-151",
        "denial_category": "Documentation",
        "denial_reason": "Insufficient documentation to support medical necessity",
        "claim_amount": 3200.00,
        "paid_amount": 0.00,
        "denied_amount": 3200.00,
        "procedure_code": "64483",
        "diagnosis_codes": ["M54.16", "G89.29"],
        "service_description": "Epidural Steroid Injection",
        "status": "pending",
        "priority": "normal",
        "internal_notes": "Patient has chronic lumbar radiculopathy"
    },
    {
        "claim_number": "CLM-2025-005",
        "patient_name": "Amanda Williams",
        "patient_id": "PAT-007890",
        "patient_dob": "1990-09-05",
        "provider_name": "Dr. John Smith",
        "provider_id": "PRV-004",
        "payer_name": "Humana",
        "payer_id": "PAY-HUMANA",
        "policy_number": "POL-HUMANA-456123",
        "service_date": "2025-01-14",
        "denial_date": "2025-01-21",
        "denial_code": "CO-50",
        "denial_category": "Medical Necessity",
        "denial_reason": "Knee arthroscopy not medically necessary per clinical guidelines",
        "claim_amount": 5600.00,
        "paid_amount": 0.00,
        "denied_amount": 5600.00,
        "procedure_code": "29881",
        "diagnosis_codes": ["M23.201", "M25.561"],
        "service_description": "Knee Arthroscopy with Meniscectomy",
        "status": "pending",
        "priority": "high",
        "internal_notes": "Patient has recurrent knee pain and locking episodes"
    }
]

def seed_denials():
    """Seed denial cases into the database."""
    print("Starting denial seeding...")

    # Clear existing denials (optional - comment out if you want to keep existing data)
    # print("Clearing existing denials...")
    # denials_collection.delete_many({})

    inserted_count = 0
    for denial_data in denial_cases:
        # Check if denial already exists
        existing = denials_collection.find_one({"claim_number": denial_data["claim_number"]})
        if existing:
            print(f"⚠️  Denial {denial_data['claim_number']} already exists, skipping...")
            continue

        # Convert string dates to datetime
        if isinstance(denial_data['service_date'], str):
            denial_data['service_date'] = datetime.fromisoformat(denial_data['service_date'])
        if isinstance(denial_data['denial_date'], str):
            denial_data['denial_date'] = datetime.fromisoformat(denial_data['denial_date'])
        if isinstance(denial_data.get('patient_dob'), str):
            denial_data['patient_dob'] = datetime.fromisoformat(denial_data['patient_dob'])

        # Add timestamps
        denial_data['created_at'] = datetime.utcnow()
        denial_data['updated_at'] = datetime.utcnow()
        denial_data['appeal_deadline'] = calculate_appeal_deadline(denial_data['denial_date'])

        # Insert denial
        result = denials_collection.insert_one(denial_data)
        inserted_count += 1
        print(f"✓ Created denial: {denial_data['claim_number']} - {denial_data['patient_name']}")

    print(f"\n✅ Seeding complete! Added {inserted_count} new denials.")
    print(f"   Total denials in database: {denials_collection.count_documents({})}")

if __name__ == "__main__":
    try:
        seed_denials()
    except Exception as e:
        print(f"❌ Error seeding data: {str(e)}")
        import traceback
        traceback.print_exc()
