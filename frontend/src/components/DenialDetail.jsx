import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  PaperAirplaneIcon,
  EyeIcon,
  PencilIcon,
  CheckIcon,
  XMarkIcon,
  CloudArrowUpIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { denialsAPI, criteriaAPI, documentsAPI, appealsAPI } from '../services/api';
import PDFViewer from './PDFViewer';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import DocumentChecklist from './DocumentChecklist';
import DocumentUploadModal from './DocumentUploadModal';
import QuestionnaireTreeView from './QuestionnaireTreeView';
import { getDocumentTypeLabel, getDocumentTypeColor } from '../constants/documentTypes';

// Helper functions for status and deadline display
const getStatusColor = (status) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    in_review: 'bg-blue-100 text-blue-800',
    appeal_ready: 'bg-purple-100 text-purple-800',
    submitted: 'bg-green-100 text-green-800',
    approved: 'bg-emerald-100 text-emerald-800',
    denied: 'bg-red-100 text-red-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

const formatStatusLabel = (status) => {
  return status?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Unknown';
};

const getDeadlineColor = (deadlineStr) => {
  if (!deadlineStr) return 'text-gray-900';

  const deadline = new Date(deadlineStr);
  const now = new Date();
  const daysRemaining = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));

  if (daysRemaining < 0) return 'text-red-700 font-bold'; // Overdue
  if (daysRemaining < 7) return 'text-red-600 font-semibold'; // Urgent (<7 days)
  if (daysRemaining < 14) return 'text-yellow-600 font-semibold'; // Warning (<14 days)
  return 'text-gray-900'; // Normal
};

const getDeadlineLabel = (deadlineStr) => {
  if (!deadlineStr) return 'Not set';

  const deadline = new Date(deadlineStr);
  const now = new Date();
  const daysRemaining = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));

  const dateStr = deadline.toLocaleDateString();

  if (daysRemaining < 0) return `${dateStr} (Overdue)`;
  if (daysRemaining === 0) return `${dateStr} (Today!)`;
  if (daysRemaining === 1) return `${dateStr} (Tomorrow)`;
  if (daysRemaining < 7) return `${dateStr} (${daysRemaining} days)`;

  return dateStr;
};

const DenialDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [denial, setDenial] = useState(null);
  const [criteriaResults, setCriteriaResults] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [appealLetter, setAppealLetter] = useState(null);
  const [selectedEvidenceKey, setSelectedEvidenceKey] = useState(null);
  const [activeBoundingBoxes, setActiveBoundingBoxes] = useState([]);
  const [activeDocumentData, setActiveDocumentData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isEditingLetter, setIsEditingLetter] = useState(false);
  const [editedLetterContent, setEditedLetterContent] = useState('');
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [showRegenerateDialog, setShowRegenerateDialog] = useState(false);
  const [hasLocalEdits, setHasLocalEdits] = useState(false);

  // Documents tab state
  const [selectedDocId, setSelectedDocId] = useState(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [uploadPreselectedType, setUploadPreselectedType] = useState(null);

  // Appeal workflow state
  const [isLetterAccepted, setIsLetterAccepted] = useState(false);
  const [isGeneratingPackage, setIsGeneratingPackage] = useState(false);
  const [packageData, setPackageData] = useState(null);

  // Helper function to determine if denial is in submitted/final state
  const isSubmittedState = (status) => {
    return ['submitted', 'approved', 'denied'].includes(status);
  };

  useEffect(() => {
    loadDenialData();
  }, [id]);

  const loadDenialData = async () => {
    try {
      setIsLoading(true);
      const denialData = await denialsAPI.getById(id);
      setDenial(denialData);

      // Load criteria results
      try {
        const criteriaData = await criteriaAPI.getResults(id);
        setCriteriaResults(criteriaData);
      } catch (error) {
        // No criteria results yet
      }

      // Resume polling if evaluation is still in progress
      if (denialData.evaluation_status === 'processing') {
        setIsEvaluating(true);
        criteriaAPI.evaluate(id).then(results => {
          setCriteriaResults(results);
          setActiveTab('evidence');
        }).catch(err => {
          console.error('Evaluation failed:', err);
          alert(`Criteria evaluation failed: ${err.message}`);
        }).finally(() => setIsEvaluating(false));
      }

      // Load documents by patient_id
      if (denialData.patient_id) {
        try {
          const docsData = await documentsAPI.getByPatientId(denialData.patient_id);
          setDocuments(docsData);
        } catch (error) {
          console.error('Failed to load documents:', error);
        }
      }

      // Try to load appeal letter if exists
      try {
        const letter = await appealsAPI.getLetter(id);
        setAppealLetter(letter);
      } catch (error) {
        // Letter doesn't exist yet
      }

      // Resume polling if appeal generation is still in progress
      if (denialData.appeal_status === 'processing') {
        setIsGenerating(true);
        appealsAPI.generateLetter(id).then(letter => {
          setAppealLetter(letter);
          setActiveTab('appeal');
        }).catch(err => {
          console.error('Appeal generation failed:', err);
          alert(`Appeal letter generation failed: ${err.message}`);
        }).finally(() => setIsGenerating(false));
      }

      // Try to load package data if exists
      try {
        const pkg = await appealsAPI.getPackage(id);
        setPackageData(pkg);
      } catch (error) {
        // Package doesn't exist yet
      }
    } catch (error) {
      console.error('Failed to load denial data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEvaluateCriteria = async () => {
    try {
      setIsEvaluating(true);
      const results = await criteriaAPI.evaluate(id);
      setCriteriaResults(results);
      // Auto-switch to evidence view after evaluation
      setActiveTab('evidence');
    } catch (error) {
      console.error('Failed to evaluate criteria:', error);
      alert(`Failed to evaluate criteria: ${error.message}`);
    } finally {
      setIsEvaluating(false);
    }
  };

  const handleGenerateAppeal = async () => {
    try {
      setIsGenerating(true);
      const letter = await appealsAPI.generateLetter(id);
      setAppealLetter(letter);
      setActiveTab('appeal');
    } catch (error) {
      console.error('Failed to generate appeal:', error);
      alert(`Failed to generate appeal letter: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRegenerateLetter = () => {
    setShowRegenerateDialog(true);
  };

  const confirmRegenerate = async () => {
    setShowRegenerateDialog(false);
    setIsRegenerating(true);

    try {
      // Call the same endpoint - backend already supports upsert
      const letter = await appealsAPI.generateLetter(id);

      // Update state with new letter
      setAppealLetter(letter);
      setEditedLetterContent(''); // Reset edited version
      setHasLocalEdits(false); // Clear local edit flag
      setIsEditingLetter(false); // Exit edit mode
      setIsLetterAccepted(false); // Reset acceptance state

      alert('Appeal letter regenerated successfully with latest evidence');

      // If there was a package, warn user to regenerate it
      if (packageData) {
        alert('Please regenerate the final package to include the updated letter');
      }

    } catch (error) {
      console.error('Error regenerating letter:', error);
      alert('Failed to regenerate letter. Please try again.');
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleDownloadPDF = async () => {
    try {
      // If package exists, download the full package (letter + all documents)
      // Otherwise, download just the appeal letter
      const blob = packageData
        ? await appealsAPI.downloadPackage(id)
        : await appealsAPI.downloadPDF(id);

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      // Use appropriate filename
      a.download = packageData
        ? `appeal_package_${denial.claim_number}.pdf`
        : `appeal_letter_${denial.claim_number}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download PDF:', error);
      alert('Failed to download PDF. Please try again.');
    }
  };

  const handleSubmitAppeal = async () => {
    if (!window.confirm('Are you sure you want to submit this appeal?')) return;

    try {
      await appealsAPI.submit(id);
      alert('Appeal submitted successfully!');
      await loadDenialData();
    } catch (error) {
      console.error('Failed to submit appeal:', error);
      alert('Failed to submit appeal. Please try again.');
    }
  };

  const handleEvidenceClick = (evidence, criterionIndex, evidenceIndex) => {
    const key = `${criterionIndex}-${evidenceIndex}`;
    setSelectedEvidenceKey(key);

    const token = localStorage.getItem('authToken');
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
    const apiHost = baseUrl.replace('/api', '');

    // Find the document from our loaded documents list
    const matchingDoc = documents.find(d =>
      d.document_name === evidence.document_name ||
      d.id === evidence.document_id
    );

    if (matchingDoc) {
      // Build presigned URLs with token for each page
      const presignedUrlsWithToken = {};
      Object.entries(matchingDoc.presigned_urls || {}).forEach(([page, url]) => {
        // Convert relative URLs to absolute with token
        if (url.startsWith('/api/')) {
          presignedUrlsWithToken[page] = `${apiHost}${url}?token=${token}`;
        } else {
          presignedUrlsWithToken[page] = url;
        }
      });

      const docData = {
        files: [matchingDoc.document_name],
        presigned_urls: {
          [matchingDoc.document_name]: presignedUrlsWithToken
        }
      };
      setActiveDocumentData(docData);

      // Set bounding boxes for the PDF viewer to highlight
      // Support grouped evidence (allBboxes) from QuestionnaireTreeView
      const bboxes = evidence.allBboxes || [evidence.bbox];
      setActiveBoundingBoxes([{
        page_number: evidence.page,
        document_name: matchingDoc.document_name,
        bbox: bboxes,
        label: bboxes.map((_, i) => `Evidence ${i + 1}`),
        color: bboxes.map(() => '#fc459d')
      }]);
    } else {
      // Fallback: create document data from evidence itself
      const docData = {
        files: [evidence.document_name],
        presigned_urls: {
          [evidence.document_name]: {
            [String(evidence.page)]: `${apiHost}/api/documents/${evidence.document_id}/page/${evidence.page}/image?token=${token}`
          }
        }
      };
      setActiveDocumentData(docData);
      const bboxesFallback = evidence.allBboxes || [evidence.bbox];
      setActiveBoundingBoxes([{
        page_number: evidence.page,
        document_name: evidence.document_name,
        bbox: bboxesFallback,
        label: bboxesFallback.map((_, i) => `Evidence ${i + 1}`),
        color: bboxesFallback.map(() => '#fc459d')
      }]);
    }
  };

  // Handle document upload
  const handleDocumentUpload = async ({ file, documentType, documentDate, denialId, patientId }) => {
    await documentsAPI.upload(file, denialId, patientId, documentType, documentDate);
    // Reload documents
    const docsData = await documentsAPI.getByPatientId(denial.patient_id);
    setDocuments(docsData);
  };

  // Handle upload modal open from checklist
  const handleUploadClick = (docType) => {
    setUploadPreselectedType(docType);
    setIsUploadModalOpen(true);
  };

  // Handle re-run evidence review
  const handleRerunEvaluation = async () => {
    try {
      setIsEvaluating(true);
      const results = await criteriaAPI.evaluate(id);
      setCriteriaResults(results);
      setActiveTab('evidence');
    } catch (error) {
      console.error('Failed to evaluate criteria:', error);
      alert('Failed to evaluate criteria. Please try again.');
    } finally {
      setIsEvaluating(false);
    }
  };

  // Get single document data for PDF viewer
  const getSelectedDocumentData = () => {
    if (!selectedDocId || !documents.length) return null;

    const doc = documents.find(d => d.id === selectedDocId);
    if (!doc) return null;

    const token = localStorage.getItem('authToken');
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
    const apiHost = baseUrl.replace('/api', '');

    const urlsWithToken = {};
    Object.entries(doc.presigned_urls || {}).forEach(([page, url]) => {
      if (url.startsWith('/api/')) {
        urlsWithToken[page] = `${apiHost}${url}?token=${token}`;
      } else {
        urlsWithToken[page] = url;
      }
    });

    return {
      files: [doc.document_name],
      presigned_urls: {
        [doc.document_name]: urlsWithToken
      }
    };
  };

  // Handle generate package
  const handleGeneratePackage = async () => {
    try {
      setIsGeneratingPackage(true);
      const result = await appealsAPI.generatePackage(id);
      setPackageData(result);
    } catch (error) {
      console.error('Failed to generate package:', error);
      alert('Failed to generate package. Please try again.');
    } finally {
      setIsGeneratingPackage(false);
    }
  };

  // Build document data for All Documents tab
  const getAllDocumentsData = () => {
    if (!documents || documents.length === 0) return null;

    const token = localStorage.getItem('authToken');
    const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
    const apiHost = baseUrl.replace('/api', '');

    const presignedUrls = {};
    documents.forEach(doc => {
      const urlsWithToken = {};
      Object.entries(doc.presigned_urls || {}).forEach(([page, url]) => {
        if (url.startsWith('/api/')) {
          urlsWithToken[page] = `${apiHost}${url}?token=${token}`;
        } else {
          urlsWithToken[page] = url;
        }
      });
      presignedUrls[doc.document_name] = urlsWithToken;
    });

    return {
      files: documents.map(d => d.document_name),
      presigned_urls: presignedUrls
    };
  };

  const RegenerateConfirmDialog = () => {
    if (!showRegenerateDialog) return null;

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" onClick={() => setShowRegenerateDialog(false)} />
        <div className="relative bg-white rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="w-6 h-6 text-amber-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Regenerate Appeal Letter?
              </h3>
              <div className="text-sm text-gray-600 space-y-2">
                <p>This will regenerate the letter using the latest evidence and document checklist.</p>

                {hasLocalEdits && (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
                    <p className="font-medium text-amber-900">⚠️ You have unsaved edits</p>
                    <p className="text-amber-800 mt-1">Local changes will be discarded when regenerating.</p>
                  </div>
                )}

                {packageData && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="font-medium text-red-900">⚠️ Existing package will be invalidated</p>
                    <p className="text-red-800 mt-1">You'll need to regenerate the final package after this.</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => setShowRegenerateDialog(false)}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={confirmRegenerate}
              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Regenerate Letter
            </button>
          </div>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-12 h-12 border-4 border-gray-200 border-t-[#fc459d] rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!denial) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-500">Denial not found</p>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: DocumentTextIcon },
    { id: 'documents', name: 'Documents', icon: DocumentIcon },
    { id: 'evidence', name: 'Evidence Review', icon: EyeIcon },
    { id: 'appeal', name: 'Appeal Letter', icon: DocumentTextIcon }
  ];

  const allDocumentsData = getAllDocumentsData();

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <button
              onClick={() => navigate('/denials')}
              className="mr-4 p-2 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Claim {denial.claim_number}
              </h1>
              <p className="text-sm text-gray-600">
                {denial.patient_name} - {denial.payer_name}
              </p>
            </div>
          </div>
          <div className="flex gap-3">
            {!criteriaResults && (
              <button
                onClick={handleEvaluateCriteria}
                disabled={isEvaluating}
                className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50"
              >
                {isEvaluating ? 'Evaluating... (this may take a few minutes)' : 'Evaluate Criteria'}
              </button>
            )}
            {criteriaResults && !appealLetter && (
              <button
                onClick={handleGenerateAppeal}
                disabled={isGenerating}
                className="px-4 py-2 bg-purple-600 text-white rounded-xl hover:bg-purple-700 disabled:opacity-50"
              >
                {isGenerating ? 'Generating... (this may take a minute)' : 'Generate Appeal'}
              </button>
            )}
            {appealLetter && (
              <>
                <button
                  onClick={handleDownloadPDF}
                  className="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50"
                >
                  <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
                  Download PDF
                </button>
                {/* Only show Submit button if not already submitted */}
                {!isSubmittedState(denial?.status) && (
                  <button
                    onClick={handleSubmitAppeal}
                    className="flex items-center px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:shadow-lg"
                  >
                    <PaperAirplaneIcon className="w-5 h-5 mr-2" />
                    Submit Appeal
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mt-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-[#fc459d] to-purple-600 text-white'
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-5 h-5 mr-2" />
                {tab.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'overview' && (
          <div className="p-6 overflow-auto h-full">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Patient Info */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Patient Information</h2>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Name</p>
                    <p className="font-semibold">{denial.patient_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Patient ID</p>
                    <p className="font-semibold">{denial.patient_id}</p>
                  </div>
                  {denial.patient_dob && (
                    <div>
                      <p className="text-sm text-gray-600">Date of Birth</p>
                      <p className="font-semibold">{new Date(denial.patient_dob).toLocaleDateString()}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Claim Details */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Claim Details</h2>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Submitted Claim Amount</p>
                    <p className="font-semibold text-2xl text-gray-900">
                      ${denial.claim_amount?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Paid Amount</p>
                    <p className="font-semibold text-xl text-green-600">
                      ${denial.paid_amount?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Denied Amount</p>
                    <p className="font-semibold text-xl text-[#fc459d]">
                      ${denial.denied_amount?.toLocaleString() || 0}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Service Date</p>
                    <p className="font-semibold">{new Date(denial.service_date).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Payer</p>
                    <p className="font-semibold">{denial.payer_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Procedure Code</p>
                    <p className="font-semibold">{denial.procedure_code}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Diagnosis Codes</p>
                    <p className="font-semibold">
                      {Array.isArray(denial.diagnosis_codes)
                        ? denial.diagnosis_codes.join(', ')
                        : denial.diagnosis_codes}
                    </p>
                  </div>
                </div>
              </div>

              {/* Win Probability */}
              {criteriaResults && (
                <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Win Probability</h2>
                  <div className="flex items-center justify-center">
                    <div className="relative w-32 h-32">
                      <svg className="w-full h-full transform -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          fill="none"
                          stroke="#e5e7eb"
                          strokeWidth="12"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r="56"
                          fill="none"
                          stroke="url(#gradient)"
                          strokeWidth="12"
                          strokeLinecap="round"
                          strokeDasharray={`${(criteriaResults.win_probability / 100) * 352} 352`}
                        />
                        <defs>
                          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor="#fc459d" />
                            <stop offset="100%" stopColor="#a855f7" />
                          </linearGradient>
                        </defs>
                      </svg>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <span className="text-3xl font-bold text-gray-900">
                          {criteriaResults.win_probability}%
                        </span>
                      </div>
                    </div>
                  </div>
                  <p className="text-center text-sm text-gray-600 mt-4">
                    {criteriaResults.criteria_met} of {criteriaResults.total_criteria} criteria met
                  </p>
                </div>
              )}

              {/* Denial Info */}
              <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Denial Information</h2>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Status</p>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(denial.status)}`}>
                      {formatStatusLabel(denial.status)}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Denial Date</p>
                    <p className="font-semibold">{new Date(denial.denial_date).toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Category</p>
                    <p className="font-semibold">{denial.denial_category}</p>
                  </div>
                  {denial.denial_reason && (
                    <div>
                      <p className="text-sm text-gray-600">Reason</p>
                      <p className="font-semibold">{denial.denial_reason}</p>
                    </div>
                  )}
                  <div>
                    <p className="text-sm text-gray-600">Appeal Deadline</p>
                    <p className={`font-semibold ${getDeadlineColor(denial.appeal_deadline)}`}>
                      {getDeadlineLabel(denial.appeal_deadline)}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* EVIDENCE REVIEW - Split Panel View */}
        {activeTab === 'evidence' && (
          <div className="h-full flex">
            {criteriaResults ? (
              <>
                {/* Left: PDF Viewer (60%) */}
                <div className="w-3/5 h-full border-r border-gray-200 bg-gray-100">
                  {activeDocumentData ? (
                    <PDFViewer
                      documentData={activeDocumentData}
                      boundingBoxes={activeBoundingBoxes}
                      className="h-full"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <div className="text-center text-gray-500">
                        <DocumentIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                        <p className="text-lg font-medium">Select an evidence item</p>
                        <p className="text-sm mt-1">Click on any evidence in the right panel to view the document</p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Right: Evidence Panel (40%) */}
                <div className="w-2/5 h-full overflow-y-auto bg-white">
                  {criteriaResults.criteria_tree ? (
                    <QuestionnaireTreeView
                      criteriaTree={criteriaResults.criteria_tree}
                      guidelineName={criteriaResults.guideline_name}
                      criteriaMet={criteriaResults.criteria_met}
                      totalCriteria={criteriaResults.total_criteria}
                      winProbability={criteriaResults.win_probability}
                      onEvidenceClick={(evidence) => handleEvidenceClick(evidence, 0, 0)}
                    />
                  ) : (
                  <div className="p-4">
                    {/* Summary Header */}
                    <div className="bg-gradient-to-r from-[#fc459d] to-purple-600 rounded-xl p-4 mb-4 text-white">
                      <h2 className="text-lg font-bold mb-2">Criteria Evaluation</h2>
                      <div className="flex items-center justify-between">
                        <span className="text-2xl font-bold">
                          {criteriaResults.criteria_met}/{criteriaResults.total_criteria}
                        </span>
                        <span className="text-sm opacity-90">
                          Win Probability: {criteriaResults.win_probability}%
                        </span>
                      </div>
                      <div className="w-full bg-white/30 rounded-full h-2 mt-2">
                        <div
                          className="bg-white h-2 rounded-full transition-all"
                          style={{ width: `${criteriaResults.win_probability}%` }}
                        />
                      </div>
                    </div>

                    {/* Criteria List */}
                    <div className="space-y-4">
                      {criteriaResults.criteria.map((criterion, criterionIndex) => (
                        <div
                          key={criterionIndex}
                          className={`rounded-xl border p-4 ${
                            criterion.met
                              ? 'border-green-200 bg-green-50'
                              : 'border-red-200 bg-red-50'
                          }`}
                        >
                          <div className="flex items-start gap-3">
                            {criterion.met ? (
                              <CheckCircleIcon className="w-6 h-6 text-green-500 flex-shrink-0 mt-0.5" />
                            ) : (
                              <XCircleIcon className="w-6 h-6 text-red-500 flex-shrink-0 mt-0.5" />
                            )}
                            <div className="flex-1">
                              <p className="font-medium text-gray-900 text-sm">
                                {criterion.description}
                              </p>
                              <span className={`inline-block mt-1 text-xs font-semibold px-2 py-0.5 rounded ${
                                criterion.met
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-red-100 text-red-700'
                              }`}>
                                {criterion.met ? 'MET' : 'NOT MET'}
                              </span>

                              {/* Explanation for NOT MET criteria */}
                              {!criterion.met && criterion.explanation && (
                                <p className="mt-2 text-xs text-gray-600 italic">
                                  {criterion.explanation}
                                </p>
                              )}

                              {/* Evidence Items */}
                              {criterion.evidence && criterion.evidence.length > 0 && (
                                <div className="mt-3 space-y-2">
                                  <p className="text-xs font-semibold text-gray-600 uppercase tracking-wider">
                                    Supporting Evidence:
                                  </p>
                                  {criterion.evidence.map((evidence, evIndex) => {
                                    const evidenceKey = `${criterionIndex}-${evIndex}`;
                                    const isSelected = selectedEvidenceKey === evidenceKey;
                                    return (
                                      <button
                                        key={evIndex}
                                        onClick={() => handleEvidenceClick(evidence, criterionIndex, evIndex)}
                                        className={`w-full text-left p-3 rounded-lg border transition-all ${
                                          isSelected
                                            ? 'border-[#fc459d] bg-pink-50 shadow-md ring-2 ring-[#fc459d]/20'
                                            : 'border-gray-200 bg-white hover:border-[#fc459d] hover:shadow-sm'
                                        }`}
                                      >
                                        <div className="flex items-center justify-between mb-1">
                                          <span className="text-xs font-semibold text-[#fc459d]">
                                            {evidence.document_name}
                                          </span>
                                          <span className="text-xs text-gray-500">
                                            Page {evidence.page}
                                          </span>
                                        </div>
                                        <p className="text-xs text-gray-700 line-clamp-2">
                                          "{evidence.text}"
                                        </p>
                                      </button>
                                    );
                                  })}
                                </div>
                              )}

                              {/* Missing Documents */}
                              {!criterion.met && criterion.missing_documents && (
                                <div className="mt-3 p-2 bg-yellow-50 rounded-lg border border-yellow-200">
                                  <p className="text-xs font-semibold text-yellow-800">
                                    Missing: {criterion.missing_documents}
                                  </p>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                  )}
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center w-full h-full">
                <EyeIcon className="w-16 h-16 text-gray-300 mb-4" />
                <p className="text-gray-500 mb-4">No criteria evaluation yet</p>
                <button
                  onClick={handleEvaluateCriteria}
                  disabled={isEvaluating}
                  className="px-6 py-3 bg-gradient-to-r from-[#fc459d] to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg disabled:opacity-50"
                >
                  {isEvaluating ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Evaluating... this may take a few minutes
                    </span>
                  ) : 'Start Evaluation'}
                </button>
              </div>
            )}
          </div>
        )}

        {/* DOCUMENTS TAB - 3-Column Layout */}
        {activeTab === 'documents' && (
          <div className="h-full flex">
            {/* Left Panel - Document List (25%) */}
            <div className="w-1/4 h-full border-r border-gray-200 bg-white flex flex-col">
              <div className="p-4 border-b border-gray-200 flex items-center justify-between">
                <h3 className="font-bold text-gray-900">Documents</h3>
                <button
                  onClick={() => {
                    setUploadPreselectedType(null);
                    setIsUploadModalOpen(true);
                  }}
                  className="p-2 text-[#fc459d] hover:bg-pink-50 rounded-lg transition-colors"
                  title="Upload document"
                >
                  <CloudArrowUpIcon className="w-5 h-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto">
                {documents.length > 0 ? (
                  <div className="divide-y divide-gray-100">
                    {documents.map((doc) => (
                      <button
                        key={doc.id}
                        onClick={() => setSelectedDocId(doc.id)}
                        className={`w-full text-left p-4 hover:bg-gray-50 transition-colors ${
                          selectedDocId === doc.id
                            ? 'bg-pink-50 border-l-4 border-[#fc459d]'
                            : ''
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <DocumentIcon className="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">
                              {doc.document_name}
                            </p>
                            <span className={`inline-block mt-1 text-xs px-2 py-0.5 rounded ${getDocumentTypeColor(doc.document_type)}`}>
                              {getDocumentTypeLabel(doc.document_type)}
                            </span>
                            {doc.document_date && (
                              <p className="text-xs text-gray-500 mt-1">
                                {new Date(doc.document_date).toLocaleDateString()}
                              </p>
                            )}
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full p-4 text-center">
                    <DocumentIcon className="w-12 h-12 text-gray-300 mb-2" />
                    <p className="text-sm text-gray-500">No documents uploaded</p>
                    <button
                      onClick={() => setIsUploadModalOpen(true)}
                      className="mt-3 text-sm text-[#fc459d] hover:underline"
                    >
                      Upload a document
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Center Panel - PDF Viewer (50%) */}
            <div className="w-1/2 h-full bg-gray-100">
              {selectedDocId && getSelectedDocumentData() ? (
                <PDFViewer
                  documentData={getSelectedDocumentData()}
                  boundingBoxes={[]}
                  className="h-full"
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center text-gray-500">
                    <DocumentIcon className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                    <p className="text-lg font-medium">Select a document</p>
                    <p className="text-sm mt-1">Click on a document in the left panel to view it</p>
                  </div>
                </div>
              )}
            </div>

            {/* Right Panel - Document Checklist (25%) */}
            <div className="w-1/4 h-full border-l border-gray-200">
              <DocumentChecklist
                documents={documents}
                onUploadClick={handleUploadClick}
                onRerunEvaluation={handleRerunEvaluation}
                isEvaluating={isEvaluating}
              />
            </div>
          </div>
        )}

        {/* Document Upload Modal */}
        <DocumentUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => {
            setIsUploadModalOpen(false);
            setUploadPreselectedType(null);
          }}
          onUpload={handleDocumentUpload}
          preselectedType={uploadPreselectedType}
          denialId={id}
          patientId={denial?.patient_id}
          denial={denial}
        />

        {/* Submitted Appeal View Component - Read-only display of final appeal */}
        {activeTab === 'appeal' && (() => {
          // Helper component for submitted appeals
          const SubmittedAppealView = ({ denial, appealLetter, packageData }) => (
            <div className="p-6 overflow-auto h-full">
              <div className="max-w-4xl mx-auto space-y-6">
                {/* Status Header */}
                <div className="flex items-center justify-between bg-green-50 rounded-lg p-4 border border-green-200">
                  <div className="flex items-center space-x-3">
                    <CheckCircleIcon className="w-6 h-6 text-green-600" />
                    <div>
                      <h3 className="font-medium text-green-900">Appeal Submitted</h3>
                      <p className="text-sm text-green-700">
                        Submitted on {denial.submitted_at ? new Date(denial.submitted_at).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    denial.status === 'approved' ? 'bg-emerald-100 text-emerald-800' :
                    denial.status === 'denied' ? 'bg-red-100 text-red-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {formatStatusLabel(denial.status)}
                  </span>
                </div>

                {/* Package Download (if available) */}
                {packageData && (
                  <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold mb-4">Appeal Package</h3>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <DocumentIcon className="w-10 h-10 text-[#fc459d]" />
                        <div>
                          <p className="font-medium">Complete Appeal Package</p>
                          <p className="text-sm text-gray-500">
                            Letter + Supporting Documents
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={handleDownloadPDF}
                        className="flex items-center space-x-2 px-4 py-2 bg-[#fc459d] text-white rounded-lg hover:bg-[#e03d8a] transition"
                      >
                        <ArrowDownTrayIcon className="w-4 h-4" />
                        <span>Download Package</span>
                      </button>
                    </div>
                  </div>
                )}

                {/* Appeal Letter Preview (Read-Only) */}
                <div className="bg-white rounded-lg border border-gray-200 p-8">
                  <h3 className="text-lg font-semibold mb-6">Appeal Letter</h3>

                  {/* Letterhead */}
                  {appealLetter.provider_letterhead && (
                    <div className="mb-6 pb-4 border-b border-gray-300">
                      <p className="font-semibold text-gray-900">
                        {appealLetter.provider_letterhead.name}
                      </p>
                      {appealLetter.provider_letterhead.address && (
                        <p className="text-sm text-gray-600">
                          {appealLetter.provider_letterhead.address}
                        </p>
                      )}
                      {appealLetter.provider_letterhead.phone && (
                        <p className="text-sm text-gray-600">
                          {appealLetter.provider_letterhead.phone}
                        </p>
                      )}
                    </div>
                  )}

                  {/* RE Block */}
                  <div className="mb-6">
                    <p className="font-semibold">RE: Appeal for Claim {denial.claim_number}</p>
                    <p className="text-sm">Patient: {denial.patient_name}</p>
                    <p className="text-sm">Date of Service: {new Date(denial.service_date).toLocaleDateString()}</p>
                  </div>

                  {/* Letter Sections */}
                  <div className="space-y-6">
                    {appealLetter.sections?.map((section, idx) => (
                      <div key={idx} className="mb-6">
                        <h4 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                          {section.title}
                        </h4>
                        <div className="max-w-none text-gray-700 leading-relaxed">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              h1: ({node, ...props}) => <h3 className="text-lg font-bold text-gray-900 mt-6 mb-3" {...props} />,
                              h2: ({node, ...props}) => <h3 className="text-lg font-bold text-gray-900 mt-6 mb-3" {...props} />,
                              h3: ({node, ...props}) => <h4 className="text-base font-bold text-gray-800 mt-5 mb-2" {...props} />,
                              h4: ({node, ...props}) => <h5 className="text-sm font-bold text-gray-800 mt-4 mb-2" {...props} />,
                              p: ({node, ...props}) => <p className="text-gray-700 mb-4 leading-relaxed" {...props} />,
                              ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-4 space-y-2 text-gray-700" {...props} />,
                              ol: ({node, ...props}) => <ol className="list-decimal pl-6 mb-4 space-y-2 text-gray-700" {...props} />,
                              li: ({node, children, ...props}) => <li className="text-gray-700 leading-relaxed" {...props}>{children}</li>,
                              strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
                              em: ({node, ...props}) => <em className="italic" {...props} />,
                              blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-purple-400 pl-4 py-2 italic text-gray-600 my-4 bg-purple-50 rounded-r" {...props} />,
                              a: ({node, ...props}) => <a className="text-purple-600 underline hover:text-purple-800" {...props} />,
                              hr: ({node, ...props}) => <hr className="my-6 border-gray-200" {...props} />,
                              table: ({node, ...props}) => (
                                <div className="overflow-x-auto my-6">
                                  <table className="min-w-full divide-y divide-gray-300 border border-gray-300" {...props} />
                                </div>
                              ),
                              thead: ({node, ...props}) => <thead className="bg-gray-50" {...props} />,
                              tbody: ({node, ...props}) => <tbody className="divide-y divide-gray-200 bg-white" {...props} />,
                              tr: ({node, ...props}) => <tr className="hover:bg-gray-50" {...props} />,
                              th: ({node, ...props}) => <th className="px-4 py-3 text-left text-xs font-semibold text-gray-900 uppercase tracking-wider border-r border-gray-200 last:border-r-0" {...props} />,
                              td: ({node, ...props}) => <td className="px-4 py-3 text-sm text-gray-700 border-r border-gray-200 last:border-r-0 whitespace-normal" {...props} />,
                            }}
                          >
                            {section.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Enclosed Documents */}
                  {appealLetter.enclosed_documents && appealLetter.enclosed_documents.length > 0 && (
                    <div className="mt-6 pt-6 border-t border-gray-300">
                      <p className="font-semibold mb-2">Enclosed Documents:</p>
                      <ul className="list-disc list-inside text-sm text-gray-700">
                        {appealLetter.enclosed_documents.map((doc, index) => (
                          <li key={index}>{doc}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Signature */}
                  {appealLetter.signature && (
                    <div className="mt-8 pt-4 border-t border-gray-300">
                      <p className="font-semibold">Sincerely,</p>
                      <p className="mt-4">{appealLetter.signature.name}</p>
                      <p className="text-sm text-gray-600">{appealLetter.signature.title}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          );

          return (
            <div className="h-full overflow-hidden">
              {appealLetter ? (
                // Status-based rendering
                isSubmittedState(denial?.status) ? (
                  // Show submitted/final view (read-only)
                  <SubmittedAppealView
                    denial={denial}
                    appealLetter={appealLetter}
                    packageData={packageData}
                  />
                ) : packageData ? (
                  // Package preview mode - full width PDF viewer
                <div className="h-full flex flex-col">
                  {/* Package header */}
                  <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">Appeal Package Ready</h3>
                      <p className="text-sm text-gray-600">
                        {packageData.document_count} documents merged into final package
                      </p>
                    </div>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setPackageData(null)}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50"
                      >
                        Back to Letter
                      </button>
                      <button
                        onClick={handleDownloadPDF}
                        className="flex items-center px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50"
                      >
                        <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
                        Download Package
                      </button>
                      <button
                        onClick={handleSubmitAppeal}
                        className="flex items-center px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-xl hover:shadow-lg"
                      >
                        <PaperAirplaneIcon className="w-5 h-5 mr-2" />
                        Submit Appeal
                      </button>
                    </div>
                  </div>

                  {/* Package PDF viewer */}
                  <div className="flex-1">
                    <iframe
                      src={packageData.package_url}
                      className="w-full h-full"
                      title="Appeal Package Preview"
                    />
                  </div>
                </div>
              ) : (
                // Letter review mode
                <div className="p-6 overflow-auto h-full">
                  <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 max-w-4xl mx-auto">
                    {/* Workflow status bar */}
                    <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`flex items-center gap-2 ${isLetterAccepted ? 'text-green-600' : 'text-purple-600'}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${isLetterAccepted ? 'bg-green-100' : 'bg-purple-100'}`}>
                              {isLetterAccepted ? <CheckIcon className="w-5 h-5" /> : '1'}
                            </div>
                            <span className="font-medium">Review Letter</span>
                          </div>
                          <div className="w-8 h-0.5 bg-gray-300"></div>
                          <div className={`flex items-center gap-2 ${packageData ? 'text-green-600' : isLetterAccepted ? 'text-purple-600' : 'text-gray-400'}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center ${packageData ? 'bg-green-100' : isLetterAccepted ? 'bg-purple-100' : 'bg-gray-100'}`}>
                              {packageData ? <CheckIcon className="w-5 h-5" /> : '2'}
                            </div>
                            <span className="font-medium">Generate Package</span>
                          </div>
                          <div className="w-8 h-0.5 bg-gray-300"></div>
                          <div className="flex items-center gap-2 text-gray-400">
                            <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                              3
                            </div>
                            <span className="font-medium">Submit</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Edit/Save buttons */}
                    <div className="flex justify-between mb-4">
                      <div className="flex gap-2">
                        {isEditingLetter ? (
                          <>
                            <button
                              onClick={() => {
                                const sectionRegex = /^## (.+)$/gm;
                                const parts = editedLetterContent.split(sectionRegex);
                                const updatedSections = [];

                                if (parts[0]?.trim()) {
                                  updatedSections.push({
                                    title: 'Introduction',
                                    content: parts[0].trim()
                                  });
                                }

                                for (let i = 1; i < parts.length; i += 2) {
                                  if (parts[i] && parts[i + 1] !== undefined) {
                                    updatedSections.push({
                                      title: parts[i].trim(),
                                      content: parts[i + 1]?.trim() || ''
                                    });
                                  }
                                }

                                if (updatedSections.length === 0) {
                                  updatedSections.push({
                                    title: 'Appeal Content',
                                    content: editedLetterContent
                                  });
                                }

                                setAppealLetter({ ...appealLetter, sections: updatedSections });
                                setIsEditingLetter(false);
                                setHasLocalEdits(false);
                              }}
                              className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                            >
                              <CheckIcon className="w-4 h-4" />
                              Save
                            </button>
                            <button
                              onClick={() => {
                                setIsEditingLetter(false);
                                setHasLocalEdits(false);
                              }}
                              className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                            >
                              <XMarkIcon className="w-4 h-4" />
                              Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => {
                                const fullContent = appealLetter.sections?.map(s =>
                                  `## ${s.title}\n\n${s.content}`
                                ).join('\n\n---\n\n') || '';
                                setEditedLetterContent(fullContent);
                                setIsEditingLetter(true);
                                setIsLetterAccepted(false);
                              }}
                              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                            >
                              <PencilIcon className="w-4 h-4" />
                              Edit Letter
                            </button>
                            <button
                              onClick={handleRegenerateLetter}
                              disabled={isRegenerating}
                              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50"
                            >
                              {isRegenerating ? (
                                <>
                                  <ArrowPathIcon className="w-5 h-5 animate-spin" />
                                  Regenerating...
                                </>
                              ) : (
                                <>
                                  <ArrowPathIcon className="w-5 h-5" />
                                  Regenerate Letter
                                </>
                              )}
                            </button>
                          </>
                        )}
                      </div>

                      {/* Accept Letter / Generate Package buttons */}
                      {!isEditingLetter && (
                        <div className="flex gap-2">
                          {!isLetterAccepted ? (
                            <button
                              onClick={() => setIsLetterAccepted(true)}
                              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:shadow-lg"
                            >
                              <CheckIcon className="w-4 h-4" />
                              Accept Letter
                            </button>
                          ) : (
                            <button
                              onClick={handleGeneratePackage}
                              disabled={isGeneratingPackage}
                              className="flex items-center gap-2 px-6 py-2 bg-gradient-to-r from-[#fc459d] to-purple-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50"
                            >
                              {isGeneratingPackage ? (
                                <>
                                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                  </svg>
                                  Generating Package...
                                </>
                              ) : (
                                <>
                                  <DocumentIcon className="w-4 h-4" />
                                  Generate Final Package
                                </>
                              )}
                            </button>
                          )}
                        </div>
                      )}
                    </div>

                    <div className="relative space-y-6">
                      {/* Loading overlay during regeneration */}
                      {isRegenerating && (
                        <div className="absolute inset-0 bg-white/80 backdrop-blur-sm z-10 flex items-center justify-center">
                          <div className="text-center">
                            <ArrowPathIcon className="w-12 h-12 text-purple-600 animate-spin mx-auto mb-3" />
                            <p className="text-lg font-medium text-gray-900">Regenerating Letter...</p>
                            <p className="text-sm text-gray-600 mt-1">Analyzing latest evidence and documents</p>
                          </div>
                        </div>
                      )}

                      {/* Letterhead */}
                      <div className="border-b border-gray-200 pb-4">
                        <p className="font-semibold">{appealLetter.provider_letterhead?.name}</p>
                        <p className="text-sm text-gray-600">{appealLetter.provider_letterhead?.address}</p>
                        <p className="text-sm text-gray-600">{appealLetter.provider_letterhead?.phone}</p>
                      </div>

                      {/* RE Block */}
                      <div>
                        <p className="font-semibold">RE: Appeal for Claim {denial.claim_number}</p>
                        <p className="text-sm">Patient: {denial.patient_name}</p>
                        <p className="text-sm">Date of Service: {new Date(denial.service_date).toLocaleDateString()}</p>
                      </div>

                      {/* Letter Body - Edit or View Mode */}
                      {isEditingLetter ? (
                        <div className="border rounded-lg">
                          <textarea
                            value={editedLetterContent}
                            onChange={(e) => {
                              setEditedLetterContent(e.target.value);
                              setHasLocalEdits(true);
                            }}
                            className="w-full h-[600px] p-4 font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 rounded-lg"
                            placeholder="Edit your appeal letter content here using Markdown..."
                          />
                        </div>
                      ) : (
                        <div className="space-y-6">
                          {appealLetter.sections?.map((section, index) => (
                            <div key={index} className="mb-6">
                              <h2 className="text-xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200">
                                {section.title}
                              </h2>
                              <div className="max-w-none text-gray-700 leading-relaxed">
                                <ReactMarkdown
                                  remarkPlugins={[remarkGfm]}
                                  components={{
                                    h1: ({node, ...props}) => <h3 className="text-lg font-bold text-gray-900 mt-6 mb-3" {...props} />,
                                    h2: ({node, ...props}) => <h3 className="text-lg font-bold text-gray-900 mt-6 mb-3" {...props} />,
                                    h3: ({node, ...props}) => <h4 className="text-base font-bold text-gray-800 mt-5 mb-2" {...props} />,
                                    h4: ({node, ...props}) => <h5 className="text-sm font-bold text-gray-800 mt-4 mb-2" {...props} />,
                                    p: ({node, ...props}) => <p className="text-gray-700 mb-4 leading-relaxed" {...props} />,
                                    ul: ({node, ...props}) => <ul className="list-disc pl-6 mb-4 space-y-2 text-gray-700" {...props} />,
                                    ol: ({node, ...props}) => <ol className="list-decimal pl-6 mb-4 space-y-2 text-gray-700" {...props} />,
                                    li: ({node, children, ...props}) => <li className="text-gray-700 leading-relaxed" {...props}>{children}</li>,
                                    strong: ({node, ...props}) => <strong className="font-bold text-gray-900" {...props} />,
                                    em: ({node, ...props}) => <em className="italic" {...props} />,
                                    blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-purple-400 pl-4 py-2 italic text-gray-600 my-4 bg-purple-50 rounded-r" {...props} />,
                                    a: ({node, ...props}) => <a className="text-purple-600 underline hover:text-purple-800" {...props} />,
                                    hr: ({node, ...props}) => <hr className="my-6 border-gray-200" {...props} />,
                                    table: ({node, ...props}) => (
                                      <div className="overflow-x-auto my-6">
                                        <table className="min-w-full divide-y divide-gray-300 border border-gray-300" {...props} />
                                      </div>
                                    ),
                                    thead: ({node, ...props}) => <thead className="bg-gray-50" {...props} />,
                                    tbody: ({node, ...props}) => <tbody className="divide-y divide-gray-200 bg-white" {...props} />,
                                    tr: ({node, ...props}) => <tr className="hover:bg-gray-50" {...props} />,
                                    th: ({node, ...props}) => <th className="px-4 py-3 text-left text-xs font-semibold text-gray-900 uppercase tracking-wider border-r border-gray-200 last:border-r-0" {...props} />,
                                    td: ({node, ...props}) => <td className="px-4 py-3 text-sm text-gray-700 border-r border-gray-200 last:border-r-0 whitespace-normal" {...props} />,
                                  }}
                                >
                                  {section.content}
                                </ReactMarkdown>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Enclosed Documents */}
                      {!isEditingLetter && appealLetter.enclosed_documents && appealLetter.enclosed_documents.length > 0 && (
                        <div className="border-t pt-4">
                          <p className="font-semibold mb-2">Enclosed Documents:</p>
                          <ul className="list-disc list-inside text-sm text-gray-700">
                            {appealLetter.enclosed_documents.map((doc, index) => (
                              <li key={index}>{doc}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Signature */}
                      {!isEditingLetter && (
                        <div className="mt-8 border-t pt-4">
                          <p className="font-semibold">Sincerely,</p>
                          <p className="mt-4">{appealLetter.signature?.name}</p>
                          <p className="text-sm text-gray-600">{appealLetter.signature?.title}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )
            ) : (
              <div className="flex flex-col items-center justify-center h-full p-6">
                <DocumentTextIcon className="w-16 h-16 text-gray-300 mb-4" />
                <p className="text-gray-500 mb-4">No appeal letter generated yet</p>
                {criteriaResults && (
                  <button
                    onClick={handleGenerateAppeal}
                    disabled={isGenerating}
                    className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-xl hover:shadow-lg disabled:opacity-50"
                  >
                    {isGenerating ? (
                      <span className="flex items-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Generating... this may take a minute
                      </span>
                    ) : 'Generate Appeal Letter'}
                  </button>
                )}
              </div>
            )}
          </div>
        );
        })()}
      </div>

      {/* Regenerate Confirmation Dialog */}
      <RegenerateConfirmDialog />
    </div>
  );
};

export default DenialDetail;
