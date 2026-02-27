import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  MagnifyingGlassIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  ChevronUpDownIcon
} from '@heroicons/react/24/outline';
import { denialsAPI, referenceDataAPI } from '../services/api';

const SubmittedAppealsList = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [denials, setDenials] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    status: 'submitted,approved,denied', // Filter for submitted appeals only
    payer: '',
    category: ''
  });
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const [payers, setPayers] = useState([]);
  const [providers, setProviders] = useState([]);

  useEffect(() => {
    referenceDataAPI.getPayers().then(setPayers).catch(() => {});
    referenceDataAPI.getProviders().then(setProviders).catch(() => {});
  }, []);

  useEffect(() => {
    loadDenials();
  }, [filters]);

  // Reload denials when navigating back to this page
  useEffect(() => {
    loadDenials();
  }, [location.key]);

  const loadDenials = async () => {
    try {
      setIsLoading(true);
      const data = await denialsAPI.getAll(filters);
      setDenials(data);
    } catch (error) {
      console.error('Failed to load submitted appeals:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Filter denials by search term
  const filteredDenials = useMemo(() => {
    let result = denials.filter(denial =>
      denial.claim_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      denial.patient_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      denial.payer_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Apply payer filter
    if (filters.payer) {
      result = result.filter(d => d.payer_name === filters.payer);
    }

    // Apply sorting
    if (sortConfig.key) {
      result = [...result].sort((a, b) => {
        let aVal, bVal;

        // Handle pending_amount (which is the denied_amount field)
        if (sortConfig.key === 'pending_amount') {
          aVal = a.denied_amount || 0;
          bVal = b.denied_amount || 0;
        }
        // Handle submission_date
        else if (sortConfig.key === 'submission_date') {
          aVal = a.submitted_at ? new Date(a.submitted_at).getTime() : -Infinity;
          bVal = b.submitted_at ? new Date(b.submitted_at).getTime() : -Infinity;
        }
        // Handle appeal_deadline (date sorting)
        else if (sortConfig.key === 'appeal_deadline') {
          aVal = a.appeal_deadline ? new Date(a.appeal_deadline).getTime() : -Infinity;
          bVal = b.appeal_deadline ? new Date(b.appeal_deadline).getTime() : -Infinity;
        }
        // Handle existing fields
        else {
          aVal = a[sortConfig.key];
          bVal = b[sortConfig.key];

          // Handle null/undefined values
          if (aVal == null) aVal = sortConfig.key === 'win_probability' ? 0 : -Infinity;
          if (bVal == null) bVal = sortConfig.key === 'win_probability' ? 0 : -Infinity;
        }

        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return result;
  }, [denials, searchTerm, filters.payer, sortConfig]);

  // Handle sort click on column headers
  const handleSort = (key) => {
    setSortConfig(prev => {
      if (prev.key === key) {
        // Toggle direction or clear if already descending
        if (prev.direction === 'asc') return { key, direction: 'desc' };
        return { key: null, direction: 'asc' };
      }
      return { key, direction: 'asc' };
    });
  };

  // Get sort icon for column
  const getSortIcon = (key) => {
    if (sortConfig.key !== key) {
      return <ChevronUpDownIcon className="w-4 h-4 ml-1 text-gray-400" />;
    }
    return sortConfig.direction === 'asc'
      ? <ChevronUpIcon className="w-4 h-4 ml-1 text-[#fc459d]" />
      : <ChevronDownIcon className="w-4 h-4 ml-1 text-[#fc459d]" />;
  };

  const getStatusColor = (status) => {
    const colors = {
      submitted: 'bg-green-100 text-green-800',
      approved: 'bg-emerald-100 text-emerald-800',
      denied: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getProbabilityColor = (probability) => {
    if (probability >= 70) return 'text-green-600';
    if (probability >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="w-12 h-12 border-4 border-gray-200 border-t-[#fc459d] rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Submitted Appeals</h1>
        <p className="text-gray-600 mt-1">Track appeals submitted to payers</p>
      </div>

      {/* Actions Bar */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-4 mb-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          {/* Search */}
          <div className="relative flex-1 min-w-[300px]">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by claim number, patient, or payer..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
            />
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mt-4">
          <select
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
          >
            <option value="submitted,approved,denied">All Submitted</option>
            <option value="submitted">Submitted</option>
            <option value="approved">Approved</option>
            <option value="denied">Denied</option>
          </select>

          <select
            value={filters.payer}
            onChange={(e) => setFilters({ ...filters, payer: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
          >
            <option value="">All Payers</option>
            {payers.map(payer => (
              <option key={payer} value={payer}>{payer}</option>
            ))}
          </select>

          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#fc459d]"
          >
            <option value="">All Categories</option>
            <option value="Medical Necessity">Medical Necessity</option>
            <option value="Prior Authorization">Prior Authorization</option>
            <option value="Coding Error">Coding Error</option>
            <option value="Documentation">Documentation</option>
            <option value="Other">Other</option>
          </select>

          {/* Sort Options */}
          <div className="flex items-center gap-2 ml-auto">
            <span className="text-sm text-gray-500">Sort by:</span>
            <button
              onClick={() => handleSort('submission_date')}
              className={`px-3 py-2 border rounded-xl text-sm font-medium transition-all flex items-center ${
                sortConfig.key === 'submission_date'
                  ? 'border-[#fc459d] bg-pink-50 text-[#fc459d]'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Submitted {getSortIcon('submission_date')}
            </button>
            <button
              onClick={() => handleSort('pending_amount')}
              className={`px-3 py-2 border rounded-xl text-sm font-medium transition-all flex items-center ${
                sortConfig.key === 'pending_amount'
                  ? 'border-[#fc459d] bg-pink-50 text-[#fc459d]'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Pending {getSortIcon('pending_amount')}
            </button>
            <button
              onClick={() => handleSort('appeal_deadline')}
              className={`px-3 py-2 border rounded-xl text-sm font-medium transition-all flex items-center ${
                sortConfig.key === 'appeal_deadline'
                  ? 'border-[#fc459d] bg-pink-50 text-[#fc459d]'
                  : 'border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              Deadline {getSortIcon('appeal_deadline')}
            </button>
          </div>
        </div>
      </div>

      {/* Denials Table */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Claim #</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Patient</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Payer</th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Service Date</th>
                <th
                  className="text-left py-4 px-6 text-sm font-semibold text-gray-700 cursor-pointer hover:text-[#fc459d] select-none"
                  onClick={() => handleSort('submission_date')}
                >
                  <div className="flex items-center">
                    Submission Date {getSortIcon('submission_date')}
                  </div>
                </th>
                <th
                  className="text-left py-4 px-6 text-sm font-semibold text-gray-700 cursor-pointer hover:text-[#fc459d] select-none"
                  onClick={() => handleSort('pending_amount')}
                >
                  <div className="flex items-center">
                    Pending Amount {getSortIcon('pending_amount')}
                  </div>
                </th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Category</th>
                <th
                  className="text-left py-4 px-6 text-sm font-semibold text-gray-700 cursor-pointer hover:text-[#fc459d] select-none"
                  onClick={() => handleSort('win_probability')}
                >
                  <div className="flex items-center">
                    Win Probability {getSortIcon('win_probability')}
                  </div>
                </th>
                <th className="text-left py-4 px-6 text-sm font-semibold text-gray-700">Status</th>
                <th
                  className="text-left py-4 px-6 text-sm font-semibold text-gray-700 cursor-pointer hover:text-[#fc459d] select-none"
                  onClick={() => handleSort('appeal_deadline')}
                >
                  <div className="flex items-center">
                    Deadline {getSortIcon('appeal_deadline')}
                  </div>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredDenials.map((denial) => (
                <tr
                  key={denial.id}
                  onClick={() => navigate(`/denials/${denial.id}`)}
                  className="hover:bg-gray-50 cursor-pointer transition-colors duration-200"
                >
                  <td className="py-4 px-6 text-sm font-medium text-gray-900">
                    {denial.claim_number}
                  </td>
                  <td className="py-4 px-6 text-sm text-gray-900">
                    <div>
                      <div className="font-medium">{denial.patient_name}</div>
                      <div className="text-gray-500 text-xs">{denial.patient_id}</div>
                    </div>
                  </td>
                  <td className="py-4 px-6 text-sm text-gray-900">{denial.payer_name}</td>
                  <td className="py-4 px-6 text-sm text-gray-900">
                    {new Date(denial.service_date).toLocaleDateString()}
                  </td>
                  <td className="py-4 px-6 text-sm text-gray-900">
                    {denial.submitted_at ? (
                      new Date(denial.submitted_at).toLocaleDateString()
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="py-4 px-6 text-sm font-semibold text-gray-900">
                    ${(denial.denied_amount || 0).toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2
                    })}
                  </td>
                  <td className="py-4 px-6 text-sm text-gray-900">{denial.denial_category}</td>
                  <td className="py-4 px-6 text-sm">
                    <span className={`font-semibold ${getProbabilityColor(denial.win_probability)}`}>
                      {denial.win_probability}%
                    </span>
                  </td>
                  <td className="py-4 px-6">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(denial.status)}`}>
                      {denial.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-sm text-gray-900">
                    {denial.appeal_deadline ? (
                      <span className={new Date(denial.appeal_deadline) - new Date() < 7 * 24 * 60 * 60 * 1000 ? 'text-red-600 font-semibold' : ''}>
                        {new Date(denial.appeal_deadline).toLocaleDateString()}
                      </span>
                    ) : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredDenials.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No submitted appeals found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SubmittedAppealsList;
