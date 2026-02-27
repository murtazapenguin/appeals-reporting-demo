"""
Create 10 realistic sample medical PDFs for patient PT-100000
These documents support a Total Knee Arthroplasty (TKA) appeal case
"""

import os
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Patient info
PATIENT_NAME = "Margaret Johnson"
PATIENT_ID = "PT-100000"
PATIENT_DOB = "03/15/1958"
PROVIDER = "Dr. Sarah Wilson"
PROVIDER_PRACTICE = "Wilson Orthopedic Center"

# Base date (service date for TKA)
SERVICE_DATE = datetime(2024, 12, 1)

# Output directory
OUTPUT_DIR = "/Users/vaatsav/Desktop/claim-appeals-v2/backend/documents/PT-100000"

def create_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='DocTitle',
        fontSize=14,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=12
    ))
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='MedBody',
        fontSize=10,
        fontName='Helvetica',
        spaceBefore=3,
        spaceAfter=3,
        leading=14
    ))
    styles.add(ParagraphStyle(
        name='SmallText',
        fontSize=9,
        fontName='Helvetica',
        spaceBefore=2,
        spaceAfter=2
    ))
    return styles

def add_header(story, styles, doc_type, doc_date):
    """Add standard medical document header"""
    story.append(Paragraph(f"<b>{PROVIDER_PRACTICE}</b>", styles['DocTitle']))
    story.append(Paragraph("123 Medical Plaza, Suite 400, Austin, TX 78701", styles['SmallText']))
    story.append(Paragraph("Phone: (512) 555-0100 | Fax: (512) 555-0101", styles['SmallText']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(f"<b>{doc_type}</b>", styles['DocTitle']))
    story.append(Spacer(1, 0.1*inch))

    # Patient info table
    data = [
        ["Patient:", PATIENT_NAME, "DOB:", PATIENT_DOB],
        ["MRN:", PATIENT_ID, "Date:", doc_date.strftime("%m/%d/%Y")],
        ["Provider:", PROVIDER, "", ""]
    ]
    t = Table(data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

def create_progress_note_1():
    """Initial orthopedic consultation - 6 months before surgery"""
    doc_date = SERVICE_DATE - timedelta(days=180)
    filename = f"{OUTPUT_DIR}/2024/01/progress_note_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    add_header(story, styles, "PROGRESS NOTE - INITIAL ORTHOPEDIC CONSULTATION", doc_date)

    story.append(Paragraph("<b>CHIEF COMPLAINT:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient presents with chronic right knee pain that has been ongoing for approximately 18 months. "
        "Pain is described as constant, aching, and worsening with activity. Patient rates pain as 7/10 on average.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>HISTORY OF PRESENT ILLNESS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "65-year-old female with progressive right knee osteoarthritis. Patient reports significant difficulty "
        "with ambulation, unable to walk more than one block without rest. She has difficulty with stairs and "
        "cannot kneel or squat. Sleep is frequently interrupted by knee pain. Patient has tried over-the-counter "
        "NSAIDs (ibuprofen, naproxen) with minimal relief. She uses a cane for ambulation.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>PHYSICAL EXAMINATION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Right Knee: Moderate effusion present. Varus deformity noted. Range of motion 5-100 degrees "
        "(normal 0-135). Crepitus with flexion/extension. Tenderness along medial joint line. "
        "McMurray test positive. Ligaments stable. No erythema or warmth.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>IMAGING REVIEW:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "X-ray right knee (obtained today): Severe tricompartmental osteoarthritis with bone-on-bone contact "
        "in the medial compartment. Kellgren-Lawrence Grade 4. Osteophyte formation. Subchondral sclerosis.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>ASSESSMENT:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "1. Severe right knee osteoarthritis, Kellgren-Lawrence Grade 4<br/>"
        "2. Chronic knee pain with functional limitation<br/>"
        "3. Failed conservative management with NSAIDs",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>PLAN:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "1. Refer to physical therapy for 6-8 weeks of structured PT program<br/>"
        "2. Continue NSAIDs as needed<br/>"
        "3. Consider intra-articular corticosteroid injection if no improvement<br/>"
        "4. If conservative measures fail, patient may be candidate for total knee arthroplasty<br/>"
        "5. Follow up in 6 weeks",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Electronically signed by: {PROVIDER}, MD", styles['SmallText']))
    story.append(Paragraph(f"Date: {doc_date.strftime('%m/%d/%Y')}", styles['SmallText']))

    doc.build(story)
    return filename

def create_pt_initial_eval():
    """Physical therapy initial evaluation"""
    doc_date = SERVICE_DATE - timedelta(days=165)
    filename = f"{OUTPUT_DIR}/2024/01/pt_initial_eval_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    add_header(story, styles, "PHYSICAL THERAPY - INITIAL EVALUATION", doc_date)

    story.append(Paragraph("<b>REFERRAL DIAGNOSIS:</b>", styles['SectionHeader']))
    story.append(Paragraph("Right knee osteoarthritis, chronic pain", styles['MedBody']))

    story.append(Paragraph("<b>PATIENT HISTORY:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient referred by Dr. Sarah Wilson for evaluation and treatment of right knee osteoarthritis. "
        "Reports 18+ months of progressive knee pain. Currently using a cane. Unable to perform many daily "
        "activities including climbing stairs, kneeling, and walking distances greater than one block.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>OBJECTIVE MEASUREMENTS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Range of Motion (Right Knee):<br/>"
        "- Flexion: 100 degrees (WNL: 135)<br/>"
        "- Extension: -5 degrees (WNL: 0)<br/><br/>"
        "Strength Testing (Right Lower Extremity):<br/>"
        "- Quadriceps: 3+/5<br/>"
        "- Hamstrings: 4/5<br/><br/>"
        "Gait Analysis:<br/>"
        "- Antalgic gait pattern<br/>"
        "- Decreased stance phase on right<br/>"
        "- Uses cane in left hand",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>FUNCTIONAL LIMITATIONS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "- Unable to walk more than 1 block without rest due to pain<br/>"
        "- Unable to climb stairs without rail support<br/>"
        "- Unable to kneel or squat<br/>"
        "- Difficulty with sit-to-stand transfers<br/>"
        "- WOMAC Score: 68/96 (significant impairment)",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>TREATMENT PLAN:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Physical therapy 2x/week for 8 weeks focusing on:<br/>"
        "1. Therapeutic exercises for quadriceps strengthening<br/>"
        "2. Range of motion exercises<br/>"
        "3. Manual therapy for joint mobilization<br/>"
        "4. Gait training<br/>"
        "5. Modalities for pain management (heat, TENS)",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Physical Therapist: Jennifer Adams, PT, DPT", styles['SmallText']))
    story.append(Paragraph(f"Date: {doc_date.strftime('%m/%d/%Y')}", styles['SmallText']))

    doc.build(story)
    return filename

def create_pt_discharge():
    """Physical therapy discharge summary after 8 weeks"""
    doc_date = SERVICE_DATE - timedelta(days=109)
    filename = f"{OUTPUT_DIR}/2024/01/pt_discharge_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    add_header(story, styles, "PHYSICAL THERAPY - DISCHARGE SUMMARY", doc_date)

    story.append(Paragraph("<b>TREATMENT SUMMARY:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        f"Patient completed 16 sessions of physical therapy from {(SERVICE_DATE - timedelta(days=165)).strftime('%m/%d/%Y')} "
        f"to {doc_date.strftime('%m/%d/%Y')} (8 weeks, 2x/week).",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>PROGRESS SUMMARY:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Despite compliance with the prescribed physical therapy program, patient has shown minimal "
        "improvement in functional status. Patient continues to report significant pain with activity "
        "and functional limitations that impact daily living.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>OBJECTIVE OUTCOMES:</b>", styles['SectionHeader']))
    data = [
        ["Measure", "Initial", "Discharge", "Change"],
        ["Knee Flexion ROM", "100°", "105°", "+5°"],
        ["Knee Extension", "-5°", "-3°", "+2°"],
        ["Quadriceps Strength", "3+/5", "4-/5", "Minimal"],
        ["Walking Distance", "<1 block", "<1.5 blocks", "Minimal"],
        ["WOMAC Score", "68/96", "62/96", "-6 points"],
        ["Pain Level (avg)", "7/10", "6/10", "-1 point"]
    ]
    t = Table(data, colWidths=[2*inch, 1.25*inch, 1.25*inch, 1.25*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(t)

    story.append(Paragraph("<b>CLINICAL IMPRESSION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient has plateaued in therapy with minimal functional gains despite good compliance. "
        "The underlying severe osteoarthritis limits the effectiveness of conservative treatment. "
        "Physical therapy alone is insufficient to address the structural joint damage present.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>RECOMMENDATIONS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "1. Conservative treatment including physical therapy has failed to provide adequate relief<br/>"
        "2. Recommend follow-up with orthopedic surgeon to discuss surgical options<br/>"
        "3. Patient may benefit from total knee arthroplasty given severity of OA and failed PT",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Physical Therapist: Jennifer Adams, PT, DPT", styles['SmallText']))

    doc.build(story)
    return filename

def create_injection_note():
    """Cortisone injection note"""
    doc_date = SERVICE_DATE - timedelta(days=100)
    filename = f"{OUTPUT_DIR}/2024/01/injection_note_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    add_header(story, styles, "PROCEDURE NOTE - INTRA-ARTICULAR INJECTION", doc_date)

    story.append(Paragraph("<b>PROCEDURE:</b>", styles['SectionHeader']))
    story.append(Paragraph("Right knee intra-articular corticosteroid injection", styles['MedBody']))

    story.append(Paragraph("<b>INDICATION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Severe right knee osteoarthritis with persistent pain despite 8 weeks of physical therapy. "
        "Patient has failed NSAID therapy. Injection performed for pain relief and to assess potential "
        "surgical candidacy.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>PROCEDURE DETAILS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "After informed consent was obtained, the right knee was prepped in sterile fashion. "
        "Using a lateral suprapatellar approach, an 18-gauge needle was advanced into the joint space. "
        "Approximately 15cc of straw-colored synovial fluid was aspirated. 80mg of Depo-Medrol mixed with "
        "4cc of 1% lidocaine was injected into the joint. Patient tolerated the procedure well.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>POST-PROCEDURE:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient advised to rest for 24-48 hours. May resume normal activities as tolerated. "
        "Expect pain relief within 3-5 days if injection is effective. Follow up in 4 weeks to assess response.",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Physician: {PROVIDER}, MD", styles['SmallText']))

    doc.build(story)
    return filename

def create_followup_note_1():
    """Follow-up after injection - minimal relief"""
    doc_date = SERVICE_DATE - timedelta(days=72)
    filename = f"{OUTPUT_DIR}/2024/01/followup_note_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    add_header(story, styles, "PROGRESS NOTE - POST-INJECTION FOLLOW-UP", doc_date)

    story.append(Paragraph("<b>SUBJECTIVE:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient returns 4 weeks after right knee corticosteroid injection. Reports initial improvement "
        "lasting approximately 10 days, but pain has returned to baseline. Current pain level 7/10. "
        "Continues to have significant difficulty with ambulation and daily activities. "
        "Reports frustration with lack of sustained improvement despite multiple conservative treatments.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>OBJECTIVE:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Right knee examination unchanged from prior visit. Moderate effusion. Varus alignment. "
        "ROM 5-100 degrees. Tenderness medial joint line. Crepitus present.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>CONSERVATIVE TREATMENT SUMMARY:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient has now failed the following conservative measures:<br/>"
        "1. NSAIDs (ibuprofen, naproxen) - 18+ months - minimal relief<br/>"
        "2. Physical therapy - 8 weeks (16 sessions) - minimal improvement<br/>"
        "3. Intra-articular corticosteroid injection - transient relief only<br/>"
        "4. Activity modification and weight management - ongoing",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>ASSESSMENT:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Severe right knee osteoarthritis (Kellgren-Lawrence Grade 4) with failure of comprehensive "
        "conservative treatment program spanning over 6 months. Patient remains significantly disabled "
        "by knee pain and functional limitations.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>PLAN:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Given failure of conservative treatment, I have discussed surgical options with patient. "
        "Total knee arthroplasty is recommended. Discussed risks, benefits, and alternatives. "
        "Patient wishes to proceed. Will obtain pre-operative clearance and schedule surgery.",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"Physician: {PROVIDER}, MD", styles['SmallText']))

    doc.build(story)
    return filename

def create_mri_report():
    """MRI report confirming severity"""
    doc_date = SERVICE_DATE - timedelta(days=60)
    filename = f"{OUTPUT_DIR}/2024/01/mri_report_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    story.append(Paragraph("<b>RADIOLOGY REPORT</b>", styles['DocTitle']))
    story.append(Paragraph("Austin Diagnostic Imaging Center", styles['SmallText']))
    story.append(Spacer(1, 0.2*inch))

    data = [
        ["Patient:", PATIENT_NAME, "DOB:", PATIENT_DOB],
        ["MRN:", PATIENT_ID, "Date:", doc_date.strftime("%m/%d/%Y")],
        ["Exam:", "MRI RIGHT KNEE WITHOUT CONTRAST", "", ""],
        ["Ordering:", PROVIDER, "", ""]
    ]
    t = Table(data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>CLINICAL INDICATION:</b>", styles['SectionHeader']))
    story.append(Paragraph("Severe knee osteoarthritis, pre-operative planning for total knee arthroplasty", styles['MedBody']))

    story.append(Paragraph("<b>TECHNIQUE:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Multiplanar multisequence MRI of the right knee performed on 3T magnet. "
        "Sequences include T1, T2, PD fat-saturated, and STIR.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>FINDINGS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "<b>Osseous Structures:</b><br/>"
        "Severe tricompartmental degenerative changes. Full-thickness cartilage loss in the medial "
        "compartment with bone-on-bone articulation. Grade IV chondral changes. Subchondral cyst "
        "formation in medial tibial plateau. Bone marrow edema pattern consistent with degenerative changes.<br/><br/>"

        "<b>Menisci:</b><br/>"
        "Medial meniscus: Complex degenerative tear involving the posterior horn. Meniscal extrusion.<br/>"
        "Lateral meniscus: Degenerative signal, no discrete tear.<br/><br/>"

        "<b>Ligaments:</b><br/>"
        "ACL and PCL: Intact.<br/>"
        "MCL and LCL: Intact.<br/><br/>"

        "<b>Patellofemoral Compartment:</b><br/>"
        "Moderate chondromalacia patella. Patellar tracking normal.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>IMPRESSION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "1. SEVERE TRICOMPARTMENTAL OSTEOARTHRITIS with full-thickness cartilage loss and bone-on-bone "
        "contact in the medial compartment. Findings consistent with Kellgren-Lawrence Grade 4.<br/>"
        "2. Complex degenerative medial meniscal tear with extrusion.<br/>"
        "3. Bone marrow edema consistent with advanced degenerative disease.<br/><br/>"
        "These findings support the clinical diagnosis of end-stage osteoarthritis. "
        "Total knee arthroplasty may be indicated given severity of findings.",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Radiologist: Robert Kim, MD", styles['SmallText']))

    doc.build(story)
    return filename

def create_preop_clearance():
    """Pre-operative medical clearance"""
    doc_date = SERVICE_DATE - timedelta(days=30)
    filename = f"{OUTPUT_DIR}/2024/01/preop_clearance_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    story.append(Paragraph("<b>PRE-OPERATIVE MEDICAL CLEARANCE</b>", styles['DocTitle']))
    story.append(Paragraph("Austin Internal Medicine Associates", styles['SmallText']))
    story.append(Spacer(1, 0.2*inch))

    data = [
        ["Patient:", PATIENT_NAME, "DOB:", PATIENT_DOB],
        ["MRN:", PATIENT_ID, "Date:", doc_date.strftime("%m/%d/%Y")],
        ["Procedure:", "Total Knee Arthroplasty", "", ""],
        ["Surgeon:", PROVIDER, "", ""]
    ]
    t = Table(data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>MEDICAL HISTORY:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "- Hypertension (controlled on lisinopril)<br/>"
        "- Hyperlipidemia (on atorvastatin)<br/>"
        "- Osteoarthritis<br/>"
        "- No history of cardiac disease, diabetes, or bleeding disorders",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>VITAL SIGNS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "BP: 128/78 | HR: 72 | RR: 16 | SpO2: 98% RA<br/>"
        "Height: 5'4\" | Weight: 165 lbs | BMI: 28.3",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>LABORATORY RESULTS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "CBC: WNL | BMP: WNL | PT/INR: 1.0 | Hemoglobin A1c: 5.6% | Type & Screen: Completed",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>CARDIAC EVALUATION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "EKG: Normal sinus rhythm, no acute changes. Patient has functional capacity >4 METs. "
        "Low cardiac risk for non-cardiac surgery per ACC/AHA guidelines.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>CLEARANCE:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "<b>PATIENT IS CLEARED FOR SURGERY</b><br/><br/>"
        "This patient has been evaluated and is medically optimized for the planned total knee "
        "arthroplasty procedure. BMI of 28.3 is within acceptable range for surgery. "
        "No significant cardiac, pulmonary, or other medical contraindications identified.",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Physician: Mark Thompson, MD, Internal Medicine", styles['SmallText']))

    doc.build(story)
    return filename

def create_surgical_recommendation():
    """Orthopedic surgeon recommendation letter"""
    doc_date = SERVICE_DATE - timedelta(days=45)
    filename = f"{OUTPUT_DIR}/2024/01/surgical_recommendation_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    add_header(story, styles, "SURGICAL RECOMMENDATION - TOTAL KNEE ARTHROPLASTY", doc_date)

    story.append(Paragraph("<b>SUMMARY:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        f"This letter serves as documentation of my recommendation for total knee arthroplasty (TKA) "
        f"for patient {PATIENT_NAME}.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>CLINICAL PRESENTATION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "This 65-year-old female presents with severe right knee osteoarthritis causing significant "
        "pain and functional disability. Her symptoms have been progressive over the past 18+ months "
        "and have not responded adequately to comprehensive conservative management.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>CONSERVATIVE TREATMENT FAILURE:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient has exhausted conservative treatment options including:<br/>"
        "- NSAIDs for over 18 months<br/>"
        "- Structured physical therapy program (8 weeks, 16 sessions)<br/>"
        "- Intra-articular corticosteroid injection (transient relief only)<br/>"
        "- Activity modification and weight management",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>IMAGING FINDINGS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "X-ray and MRI demonstrate Kellgren-Lawrence Grade 4 osteoarthritis with bone-on-bone contact "
        "in the medial compartment, full-thickness cartilage loss, and complex degenerative meniscal tear.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>FUNCTIONAL IMPACT:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient is unable to walk more than 1-2 blocks, cannot climb stairs independently, "
        "requires a cane for ambulation, and has significant sleep disruption due to pain. "
        "Her quality of life is substantially impaired.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>RECOMMENDATION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "<b>I recommend Total Knee Arthroplasty for this patient.</b><br/><br/>"
        "This recommendation is based on:<br/>"
        "1. Severe structural joint damage (Grade 4 OA, bone-on-bone)<br/>"
        "2. Failure of comprehensive conservative treatment over 6+ months<br/>"
        "3. Significant functional disability affecting daily activities<br/>"
        "4. Good surgical candidacy (BMI 28.3, cleared by medicine)<br/>"
        "5. Patient understanding of risks, benefits, and alternatives<br/><br/>"
        "This surgery is medically necessary to restore function and quality of life.",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"{PROVIDER}, MD", styles['MedBody']))
    story.append(Paragraph("Board Certified Orthopedic Surgeon", styles['SmallText']))
    story.append(Paragraph("Fellowship Trained in Adult Joint Reconstruction", styles['SmallText']))

    doc.build(story)
    return filename

def create_xray_report():
    """X-ray report"""
    doc_date = SERVICE_DATE - timedelta(days=180)
    filename = f"{OUTPUT_DIR}/2024/01/xray_report_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    story.append(Paragraph("<b>RADIOLOGY REPORT</b>", styles['DocTitle']))
    story.append(Paragraph("Austin Diagnostic Imaging Center", styles['SmallText']))
    story.append(Spacer(1, 0.2*inch))

    data = [
        ["Patient:", PATIENT_NAME, "DOB:", PATIENT_DOB],
        ["MRN:", PATIENT_ID, "Date:", doc_date.strftime("%m/%d/%Y")],
        ["Exam:", "X-RAY RIGHT KNEE 3 VIEWS", "", ""]
    ]
    t = Table(data, colWidths=[1*inch, 2.5*inch, 0.8*inch, 2*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.2*inch))

    story.append(Paragraph("<b>CLINICAL INDICATION:</b>", styles['SectionHeader']))
    story.append(Paragraph("Chronic right knee pain, rule out osteoarthritis", styles['MedBody']))

    story.append(Paragraph("<b>FINDINGS:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "<b>Standing AP view:</b> Severe joint space narrowing in the medial compartment with "
        "bone-on-bone contact. Varus angulation of 8 degrees. Osteophyte formation along medial and "
        "lateral tibial plateaus and femoral condyles.<br/><br/>"

        "<b>Lateral view:</b> Large posterior osteophytes. Patellofemoral joint space preserved.<br/><br/>"

        "<b>Sunrise view:</b> Mild patellofemoral joint space narrowing. No patellar subluxation.",
        styles['MedBody']
    ))

    story.append(Paragraph("<b>IMPRESSION:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "1. SEVERE OSTEOARTHRITIS of the right knee, Kellgren-Lawrence Grade 4<br/>"
        "2. Bone-on-bone contact in medial compartment<br/>"
        "3. Varus deformity (8 degrees)<br/>"
        "4. Large osteophyte formation<br/><br/>"
        "Findings consistent with end-stage osteoarthritis.",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Radiologist: Robert Kim, MD", styles['SmallText']))

    doc.build(story)
    return filename

def create_medication_list():
    """Medication history showing NSAID use"""
    doc_date = SERVICE_DATE - timedelta(days=50)
    filename = f"{OUTPUT_DIR}/2024/01/medication_list_{doc_date.strftime('%Y%m%d')}.pdf"
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = create_styles()
    story = []

    add_header(story, styles, "MEDICATION RECONCILIATION", doc_date)

    story.append(Paragraph("<b>CURRENT MEDICATIONS:</b>", styles['SectionHeader']))

    data = [
        ["Medication", "Dose", "Frequency", "Start Date", "Indication"],
        ["Lisinopril", "10mg", "Daily", "2018", "Hypertension"],
        ["Atorvastatin", "20mg", "Daily", "2019", "Hyperlipidemia"],
        ["Ibuprofen", "800mg", "TID PRN", "2023", "Knee Pain - OA"],
        ["Naproxen", "500mg", "BID PRN", "2023", "Knee Pain - OA"],
        ["Acetaminophen", "1000mg", "TID PRN", "2023", "Knee Pain"],
        ["Omeprazole", "20mg", "Daily", "2023", "GI Protection w/NSAIDs"]
    ]
    t = Table(data, colWidths=[1.5*inch, 0.8*inch, 1*inch, 1*inch, 1.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("<b>NSAID TREATMENT HISTORY:</b>", styles['SectionHeader']))
    story.append(Paragraph(
        "Patient has been using over-the-counter and prescription NSAIDs for knee pain management "
        "since early 2023 (approximately 18+ months). Has cycled through ibuprofen and naproxen "
        "with only partial and temporary relief of symptoms. Added omeprazole for gastric protection "
        "due to chronic NSAID use. Despite maximal NSAID therapy, patient continues to have "
        "significant pain and functional limitation.",
        styles['MedBody']
    ))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Verified by: Clinical Pharmacy Team", styles['SmallText']))

    doc.build(story)
    return filename

def main():
    """Generate all sample PDFs"""
    print("Creating sample medical PDFs for patient PT-100000...")
    print("=" * 60)

    files = [
        ("Progress Note (Initial Consult)", create_progress_note_1()),
        ("X-Ray Report", create_xray_report()),
        ("PT Initial Evaluation", create_pt_initial_eval()),
        ("PT Discharge Summary", create_pt_discharge()),
        ("Injection Procedure Note", create_injection_note()),
        ("Follow-up Note (Post-Injection)", create_followup_note_1()),
        ("MRI Report", create_mri_report()),
        ("Medication List", create_medication_list()),
        ("Surgical Recommendation", create_surgical_recommendation()),
        ("Pre-op Clearance", create_preop_clearance()),
    ]

    for name, filepath in files:
        print(f"  ✓ Created: {name}")
        print(f"    Path: {filepath}")

    print("=" * 60)
    print(f"Created {len(files)} PDF documents for patient {PATIENT_ID}")
    print(f"Location: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
