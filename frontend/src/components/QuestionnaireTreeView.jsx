import { useState } from 'react';
import {
  CheckCircleIcon,
  XCircleIcon,
  ChevronRightIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

const LOGIC_BADGES = {
  AND: { label: 'ALL required', bg: 'bg-blue-100', text: 'text-blue-700' },
  OR: { label: 'ANY one', bg: 'bg-green-100', text: 'text-green-700' },
  NOR: { label: 'NONE allowed', bg: 'bg-red-100', text: 'text-red-700' },
  AT_LEAST_N: { label: 'At least', bg: 'bg-purple-100', text: 'text-purple-700' },
};

const LogicBadge = ({ logic, requiredCount }) => {
  const badge = LOGIC_BADGES[logic?.toUpperCase()] || LOGIC_BADGES.AND;
  const label = logic?.toUpperCase() === 'AT_LEAST_N'
    ? `${badge.label} ${requiredCount || '?'}`
    : badge.label;

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${badge.bg} ${badge.text}`}>
      {label}
    </span>
  );
};

const TreeNode = ({ node, depth = 0, defaultExpanded = true, onEvidenceClick }) => {
  const [expanded, setExpanded] = useState(defaultExpanded && depth < 2);
  const isLeaf = node.evaluatable && (!node.subcriteria || node.subcriteria.length === 0);
  const hasChildren = node.subcriteria && node.subcriteria.length > 0;

  // Count met/total for this subtree
  const countLeaves = (n) => {
    if (n.evaluatable && (!n.subcriteria || n.subcriteria.length === 0)) {
      return { met: n.met ? 1 : 0, total: 1 };
    }
    let met = 0, total = 0;
    for (const sc of (n.subcriteria || [])) {
      const r = countLeaves(sc);
      met += r.met;
      total += r.total;
    }
    return { met, total };
  };

  const stats = hasChildren ? countLeaves(node) : null;

  if (isLeaf) {
    return (
      <div className={`ml-${Math.min(depth * 4, 16)} mb-2`} style={{ marginLeft: `${depth * 1.25}rem` }}>
        <div className={`rounded-lg border p-3 ${
          node.met ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
        }`}>
          <div className="flex items-start gap-2">
            {node.met ? (
              <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
            ) : (
              <XCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">{node.criteria}</p>
              <span className={`inline-block mt-1 text-xs font-semibold px-2 py-0.5 rounded ${
                node.met ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {node.met ? 'MET' : 'NOT MET'}
              </span>

              {/* Evidence cards — grouped by document + page */}
              {node.evidence && node.evidence.length > 0 && (() => {
                // Group evidence by document_name + page
                const groups = [];
                const groupMap = new Map();
                for (const ev of node.evidence) {
                  const key = `${ev.document_name}::${ev.page}`;
                  if (!groupMap.has(key)) {
                    const group = { ...ev, allBboxes: [ev.bbox], allTexts: [ev.text] };
                    groupMap.set(key, group);
                    groups.push(group);
                  } else {
                    const group = groupMap.get(key);
                    group.allBboxes.push(ev.bbox);
                    if (ev.text && !group.allTexts.includes(ev.text)) {
                      group.allTexts.push(ev.text);
                    }
                  }
                }

                return (
                  <div className="mt-2 space-y-1.5">
                    {groups.map((group, idx) => (
                      <button
                        key={idx}
                        onClick={() => onEvidenceClick && onEvidenceClick(group)}
                        className="w-full text-left p-2 rounded border border-gray-200 bg-white hover:border-[#fc459d] hover:shadow-sm transition-all"
                      >
                        <div className="flex items-center justify-between mb-0.5">
                          <span className="text-xs font-semibold text-[#fc459d] truncate">
                            {group.document_name}
                          </span>
                          <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                            Page {group.page}{group.allBboxes.length > 1 ? ` (${group.allBboxes.length} highlights)` : ''}
                          </span>
                        </div>
                        <p className="text-xs text-gray-700 line-clamp-2">
                          &ldquo;{group.allTexts[0]}&rdquo;
                        </p>
                      </button>
                    ))}
                  </div>
                );
              })()}

              {/* Explanation for not-met */}
              {!node.met && node.explanation && (
                <p className="mt-1.5 text-xs text-gray-500 italic">{node.explanation}</p>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Branch node
  return (
    <div className="mb-1" style={{ marginLeft: `${depth * 1.25}rem` }}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full text-left flex items-center gap-2 py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors group"
      >
        {hasChildren && (
          expanded
            ? <ChevronDownIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
            : <ChevronRightIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
        )}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-gray-900 truncate">
              {node.criteria}
            </span>
            {node.logic && <LogicBadge logic={node.logic} requiredCount={node.required_count} />}
            {node.met !== undefined && node.met !== null && (
              node.met
                ? <CheckCircleIcon className="w-4 h-4 text-green-500 flex-shrink-0" />
                : <XCircleIcon className="w-4 h-4 text-red-500 flex-shrink-0" />
            )}
          </div>
          {stats && (
            <p className="text-xs text-gray-500 mt-0.5">
              {stats.met}/{stats.total} criteria met
            </p>
          )}
        </div>
      </button>

      {/* Context info */}
      {expanded && node.context && node.context.length > 0 && (
        <div className="ml-6 mb-2 px-3 py-2 bg-gray-50 rounded-lg border-l-2 border-gray-300">
          {node.context.map((ctx, i) => (
            <p key={i} className="text-xs text-gray-600">{ctx}</p>
          ))}
        </div>
      )}

      {/* Children */}
      {expanded && hasChildren && (
        <div>
          {node.subcriteria.map((sc, i) => (
            <TreeNode
              key={sc.question || i}
              node={sc}
              depth={depth + 1}
              defaultExpanded={depth < 1}
              onEvidenceClick={onEvidenceClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const QuestionnaireTreeView = ({ criteriaTree, guidelineName, criteriaMet, totalCriteria, winProbability, onEvidenceClick }) => {
  if (!criteriaTree) return null;

  return (
    <div className="p-4">
      {/* Summary Header */}
      <div className="bg-gradient-to-r from-[#fc459d] to-purple-600 rounded-xl p-4 mb-4 text-white">
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-lg font-bold">Questionnaire Evaluation</h2>
          {criteriaTree.met !== undefined && (
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${
              criteriaTree.met ? 'bg-green-400/30 text-green-100' : 'bg-red-400/30 text-red-100'
            }`}>
              {criteriaTree.met ? 'APPROVED' : 'NOT MET'}
            </span>
          )}
        </div>
        {guidelineName && (
          <p className="text-sm opacity-90 mb-2">{guidelineName}</p>
        )}
        <div className="flex items-center justify-between">
          <span className="text-2xl font-bold">
            {criteriaMet}/{totalCriteria}
          </span>
          <span className="text-sm opacity-90">
            Win Probability: {winProbability}%
          </span>
        </div>
        <div className="w-full bg-white/30 rounded-full h-2 mt-2">
          <div
            className="bg-white h-2 rounded-full transition-all"
            style={{ width: `${winProbability}%` }}
          />
        </div>
      </div>

      {/* Tree */}
      <div className="space-y-1">
        <TreeNode
          node={criteriaTree}
          depth={0}
          defaultExpanded={true}
          onEvidenceClick={onEvidenceClick}
        />
      </div>
    </div>
  );
};

export default QuestionnaireTreeView;
