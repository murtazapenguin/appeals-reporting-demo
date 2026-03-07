const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

// Fixed demo denials (for VITE_DEMO_MODE=true). id used for routing /denials/:id.
export const mockDenials = [
  { id: 'demo-1', claim_number: 'CLM-2025-0001', patient_name: 'Margaret Johnson', patient_id: 'PT-200001', patient_dob: '1958-03-15', provider_name: 'Dr. Sarah Wilson', provider_id: 'PRV-001', provider_practice_name: 'Main Street Medical', payer_name: 'Blue Cross Blue Shield', service_date: '2025-01-15', denial_date: '2025-02-01', denial_code: 'CO-50', denial_category: 'Medical Necessity', denial_reason: 'Medical necessity not established for Total Knee Arthroplasty', claim_amount: 44814, denied_amount: 44814, paid_amount: 0, procedure_code: '27447', procedure_description: 'Total Knee Arthroplasty', diagnosis_codes: 'M17.11', service_description: 'Total Knee Arthroplasty', status: 'denied', win_probability: 62, priority: 'high', appeal_deadline: '2025-03-03', internal_notes: 'Appeal REJECTED by payer — consider second-level appeal.' },
  { id: 'demo-2', claim_number: 'CLM-2025-0002', patient_name: 'Robert Chen', patient_id: 'PT-200002', patient_dob: '1972-07-22', provider_name: 'Dr. Michael Torres', provider_id: 'PRV-002', provider_practice_name: 'Valley Orthopedics', payer_name: 'UnitedHealthcare', service_date: '2025-01-10', denial_date: '2025-01-28', denial_code: 'CO-197', denial_category: 'Prior Authorization', denial_reason: 'Prior authorization was not obtained', claim_amount: 2230, denied_amount: 2230, paid_amount: 0, procedure_code: '99285', procedure_description: 'ED Visit Level 5', diagnosis_codes: 'I21.3', service_description: 'ED Visit Level 5', status: 'denied', win_probability: 45, priority: 'urgent', appeal_deadline: '2025-02-27', internal_notes: 'Appeal REJECTED.' },
  { id: 'demo-3', claim_number: 'CLM-2025-0003', patient_name: 'Linda Martinez', patient_id: 'PT-200003', patient_dob: '1965-11-08', provider_name: 'Dr. Emily Parker', provider_id: 'PRV-003', provider_practice_name: 'Sunrise Family Practice', payer_name: 'Aetna', service_date: '2025-01-05', denial_date: '2025-01-20', denial_code: 'CO-50', denial_category: 'Medical Necessity', denial_reason: 'Documentation does not support medical necessity', claim_amount: 48159, denied_amount: 48159, paid_amount: 0, procedure_code: '27130', procedure_description: 'Total Hip Arthroplasty', diagnosis_codes: 'M16.11', service_description: 'Total Hip Arthroplasty', status: 'denied', win_probability: 55, priority: 'high', appeal_deadline: '2025-02-19', internal_notes: 'Rejected appeal.' },
  { id: 'demo-4', claim_number: 'CLM-2025-0004', patient_name: 'James Anderson', patient_id: 'PT-200004', patient_dob: '1950-05-20', provider_name: 'Dr. Sarah Wilson', provider_id: 'PRV-001', provider_practice_name: 'Main Street Medical', payer_name: 'UnitedHealthcare', service_date: '2024-12-01', denial_date: '2024-12-18', denial_code: 'CO-45', denial_category: 'Coding Error', denial_reason: 'Charges exceed contracted amount', claim_amount: 1867, denied_amount: 1867, paid_amount: 0, procedure_code: '99284', procedure_description: 'ED Visit Level 4', diagnosis_codes: 'R07.9', service_description: 'ED Visit Level 4', status: 'approved', win_probability: 78, priority: 'normal', appeal_deadline: '2025-01-17', internal_notes: 'OVERTURNED — payer approved the appeal.' },
  { id: 'demo-5', claim_number: 'CLM-2025-0005', patient_name: 'Patricia Brown', patient_id: 'PT-200005', patient_dob: '1980-09-12', provider_name: 'Dr. Emily Parker', provider_id: 'PRV-003', provider_practice_name: 'Lakeside Cardiology', payer_name: 'Aetna', service_date: '2024-11-20', denial_date: '2024-12-05', denial_code: 'CO-167', denial_category: 'Medical Necessity', denial_reason: 'Diagnosis not covered per policy', claim_amount: 1846, denied_amount: 0, paid_amount: 1846, procedure_code: '72148', procedure_description: 'MRI Lumbar Spine', diagnosis_codes: 'M54.5', service_description: 'MRI Lumbar Spine', status: 'approved', win_probability: 88, priority: 'normal', appeal_deadline: '2025-01-04', internal_notes: 'Approved.' },
  { id: 'demo-6', claim_number: 'CLM-2025-0006', patient_name: 'William Taylor', patient_id: 'PT-200006', patient_dob: '1968-02-28', provider_name: 'Dr. Harvey Dent', provider_id: 'PRV-004', provider_practice_name: 'Metro Surgical Associates', payer_name: 'Cigna', service_date: '2025-02-01', denial_date: '2025-02-10', denial_code: 'CO-16', denial_category: 'Documentation', denial_reason: 'Claim lacks required supporting documentation', claim_amount: 1929, denied_amount: 1929, paid_amount: 0, procedure_code: '29881', procedure_description: 'Knee Arthroscopy', diagnosis_codes: 'S83.211A', service_description: 'Knee Arthroscopy', status: 'submitted', win_probability: 72, priority: 'normal', appeal_deadline: '2025-03-12', internal_notes: 'Awaiting payer decision.' },
  { id: 'demo-7', claim_number: 'CLM-2025-0007', patient_name: 'Susan White', patient_id: 'PT-200007', patient_dob: '1955-12-03', provider_name: 'Dr. Sarah Wilson', provider_id: 'PRV-001', provider_practice_name: 'Main Street Medical', payer_name: 'Humana', service_date: '2025-01-22', denial_date: '2025-02-05', denial_code: 'CO-50', denial_category: 'Medical Necessity', denial_reason: 'Non-covered service per benefit plan', claim_amount: 34976, denied_amount: 34976, paid_amount: 0, procedure_code: '63047', procedure_description: 'Lumbar Laminectomy', diagnosis_codes: 'M48.06', service_description: 'Lumbar Laminectomy', status: 'denied', win_probability: 50, priority: 'high', appeal_deadline: '2025-03-07', internal_notes: 'Rejected.' },
  { id: 'demo-8', claim_number: 'CLM-2025-0008', patient_name: 'David Lee', patient_id: 'PT-200008', patient_dob: '1978-04-14', provider_name: 'Dr. Thomas Elliot', provider_id: 'PRV-006', provider_practice_name: 'Valley Orthopedics', payer_name: 'Blue Cross Blue Shield', service_date: '2024-10-15', denial_date: '2024-11-01', denial_code: 'CO-197', denial_category: 'Prior Authorization', denial_reason: 'Precertification absent', claim_amount: 52211, denied_amount: 0, paid_amount: 52211, procedure_code: '22551', procedure_description: 'ACDF', diagnosis_codes: 'M50.12', service_description: 'ACDF', status: 'approved', win_probability: 90, priority: 'high', appeal_deadline: '2024-12-01', internal_notes: 'Overturned.' },
  { id: 'demo-9', claim_number: 'CLM-2025-0009', patient_name: 'Jennifer Garcia', patient_id: 'PT-200009', patient_dob: '1990-08-30', provider_name: 'Dr. Leslie Thompkins', provider_id: 'PRV-005', provider_practice_name: 'Sunrise Family Practice', payer_name: 'Cigna', service_date: '2025-02-05', denial_date: '2025-02-14', denial_code: 'CO-96', denial_category: 'Medical Necessity', denial_reason: 'Non-covered charge(s)', claim_amount: 8341, denied_amount: 8341, paid_amount: 0, procedure_code: '43239', procedure_description: 'Upper GI Endoscopy', diagnosis_codes: 'K21.0', service_description: 'Upper GI Endoscopy', status: 'appeal_ready', win_probability: 58, priority: 'normal', appeal_deadline: '2025-03-16', internal_notes: 'Letter drafted — ready for submission.' },
  { id: 'demo-10', claim_number: 'CLM-2025-0010', patient_name: 'Michael Williams', patient_id: 'PT-200010', patient_dob: '1962-01-25', provider_name: 'Dr. Michael Torres', provider_id: 'PRV-002', provider_practice_name: 'Lakeside Cardiology', payer_name: 'UnitedHealthcare', service_date: '2025-01-28', denial_date: '2025-02-08', denial_code: 'CO-45', denial_category: 'Coding Error', denial_reason: 'Procedure code inconsistent with modifier', claim_amount: 3157, denied_amount: 3157, paid_amount: 0, procedure_code: '99291', procedure_description: 'Critical Care First Hour', diagnosis_codes: 'R65.20', service_description: 'Critical Care', status: 'in_review', win_probability: 75, priority: 'urgent', appeal_deadline: '2025-03-10', internal_notes: 'Under review — gathering supporting documentation.' },
  { id: 'demo-11', claim_number: 'CLM-2025-0011', patient_name: 'Elizabeth Jones', patient_id: 'PT-200011', patient_dob: '1975-06-12', provider_name: 'Dr. Emily Parker', provider_id: 'PRV-003', provider_practice_name: 'Metro Surgical Associates', payer_name: 'Aetna', service_date: '2024-12-20', denial_date: '2025-01-05', denial_code: 'CO-11', denial_category: 'Coding Error', denial_reason: 'Diagnosis inconsistent with procedure', claim_amount: 18500, denied_amount: 0, paid_amount: 18500, procedure_code: '27447', procedure_description: 'Total Knee Arthroplasty', diagnosis_codes: 'M17.11', service_description: 'Total Knee Arthroplasty', status: 'approved', win_probability: 82, priority: 'normal', appeal_deadline: '2025-02-04', internal_notes: 'Approved.' },
  { id: 'demo-12', claim_number: 'CLM-2025-0012', patient_name: 'Thomas Davis', patient_id: 'PT-200012', patient_dob: '1948-09-08', provider_name: 'Dr. Sarah Wilson', provider_id: 'PRV-001', provider_practice_name: 'Main Street Medical', payer_name: 'Medicare', service_date: '2025-02-10', denial_date: '2025-02-18', denial_code: 'CO-29', denial_category: 'Prior Authorization', denial_reason: 'Time limit for filing exceeded', claim_amount: 4200, denied_amount: 4200, paid_amount: 0, procedure_code: '70553', procedure_description: 'MRI Brain', diagnosis_codes: 'G43.909', service_description: 'MRI Brain', status: 'pending', win_probability: null, priority: 'low', appeal_deadline: '2025-03-20', internal_notes: 'New denial — awaiting initial review.' },
];

// Mock documents for demo (by patient_id). DenialDetail uses getByPatientId(patient_id).
export const mockDocumentsByPatient = {};
mockDenials.forEach((d) => {
  const pid = d.patient_id;
  if (!mockDocumentsByPatient[pid]) mockDocumentsByPatient[pid] = [];
  mockDocumentsByPatient[pid].push({
    _id: `doc-${d.id}-1`,
    denial_id: d.id,
    patient_id: pid,
    document_name: 'progress_notes.pdf',
    document_type: 'progress_notes',
    document_date: d.service_date,
    total_pages: 3,
    uploaded_at: d.service_date,
  });
  mockDocumentsByPatient[pid].push({
    _id: `doc-${d.id}-2`,
    denial_id: d.id,
    patient_id: pid,
    document_name: 'eob.pdf',
    document_type: 'eob',
    document_date: d.denial_date,
    total_pages: 2,
    uploaded_at: d.denial_date,
  });
});

// Mock criteria evaluation result for any denial in demo.
export const mockCriteriaResult = {
  denial_id: 'demo-1',
  total_criteria: 5,
  criteria_met: 3,
  win_probability: 62,
  criteria: [
    { id: 'TKA-1', question: 'Has the patient completed at least 6 months of conservative treatment?', met: true, evidence: [{ document_id: 'doc-demo-1-1', document_name: 'progress_notes.pdf', page: 1, text: 'Patient completed 8 months PT and NSAIDs without adequate relief.', bbox: [0.1, 0.2, 0.9, 0.25] }] },
    { id: 'TKA-2', question: 'Does imaging show bone-on-bone or Grade IV cartilage loss?', met: true, evidence: [{ document_id: 'doc-demo-1-1', document_name: 'progress_notes.pdf', page: 2, text: 'X-ray shows Kellgren-Lawrence Grade 4 changes.', bbox: [0.1, 0.3, 0.9, 0.35] }] },
    { id: 'TKA-3', question: 'Is there documented significant functional limitation?', met: true, evidence: [{ document_id: 'doc-demo-1-1', document_name: 'progress_notes.pdf', page: 1, text: 'Unable to walk more than 2 blocks; difficulty with stairs.', bbox: [0.1, 0.4, 0.9, 0.45] }] },
    { id: 'TKA-4', question: 'Has the condition failed to improve despite conservative measures?', met: false, missing_documents: 'No explicit failure statement in submitted records.' },
    { id: 'TKA-5', question: 'Is BMI documented as < 40 or with bariatric clearance?', met: false, missing_documents: 'BMI not found in submitted documents.' },
  ],
  evaluated_at: new Date().toISOString(),
};

// Mock appeal letter for demo.
export const mockAppealLetter = {
  denial_id: 'demo-1',
  provider_letterhead: { name: 'Main Street Medical\nDr. Sarah Wilson', address: '123 Medical Plaza, Suite 400', phone: '(512) 555-0100' },
  sections: [
    { title: 'RE: Appeal of Claim Denial', content: 'Dear Blue Cross Blue Shield Appeals Department,\n\nWe are writing to formally appeal the denial of claim CLM-2025-0001 for patient Margaret Johnson. The claim for Total Knee Arthroplasty was denied under code CO-50. We respectfully disagree and submit the following evidence in support of medical necessity.' },
    { title: 'Clinical Summary', content: 'Margaret Johnson presented with significant and progressive symptoms that warranted Total Knee Arthroplasty. The patient had undergone extensive conservative treatment including physical therapy and pharmacological management without adequate relief. Clinical examination and diagnostic imaging confirmed the need for surgical intervention.' },
    { title: 'Supporting Evidence', content: 'The enclosed medical records demonstrate documented failure of conservative treatment, diagnostic imaging confirming the clinical diagnosis, functional limitations affecting activities of daily living, and specialist recommendation for the procedure.' },
    { title: 'Conclusion', content: 'Based on the comprehensive clinical evidence, we believe Total Knee Arthroplasty was medically necessary and appropriate. We respectfully request that Blue Cross Blue Shield reverse the denial and provide coverage for this claim.' },
  ],
  enclosed_documents: ['Medical Records', 'Progress Notes', 'X-Ray Report'],
  signature: { name: 'Dr. Sarah Wilson', title: 'Attending Physician, Main Street Medical' },
  generated_at: new Date().toISOString(),
};

export const mockDashboard = {
  total_open_denials: 47,
  total_at_risk: 312450,
  urgent_appeals: 8,
  high_probability_count: 19,
  recovered_this_month: 87250,
  recovery_rate_this_month: 64,
  total_recovered_ytd: 1245800,
  total_claims_recovered: 142,
};

export const mockPayerMetrics = [
  { payer_name: 'UnitedHealthcare', success_rate: 72 },
  { payer_name: 'Aetna', success_rate: 58 },
  { payer_name: 'Blue Cross', success_rate: 65 },
  { payer_name: 'Cigna', success_rate: 49 },
  { payer_name: 'Humana', success_rate: 71 },
  { payer_name: 'Medicare', success_rate: 44 },
];

export const mockCategoryMetrics = [
  { category: 'Medical Necessity', total_denials: 85, appeals_submitted: 62, success_rate: 58, recovered_amount: 487200 },
  { category: 'Prior Authorization', total_denials: 52, appeals_submitted: 41, success_rate: 73, recovered_amount: 312500 },
  { category: 'Coding Error', total_denials: 38, appeals_submitted: 35, success_rate: 80, recovered_amount: 198400 },
  { category: 'Documentation', total_denials: 29, appeals_submitted: 18, success_rate: 44, recovered_amount: 96700 },
  { category: 'Other', total_denials: 14, appeals_submitted: 9, success_rate: 33, recovered_amount: 41200 },
];

export const mockTrends = months.map((m, i) => ({
  month: m,
  recovered_amount: 65000 + Math.round(Math.sin(i / 2) * 25000 + i * 5000),
  submitted_appeals: 18 + Math.round(Math.sin(i / 3) * 6 + i * 1.5),
}));

export const mockPayers = [
  'UnitedHealthcare', 'Aetna', 'Blue Cross Blue Shield', 'Cigna', 'Humana', 'Medicare',
];

export const mockProviders = [
  'Main Street Medical', 'Valley Orthopedics', 'Sunrise Family Practice', 'Lakeside Cardiology', 'Metro Surgical Associates',
];

export const mockExecutiveSummary = {
  total_denials: 218,
  overall_overturn_rate: 52,
  total_recovered: 1245800,
  avg_resolution_days: 18,
  preventable_rate: 41,
  volume_trend: months.map((m, i) => ({
    month: m,
    clinical: 8 + Math.round(Math.sin(i / 2) * 3),
    administrative: 6 + Math.round(Math.cos(i / 3) * 2),
    other: 2 + (i % 3),
  })),
  recovery_trend: months.map((m, i) => ({
    month: m,
    recovered_amount: 72000 + Math.round(i * 6500 + Math.sin(i) * 15000),
  })),
  top_denial_codes: [
    { name: 'CO-16', count: 34 },
    { name: 'CO-197', count: 28 },
    { name: 'CO-50', count: 22 },
    { name: 'PR-96', count: 17 },
    { name: 'CO-4', count: 14 },
  ],
  top_payers: [
    { name: 'UnitedHealthcare', count: 52 },
    { name: 'Aetna', count: 41 },
    { name: 'Blue Cross Blue Shield', count: 38 },
    { name: 'Cigna', count: 29 },
    { name: 'Humana', count: 24 },
  ],
};

export const mockDenialAnalysis = {
  admin_split: { count: 87, total_denied: 175823.73, recovered: 119560, overturn_rate: 68 },
  clinical_split: { count: 104, total_denied: 489210.50, recovered: 185900, overturn_rate: 38 },
  other_split: { count: 27, total_denied: 52400.00, recovered: 17290, overturn_rate: 33 },
  code_breakdown: [
    { code: 'CO-16', description: 'Claim/service lacks information needed for adjudication', count: 34, total_denied: 98200, recovered: 74630, overturn_rate: 76, classification: 'administrative', preventability: 'high' },
    { code: 'CO-197', description: 'Precertification/authorization/notification absent', count: 28, total_denied: 142500, recovered: 88350, overturn_rate: 62, classification: 'administrative', preventability: 'high' },
    { code: 'CO-50', description: 'Non-covered service based on payer guidelines', count: 22, total_denied: 187300, recovered: 58060, overturn_rate: 31, classification: 'clinical', preventability: 'low' },
    { code: 'PR-96', description: 'Non-covered charge(s) - patient liability', count: 17, total_denied: 64800, recovered: 15550, overturn_rate: 24, classification: 'clinical', preventability: 'medium' },
    { code: 'CO-4', description: 'Procedure code inconsistent with modifier or billing guidelines', count: 14, total_denied: 38900, recovered: 31900, overturn_rate: 82, classification: 'administrative', preventability: 'high' },
    { code: 'CO-29', description: 'Timely filing limit exceeded', count: 12, total_denied: 31200, recovered: 4680, overturn_rate: 15, classification: 'administrative', preventability: 'high' },
    { code: 'OA-23', description: 'Impact of prior payer adjudication', count: 10, total_denied: 28700, recovered: 12920, overturn_rate: 45, classification: 'clinical', preventability: 'medium' },
    { code: 'CO-11', description: 'Diagnosis inconsistent with procedure', count: 9, total_denied: 42100, recovered: 23160, overturn_rate: 55, classification: 'clinical', preventability: 'medium' },
    { code: 'PI-204', description: 'Service not authorized on this date of service', count: 8, total_denied: 19400, recovered: 13770, overturn_rate: 71, classification: 'administrative', preventability: 'high' },
    { code: 'CO-236', description: 'Level of care or service not appropriate', count: 7, total_denied: 89600, recovered: 25980, overturn_rate: 29, classification: 'clinical', preventability: 'low' },
  ],
  procedure_matrix: [
    { procedure_code: '99214', total: 18, medical_necessity: 8, prior_authorization: 4, coding_error: 3, documentation: 2, other: 1 },
    { procedure_code: '99213', total: 14, medical_necessity: 5, prior_authorization: 3, coding_error: 4, documentation: 1, other: 1 },
    { procedure_code: '27447', total: 11, medical_necessity: 7, prior_authorization: 2, coding_error: 0, documentation: 2, other: 0 },
    { procedure_code: '29881', total: 9, medical_necessity: 4, prior_authorization: 3, coding_error: 1, documentation: 1, other: 0 },
    { procedure_code: '43239', total: 7, medical_necessity: 5, prior_authorization: 1, coding_error: 0, documentation: 1, other: 0 },
  ],
  top_diagnosis_codes: [
    { code: 'M17.11 - Primary OA, right knee', count: 15 },
    { code: 'M54.5 - Low back pain', count: 12 },
    { code: 'I25.10 - Coronary artery disease', count: 10 },
    { code: 'E11.9 - Type 2 diabetes', count: 8 },
    { code: 'J44.1 - COPD with exacerbation', count: 7 },
    { code: 'M75.12 - Rotator cuff tear, left', count: 6 },
  ],
};

export const mockOverturnRates = (groupBy) => {
  const byPayer = [
    { name: 'UnitedHealthcare', total_appeals: 42, overturned: 30, overturn_rate: 71, avg_days_to_decision: 14, recovered_amount: 218400 },
    { name: 'Humana', total_appeals: 19, overturned: 13, overturn_rate: 68, avg_days_to_decision: 12, recovered_amount: 94200 },
    { name: 'Blue Cross Blue Shield', total_appeals: 31, overturned: 20, overturn_rate: 65, avg_days_to_decision: 21, recovered_amount: 175600 },
    { name: 'Aetna', total_appeals: 35, overturned: 20, overturn_rate: 57, avg_days_to_decision: 18, recovered_amount: 148300 },
    { name: 'Cigna', total_appeals: 24, overturned: 12, overturn_rate: 50, avg_days_to_decision: 25, recovered_amount: 87500 },
    { name: 'Medicare', total_appeals: 18, overturned: 8, overturn_rate: 44, avg_days_to_decision: 32, recovered_amount: 62400 },
  ];
  const byPractice = [
    { name: 'Sunrise Family Practice', total_appeals: 28, overturned: 21, overturn_rate: 75, extra: 'CO-16', recovered_amount: 142500 },
    { name: 'Valley Orthopedics', total_appeals: 34, overturned: 22, overturn_rate: 65, extra: 'CO-50', recovered_amount: 198700 },
    { name: 'Metro Surgical Associates', total_appeals: 22, overturned: 13, overturn_rate: 59, extra: 'CO-197', recovered_amount: 114200 },
    { name: 'Lakeside Cardiology', total_appeals: 19, overturned: 10, overturn_rate: 53, extra: 'CO-11', recovered_amount: 87600 },
    { name: 'Main Street Medical', total_appeals: 26, overturned: 11, overturn_rate: 42, extra: 'CO-16', recovered_amount: 73800 },
  ];
  const byCategory = [
    { name: 'Coding Error', total_appeals: 35, overturned: 28, overturn_rate: 80, extra: '82% vs 75%', recovered_amount: 198400 },
    { name: 'Prior Authorization', total_appeals: 41, overturned: 30, overturn_rate: 73, extra: '73% vs 68%', recovered_amount: 312500 },
    { name: 'Medical Necessity', total_appeals: 62, overturned: 36, overturn_rate: 58, extra: '58% vs 52%', recovered_amount: 487200 },
    { name: 'Documentation', total_appeals: 18, overturned: 8, overturn_rate: 44, extra: '44% vs 50%', recovered_amount: 96700 },
    { name: 'Other', total_appeals: 9, overturned: 3, overturn_rate: 33, extra: '33% vs 40%', recovered_amount: 41200 },
  ];
  const byCode = [
    { name: 'CO-4', total_appeals: 12, overturned: 10, overturn_rate: 83, extra: 'Administrative', recovered_amount: 38900 },
    { name: 'CO-16', total_appeals: 30, overturned: 23, overturn_rate: 77, extra: 'Administrative', recovered_amount: 98200 },
    { name: 'PI-204', total_appeals: 7, overturned: 5, overturn_rate: 71, extra: 'Administrative', recovered_amount: 19400 },
    { name: 'CO-197', total_appeals: 24, overturned: 15, overturn_rate: 63, extra: 'Administrative', recovered_amount: 142500 },
    { name: 'CO-11', total_appeals: 8, overturned: 4, overturn_rate: 50, extra: 'Clinical', recovered_amount: 42100 },
    { name: 'CO-50', total_appeals: 18, overturned: 6, overturn_rate: 33, extra: 'Clinical', recovered_amount: 187300 },
  ];
  const rowMap = { payer: byPayer, practice: byPractice, category: byCategory, code: byCode };
  return {
    overall_overturn_rate: 52,
    trend: months.map((m, i) => ({ month: m, overturn_rate: 42 + Math.round(Math.sin(i / 2) * 8 + i * 0.8) })),
    rows: rowMap[groupBy] || byPayer,
  };
};

export const mockPatterns = {
  actionable_insights: [
    'CO-16 (missing information) accounts for 16% of all denials and has a 76% overturn rate -- most of these are preventable with better claim scrubbing before submission.',
    'Valley Orthopedics has the highest clinical denial volume. Consider targeted documentation training for knee arthroplasty and shoulder procedure claims.',
    'Prior authorization denials from Aetna increased 35% in the last quarter. Review their updated PA requirements for imaging and surgical procedures.',
    'Administrative denials represent 40% of volume but 68% overturn rate -- prioritize these as quick wins to recover $175K+ currently at risk.',
    'UnitedHealthcare has the highest overturn rate (71%). Appeals against UHC should be prioritized as they have the best ROI.',
  ],
  preventability_trend: months.map((m, i) => ({ month: m, high: 5 + Math.round(Math.sin(i / 2) * 2), medium: 4 + (i % 3), low: 6 + Math.round(Math.cos(i / 3) * 2) })),
  recurring_patterns: [
    { code: 'CO-16', frequency: 34, trend: 'up', common_payer: 'Aetna', common_practice: 'Main Street Medical', suggested_action: 'Implement pre-submission claim validation checklist for required fields' },
    { code: 'CO-197', frequency: 28, trend: 'up', common_payer: 'UnitedHealthcare', common_practice: 'Valley Orthopedics', suggested_action: 'Automate prior auth verification before scheduling procedures' },
    { code: 'CO-50', frequency: 22, trend: 'stable', common_payer: 'Medicare', common_practice: 'Lakeside Cardiology', suggested_action: 'Review LCD/NCD criteria alignment for cardiology services' },
    { code: 'CO-4', frequency: 14, trend: 'down', common_payer: 'Cigna', common_practice: 'Sunrise Family Practice', suggested_action: 'Coding education on modifier usage -- recent training is showing results' },
  ],
  practice_insights: [
    { practice: 'Main Street Medical', total_denials: 42, preventable_count: 29, preventable_rate: 69, top_codes: ['CO-16', 'CO-197', 'CO-29'] },
    { practice: 'Valley Orthopedics', total_denials: 51, preventable_count: 18, preventable_rate: 35, top_codes: ['CO-50', 'CO-236', 'CO-11'] },
    { practice: 'Sunrise Family Practice', total_denials: 36, preventable_count: 22, preventable_rate: 61, top_codes: ['CO-4', 'CO-16', 'PR-96'] },
    { practice: 'Lakeside Cardiology', total_denials: 31, preventable_count: 10, preventable_rate: 32, top_codes: ['CO-50', 'OA-23'] },
    { practice: 'Metro Surgical Associates', total_denials: 28, preventable_count: 15, preventable_rate: 54, top_codes: ['CO-197', 'PI-204'] },
  ],
  payer_behavior: [
    { payer: 'UnitedHealthcare', total_denials: 52, overturn_rate: 71, top_codes: ['CO-16', 'CO-197'] },
    { payer: 'Aetna', total_denials: 41, overturn_rate: 57, top_codes: ['CO-16', 'CO-50', 'PR-96'] },
    { payer: 'Blue Cross Blue Shield', total_denials: 38, overturn_rate: 65, top_codes: ['CO-197', 'CO-4'] },
    { payer: 'Cigna', total_denials: 29, overturn_rate: 50, top_codes: ['CO-50', 'CO-11'] },
    { payer: 'Humana', total_denials: 24, overturn_rate: 68, top_codes: ['CO-16', 'PI-204'] },
    { payer: 'Medicare', total_denials: 18, overturn_rate: 44, top_codes: ['CO-50', 'CO-236'] },
  ],
};

export const mockOperationalKPIs = {
  avg_processing_days: 4.2,
  avg_letter_generation_seconds: 12,
  ai_auto_approval_rate: 68,
  appeals_per_week: 14,
  avg_review_hours: null,
  fte_capacity_gain: null,
  processing_trend: months.map((m, i) => ({ month: m, avg_days: 6.5 - i * 0.18 + Math.round(Math.sin(i / 2) * 0.8 * 10) / 10 })),
  throughput_trend: [
    { week: 'W1', count: 11 }, { week: 'W2', count: 14 }, { week: 'W3', count: 9 },
    { week: 'W4', count: 16 }, { week: 'W5', count: 13 }, { week: 'W6', count: 15 },
    { week: 'W7', count: 12 }, { week: 'W8', count: 17 }, { week: 'W9', count: 14 },
    { week: 'W10', count: 18 }, { week: 'W11', count: 15 }, { week: 'W12', count: 16 },
  ],
};

// ── Practice Scorecard Mock Data ────────────────────────────────

const practiceDB = {
  'Main Street Medical': {
    total_denials: 42, total_denied: 198400, total_recovered: 73800, overturn_rate: 42, preventable_rate: 69, avg_resolution_days: 21,
    admin_split: { count: 29, total_denied: 82100, recovered: 56200, overturn_rate: 68 },
    clinical_split: { count: 13, total_denied: 116300, recovered: 17600, overturn_rate: 15 },
    top_denial_codes: [
      { code: 'CO-16', description: 'Claim/service lacks information needed for adjudication', count: 12, total_denied: 34800, recovered: 26400, overturn_rate: 76, classification: 'administrative', preventability: 'high' },
      { code: 'CO-197', description: 'Precertification/authorization/notification absent', count: 9, total_denied: 41200, recovered: 25500, overturn_rate: 62, classification: 'administrative', preventability: 'high' },
      { code: 'CO-29', description: 'Timely filing limit exceeded', count: 8, total_denied: 22100, recovered: 3300, overturn_rate: 15, classification: 'administrative', preventability: 'high' },
      { code: 'CO-50', description: 'Non-covered service based on payer guidelines', count: 5, total_denied: 42800, recovered: 6400, overturn_rate: 15, classification: 'clinical', preventability: 'low' },
      { code: 'PR-96', description: 'Non-covered charge(s) - patient liability', count: 4, total_denied: 18200, recovered: 4400, overturn_rate: 24, classification: 'clinical', preventability: 'medium' },
    ],
    top_procedures: [
      { procedure_code: '99214', total: 10, medical_necessity: 4, prior_authorization: 3, coding_error: 2, documentation: 1, other: 0 },
      { procedure_code: '99213', total: 8, medical_necessity: 2, prior_authorization: 2, coding_error: 3, documentation: 0, other: 1 },
      { procedure_code: '72148', total: 5, medical_necessity: 3, prior_authorization: 1, coding_error: 0, documentation: 1, other: 0 },
    ],
    payer_breakdown: [
      { name: 'Aetna', total_appeals: 14, overturned: 6, overturn_rate: 43, avg_days_to_decision: 19, recovered_amount: 28100 },
      { name: 'UnitedHealthcare', total_appeals: 11, overturned: 5, overturn_rate: 45, avg_days_to_decision: 15, recovered_amount: 22400 },
      { name: 'Cigna', total_appeals: 8, overturned: 3, overturn_rate: 38, avg_days_to_decision: 24, recovered_amount: 12800 },
      { name: 'Medicare', total_appeals: 5, overturned: 1, overturn_rate: 20, avg_days_to_decision: 30, recovered_amount: 5200 },
    ],
    denial_trend: months.map((m, i) => ({ month: m, clinical: 1 + (i % 2), administrative: 2 + Math.round(Math.sin(i / 2)), other: i % 3 === 0 ? 1 : 0 })),
    actionable_insights: [
      'CO-16 accounts for 29% of denials at this practice -- implement a pre-submission checklist to verify all required fields before claims go out.',
      'Timely filing denials (CO-29) cost $22K with only 15% overturn rate. These are almost never recoverable -- focus on preventing them with automated deadline tracking.',
      '69% of denials here are preventable (administrative). A focused billing staff training session could reduce denial volume by 30-40%.',
    ],
  },
  'Valley Orthopedics': {
    total_denials: 51, total_denied: 412600, total_recovered: 198700, overturn_rate: 65, preventable_rate: 35, avg_resolution_days: 16,
    admin_split: { count: 14, total_denied: 58200, recovered: 42100, overturn_rate: 72 },
    clinical_split: { count: 37, total_denied: 354400, recovered: 156600, overturn_rate: 62 },
    top_denial_codes: [
      { code: 'CO-50', description: 'Non-covered service based on payer guidelines', count: 14, total_denied: 148200, recovered: 68600, overturn_rate: 46, classification: 'clinical', preventability: 'low' },
      { code: 'CO-236', description: 'Level of care or service not appropriate', count: 10, total_denied: 92400, recovered: 42800, overturn_rate: 46, classification: 'clinical', preventability: 'low' },
      { code: 'CO-11', description: 'Diagnosis inconsistent with procedure', count: 7, total_denied: 38900, recovered: 27200, overturn_rate: 70, classification: 'clinical', preventability: 'medium' },
      { code: 'CO-16', description: 'Claim/service lacks information needed for adjudication', count: 6, total_denied: 18400, recovered: 15600, overturn_rate: 85, classification: 'administrative', preventability: 'high' },
      { code: 'CO-197', description: 'Precertification/authorization/notification absent', count: 5, total_denied: 42100, recovered: 28400, overturn_rate: 67, classification: 'administrative', preventability: 'high' },
    ],
    top_procedures: [
      { procedure_code: '27447', total: 14, medical_necessity: 9, prior_authorization: 3, coding_error: 0, documentation: 2, other: 0 },
      { procedure_code: '29881', total: 11, medical_necessity: 5, prior_authorization: 4, coding_error: 1, documentation: 1, other: 0 },
      { procedure_code: '27130', total: 8, medical_necessity: 6, prior_authorization: 1, coding_error: 0, documentation: 1, other: 0 },
    ],
    payer_breakdown: [
      { name: 'Blue Cross Blue Shield', total_appeals: 16, overturned: 11, overturn_rate: 69, avg_days_to_decision: 18, recovered_amount: 72400 },
      { name: 'UnitedHealthcare', total_appeals: 13, overturned: 9, overturn_rate: 69, avg_days_to_decision: 13, recovered_amount: 58200 },
      { name: 'Aetna', total_appeals: 10, overturned: 6, overturn_rate: 60, avg_days_to_decision: 17, recovered_amount: 38600 },
      { name: 'Humana', total_appeals: 7, overturned: 5, overturn_rate: 71, avg_days_to_decision: 11, recovered_amount: 24800 },
    ],
    denial_trend: months.map((m, i) => ({ month: m, clinical: 3 + Math.round(Math.sin(i / 2) * 1.5), administrative: 1 + (i % 2), other: i % 4 === 0 ? 1 : 0 })),
    actionable_insights: [
      'Strong overturn rate (65%) -- this practice fights clinical denials effectively. Focus appeals resources here for highest dollar recovery.',
      'CO-50 and CO-236 drive most clinical denials for orthopedic procedures. Strengthen medical necessity documentation with specific functional limitation scores.',
      'Low preventable rate (35%) means most denials here are legitimate payer disputes, not billing errors. The right strategy is better appeal letters, not process changes.',
    ],
  },
  'Sunrise Family Practice': {
    total_denials: 36, total_denied: 124800, total_recovered: 142500, overturn_rate: 75, preventable_rate: 61, avg_resolution_days: 14,
    admin_split: { count: 22, total_denied: 68400, recovered: 98200, overturn_rate: 82 },
    clinical_split: { count: 14, total_denied: 56400, recovered: 44300, overturn_rate: 64 },
    top_denial_codes: [
      { code: 'CO-4', description: 'Procedure code inconsistent with modifier or billing guidelines', count: 10, total_denied: 28600, recovered: 24800, overturn_rate: 87, classification: 'administrative', preventability: 'high' },
      { code: 'CO-16', description: 'Claim/service lacks information needed for adjudication', count: 8, total_denied: 22400, recovered: 18700, overturn_rate: 83, classification: 'administrative', preventability: 'high' },
      { code: 'PR-96', description: 'Non-covered charge(s) - patient liability', count: 6, total_denied: 21800, recovered: 14200, overturn_rate: 65, classification: 'clinical', preventability: 'medium' },
      { code: 'CO-50', description: 'Non-covered service based on payer guidelines', count: 5, total_denied: 28200, recovered: 12600, overturn_rate: 45, classification: 'clinical', preventability: 'low' },
      { code: 'CO-197', description: 'Precertification/authorization/notification absent', count: 4, total_denied: 14200, recovered: 11800, overturn_rate: 83, classification: 'administrative', preventability: 'high' },
    ],
    top_procedures: [
      { procedure_code: '99214', total: 12, medical_necessity: 4, prior_authorization: 2, coding_error: 4, documentation: 1, other: 1 },
      { procedure_code: '99213', total: 9, medical_necessity: 2, prior_authorization: 2, coding_error: 3, documentation: 1, other: 1 },
      { procedure_code: '99215', total: 5, medical_necessity: 3, prior_authorization: 1, coding_error: 1, documentation: 0, other: 0 },
    ],
    payer_breakdown: [
      { name: 'Cigna', total_appeals: 12, overturned: 10, overturn_rate: 83, avg_days_to_decision: 12, recovered_amount: 52400 },
      { name: 'Aetna', total_appeals: 9, overturned: 7, overturn_rate: 78, avg_days_to_decision: 14, recovered_amount: 38600 },
      { name: 'UnitedHealthcare', total_appeals: 8, overturned: 6, overturn_rate: 75, avg_days_to_decision: 13, recovered_amount: 32400 },
      { name: 'Medicare', total_appeals: 4, overturned: 2, overturn_rate: 50, avg_days_to_decision: 28, recovered_amount: 12800 },
    ],
    denial_trend: months.map((m, i) => ({ month: m, clinical: 1 + (i % 2), administrative: 2 + Math.round(Math.cos(i / 3)), other: i % 5 === 0 ? 1 : 0 })),
    actionable_insights: [
      'Best overturn rate across all practices (75%). This team writes excellent appeals -- consider sharing their approach as a template for others.',
      'CO-4 (modifier issues) is the top code but easily fixable with a coding reference guide. Quick win to eliminate 28% of denials.',
      '61% preventable rate is moderate. A short training on modifier usage and PA requirements would cut admin denials significantly.',
    ],
  },
  'Lakeside Cardiology': {
    total_denials: 31, total_denied: 287400, total_recovered: 87600, overturn_rate: 53, preventable_rate: 32, avg_resolution_days: 22,
    admin_split: { count: 8, total_denied: 34200, recovered: 24800, overturn_rate: 73 },
    clinical_split: { count: 23, total_denied: 253200, recovered: 62800, overturn_rate: 47 },
    top_denial_codes: [
      { code: 'CO-50', description: 'Non-covered service based on payer guidelines', count: 10, total_denied: 124600, recovered: 32400, overturn_rate: 26, classification: 'clinical', preventability: 'low' },
      { code: 'OA-23', description: 'Impact of prior payer adjudication', count: 7, total_denied: 58200, recovered: 24800, overturn_rate: 43, classification: 'clinical', preventability: 'medium' },
      { code: 'CO-11', description: 'Diagnosis inconsistent with procedure', count: 5, total_denied: 42100, recovered: 18400, overturn_rate: 44, classification: 'clinical', preventability: 'medium' },
      { code: 'CO-16', description: 'Claim/service lacks information needed for adjudication', count: 4, total_denied: 12800, recovered: 10200, overturn_rate: 80, classification: 'administrative', preventability: 'high' },
      { code: 'CO-236', description: 'Level of care or service not appropriate', count: 3, total_denied: 38200, recovered: 8400, overturn_rate: 22, classification: 'clinical', preventability: 'low' },
    ],
    top_procedures: [
      { procedure_code: '93306', total: 9, medical_necessity: 6, prior_authorization: 2, coding_error: 0, documentation: 1, other: 0 },
      { procedure_code: '93458', total: 7, medical_necessity: 5, prior_authorization: 1, coding_error: 0, documentation: 1, other: 0 },
      { procedure_code: '33533', total: 5, medical_necessity: 4, prior_authorization: 1, coding_error: 0, documentation: 0, other: 0 },
    ],
    payer_breakdown: [
      { name: 'Medicare', total_appeals: 10, overturned: 4, overturn_rate: 40, avg_days_to_decision: 30, recovered_amount: 28400 },
      { name: 'Blue Cross Blue Shield', total_appeals: 8, overturned: 5, overturn_rate: 63, avg_days_to_decision: 20, recovered_amount: 26800 },
      { name: 'Aetna', total_appeals: 7, overturned: 3, overturn_rate: 43, avg_days_to_decision: 22, recovered_amount: 18200 },
      { name: 'UnitedHealthcare', total_appeals: 4, overturned: 3, overturn_rate: 75, avg_days_to_decision: 14, recovered_amount: 12400 },
    ],
    denial_trend: months.map((m, i) => ({ month: m, clinical: 2 + Math.round(Math.sin(i / 3)), administrative: i % 3 === 0 ? 1 : 0, other: i % 6 === 0 ? 1 : 0 })),
    actionable_insights: [
      'Medicare denials have a 40% overturn rate with 30-day avg decision time. Consider peer-to-peer reviews for cardiology cases to improve success.',
      'CO-50 denials are the biggest dollar exposure ($124K denied, only $32K recovered). Review payer coverage policies for echocardiography and catheterization.',
      'Low preventable rate (32%) -- most denials are legitimate clinical disputes. Invest in stronger clinical evidence packages for appeals.',
    ],
  },
  'Metro Surgical Associates': {
    total_denials: 28, total_denied: 342800, total_recovered: 114200, overturn_rate: 59, preventable_rate: 54, avg_resolution_days: 17,
    admin_split: { count: 15, total_denied: 98400, recovered: 68200, overturn_rate: 69 },
    clinical_split: { count: 13, total_denied: 244400, recovered: 46000, overturn_rate: 47 },
    top_denial_codes: [
      { code: 'CO-197', description: 'Precertification/authorization/notification absent', count: 8, total_denied: 68400, recovered: 42800, overturn_rate: 63, classification: 'administrative', preventability: 'high' },
      { code: 'PI-204', description: 'Service not authorized on this date of service', count: 5, total_denied: 32600, recovered: 24200, overturn_rate: 74, classification: 'administrative', preventability: 'high' },
      { code: 'CO-50', description: 'Non-covered service based on payer guidelines', count: 5, total_denied: 98200, recovered: 18400, overturn_rate: 19, classification: 'clinical', preventability: 'low' },
      { code: 'CO-236', description: 'Level of care or service not appropriate', count: 4, total_denied: 82400, recovered: 14600, overturn_rate: 18, classification: 'clinical', preventability: 'low' },
      { code: 'CO-16', description: 'Claim/service lacks information needed for adjudication', count: 3, total_denied: 12400, recovered: 10200, overturn_rate: 82, classification: 'administrative', preventability: 'high' },
    ],
    top_procedures: [
      { procedure_code: '43239', total: 8, medical_necessity: 5, prior_authorization: 2, coding_error: 0, documentation: 1, other: 0 },
      { procedure_code: '47562', total: 6, medical_necessity: 3, prior_authorization: 2, coding_error: 0, documentation: 1, other: 0 },
      { procedure_code: '44120', total: 4, medical_necessity: 3, prior_authorization: 1, coding_error: 0, documentation: 0, other: 0 },
    ],
    payer_breakdown: [
      { name: 'UnitedHealthcare', total_appeals: 9, overturned: 6, overturn_rate: 67, avg_days_to_decision: 14, recovered_amount: 38400 },
      { name: 'Blue Cross Blue Shield', total_appeals: 7, overturned: 4, overturn_rate: 57, avg_days_to_decision: 19, recovered_amount: 28600 },
      { name: 'Humana', total_appeals: 6, overturned: 4, overturn_rate: 67, avg_days_to_decision: 12, recovered_amount: 26800 },
      { name: 'Aetna', total_appeals: 4, overturned: 2, overturn_rate: 50, avg_days_to_decision: 20, recovered_amount: 14200 },
    ],
    denial_trend: months.map((m, i) => ({ month: m, clinical: 1 + (i % 2), administrative: 1 + Math.round(Math.sin(i / 2)), other: i % 4 === 0 ? 1 : 0 })),
    actionable_insights: [
      'CO-197 (missing prior auth) is the top denial code. Implement an automated PA verification step in the surgical scheduling workflow.',
      'PI-204 denials have a 74% overturn rate -- these are easy wins where the auth existed but wasn\'t linked correctly. Fix the submission process.',
      '54% preventable rate with strong admin overturn rates (69%). Tightening the PA workflow alone could prevent 46% of denials at this practice.',
    ],
  },
};

export const mockPracticeSummaries = Object.entries(practiceDB).map(([name, d]) => ({
  name,
  total_denials: d.total_denials,
  total_denied: d.total_denied,
  total_recovered: d.total_recovered,
  overturn_rate: d.overturn_rate,
  preventable_rate: d.preventable_rate,
}));

export const mockPracticeScorecard = (name) => {
  const data = practiceDB[name];
  if (!data) return null;
  return { practice_name: name, ...data };
};

export const mockPracticeComparison = (names) => {
  return names.map((n) => mockPracticeScorecard(n)).filter(Boolean);
};
