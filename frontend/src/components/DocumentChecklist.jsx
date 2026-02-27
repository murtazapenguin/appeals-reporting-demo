import { useState } from 'react';
import {
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline';
import { REQUIRED_DOCUMENTS, DOCUMENT_CATEGORIES } from '../constants/documentRequirements';

const DocumentChecklist = ({
  documents = [],
  onUploadClick,
  onRerunEvaluation,
  isEvaluating = false
}) => {
  // Check which document types are present
  const presentDocTypes = new Set(documents.map(d => d.document_type));

  // Calculate completion stats
  const requiredDocs = REQUIRED_DOCUMENTS.filter(d => d.required);
  const requiredMet = requiredDocs.filter(d => presentDocTypes.has(d.id)).length;
  const totalRequired = requiredDocs.length;
  const completionPercent = Math.round((requiredMet / totalRequired) * 100);

  // Group by category
  const groupedDocs = DOCUMENT_CATEGORIES.map(category => ({
    category,
    docs: REQUIRED_DOCUMENTS.filter(d => d.category === category)
  }));

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h3 className="text-lg font-bold text-gray-900">Document Checklist</h3>
        <p className="text-sm text-gray-500 mt-1">
          {requiredMet} of {totalRequired} required documents
        </p>

        {/* Progress bar */}
        <div className="mt-3">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${
                completionPercent === 100
                  ? 'bg-green-500'
                  : completionPercent >= 50
                  ? 'bg-yellow-500'
                  : 'bg-red-500'
              }`}
              style={{ width: `${completionPercent}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 mt-1 text-right">{completionPercent}% complete</p>
        </div>
      </div>

      {/* Checklist */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-6">
          {groupedDocs.map(({ category, docs }) => (
            <div key={category}>
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                {category}
              </h4>
              <div className="space-y-2">
                {docs.map(doc => {
                  const isPresent = presentDocTypes.has(doc.id);
                  const isRequired = doc.required;

                  return (
                    <div
                      key={doc.id}
                      className={`flex items-start gap-3 p-3 rounded-lg border ${
                        isPresent
                          ? 'border-green-200 bg-green-50'
                          : isRequired
                          ? 'border-red-200 bg-red-50'
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      {/* Status icon */}
                      <div className="flex-shrink-0 mt-0.5">
                        {isPresent ? (
                          <CheckCircleIcon className="w-5 h-5 text-green-500" />
                        ) : isRequired ? (
                          <XCircleIcon className="w-5 h-5 text-red-500" />
                        ) : (
                          <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
                        )}
                      </div>

                      {/* Label */}
                      <div className="flex-1 min-w-0">
                        <p className={`text-sm ${isPresent ? 'text-green-800' : 'text-gray-700'}`}>
                          {doc.label}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          {isRequired && !isPresent && (
                            <span className="text-xs font-medium text-red-600">Required</span>
                          )}
                          {!isRequired && (
                            <span className="text-xs text-gray-500">Optional</span>
                          )}
                        </div>
                      </div>

                      {/* Upload button for missing docs */}
                      {!isPresent && (
                        <button
                          onClick={() => onUploadClick?.(doc.id)}
                          className="flex-shrink-0 p-1.5 text-gray-400 hover:text-[#fc459d] hover:bg-pink-50 rounded-lg transition-colors"
                          title="Upload document"
                        >
                          <CloudArrowUpIcon className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Re-run Evaluation Button */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={onRerunEvaluation}
          disabled={isEvaluating}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-[#fc459d] to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg disabled:opacity-50 transition-all"
        >
          <ArrowPathIcon className={`w-5 h-5 ${isEvaluating ? 'animate-spin' : ''}`} />
          {isEvaluating ? 'Evaluating...' : 'Re-run Evidence Review'}
        </button>
      </div>
    </div>
  );
};

export default DocumentChecklist;
