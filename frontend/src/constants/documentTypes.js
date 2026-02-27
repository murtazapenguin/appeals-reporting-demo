/**
 * Document Type Definitions
 *
 * Maps document types to their display labels and icons.
 */

export const DOCUMENT_TYPES = {
  'medical_records': {
    label: 'Medical Records',
    icon: 'DocumentTextIcon',
    color: 'bg-blue-100 text-blue-800'
  },
  'prior_visit_notes': {
    label: 'Prior Visit Notes',
    icon: 'ClipboardDocumentListIcon',
    color: 'bg-indigo-100 text-indigo-800'
  },
  'diagnostic_tests': {
    label: 'Diagnostic Tests',
    icon: 'BeakerIcon',
    color: 'bg-purple-100 text-purple-800'
  },
  'claim_form': {
    label: 'Claim Form',
    icon: 'DocumentIcon',
    color: 'bg-gray-100 text-gray-800'
  },
  'eob': {
    label: 'EOB/Remittance',
    icon: 'BanknotesIcon',
    color: 'bg-green-100 text-green-800'
  },
  'denial_letter': {
    label: 'Denial Letter',
    icon: 'ExclamationCircleIcon',
    color: 'bg-red-100 text-red-800'
  },
  'payer_policy': {
    label: 'Payer Policy',
    icon: 'BookOpenIcon',
    color: 'bg-yellow-100 text-yellow-800'
  },
  'clinical_guidelines': {
    label: 'Clinical Guidelines',
    icon: 'AcademicCapIcon',
    color: 'bg-teal-100 text-teal-800'
  },
  'prior_auth': {
    label: 'Prior Authorization',
    icon: 'CheckBadgeIcon',
    color: 'bg-emerald-100 text-emerald-800'
  },
  'peer_reviewed': {
    label: 'Peer-Reviewed Literature',
    icon: 'NewspaperIcon',
    color: 'bg-orange-100 text-orange-800'
  },
  'other': {
    label: 'Other Document',
    icon: 'PaperClipIcon',
    color: 'bg-slate-100 text-slate-800'
  }
};

export const getDocumentTypeInfo = (type) => {
  return DOCUMENT_TYPES[type] || DOCUMENT_TYPES['other'];
};

export const getDocumentTypeLabel = (type) => {
  return getDocumentTypeInfo(type).label;
};

export const getDocumentTypeColor = (type) => {
  return getDocumentTypeInfo(type).color;
};
