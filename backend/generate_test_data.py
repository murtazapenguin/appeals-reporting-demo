"""
Script to generate test medical documents (PDFs) for patient PT-100001
and a CSV file for testing the upload functionality.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import csv

# Patient info for PT-100001
PATIENT_INFO = {
    "name": "Robert Smith",
    "dob": "07/22/1962",
    "mrn": "PT-100001"
}

# Base path for documents
BASE_PATH = "/Users/vaatsav/Desktop/claim-appeals-v2/backend/documents/PT-100001/2024/11"


def create_pdf(filename, title, content_func):
    """Create a PDF with the given content function."""
    filepath = os.path.join(BASE_PATH, filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    content_func(c, width, height)

    c.save()
    print(f"Created: {filepath}")


def add_header(c, width, height, clinic_name, title, date):
    """Add standard header to PDF."""
    # Clinic name
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height - 0.75*inch, clinic_name)

    # Clinic address
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 1*inch, "456 Spine Care Drive, Houston, TX 77001")
    c.drawCentredString(width/2, height - 1.2*inch, "Phone: (713) 555-0200 | Fax: (713) 555-0201")

    # Title
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 1.7*inch, title)

    # Patient info box
    y = height - 2.2*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75*inch, y, "Patient:")
    c.drawString(3*inch, y, "DOB:")
    c.setFont("Helvetica", 10)
    c.drawString(1.5*inch, y, PATIENT_INFO["name"])
    c.drawString(3.5*inch, y, PATIENT_INFO["dob"])

    y -= 0.25*inch
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.75*inch, y, "MRN:")
    c.drawString(3*inch, y, "Date:")
    c.setFont("Helvetica", 10)
    c.drawString(1.5*inch, y, PATIENT_INFO["mrn"])
    c.drawString(3.5*inch, y, date)

    return y - 0.5*inch


def add_section(c, y, title, content, width):
    """Add a section with title and content."""
    c.setFont("Helvetica-Bold", 11)
    c.drawString(0.75*inch, y, title)
    y -= 0.25*inch

    c.setFont("Helvetica", 10)
    for line in content:
        if y < 1*inch:
            c.showPage()
            y = 10.5*inch
        c.drawString(0.75*inch, y, line)
        y -= 0.2*inch

    return y - 0.2*inch


def add_signature(c, y, doctor_name, date):
    """Add electronic signature."""
    if y < 1.5*inch:
        c.showPage()
        y = 10.5*inch
    y -= 0.3*inch
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(0.75*inch, y, f"Electronically signed by: {doctor_name}")
    y -= 0.2*inch
    c.drawString(0.75*inch, y, f"Date: {date}")


# Document 1: Initial Consultation - Lumbar Spine
def doc1_initial_consult(c, width, height):
    y = add_header(c, width, height, "Houston Spine & Pain Center",
                   "INITIAL CONSULTATION - LUMBAR SPINE", "09/15/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Provider:")
    c.setFont("Helvetica", 10)
    c.drawString(6*inch, height - 2.45*inch, "Dr. Michael Chen")

    y = add_section(c, y, "CHIEF COMPLAINT:", [
        "Patient presents with chronic lower back pain radiating to bilateral lower extremities,",
        "worse on the left side. Pain has been ongoing for 14 months with progressive worsening.",
        "Patient rates pain as 8/10 on average, interfering with daily activities and sleep."
    ], width)

    y = add_section(c, y, "HISTORY OF PRESENT ILLNESS:", [
        "62-year-old male with progressive lumbar radiculopathy. Patient reports significant",
        "difficulty with prolonged standing (>10 minutes) and walking (limited to 1/4 mile).",
        "Pain is described as sharp, shooting, and burning. Numbness and tingling in both feet.",
        "Patient has tried conservative management including physical therapy (12 weeks),",
        "chiropractic care, and multiple medications (gabapentin, NSAIDs, muscle relaxants).",
        "ESI injections (3 series) provided only temporary relief lasting 2-3 weeks each."
    ], width)

    y = add_section(c, y, "PHYSICAL EXAMINATION:", [
        "Lumbar spine: Decreased lordosis. Tenderness at L4-L5 and L5-S1 levels.",
        "Range of motion: Flexion 40 degrees (normal 80), Extension 10 degrees (normal 25).",
        "Straight leg raise: Positive bilaterally at 30 degrees.",
        "Motor: 4/5 strength bilateral ankle dorsiflexion and great toe extension.",
        "Sensory: Diminished sensation L5-S1 dermatomal distribution bilaterally.",
        "Reflexes: Diminished ankle reflexes bilaterally."
    ], width)

    y = add_section(c, y, "IMAGING REVIEW:", [
        "MRI lumbar spine (09/10/2024): Severe degenerative disc disease at L4-L5 and L5-S1.",
        "Central canal stenosis at L4-L5 with AP diameter 6mm (normal >12mm).",
        "Bilateral foraminal stenosis at L5-S1. Disc herniation at L4-L5 with nerve impingement."
    ], width)

    y = add_section(c, y, "ASSESSMENT:", [
        "1. Lumbar spinal stenosis with neurogenic claudication",
        "2. L4-L5 disc herniation with bilateral L5 radiculopathy",
        "3. Failed conservative management over 14 months",
        "4. Significant functional impairment"
    ], width)

    y = add_section(c, y, "PLAN:", [
        "1. Patient is a candidate for lumbar decompression surgery (CPT 63047, 63048)",
        "2. Order pre-operative clearance",
        "3. Submit for insurance authorization",
        "4. Continue current pain management regimen pending surgery"
    ], width)

    add_signature(c, y, "Dr. Michael Chen, MD, Spine Surgery", "09/15/2024")


# Document 2: MRI Report
def doc2_mri_report(c, width, height):
    y = add_header(c, width, height, "Houston Medical Imaging",
                   "MRI LUMBAR SPINE WITHOUT CONTRAST", "09/10/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Radiologist:")
    c.setFont("Helvetica", 10)
    c.drawString(6.2*inch, height - 2.45*inch, "Dr. Lisa Wang")

    y = add_section(c, y, "CLINICAL INDICATION:", [
        "Chronic low back pain with bilateral lower extremity radiculopathy.",
        "Rule out disc herniation, spinal stenosis."
    ], width)

    y = add_section(c, y, "TECHNIQUE:", [
        "Multiplanar multisequence MRI of the lumbar spine performed on 3T scanner.",
        "Sagittal T1, T2, STIR. Axial T1, T2 at each level."
    ], width)

    y = add_section(c, y, "FINDINGS:", [
        "",
        "L3-L4: Mild disc bulge without significant stenosis. Facet arthropathy.",
        "",
        "L4-L5: SEVERE central disc herniation measuring 8mm with extrusion.",
        "Central canal stenosis with AP diameter reduced to 6mm (severe).",
        "Bilateral neural foraminal narrowing, moderate to severe.",
        "Compression of traversing L5 nerve roots bilaterally.",
        "",
        "L5-S1: Moderate disc bulge with annular tear. Bilateral foraminal stenosis,",
        "moderate severity. Grade 1 anterolisthesis of L5 on S1 (4mm).",
        "",
        "Conus medullaris terminates normally at L1 level.",
        "No evidence of infection, tumor, or fracture."
    ], width)

    y = add_section(c, y, "IMPRESSION:", [
        "1. Severe L4-L5 central disc herniation with significant spinal stenosis (6mm AP)",
        "2. Bilateral L5 nerve root compression at L4-L5 level",
        "3. Moderate L5-S1 degenerative changes with Grade 1 spondylolisthesis",
        "4. Multilevel degenerative disc disease",
        "",
        "SURGICAL CORRELATION RECOMMENDED given severity of findings."
    ], width)

    add_signature(c, y, "Dr. Lisa Wang, MD, Neuroradiology", "09/10/2024")


# Document 3: Physical Therapy Discharge Summary
def doc3_pt_discharge(c, width, height):
    y = add_header(c, width, height, "Premier Physical Therapy",
                   "PHYSICAL THERAPY DISCHARGE SUMMARY", "08/30/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Therapist:")
    c.setFont("Helvetica", 10)
    c.drawString(6*inch, height - 2.45*inch, "Jennifer Martinez, PT, DPT")

    y = add_section(c, y, "DIAGNOSIS:", [
        "Lumbar radiculopathy, lumbar spinal stenosis"
    ], width)

    y = add_section(c, y, "TREATMENT PERIOD:", [
        "Start Date: 06/01/2024    End Date: 08/30/2024",
        "Total Sessions Completed: 24 sessions over 12 weeks"
    ], width)

    y = add_section(c, y, "TREATMENT PROVIDED:", [
        "- Manual therapy: Soft tissue mobilization, joint mobilization",
        "- Therapeutic exercises: Core stabilization, lumbar extension exercises",
        "- Modalities: TENS, ultrasound, heat/ice therapy",
        "- Gait training and body mechanics education",
        "- Home exercise program instruction"
    ], width)

    y = add_section(c, y, "FUNCTIONAL OUTCOMES:", [
        "                              Initial         Discharge       Goal",
        "Walking tolerance:            1/4 mile        1/2 mile        1 mile",
        "Standing tolerance:           10 min          15 min          30 min",
        "Pain level (VAS):             8/10            7/10            3/10",
        "ODI Score:                    62%             58%             <40%",
        "",
        "GOALS NOT MET - Patient showed minimal functional improvement despite compliance."
    ], width)

    y = add_section(c, y, "PATIENT COMPLIANCE:", [
        "Patient demonstrated excellent compliance with therapy program.",
        "Attended 24/24 scheduled sessions (100% attendance).",
        "Consistently performed home exercise program as instructed."
    ], width)

    y = add_section(c, y, "DISCHARGE REASON:", [
        "Patient has reached a plateau with conservative physical therapy.",
        "Despite 12 weeks of aggressive treatment, functional goals not achieved.",
        "Symptoms persist with minimal improvement. Further conservative care",
        "unlikely to provide significant benefit."
    ], width)

    y = add_section(c, y, "RECOMMENDATIONS:", [
        "Patient should follow up with spine surgeon for surgical evaluation.",
        "Physical therapy alone is insufficient for this patient's condition."
    ], width)

    add_signature(c, y, "Jennifer Martinez, PT, DPT", "08/30/2024")


# Document 4: Pain Management Note
def doc4_pain_management(c, width, height):
    y = add_header(c, width, height, "Houston Spine & Pain Center",
                   "PAIN MANAGEMENT FOLLOW-UP NOTE", "09/01/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Provider:")
    c.setFont("Helvetica", 10)
    c.drawString(6*inch, height - 2.45*inch, "Dr. Rachel Kumar")

    y = add_section(c, y, "CHIEF COMPLAINT:", [
        "Follow-up for chronic lumbar pain management. Patient reports pain remains 7-8/10."
    ], width)

    y = add_section(c, y, "INJECTION HISTORY:", [
        "ESI #1 (03/15/2024): L4-L5 interlaminar - 50% relief x 3 weeks",
        "ESI #2 (05/10/2024): L4-L5 transforaminal - 40% relief x 2 weeks",
        "ESI #3 (07/20/2024): L5-S1 transforaminal - 30% relief x 2 weeks",
        "",
        "Patient has received maximum benefit from epidural steroid injections.",
        "Diminishing returns noted with each subsequent injection."
    ], width)

    y = add_section(c, y, "CURRENT MEDICATIONS:", [
        "- Gabapentin 600mg TID - provides minimal relief",
        "- Meloxicam 15mg daily - GI upset, limited use",
        "- Cyclobenzaprine 10mg TID PRN - helps muscle spasms",
        "- Tramadol 50mg QID PRN - provides 2-3 hours relief"
    ], width)

    y = add_section(c, y, "FUNCTIONAL STATUS:", [
        "- Unable to work (was warehouse supervisor)",
        "- Cannot sit >20 minutes without repositioning",
        "- Sleep interrupted 4-5 times nightly due to pain",
        "- Requires assistance with household tasks",
        "- Uses cane for ambulation"
    ], width)

    y = add_section(c, y, "ASSESSMENT:", [
        "Chronic intractable lumbar pain with radiculopathy.",
        "Patient has exhausted conservative pain management options.",
        "Epidural injections provided only temporary, diminishing relief."
    ], width)

    y = add_section(c, y, "PLAN:", [
        "1. Continue current medication regimen",
        "2. Strongly support surgical consultation - conservative measures exhausted",
        "3. Patient is appropriate surgical candidate from pain management perspective",
        "4. Will continue to manage pain perioperatively"
    ], width)

    add_signature(c, y, "Dr. Rachel Kumar, MD, Pain Medicine", "09/01/2024")


# Document 5: EMG/Nerve Conduction Study
def doc5_emg(c, width, height):
    y = add_header(c, width, height, "Houston Neurology Associates",
                   "ELECTRODIAGNOSTIC STUDY REPORT", "08/20/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Neurologist:")
    c.setFont("Helvetica", 10)
    c.drawString(6.2*inch, height - 2.45*inch, "Dr. James Park")

    y = add_section(c, y, "CLINICAL INDICATION:", [
        "Bilateral lower extremity pain, numbness, and weakness.",
        "Evaluate for lumbar radiculopathy."
    ], width)

    y = add_section(c, y, "NERVE CONDUCTION STUDIES:", [
        "Motor Studies:",
        "  Peroneal nerve (L): Prolonged distal latency, reduced amplitude",
        "  Peroneal nerve (R): Mildly prolonged distal latency",
        "  Tibial nerve bilateral: Within normal limits",
        "",
        "Sensory Studies:",
        "  Sural nerve bilateral: Reduced amplitude",
        "  Superficial peroneal bilateral: Reduced amplitude"
    ], width)

    y = add_section(c, y, "NEEDLE EMG FINDINGS:", [
        "Muscle                    Insertional   Fibrillations   Motor Units",
        "L paraspinal L4-S1        Increased     2+              N/A",
        "L tibialis anterior       Increased     2+              Reduced",
        "L ext hallucis longus     Increased     2+              Reduced",
        "L gastrocnemius           Normal        1+              Normal",
        "R tibialis anterior       Increased     1+              Mildly reduced",
        "R ext hallucis longus     Normal        1+              Normal"
    ], width)

    y = add_section(c, y, "INTERPRETATION:", [
        "This electrodiagnostic study demonstrates:",
        "",
        "1. BILATERAL L5 RADICULOPATHY - active denervation present",
        "   Left side more severely affected than right",
        "",
        "2. Evidence of ongoing nerve root compression with acute changes",
        "",
        "3. Findings correlate with MRI showing L4-L5 disc herniation",
        "   with bilateral L5 nerve root compression",
        "",
        "These findings support the clinical diagnosis and indicate",
        "active nerve damage requiring intervention."
    ], width)

    add_signature(c, y, "Dr. James Park, MD, Neurology", "08/20/2024")


# Document 6: Pre-operative Clearance
def doc6_preop(c, width, height):
    y = add_header(c, width, height, "Houston Internal Medicine",
                   "PRE-OPERATIVE MEDICAL CLEARANCE", "09/20/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Provider:")
    c.setFont("Helvetica", 10)
    c.drawString(6*inch, height - 2.45*inch, "Dr. Amanda Foster")

    y = add_section(c, y, "PROPOSED PROCEDURE:", [
        "Lumbar decompression surgery (laminectomy L4-L5, L5-S1)"
    ], width)

    y = add_section(c, y, "MEDICAL HISTORY:", [
        "- Hypertension - well controlled on lisinopril",
        "- Type 2 Diabetes - HbA1c 6.8%, well controlled",
        "- Hyperlipidemia - on atorvastatin",
        "- No history of cardiac disease, stroke, or bleeding disorders",
        "- No prior surgeries"
    ], width)

    y = add_section(c, y, "CURRENT MEDICATIONS:", [
        "- Lisinopril 20mg daily",
        "- Metformin 1000mg BID",
        "- Atorvastatin 40mg daily",
        "- Aspirin 81mg daily (will hold 7 days pre-op)"
    ], width)

    y = add_section(c, y, "PRE-OPERATIVE WORKUP:", [
        "CBC: WBC 7.2, Hgb 14.1, Plt 245 - Normal",
        "BMP: All values within normal limits, Cr 0.9",
        "PT/INR: 1.0 - Normal",
        "HbA1c: 6.8% - Acceptable for surgery",
        "EKG: Normal sinus rhythm, no acute changes",
        "Chest X-ray: No acute cardiopulmonary disease"
    ], width)

    y = add_section(c, y, "ASSESSMENT:", [
        "62-year-old male with well-controlled comorbidities.",
        "ASA Physical Status Classification: II",
        "Revised Cardiac Risk Index: 0 (Low risk)"
    ], width)

    y = add_section(c, y, "MEDICAL CLEARANCE:", [
        "",
        "*** PATIENT IS CLEARED FOR LUMBAR SPINE SURGERY ***",
        "",
        "Patient is at low cardiac and perioperative risk.",
        "Medical conditions are optimized for surgery.",
        "",
        "Pre-operative instructions:",
        "- Hold aspirin 7 days before surgery",
        "- Hold metformin 48 hours before surgery",
        "- Continue other medications with sip of water morning of surgery"
    ], width)

    add_signature(c, y, "Dr. Amanda Foster, MD, Internal Medicine", "09/20/2024")


# Document 7: Second Opinion Consultation
def doc7_second_opinion(c, width, height):
    y = add_header(c, width, height, "Texas Spine Institute",
                   "SECOND OPINION CONSULTATION", "09/25/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Provider:")
    c.setFont("Helvetica", 10)
    c.drawString(6*inch, height - 2.45*inch, "Dr. David Rodriguez")

    y = add_section(c, y, "REASON FOR CONSULTATION:", [
        "Second opinion requested for surgical recommendation - lumbar decompression."
    ], width)

    y = add_section(c, y, "RECORDS REVIEWED:", [
        "- Initial consultation note (Dr. Chen, 09/15/2024)",
        "- MRI lumbar spine (09/10/2024)",
        "- Physical therapy discharge summary (08/30/2024)",
        "- Pain management notes and injection records",
        "- EMG/NCS report (08/20/2024)"
    ], width)

    y = add_section(c, y, "INDEPENDENT EXAMINATION:", [
        "Physical examination consistent with documented findings.",
        "Positive straight leg raise bilateral. Diminished reflexes.",
        "Motor weakness bilateral L5 distribution.",
        "Antalgic gait with use of cane."
    ], width)

    y = add_section(c, y, "IMAGING REVIEW:", [
        "Independently reviewed MRI dated 09/10/2024.",
        "Concur with findings of severe L4-L5 stenosis and disc herniation.",
        "Central canal diameter of 6mm is significantly compromised.",
        "Bilateral nerve root compression clearly visualized."
    ], width)

    y = add_section(c, y, "OPINION:", [
        "I have thoroughly reviewed the medical records and independently examined",
        "the patient. I CONCUR with the surgical recommendation.",
        "",
        "This patient has:",
        "1. Severe, symptomatic lumbar spinal stenosis with radiculopathy",
        "2. Failed comprehensive conservative treatment for >12 months",
        "3. Documented neurological deficits (motor weakness, sensory changes)",
        "4. EMG-confirmed active radiculopathy",
        "5. MRI findings that correlate with clinical presentation",
        "",
        "Surgical intervention is MEDICALLY NECESSARY. Further delay may result",
        "in permanent neurological damage. Conservative options have been exhausted."
    ], width)

    add_signature(c, y, "Dr. David Rodriguez, MD, FACS, Spine Surgery", "09/25/2024")


# Document 8: Medication List
def doc8_medication_list(c, width, height):
    y = add_header(c, width, height, "Houston Spine & Pain Center",
                   "COMPREHENSIVE MEDICATION LIST", "10/01/2024")
    c.setFont("Helvetica-Bold", 10)
    c.drawString(5*inch, height - 2.45*inch, "Provider:")
    c.setFont("Helvetica", 10)
    c.drawString(6*inch, height - 2.45*inch, "Dr. Michael Chen")

    y = add_section(c, y, "CURRENT MEDICATIONS FOR SPINE CONDITION:", [
        "",
        "Medication              Dose           Frequency    Start Date    Response",
        "---------------------------------------------------------------------------",
        "Gabapentin              600mg          TID          01/15/2024    Minimal",
        "Meloxicam               15mg           Daily        02/01/2024    Limited*",
        "Cyclobenzaprine         10mg           TID PRN      03/01/2024    Moderate",
        "Tramadol                50mg           QID PRN      04/15/2024    Moderate",
        "",
        "*Discontinued due to GI side effects, resumed at lower frequency"
    ], width)

    y = add_section(c, y, "FAILED MEDICATIONS (Previously Tried):", [
        "",
        "Medication              Dose           Duration     Reason Discontinued",
        "---------------------------------------------------------------------------",
        "Ibuprofen OTC           800mg TID      6 months     Ineffective",
        "Naproxen OTC            500mg BID      4 months     Ineffective",
        "Diclofenac gel          Topical        3 months     No relief",
        "Prednisone taper        60mg taper     2 courses    Temporary only",
        "Duloxetine              60mg daily     8 weeks      Intolerable side effects",
        "Pregabalin              150mg BID      6 weeks      Dizziness, switched to gabapentin"
    ], width)

    y = add_section(c, y, "NON-PHARMACOLOGICAL TREATMENTS TRIED:", [
        "- Physical therapy: 24 sessions over 12 weeks - minimal improvement",
        "- Chiropractic care: 16 visits - no sustained relief",
        "- Acupuncture: 8 sessions - did not help",
        "- TENS unit: Daily use - provides temporary distraction only",
        "- Lumbar support brace: Ongoing use - mild comfort"
    ], width)

    y = add_section(c, y, "INJECTION THERAPY:", [
        "Date         Type                    Location    Relief Duration",
        "-----------------------------------------------------------------",
        "03/15/2024   ESI interlaminar        L4-L5      3 weeks (50%)",
        "05/10/2024   ESI transforaminal      L4-L5      2 weeks (40%)",
        "07/20/2024   ESI transforaminal      L5-S1      2 weeks (30%)",
        "",
        "Maximum epidural injections administered. Diminishing effectiveness noted."
    ], width)

    y = add_section(c, y, "SUMMARY:", [
        "Patient has exhausted comprehensive conservative treatment including:",
        "- Multiple oral medications (NSAIDs, muscle relaxants, neuropathic agents)",
        "- Physical therapy (24 sessions)",
        "- Three epidural steroid injections",
        "- Alternative therapies (chiropractic, acupuncture)",
        "",
        "CONSERVATIVE MANAGEMENT HAS FAILED. Surgical intervention recommended."
    ], width)

    add_signature(c, y, "Dr. Michael Chen, MD, Spine Surgery", "10/01/2024")


def create_csv_file():
    """Create a CSV file for testing the upload functionality."""
    csv_path = "/Users/vaatsav/Desktop/claim-appeals-v2/backend/test_upload.csv"

    # Sample denial data for testing
    denials = [
        {
            "claim_number": "CLM-2024-90001",
            "patient_name": "Robert Smith",
            "patient_id": "PT-100001",
            "patient_dob": "1962-07-22",
            "provider_name": "Dr. Michael Chen",
            "provider_id": "NPI-1234567890",
            "payer_name": "Blue Cross Blue Shield",
            "payer_id": "BCBS-TX",
            "policy_number": "POL-789456123",
            "service_date": "2024-10-05",
            "denial_date": "2024-10-15",
            "denial_code": "MN-001",
            "denial_category": "medical_necessity",
            "denial_reason": "Service not medically necessary - insufficient documentation of conservative treatment failure",
            "claim_amount": "45000.00",
            "procedure_code": "63047",
            "diagnosis_codes": "M47.816,M54.5,G89.29",
            "service_description": "Lumbar laminectomy with decompression",
            "priority": "high",
            "internal_notes": "Strong case - extensive conservative treatment documented"
        },
        {
            "claim_number": "CLM-2024-90002",
            "patient_name": "Sarah Williams",
            "patient_id": "PT-100002",
            "patient_dob": "1975-03-14",
            "provider_name": "Dr. Lisa Thompson",
            "provider_id": "NPI-0987654321",
            "payer_name": "Aetna",
            "payer_id": "AETNA-001",
            "policy_number": "POL-456789012",
            "service_date": "2024-09-28",
            "denial_date": "2024-10-10",
            "denial_code": "MN-003",
            "denial_category": "medical_necessity",
            "denial_reason": "Prior authorization not obtained",
            "claim_amount": "12500.00",
            "procedure_code": "27447",
            "diagnosis_codes": "M17.11,M25.561",
            "service_description": "Total knee arthroplasty",
            "priority": "normal",
            "internal_notes": "PA was submitted - check records"
        },
        {
            "claim_number": "CLM-2024-90003",
            "patient_name": "James Martinez",
            "patient_id": "PT-100003",
            "patient_dob": "1958-11-30",
            "provider_name": "Dr. Robert Kim",
            "provider_id": "NPI-5678901234",
            "payer_name": "United Healthcare",
            "payer_id": "UHC-001",
            "policy_number": "POL-321654987",
            "service_date": "2024-10-01",
            "denial_date": "2024-10-18",
            "denial_code": "MN-002",
            "denial_category": "medical_necessity",
            "denial_reason": "Alternative less invasive treatment options available",
            "claim_amount": "38000.00",
            "procedure_code": "22612",
            "diagnosis_codes": "M43.16,M48.06",
            "service_description": "Lumbar fusion surgery",
            "priority": "high",
            "internal_notes": "Patient has tried all conservative options - need to document"
        },
        {
            "claim_number": "CLM-2024-90004",
            "patient_name": "Emily Chen",
            "patient_id": "PT-100004",
            "patient_dob": "1982-06-08",
            "provider_name": "Dr. Sarah Wilson",
            "provider_id": "NPI-3456789012",
            "payer_name": "Cigna",
            "payer_id": "CIGNA-001",
            "policy_number": "POL-654321789",
            "service_date": "2024-09-15",
            "denial_date": "2024-10-05",
            "denial_code": "MN-004",
            "denial_category": "medical_necessity",
            "denial_reason": "Documentation does not support medical necessity",
            "claim_amount": "8500.00",
            "procedure_code": "29881",
            "diagnosis_codes": "M23.201,S83.511A",
            "service_description": "Knee arthroscopy with meniscectomy",
            "priority": "normal",
            "internal_notes": "MRI clearly shows tear - gather supporting docs"
        },
        {
            "claim_number": "CLM-2024-90005",
            "patient_name": "Michael Johnson",
            "patient_id": "PT-100005",
            "patient_dob": "1970-01-25",
            "provider_name": "Dr. Michael Chen",
            "provider_id": "NPI-1234567890",
            "payer_name": "Humana",
            "payer_id": "HUMANA-001",
            "policy_number": "POL-987654321",
            "service_date": "2024-10-10",
            "denial_date": "2024-10-20",
            "denial_code": "MN-001",
            "denial_category": "medical_necessity",
            "denial_reason": "Conservative treatment not exhausted",
            "claim_amount": "52000.00",
            "procedure_code": "63048",
            "diagnosis_codes": "M47.817,M54.16,G89.4",
            "service_description": "Cervical laminectomy with fusion",
            "priority": "urgent",
            "internal_notes": "14 months of conservative treatment documented"
        }
    ]

    fieldnames = [
        "claim_number", "patient_name", "patient_id", "patient_dob",
        "provider_name", "provider_id", "payer_name", "payer_id",
        "policy_number", "service_date", "denial_date", "denial_code",
        "denial_category", "denial_reason", "claim_amount", "procedure_code",
        "diagnosis_codes", "service_description", "priority", "internal_notes"
    ]

    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(denials)

    print(f"Created CSV file: {csv_path}")


def main():
    # Create directory structure
    os.makedirs(BASE_PATH, exist_ok=True)

    print("Creating medical documents for patient PT-100001...")
    print("-" * 50)

    # Create all 8 PDFs
    documents = [
        ("initial_consultation_20240915.pdf", "Initial Consultation", doc1_initial_consult),
        ("mri_lumbar_20240910.pdf", "MRI Report", doc2_mri_report),
        ("pt_discharge_20240830.pdf", "PT Discharge", doc3_pt_discharge),
        ("pain_management_20240901.pdf", "Pain Management", doc4_pain_management),
        ("emg_report_20240820.pdf", "EMG Report", doc5_emg),
        ("preop_clearance_20240920.pdf", "Pre-op Clearance", doc6_preop),
        ("second_opinion_20240925.pdf", "Second Opinion", doc7_second_opinion),
        ("medication_list_20241001.pdf", "Medication List", doc8_medication_list),
    ]

    for filename, title, content_func in documents:
        create_pdf(filename, title, content_func)

    print("-" * 50)
    print("Creating CSV file for upload testing...")
    create_csv_file()

    print("-" * 50)
    print("Done! Created 8 PDFs and 1 CSV file.")


if __name__ == "__main__":
    main()
