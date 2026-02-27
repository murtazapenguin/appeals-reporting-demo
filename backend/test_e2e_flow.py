"""
End-to-end test of AI processing flow.

Tests the complete workflow:
1. Mock document processing
2. Criteria evaluation
3. Appeal letter generation
"""

import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_criteria_evaluation():
    """Test criteria evaluation with mock data."""
    logger.info("[E2E TEST] Testing criteria evaluation...")

    from services.ai_processor import get_processor

    processor = get_processor()

    # Mock denial data
    denial_data = {
        "_id": "test_denial_001",
        "patient_id": "PT-001234",
        "service_date": "2024-03-15",
        "denial_date": "2024-04-01",
        "procedure_code": "27447",
        "diagnosis_codes": "M17.11, M25.561",
        "claim_number": "CLM-2024-001",
        "patient_name": "Margaret Johnson"
    }

    # Mock criteria
    criteria = [
        {
            "id": "criteria1",
            "category": "Medical Necessity",
            "question": "Patient has documented chronic joint pain for >6 months",
            "required": True,
            "weight": 1.5,
            "evidence_keywords": ["chronic pain", "joint pain", "6 months"],
            "document_types_expected": ["progress_note"]
        },
        {
            "id": "criteria2",
            "category": "Conservative Treatment",
            "question": "Conservative treatment tried and failed",
            "required": True,
            "weight": 2.0,
            "evidence_keywords": ["physical therapy", "PT", "failed"],
            "document_types_expected": ["physical_therapy_notes"]
        }
    ]

    # Mock documents with OCR results
    documents = [
        {
            "document_id": "doc001",
            "document_name": "progress_note.pdf",
            "document_type": "progress_note",
            "document_date": "2024-01-15",
            "full_text": """
Progress Note - January 15, 2024

Chief Complaint: Chronic right knee pain

History of Present Illness:
Patient presents with chronic right knee pain ongoing since July 2023 (7 months duration).
Pain is described as constant, aching, worse with ambulation and stair climbing.
Patient reports significant functional impairment affecting daily activities.

Past Medical History:
- Osteoarthritis, right knee
- Hypertension, controlled

Physical Exam:
- Moderate joint effusion noted
- Decreased range of motion
- Crepitus with flexion/extension
- Tenderness to palpation

Assessment:
Chronic knee pain secondary to osteoarthritis, progressive despite conservative management.

Plan:
- Continue current pain management
- Consider orthopedic referral for surgical evaluation
- Follow up in 4 weeks
""",
            "lines": [
                {
                    "content": "Patient presents with chronic right knee pain ongoing since July 2023 (7 months duration).",
                    "page": 1,
                    "bbox": [0.1, 0.3, 0.9, 0.3, 0.9, 0.35, 0.1, 0.35],
                    "confidence": 0.98
                }
            ]
        },
        {
            "document_id": "doc002",
            "document_name": "pt_records.pdf",
            "document_type": "physical_therapy_notes",
            "document_date": "2024-02-20",
            "full_text": """
Physical Therapy Progress Report - February 20, 2024

Patient: Margaret Johnson
DOB: 03/15/1958

Treatment Duration: September 2023 - February 2024 (6 months)

Interventions:
- Therapeutic exercises
- Manual therapy
- Modalities (heat, ice, TENS)
- Gait training
- Strengthening program

Progress:
Patient has completed 6 months of intensive physical therapy with minimal improvement in pain levels.
Functional limitations persist despite compliance with home exercise program.
Pain continues to restrict daily activities and ambulation.

Clinical Impression:
Conservative treatment has been unsuccessful in managing symptoms.
Patient remains significantly limited in function.

Recommendation:
Discharge from PT. Consider alternative treatment options including surgical intervention.
""",
            "lines": [
                {
                    "content": "Patient has completed 6 months of intensive physical therapy with minimal improvement.",
                    "page": 1,
                    "bbox": [0.1, 0.5, 0.9, 0.5, 0.9, 0.55, 0.1, 0.55],
                    "confidence": 0.97
                }
            ]
        }
    ]

    try:
        # Run evaluation
        result = await processor.evaluate_criteria(
            denial_id="test_denial_001",
            denial_data=denial_data,
            criteria=criteria,
            documents=documents
        )

        logger.info(f"[E2E TEST] ✓ Criteria Evaluation completed")
        logger.info(f"  - Total Criteria: {result['total_criteria']}")
        logger.info(f"  - Criteria Met: {result['criteria_met']}")
        logger.info(f"  - Win Probability: {result['win_probability']}%")

        for criterion in result['criteria']:
            status = "✓ MET" if criterion['met'] else "✗ NOT MET"
            logger.info(f"  - {criterion['id']}: {status}")

        return True

    except Exception as e:
        logger.error(f"[E2E TEST] ✗ Criteria evaluation failed: {str(e)}")
        return False


async def test_appeal_generation():
    """Test appeal letter generation with mock data."""
    logger.info("[E2E TEST] Testing appeal letter generation...")

    from services.ai_processor import get_processor

    processor = get_processor()

    # Mock denial data
    denial_data = {
        "_id": "test_denial_001",
        "claim_number": "CLM-2024-001",
        "patient_name": "Margaret Johnson",
        "patient_dob": "1958-03-15",
        "provider_name": "Dr. Sarah Wilson",
        "payer_name": "Blue Cross Blue Shield",
        "service_date": "2024-03-15",
        "denial_date": "2024-04-01",
        "procedure_code": "27447",
        "diagnosis_codes": "M17.11, M25.561",
        "claim_amount": 45000.00,
        "denial_reason": "Lack of medical necessity documentation"
    }

    # Mock criteria evaluation
    criteria_evaluation = {
        "denial_id": "test_denial_001",
        "total_criteria": 2,
        "criteria_met": 2,
        "win_probability": 100,
        "criteria": [
            {
                "id": "criteria1",
                "question": "Chronic pain documented?",
                "met": True,
                "evidence": [
                    {
                        "document_name": "progress_note.pdf",
                        "text": "Chronic pain since July 2023",
                        "page": 1
                    }
                ]
            }
        ]
    }

    # Mock documents
    documents = [
        {
            "document_id": "doc001",
            "document_name": "progress_note.pdf",
            "full_text": "Patient presents with chronic knee pain..."
        }
    ]

    try:
        # Generate letter
        letter = await processor.generate_appeal_letter(
            denial_data=denial_data,
            criteria_evaluation=criteria_evaluation,
            documents=documents
        )

        logger.info(f"[E2E TEST] ✓ Appeal Letter generated")
        logger.info(f"  - Sections: {len(letter['sections'])}")
        logger.info(f"  - Provider: {letter['provider_letterhead']['name']}")

        for section in letter['sections']:
            logger.info(f"  - Section: {section['title']}")

        return True

    except Exception as e:
        logger.error(f"[E2E TEST] ✗ Appeal generation failed: {str(e)}")
        return False


async def main():
    """Run all E2E tests."""
    logger.info("="*60)
    logger.info("End-to-End AI Processing Tests")
    logger.info("="*60)

    results = []

    # Test 1: Criteria Evaluation
    results.append(await test_criteria_evaluation())

    # Test 2: Appeal Letter Generation
    results.append(await test_appeal_generation())

    # Summary
    logger.info("="*60)
    logger.info(f"Tests Passed: {sum(results)}/{len(results)}")
    logger.info("="*60)

    if all(results):
        logger.info("✓ All E2E tests passed!")
        return 0
    else:
        logger.error("✗ Some E2E tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    import sys
    sys.exit(exit_code)
