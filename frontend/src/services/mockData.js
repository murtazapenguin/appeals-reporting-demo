const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

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
  admin_split: { count: 87, total_denied: 175823.73, overturn_rate: 68 },
  clinical_split: { count: 104, total_denied: 489210.50, overturn_rate: 38 },
  other_split: { count: 27, total_denied: 52400.00, overturn_rate: 33 },
  code_breakdown: [
    { code: 'CO-16', description: 'Claim/service lacks information needed for adjudication', count: 34, total_denied: 98200, overturn_rate: 76, classification: 'administrative', preventability: 'high' },
    { code: 'CO-197', description: 'Precertification/authorization/notification absent', count: 28, total_denied: 142500, overturn_rate: 62, classification: 'administrative', preventability: 'high' },
    { code: 'CO-50', description: 'Non-covered service based on payer guidelines', count: 22, total_denied: 187300, overturn_rate: 31, classification: 'clinical', preventability: 'low' },
    { code: 'PR-96', description: 'Non-covered charge(s) - patient liability', count: 17, total_denied: 64800, overturn_rate: 24, classification: 'clinical', preventability: 'medium' },
    { code: 'CO-4', description: 'Procedure code inconsistent with modifier or billing guidelines', count: 14, total_denied: 38900, overturn_rate: 82, classification: 'administrative', preventability: 'high' },
    { code: 'CO-29', description: 'Timely filing limit exceeded', count: 12, total_denied: 31200, overturn_rate: 15, classification: 'administrative', preventability: 'high' },
    { code: 'OA-23', description: 'Impact of prior payer adjudication', count: 10, total_denied: 28700, overturn_rate: 45, classification: 'clinical', preventability: 'medium' },
    { code: 'CO-11', description: 'Diagnosis inconsistent with procedure', count: 9, total_denied: 42100, overturn_rate: 55, classification: 'clinical', preventability: 'medium' },
    { code: 'PI-204', description: 'Service not authorized on this date of service', count: 8, total_denied: 19400, overturn_rate: 71, classification: 'administrative', preventability: 'high' },
    { code: 'CO-236', description: 'Level of care or service not appropriate', count: 7, total_denied: 89600, overturn_rate: 29, classification: 'clinical', preventability: 'low' },
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
    trend: months.map((m, i) => ({
      month: m,
      overturn_rate: 42 + Math.round(Math.sin(i / 2) * 8 + i * 0.8),
    })),
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
  preventability_trend: months.map((m, i) => ({
    month: m,
    high: 5 + Math.round(Math.sin(i / 2) * 2),
    medium: 4 + (i % 3),
    low: 6 + Math.round(Math.cos(i / 3) * 2),
  })),
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
  processing_trend: months.map((m, i) => ({
    month: m,
    avg_days: 6.5 - i * 0.18 + Math.round(Math.sin(i / 2) * 0.8 * 10) / 10,
  })),
  throughput_trend: [
    { week: 'W1', count: 11 }, { week: 'W2', count: 14 }, { week: 'W3', count: 9 },
    { week: 'W4', count: 16 }, { week: 'W5', count: 13 }, { week: 'W6', count: 15 },
    { week: 'W7', count: 12 }, { week: 'W8', count: 17 }, { week: 'W9', count: 14 },
    { week: 'W10', count: 18 }, { week: 'W11', count: 15 }, { week: 'W12', count: 16 },
  ],
};
