import { useState, useRef } from 'react';
import {
  XMarkIcon,
  CloudArrowUpIcon,
  DocumentIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { DOCUMENT_TYPES } from '../constants/documentTypes';

const DocumentUploadModal = ({
  isOpen,
  onClose,
  onUpload,
  preselectedType = null,
  denialId,
  patientId,
  denial = null
}) => {
  // Calculate smart default date based on denial dates
  const getDefaultDocumentDate = () => {
    if (!denial) return new Date().toISOString().split('T')[0];

    // Default to service_date (when medical service occurred)
    // This is typically the most relevant date for medical documents
    return denial.service_date || denial.denial_date || new Date().toISOString().split('T')[0];
  };

  const [file, setFile] = useState(null);
  const [documentType, setDocumentType] = useState(preselectedType || '');
  const [documentDate, setDocumentDate] = useState(getDefaultDocumentDate());
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const fileInputRef = useRef(null);

  if (!isOpen) return null;

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.pdf')) {
        setError('Only PDF files are supported');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      if (!droppedFile.name.endsWith('.pdf')) {
        setError('Only PDF files are supported');
        return;
      }
      setFile(droppedFile);
      setError(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!documentType) {
      setError('Please select a document type');
      return;
    }

    setIsUploading(true);
    setError(null);
    setUploadProgress(0);

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => Math.min(prev + 10, 90));
      }, 200);

      await onUpload({
        file,
        documentType,
        documentDate,
        denialId,
        patientId
      });

      clearInterval(progressInterval);
      setUploadProgress(100);
      setSuccess(true);

      // Close modal after short delay
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to upload document');
      setUploadProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setDocumentType(preselectedType || '');
    setDocumentDate(getDefaultDocumentDate());
    setError(null);
    setSuccess(false);
    setUploadProgress(0);
    onClose();
  };

  // Helper function to calculate start date (service_date - 90 days)
  const calculateStartDate = (serviceDate) => {
    if (!serviceDate) return null;
    const date = new Date(serviceDate);
    date.setDate(date.getDate() - 90);
    return date.toISOString().split('T')[0];
  };

  // Check if document date is outside evaluation range
  const isDateOutOfRange = (docDate) => {
    if (!denial || !denial.service_date || !denial.denial_date) return false;

    const startDate = calculateStartDate(denial.service_date);
    const endDate = denial.denial_date;

    return docDate < startDate || docDate > endDate;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-lg mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-gray-900">Upload Document</h2>
          <button
            onClick={handleClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* File Drop Zone */}
          <div
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              file
                ? 'border-green-300 bg-green-50'
                : 'border-gray-300 hover:border-[#fc459d] hover:bg-pink-50'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="hidden"
            />

            {file ? (
              <div className="flex flex-col items-center">
                <DocumentIcon className="w-12 h-12 text-green-500 mb-2" />
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500 mt-1">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mb-2" />
                <p className="font-medium text-gray-900">Drop PDF here or click to upload</p>
                <p className="text-sm text-gray-500 mt-1">PDF files only</p>
              </div>
            )}
          </div>

          {/* Document Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Type *
            </label>
            <select
              value={documentType}
              onChange={(e) => setDocumentType(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d] focus:border-transparent"
              required
            >
              <option value="">Select document type...</option>
              {Object.entries(DOCUMENT_TYPES).map(([key, { label }]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          {/* Document Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Document Date
            </label>
            <input
              type="date"
              value={documentDate}
              onChange={(e) => setDocumentDate(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d] focus:border-transparent"
            />
            {denial && denial.service_date && denial.denial_date && (
              <p className="text-xs text-gray-500 mt-1">
                Valid range for evaluation: {calculateStartDate(denial.service_date)} to {denial.denial_date}
              </p>
            )}
            {isDateOutOfRange(documentDate) && (
              <div className="mt-2 bg-amber-50 border border-amber-200 rounded-lg p-3">
                <p className="text-xs text-amber-800">
                  ⚠️ Warning: This date is outside the evaluation range.
                  Documents may not be included in criteria evaluation.
                </p>
              </div>
            )}
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl text-green-700 text-sm flex items-center gap-2">
              <CheckCircleIcon className="w-5 h-5" />
              Document uploaded successfully!
            </div>
          )}

          {/* Upload Progress */}
          {isUploading && (
            <div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-[#fc459d] to-purple-600 h-2 rounded-full transition-all"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-1 text-center">
                Uploading... {uploadProgress}%
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={handleClose}
              className="flex-1 px-4 py-3 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isUploading || !file || !documentType}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-[#fc459d] to-purple-600 text-white font-medium rounded-xl hover:shadow-lg disabled:opacity-50 transition-all"
            >
              {isUploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DocumentUploadModal;
