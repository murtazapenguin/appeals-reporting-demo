import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckIcon, ExclamationTriangleIcon, CloudArrowUpIcon, DocumentIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { denialsAPI, medicalPoliciesAPI, documentsAPI, questionnairesAPI, referenceDataAPI } from '../services/api';

// Common CPT codes with descriptions
const CPT_CODES = [
  { code: '27447', description: 'Total Knee Arthroplasty', category: 'Orthopedic Surgery' },
  { code: '27130', description: 'Total Hip Arthroplasty', category: 'Orthopedic Surgery' },
  { code: '99285', description: 'ED Visit Level 5 (High Severity)', category: 'Emergency Medicine' },
  { code: '99284', description: 'ED Visit Level 4 (Moderate-High)', category: 'Emergency Medicine' },
  { code: '99283', description: 'ED Visit Level 3 (Moderate)', category: 'Emergency Medicine' },
  { code: '72148', description: 'MRI Lumbar Spine Without Contrast', category: 'Radiology' },
  { code: '72141', description: 'MRI Cervical Spine Without Contrast', category: 'Radiology' },
  { code: '72149', description: 'MRI Lumbar Spine With Contrast', category: 'Radiology' },
  { code: '29881', description: 'Knee Arthroscopy with Meniscectomy', category: 'Orthopedic Surgery' },
  { code: '63047', description: 'Lumbar Laminectomy', category: 'Spine Surgery' },
  { code: '63030', description: 'Lumbar Discectomy', category: 'Spine Surgery' },
  { code: '22551', description: 'Cervical Fusion', category: 'Spine Surgery' },
  { code: '27446', description: 'Partial Knee Replacement', category: 'Orthopedic Surgery' },
  { code: '20610', description: 'Joint Injection (Large)', category: 'Pain Management' },
  { code: '64483', description: 'Epidural Steroid Injection', category: 'Pain Management' },
];

const NewDenialWizard = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isUploadingDocs, setIsUploadingDocs] = useState(false);
  const [payers, setPayers] = useState([]);
  const [providers, setProviders] = useState([]);
  const [allPolicies, setAllPolicies] = useState([]);
  const [allQuestionnaires, setAllQuestionnaires] = useState([]);
  const [availableCPTCodes, setAvailableCPTCodes] = useState([]);
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const [formData, setFormData] = useState({
    // Step 1: Basic Info
    claim_number: '',
    patient_name: '',
    patient_id: '',
    patient_dob: '',
    provider_name: '',
    provider_id: '',
    // Step 2: Payer
    payer_name: '',
    payer_id: '',
    policy_number: '',
    group_number: '',
    // Step 3: Denial Details
    service_date: '',
    denial_date: '',
    denial_code: '',
    denial_category: '',
    denial_reason: '',
    // Step 4: Clinical & Financial Info
    claim_amount: '',
    paid_amount: 0,
    denied_amount: 0,
    procedure_code: '',
    diagnosis_codes: '',
    service_description: '',
    // Step 5: Notes
    internal_notes: '',
    priority: 'normal',
    // Step 6: Upload Documents
    // Step 7: Review
  });

  // Fetch payers, policies, and questionnaires
  useEffect(() => {
    const fetchPayersAndPolicies = async () => {
      try {
        const [policies, questionnaires] = await Promise.all([
          medicalPoliciesAPI.getAll(),
          questionnairesAPI.getAll().catch(() => []),
        ]);
        setAllPolicies(policies);
        setAllQuestionnaires(questionnaires);

        // Extract unique payers
        const uniquePayers = [];
        const seenPayerIds = new Set();
        policies.forEach(policy => {
          if (!seenPayerIds.has(policy.payer_id)) {
            seenPayerIds.add(policy.payer_id);
            uniquePayers.push({
              id: policy.payer_id,
              name: policy.payer_name
            });
          }
        });
        setPayers(uniquePayers);
      } catch (error) {
        console.error('Failed to fetch payers and policies:', error);
        setPayers([
          { id: 'PAY-BCBS', name: 'Blue Cross Blue Shield' },
          { id: 'PAY-UHC', name: 'United Healthcare' },
          { id: 'PAY-AETNA', name: 'Aetna' },
          { id: 'PAY-CIGNA', name: 'Cigna' },
          { id: 'PAY-HUMANA', name: 'Humana' },
        ]);
      }
    };
    fetchPayersAndPolicies();

    // Fetch providers from reference data
    referenceDataAPI.getProviders()
      .then(setProviders)
      .catch(() => setProviders([]));
  }, []);

  // Filter CPT codes based on selected payer + merge questionnaire CPTs
  useEffect(() => {
    if (formData.payer_id && (allPolicies.length > 0 || allQuestionnaires.length > 0)) {
      const seenCPTs = new Set();
      const uniqueCPTs = [];

      // CPT codes from payer-specific medical policies
      const payerPolicies = allPolicies.filter(p => p.payer_id === formData.payer_id);
      payerPolicies.forEach(policy => {
        if (!seenCPTs.has(policy.cpt_code)) {
          seenCPTs.add(policy.cpt_code);
          uniqueCPTs.push({
            code: policy.cpt_code,
            description: policy.procedure_name,
            category: getCategoryFromProcedureName(policy.procedure_name)
          });
        }
      });

      // Merge CPT codes from questionnaires (payer-agnostic)
      allQuestionnaires.forEach(q => {
        (q.cpt_codes || []).forEach(code => {
          if (!seenCPTs.has(code)) {
            seenCPTs.add(code);
            uniqueCPTs.push({
              code,
              description: q.guideline_name,
              category: getCategoryFromProcedureName(q.guideline_name)
            });
          }
        });
      });

      setAvailableCPTCodes(uniqueCPTs);
    } else {
      setAvailableCPTCodes([]);
    }
  }, [formData.payer_id, allPolicies, allQuestionnaires]);

  // Auto-calculate denied_amount when claim or paid amount changes
  useEffect(() => {
    const claim = parseFloat(formData.claim_amount) || 0;
    const paid = parseFloat(formData.paid_amount) || 0;
    const denied = Math.max(0, claim - paid);

    setFormData(prev => ({ ...prev, denied_amount: denied }));
  }, [formData.claim_amount, formData.paid_amount]);

  // Handle provider selection
  const handleProviderChange = (providerName) => {
    const provider = providers.find(p => p.name === providerName);
    if (provider) {
      setFormData({
        ...formData,
        provider_name: provider.name,
        provider_id: provider.name,
      });
    } else {
      setFormData({
        ...formData,
        provider_id: '',
        provider_name: '',
      });
    }
  };

  // Handle payer selection
  const handlePayerChange = (payerId) => {
    const payer = payers.find(p => p.id === payerId);
    if (payer) {
      setFormData({
        ...formData,
        payer_id: payer.id,
        payer_name: payer.name,
      });
    } else {
      setFormData({
        ...formData,
        payer_id: '',
        payer_name: '',
      });
    }
  };

  // Helper function to categorize procedures
  const getCategoryFromProcedureName = (name) => {
    if (!name) return 'Other';
    const lowerName = name.toLowerCase();
    if (lowerName.includes('knee') || lowerName.includes('hip') || lowerName.includes('joint')) {
      return 'Orthopedic Surgery';
    } else if (lowerName.includes('spine') || lowerName.includes('laminectomy') || lowerName.includes('fusion')) {
      return 'Spine Surgery';
    } else if (lowerName.includes('mri') || lowerName.includes('ct') || lowerName.includes('x-ray')) {
      return 'Radiology';
    } else if (lowerName.includes('ed visit') || lowerName.includes('emergency')) {
      return 'Emergency Medicine';
    } else if (lowerName.includes('injection') || lowerName.includes('epidural')) {
      return 'Pain Management';
    }
    return 'Other';
  };

  // Handle CPT code selection
  const handleCPTChange = (cptCode) => {
    const cpt = availableCPTCodes.find(c => c.code === cptCode);
    if (cpt) {
      setFormData({
        ...formData,
        procedure_code: cpt.code,
        service_description: cpt.description,
      });
    } else {
      setFormData({
        ...formData,
        procedure_code: cptCode,
      });
    }
  };

  // Document upload handlers
  const handleDocumentUpload = async (files) => {
    const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
    const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png'];

    const validFiles = Array.from(files).filter(file => {
      if (!ALLOWED_TYPES.includes(file.type)) {
        alert(`${file.name}: Invalid file type. Only PDF, JPG, PNG allowed.`);
        return false;
      }

      if (file.size > MAX_FILE_SIZE) {
        alert(`${file.name}: File too large. Max 10MB.`);
        return false;
      }

      return true;
    });

    const newDocs = validFiles.map(file => ({
      id: Date.now() + Math.random(),
      file: file,
      document_type: 'medical_records',
      document_date: new Date().toISOString().split('T')[0],
      name: file.name,
      size: file.size
    }));

    setUploadedDocuments([...uploadedDocuments, ...newDocs]);
  };

  const handleRemoveDocument = (docId) => {
    setUploadedDocuments(uploadedDocuments.filter(d => d.id !== docId));
  };

  const handleDocTypeChange = (docId, newType) => {
    setUploadedDocuments(uploadedDocuments.map(d =>
      d.id === docId ? { ...d, document_type: newType } : d
    ));
  };

  const handleDocDateChange = (docId, newDate) => {
    setUploadedDocuments(uploadedDocuments.map(d =>
      d.id === docId ? { ...d, document_date: newDate } : d
    ));
  };

  const getDocumentTypeLabel = (type) => {
    const labels = {
      'medical_records': 'Medical Records',
      'imaging': 'Imaging',
      'lab_results': 'Lab Results',
      'operative_report': 'Operative Report',
      'consultation': 'Consultation',
      'therapy_notes': 'Therapy Notes',
      'other': 'Other'
    };
    return labels[type] || type;
  };

  const steps = [
    { number: 1, name: 'Basic Info' },
    { number: 2, name: 'Payer' },
    { number: 3, name: 'Denial Details' },
    { number: 4, name: 'Clinical & Financial' },
    { number: 5, name: 'Notes' },
    { number: 6, name: 'Review' }
  ];

  const updateFormData = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleNext = () => {
    // Validation for Step 4
    if (currentStep === 4) {
      const claim = parseFloat(formData.claim_amount) || 0;
      const paid = parseFloat(formData.paid_amount) || 0;

      if (claim <= 0) {
        alert('Claim amount must be greater than $0');
        return;
      }

      if (paid < 0) {
        alert('Paid amount cannot be negative');
        return;
      }

      if (paid > claim) {
        alert('Paid amount cannot exceed claim amount');
        return;
      }
    }

    if (currentStep < 6) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      setIsSubmitting(true);

      // Create the denial and navigate to detail page
      const newDenial = await denialsAPI.create(formData);
      navigate(`/denials/${newDenial.id}`);

    } catch (error) {
      console.error('Failed to create denial:', error);
      alert('Failed to create denial. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Claim Number *
                </label>
                <input
                  type="text"
                  value={formData.claim_number}
                  onChange={(e) => updateFormData('claim_number', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Patient Name *
                </label>
                <input
                  type="text"
                  value={formData.patient_name}
                  onChange={(e) => updateFormData('patient_name', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Patient ID *
                </label>
                <input
                  type="text"
                  value={formData.patient_id}
                  onChange={(e) => updateFormData('patient_id', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Patient Date of Birth
                </label>
                <input
                  type="date"
                  value={formData.patient_dob}
                  onChange={(e) => updateFormData('patient_dob', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Provider *
                </label>
                <select
                  value={formData.provider_name}
                  onChange={(e) => handleProviderChange(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d] bg-white"
                  required
                >
                  <option value="">Select Provider</option>
                  {providers.map((provider) => (
                    <option key={provider.name} value={provider.name}>
                      {provider.name}{provider.practice ? ` - ${provider.practice}` : ''}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Payer Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Insurance Payer *
                </label>
                <select
                  value={formData.payer_id}
                  onChange={(e) => handlePayerChange(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d] bg-white"
                  required
                >
                  <option value="">Select Payer</option>
                  {payers.map((payer) => (
                    <option key={payer.id} value={payer.id}>
                      {payer.name}
                    </option>
                  ))}
                </select>
                {formData.payer_id && (
                  <p className="text-xs text-gray-500 mt-1">
                    Payer ID: {formData.payer_id}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Policy Number
                </label>
                <input
                  type="text"
                  value={formData.policy_number}
                  onChange={(e) => updateFormData('policy_number', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  placeholder="e.g., POL-123456"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Group Number
                </label>
                <input
                  type="text"
                  value={formData.group_number || ''}
                  onChange={(e) => updateFormData('group_number', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  placeholder="e.g., GRP-1234"
                />
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Denial Details</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Service Date *
                </label>
                <input
                  type="date"
                  value={formData.service_date}
                  onChange={(e) => updateFormData('service_date', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Denial Date *
                </label>
                <input
                  type="date"
                  value={formData.denial_date}
                  onChange={(e) => updateFormData('denial_date', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Denial Code
                </label>
                <input
                  type="text"
                  value={formData.denial_code}
                  onChange={(e) => updateFormData('denial_code', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Denial Category *
                </label>
                <select
                  value={formData.denial_category}
                  onChange={(e) => updateFormData('denial_category', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  required
                >
                  <option value="">Select Category</option>
                  <option value="Medical Necessity">Medical Necessity</option>
                  <option value="Prior Authorization">Prior Authorization</option>
                  <option value="Coding Error">Coding Error</option>
                  <option value="Documentation">Documentation</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Denial Reason
                </label>
                <textarea
                  value={formData.denial_reason}
                  onChange={(e) => updateFormData('denial_reason', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  rows="3"
                />
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Clinical & Financial Information</h2>

            {/* Financial Fields */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Total Claim Amount ($) *
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-3 text-gray-500">$</span>
                  <input
                    type="number"
                    value={formData.claim_amount}
                    onChange={(e) => updateFormData('claim_amount', e.target.value)}
                    className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                    placeholder="0.00"
                    required
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Amount submitted to insurance</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount Paid ($)
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-3 text-gray-500">$</span>
                  <input
                    type="number"
                    value={formData.paid_amount}
                    onChange={(e) => updateFormData('paid_amount', e.target.value)}
                    className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                    placeholder="0.00"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Amount insurance paid (if partial)</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Denied Amount ($)
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-3 text-gray-500">$</span>
                  <input
                    type="number"
                    value={formData.denied_amount}
                    readOnly
                    className="w-full pl-8 pr-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-700 cursor-not-allowed"
                    placeholder="0.00"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">Auto-calculated: Claim - Paid</p>
              </div>
            </div>

            {/* Warning for fully paid claims */}
            {formData.denied_amount === 0 && formData.claim_amount > 0 && (
              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <div className="flex items-start gap-3">
                  <ExclamationTriangleIcon className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-amber-900">Fully Paid Claim</p>
                    <p className="text-sm text-amber-700 mt-1">
                      The denied amount is $0. This appears to be a fully paid claim.
                      Are you sure this is a denial?
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Clinical Fields */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Procedure Code (CPT) *
                </label>
                <select
                  value={formData.procedure_code}
                  onChange={(e) => handleCPTChange(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d] bg-white"
                  required
                  disabled={!formData.payer_id}
                >
                  <option value="">
                    {!formData.payer_id ? 'Select Payer First' : 'Select CPT Code'}
                  </option>
                  {formData.payer_id && (() => {
                    // Group CPT codes by category
                    const categories = {};
                    availableCPTCodes.forEach(cpt => {
                      if (!categories[cpt.category]) {
                        categories[cpt.category] = [];
                      }
                      categories[cpt.category].push(cpt);
                    });

                    return Object.keys(categories).sort().map(category => (
                      <optgroup key={category} label={category}>
                        {categories[category].map(cpt => (
                          <option key={cpt.code} value={cpt.code}>
                            {cpt.code} - {cpt.description}
                          </option>
                        ))}
                      </optgroup>
                    ));
                  })()}
                </select>
                {!formData.payer_id && (
                  <p className="text-xs text-gray-500 mt-1">
                    Please select a payer first to see available procedures
                  </p>
                )}
                {formData.payer_id && availableCPTCodes.length === 0 && (
                  <p className="text-xs text-amber-600 mt-1">
                    No procedures available for this payer
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Diagnosis Codes (ICD-10) *
                </label>
                <input
                  type="text"
                  value={formData.diagnosis_codes}
                  onChange={(e) => updateFormData('diagnosis_codes', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  placeholder="e.g., M54.5, M25.511, G89.29"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">Separate multiple codes with commas</p>
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Service Description
                </label>
                <textarea
                  value={formData.service_description}
                  onChange={(e) => updateFormData('service_description', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  rows="3"
                  placeholder="Description of the service provided..."
                />
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Additional Notes</h2>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Internal Notes
                </label>
                <textarea
                  value={formData.internal_notes}
                  onChange={(e) => updateFormData('internal_notes', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                  rows="4"
                  placeholder="Add any internal notes or observations..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority Level
                </label>
                <select
                  value={formData.priority}
                  onChange={(e) => updateFormData('priority', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
                >
                  <option value="low">Low</option>
                  <option value="normal">Normal</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 6:
        return (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Review & Submit</h2>

            {/* Patient & Provider Info */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="w-6 h-6 bg-[#fc459d] text-white rounded-full text-sm flex items-center justify-center mr-2">1</span>
                Patient & Provider
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Claim Number</p>
                  <p className="font-semibold">{formData.claim_number || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Patient Name</p>
                  <p className="font-semibold">{formData.patient_name || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Patient ID</p>
                  <p className="font-semibold">{formData.patient_id || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date of Birth</p>
                  <p className="font-semibold">{formData.patient_dob || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Provider</p>
                  <p className="font-semibold">{formData.provider_name || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Provider ID</p>
                  <p className="font-semibold">{formData.provider_id || '-'}</p>
                </div>
              </div>
            </div>

            {/* Payer Info */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="w-6 h-6 bg-[#fc459d] text-white rounded-full text-sm flex items-center justify-center mr-2">2</span>
                Insurance Payer
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Payer</p>
                  <p className="font-semibold">{formData.payer_name || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Policy Number</p>
                  <p className="font-semibold">{formData.policy_number || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Group Number</p>
                  <p className="font-semibold">{formData.group_number || '-'}</p>
                </div>
              </div>
            </div>

            {/* Denial Details */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="w-6 h-6 bg-[#fc459d] text-white rounded-full text-sm flex items-center justify-center mr-2">3</span>
                Denial Details
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Service Date</p>
                  <p className="font-semibold">{formData.service_date || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Denial Date</p>
                  <p className="font-semibold">{formData.denial_date || '-'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Denial Category</p>
                  <p className="font-semibold">{formData.denial_category || '-'}</p>
                </div>
                <div className="md:col-span-3">
                  <p className="text-sm text-gray-600">Denial Reason</p>
                  <p className="font-semibold">{formData.denial_reason || '-'}</p>
                </div>
              </div>
            </div>

            {/* Financial Summary - ENHANCED */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="w-6 h-6 bg-[#fc459d] text-white rounded-full text-sm flex items-center justify-center mr-2">4</span>
                Financial Summary
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Total Claim Amount</p>
                  <p className="font-semibold text-lg text-gray-900">${formData.claim_amount || '0'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Amount Paid</p>
                  <p className="font-semibold text-lg text-green-600">${formData.paid_amount || '0'}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Denied Amount</p>
                  <p className="font-semibold text-lg text-red-600">${formData.denied_amount || '0'}</p>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">CPT Code</p>
                    <p className="font-semibold">{formData.procedure_code || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Diagnosis Codes</p>
                    <p className="font-semibold">{formData.diagnosis_codes || '-'}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-600">Service Description</p>
                    <p className="font-semibold">{formData.service_description || '-'}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Priority & Notes */}
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <span className="w-6 h-6 bg-[#fc459d] text-white rounded-full text-sm flex items-center justify-center mr-2">5</span>
                Priority & Notes
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Priority Level</p>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
                    formData.priority === 'urgent' ? 'bg-red-100 text-red-700' :
                    formData.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                    formData.priority === 'normal' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {formData.priority?.charAt(0).toUpperCase() + formData.priority?.slice(1)}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Internal Notes</p>
                  <p className="font-semibold">{formData.internal_notes || 'No notes added'}</p>
                </div>
              </div>
            </div>

          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div key={step.number} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all duration-200 ${
                    step.number === currentStep
                      ? 'bg-gradient-to-r from-[#fc459d] to-purple-600 text-white'
                      : step.number < currentStep
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-200 text-gray-600'
                  }`}
                >
                  {step.number < currentStep ? (
                    <CheckIcon className="w-6 h-6" />
                  ) : (
                    step.number
                  )}
                </div>
                <p className="text-xs mt-2 text-gray-600">{step.name}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="flex-1 h-1 bg-gray-200 mx-2">
                  <div
                    className={`h-full transition-all duration-300 ${
                      step.number < currentStep
                        ? 'bg-green-500'
                        : 'bg-gray-200'
                    }`}
                  />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Form Content */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-6">
        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <button
          onClick={handleBack}
          disabled={currentStep === 1 || isSubmitting}
          className="px-6 py-3 bg-white border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
        >
          Back
        </button>
        <div className="flex gap-3">
          <button
            onClick={() => navigate('/denials')}
            disabled={isSubmitting}
            className="px-6 py-3 bg-white border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 disabled:opacity-50 transition-all duration-200"
          >
            Cancel
          </button>
          {currentStep < 6 ? (
            <button
              onClick={handleNext}
              disabled={isSubmitting}
              className="px-6 py-3 bg-gradient-to-r from-[#fc459d] to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg disabled:opacity-50 transition-all duration-200"
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-xl hover:shadow-lg disabled:opacity-50 transition-all duration-200"
            >
              {isSubmitting ? 'Creating Denial...' : 'Submit Denial'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewDenialWizard;
