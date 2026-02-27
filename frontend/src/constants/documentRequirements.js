/**
 * Required Documents Checklist
 *
 * Defines the documents needed for a complete appeal package.
 */

export const REQUIRED_DOCUMENTS = [
  {
    id: 'medical_records',
    label: 'Complete medical records for date of service',
    required: true,
    category: 'Clinical'
  },
  {
    id: 'prior_visit_notes',
    label: 'Prior visit notes showing treatment progression',
    required: true,
    category: 'Clinical'
  },
  {
    id: 'diagnostic_tests',
    label: 'Diagnostic test reports (imaging, labs, pathology)',
    required: true,
    category: 'Clinical'
  },
  {
    id: 'claim_form',
    label: 'Copy of original claim (CMS-1500 or UB-04)',
    required: true,
    category: 'Administrative'
  },
  {
    id: 'eob',
    label: 'EOB/Remittance advice showing denial',
    required: true,
    category: 'Administrative'
  },
  {
    id: 'payer_policy',
    label: 'Payer medical policy with highlighted relevant sections',
    required: true,
    category: 'Policy'
  },
  {
    id: 'clinical_guidelines',
    label: 'Clinical practice guidelines (AAOS, ACR, etc.)',
    required: false,
    category: 'Policy'
  },
  {
    id: 'prior_auth',
    label: 'Prior authorization approval letter (if applicable)',
    required: false,
    category: 'Administrative'
  },
  {
    id: 'peer_reviewed',
    label: 'Peer-reviewed literature (if experimental/investigational)',
    required: false,
    category: 'Research'
  }
];

export const DOCUMENT_CATEGORIES = ['Clinical', 'Administrative', 'Policy', 'Research'];

export const getDocumentsByCategory = (category) => {
  return REQUIRED_DOCUMENTS.filter(doc => doc.category === category);
};

export const getRequiredDocuments = () => {
  return REQUIRED_DOCUMENTS.filter(doc => doc.required);
};

export const getOptionalDocuments = () => {
  return REQUIRED_DOCUMENTS.filter(doc => !doc.required);
};
