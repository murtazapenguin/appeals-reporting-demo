import {
  mockDashboard, mockPayerMetrics, mockCategoryMetrics, mockTrends,
  mockPayers, mockProviders, mockExecutiveSummary, mockDenialAnalysis,
  mockOverturnRates, mockPatterns, mockOperationalKPIs,
  mockPracticeSummaries, mockPracticeScorecard, mockPracticeComparison,
  mockDenials, mockDocumentsByPatient, mockCriteriaResult, mockAppealLetter,
} from './mockData';

const DEMO = import.meta.env.VITE_DEMO_MODE === 'true';
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://dev-api.penguinai.co/appeals-dev';

const delay = (ms = 300) => new Promise(r => setTimeout(r, ms));

const getHeaders = () => ({
  'Content-Type': 'application/json',
  ...(localStorage.getItem('authToken') && {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  })
});

const authHeader = () => ({
  ...(localStorage.getItem('authToken') && {
    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
  })
});

const checked = async (response, errorMsg) => {
  if (response.status === 401) {
    localStorage.removeItem('authToken');
    window.location.href = '/login';
    throw new Error('Session expired');
  }
  if (!response.ok) throw new Error(errorMsg);
  return response.json();
};

// Authentication APIs
export const authAPI = {
  login: async (email, password) => {
    if (DEMO) {
      await delay(500);
      return { access_token: 'demo-token-' + Date.now(), user: { email, name: 'Demo User' } };
    }
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) throw new Error('Login failed');
    return response.json();
  },

  getMe: async () => {
    if (DEMO) { await delay(); return { email: 'demo@penguinai.com', name: 'Demo User' }; }
    const response = await fetch(`${BASE_URL}/auth/me`, { headers: getHeaders() });
    return checked(response, 'Failed to get user');
  }
};

// Helper: filter mock denials by status, payer, category (DEMO)
function filterMockDenials(list, filters) {
  let out = [...list];
  if (filters.status) {
    const statuses = filters.status.split(',').map(s => s.trim()).filter(Boolean);
    if (statuses.length) out = out.filter(d => statuses.includes(d.status));
  }
  if (filters.payer) out = out.filter(d => d.payer_name === filters.payer);
  if (filters.category) out = out.filter(d => d.denial_category === filters.category);
  return out;
}

// Denials APIs
export const denialsAPI = {
  getAll: async (filters = {}) => {
    if (DEMO) {
      await delay();
      return filterMockDenials(mockDenials, filters);
    }
    const params = new URLSearchParams(filters);
    const response = await fetch(`${BASE_URL}/denials?${params}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch denials');
  },

  getById: async (id) => {
    if (DEMO) {
      await delay();
      const found = mockDenials.find(d => d.id === id);
      return found ?? null;
    }
    const response = await fetch(`${BASE_URL}/denials/${id}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch denial');
  },

  create: async (denialData) => {
    if (DEMO) { await delay(); return { id: 'demo-1', ...denialData }; }
    const response = await fetch(`${BASE_URL}/denials`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(denialData)
    });
    return checked(response, 'Failed to create denial');
  },

  update: async (id, denialData) => {
    if (DEMO) { await delay(); return { id, ...denialData }; }
    const response = await fetch(`${BASE_URL}/denials/${id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(denialData)
    });
    return checked(response, 'Failed to update denial');
  },

  uploadCSV: async (file) => {
    if (DEMO) { await delay(); return { imported_count: 0, failed_count: 0, errors: [], message: 'Demo mode – upload not saved.' }; }
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${BASE_URL}/denials/upload-csv`, {
      method: 'POST',
      headers: authHeader(),
      body: formData
    });
    if (response.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      throw new Error('Session expired');
    }
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed: ${errorText || response.statusText}`);
    }
    return response.json();
  }
};

// Medical Policies APIs
export const medicalPoliciesAPI = {
  getAll: async () => {
    if (DEMO) { await delay(); return []; }
    const response = await fetch(`${BASE_URL}/medical-policies`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch policies');
  },

  lookup: async (payerId, cptCode) => {
    if (DEMO) { await delay(); return null; }
    const response = await fetch(`${BASE_URL}/medical-policies/lookup?payer_id=${payerId}&cpt_code=${cptCode}`, { headers: getHeaders() });
    return checked(response, 'Failed to lookup policy');
  }
};

// Documents APIs
export const documentsAPI = {
  getByDenialId: async (denialId) => {
    if (DEMO) {
      await delay();
      const denial = mockDenials.find(d => d.id === denialId);
      const patientId = denial?.patient_id;
      return patientId ? (mockDocumentsByPatient[patientId] || []) : [];
    }
    const response = await fetch(`${BASE_URL}/documents/denial/${denialId}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch documents');
  },

  getByPatientId: async (patientId) => {
    if (DEMO) {
      await delay();
      return mockDocumentsByPatient[patientId] || [];
    }
    const response = await fetch(`${BASE_URL}/documents/patient/${patientId}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch documents');
  },

  getByDateRange: async (denialId, startDate, endDate) => {
    if (DEMO) { await delay(); return []; }
    const response = await fetch(`${BASE_URL}/documents/denial/${denialId}/date-range?start_date=${startDate}&end_date=${endDate}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch documents');
  },

  getPageImages: async (documentId) => {
    if (DEMO) { await delay(); return []; }
    const response = await fetch(`${BASE_URL}/documents/${documentId}/pages`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch page images');
  },

  getPageCount: async (documentId) => {
    if (DEMO) { await delay(); return 0; }
    const response = await fetch(`${BASE_URL}/documents/${documentId}/page-count`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch page count');
  },

  upload: async (file, denialId, patientId, documentType, documentDate) => {
    if (DEMO) {
      await delay();
      return { _id: 'demo-doc-' + Date.now(), denial_id: denialId, patient_id: patientId, document_type: documentType, document_date: documentDate, document_name: file?.name || 'uploaded.pdf', total_pages: 1 };
    }
    const formData = new FormData();
    formData.append('file', file);
    formData.append('denial_id', denialId);
    formData.append('patient_id', patientId);
    formData.append('document_type', documentType);
    formData.append('document_date', documentDate);

    const response = await fetch(`${BASE_URL}/documents/upload`, {
      method: 'POST',
      headers: authHeader(),
      body: formData
    });
    if (response.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
      throw new Error('Session expired');
    }
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Upload failed: ${errorText || response.statusText}`);
    }
    return response.json();
  }
};

// Polling utility
async function pollUntilReady(fetchFn, intervalMs = 5000, timeoutMs = 300000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const result = await fetchFn();
    if (result) return result;
    await new Promise(r => setTimeout(r, intervalMs));
  }
  throw new Error('Operation timed out');
}

// Criteria Evaluation APIs
export const criteriaAPI = {
  evaluate: async (denialId) => {
    if (DEMO) {
      await delay(600);
      return { ...mockCriteriaResult, denial_id: denialId };
    }
    const response = await fetch(`${BASE_URL}/criteria-evaluation/evaluate/${denialId}`, {
      method: 'POST',
      headers: getHeaders()
    });
    await checked(response, 'Failed to start criteria evaluation');

    return pollUntilReady(async () => {
      const statusRes = await fetch(`${BASE_URL}/criteria-evaluation/status/${denialId}`, { headers: getHeaders() });
      if (statusRes.status === 401) { localStorage.removeItem('authToken'); window.location.href = '/login'; throw new Error('Session expired'); }
      if (!statusRes.ok) return null;
      const status = await statusRes.json();
      if (status.status === 'failed') throw new Error(status.error || 'Criteria evaluation failed');
      if (status.status !== 'completed') return null;
      const res = await fetch(`${BASE_URL}/criteria-evaluation/${denialId}`, { headers: getHeaders() });
      if (!res.ok) throw new Error('Evaluation completed but failed to fetch results');
      const data = await res.json();
      if (!data || !data.criteria) throw new Error('Evaluation completed but results are empty');
      return data;
    }, 5000, 300000);
  },

  getResults: async (denialId) => {
    if (DEMO) {
      await delay();
      return { ...mockCriteriaResult, denial_id: denialId };
    }
    const response = await fetch(`${BASE_URL}/criteria-evaluation/${denialId}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch criteria results');
  },

  getStatus: async (denialId) => {
    if (DEMO) { await delay(); return { status: 'completed' }; }
    const response = await fetch(`${BASE_URL}/criteria-evaluation/status/${denialId}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch evaluation status');
  }
};

// Appeals APIs
export const appealsAPI = {
  generateLetter: async (denialId) => {
    if (DEMO) {
      await delay(800);
      return { ...mockAppealLetter, denial_id: denialId };
    }
    const response = await fetch(`${BASE_URL}/appeals/generate/${denialId}`, {
      method: 'POST',
      headers: getHeaders()
    });
    await checked(response, 'Failed to start appeal letter generation');

    return pollUntilReady(async () => {
      const statusRes = await fetch(`${BASE_URL}/appeals/status/${denialId}`, { headers: getHeaders() });
      if (statusRes.status === 401) { localStorage.removeItem('authToken'); window.location.href = '/login'; throw new Error('Session expired'); }
      if (!statusRes.ok) return null;
      const status = await statusRes.json();
      if (status.status === 'failed') throw new Error(status.error || 'Appeal letter generation failed');
      if (status.status !== 'completed') return null;
      const res = await fetch(`${BASE_URL}/appeals/${denialId}`, { headers: getHeaders() });
      if (!res.ok) throw new Error('Appeal generation completed but failed to fetch results');
      const data = await res.json();
      if (!data || !data.sections) throw new Error('Appeal generation completed but results are empty');
      return data;
    }, 5000, 300000);
  },

  getLetter: async (denialId) => {
    if (DEMO) {
      await delay();
      return { ...mockAppealLetter, denial_id: denialId };
    }
    const response = await fetch(`${BASE_URL}/appeals/${denialId}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch appeal letter');
  },

  getStatus: async (denialId) => {
    if (DEMO) { await delay(); return { status: 'completed' }; }
    const response = await fetch(`${BASE_URL}/appeals/status/${denialId}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch appeal status');
  },

  downloadPDF: async (denialId) => {
    if (DEMO) { await delay(); return new Blob(['Demo mode – no PDF'], { type: 'application/pdf' }); }
    const response = await fetch(`${BASE_URL}/appeals/${denialId}/pdf`, { headers: getHeaders() });
    if (response.status === 401) { localStorage.removeItem('authToken'); window.location.href = '/login'; throw new Error('Session expired'); }
    if (!response.ok) throw new Error('Failed to download PDF');
    return response.blob();
  },

  submit: async (denialId) => {
    if (DEMO) { await delay(); return { success: true, message: 'Demo mode – appeal not actually submitted.' }; }
    const response = await fetch(`${BASE_URL}/appeals/${denialId}/submit`, {
      method: 'POST',
      headers: getHeaders()
    });
    return checked(response, 'Failed to submit appeal');
  },

  generatePackage: async (denialId) => {
    if (DEMO) { await delay(); return { success: true, package_id: 'demo-pkg' }; }
    const response = await fetch(`${BASE_URL}/appeals/${denialId}/generate-package`, {
      method: 'POST',
      headers: getHeaders()
    });
    return checked(response, 'Failed to generate package');
  },

  getPackage: async (denialId) => {
    if (DEMO) { await delay(); return { package_id: 'demo-pkg', documents: [] }; }
    const response = await fetch(`${BASE_URL}/appeals/${denialId}/package`, { headers: getHeaders() });
    return checked(response, 'Failed to get package');
  },

  downloadPackage: async (denialId) => {
    if (DEMO) { await delay(); return new Blob(['Demo mode – no package'], { type: 'application/zip' }); }
    const response = await fetch(`${BASE_URL}/appeals/${denialId}/package/download`, { headers: getHeaders() });
    if (response.status === 401) { localStorage.removeItem('authToken'); window.location.href = '/login'; throw new Error('Session expired'); }
    if (!response.ok) throw new Error('Failed to download package');
    return response.blob();
  }
};

// Questionnaires APIs
export const questionnairesAPI = {
  getAll: async (cptCode = null) => {
    if (DEMO) { await delay(); return []; }
    const params = cptCode ? `?cpt_code=${cptCode}` : '';
    const response = await fetch(`${BASE_URL}/questionnaires${params}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch questionnaires');
  },

  lookup: async (cptCode) => {
    if (DEMO) { await delay(); return null; }
    const response = await fetch(`${BASE_URL}/questionnaires/lookup?cpt_code=${cptCode}`, { headers: getHeaders() });
    return checked(response, 'Failed to lookup questionnaire');
  },

  getById: async (id) => {
    if (DEMO) { await delay(); return null; }
    const response = await fetch(`${BASE_URL}/questionnaires/${id}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch questionnaire');
  }
};

// Reference Data APIs
export const referenceDataAPI = {
  getPayers: async () => {
    if (DEMO) { await delay(); return mockPayers; }
    const response = await fetch(`${BASE_URL}/reference-data/payers`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch payers');
  },

  getProviders: async () => {
    if (DEMO) { await delay(); return mockProviders; }
    const response = await fetch(`${BASE_URL}/reference-data/providers`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch providers');
  }
};

// Metrics APIs
export const metricsAPI = {
  getDashboard: async () => {
    if (DEMO) { await delay(); return mockDashboard; }
    const response = await fetch(`${BASE_URL}/metrics/dashboard`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch dashboard metrics');
  },

  getByPayer: async () => {
    if (DEMO) { await delay(); return mockPayerMetrics; }
    const response = await fetch(`${BASE_URL}/metrics/by-payer`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch payer metrics');
  },

  getByCategory: async () => {
    if (DEMO) { await delay(); return mockCategoryMetrics; }
    const response = await fetch(`${BASE_URL}/metrics/by-category`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch category metrics');
  },

  getTrends: async (months = 12) => {
    if (DEMO) { await delay(); return mockTrends; }
    const response = await fetch(`${BASE_URL}/metrics/trends?months=${months}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch trends');
  }
};

// Reporting APIs
export const reportingAPI = {
  getExecutiveSummary: async (params = {}) => {
    if (DEMO) { await delay(); return mockExecutiveSummary; }
    const qs = new URLSearchParams(params).toString();
    const response = await fetch(`${BASE_URL}/reporting/executive-summary?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch executive summary');
  },

  getDenialAnalysis: async (params = {}) => {
    if (DEMO) { await delay(); return mockDenialAnalysis; }
    const qs = new URLSearchParams(params).toString();
    const response = await fetch(`${BASE_URL}/reporting/denial-analysis?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch denial analysis');
  },

  getOverturnRates: async (params = {}) => {
    if (DEMO) { await delay(); return mockOverturnRates(params.group_by || 'payer'); }
    const qs = new URLSearchParams(params).toString();
    const response = await fetch(`${BASE_URL}/reporting/overturn-rates?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch overturn rates');
  },

  getPatterns: async (params = {}) => {
    if (DEMO) { await delay(); return mockPatterns; }
    const qs = new URLSearchParams(params).toString();
    const response = await fetch(`${BASE_URL}/reporting/patterns?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch patterns');
  },

  getOperationalKPIs: async (params = {}) => {
    if (DEMO) { await delay(); return mockOperationalKPIs; }
    const qs = new URLSearchParams(params).toString();
    const response = await fetch(`${BASE_URL}/reporting/operational-kpis?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch operational KPIs');
  },

  getPracticeSummaries: async () => {
    if (DEMO) { await delay(); return mockPracticeSummaries; }
    const response = await fetch(`${BASE_URL}/reporting/practice-summaries`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch practice summaries');
  },

  getPracticeScorecard: async (name, params = {}) => {
    if (DEMO) { await delay(); return mockPracticeScorecard(name); }
    const qs = new URLSearchParams({ practice: name, ...params }).toString();
    const response = await fetch(`${BASE_URL}/reporting/practice-scorecard?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch practice scorecard');
  },

  getPracticeComparison: async (names, params = {}) => {
    if (DEMO) { await delay(); return mockPracticeComparison(names); }
    const qs = new URLSearchParams({ practices: names.join(','), ...params }).toString();
    const response = await fetch(`${BASE_URL}/reporting/practice-comparison?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch practice comparison');
  },

  getPracticeComparisonInsights: async (names, params = {}) => {
    if (DEMO) { await delay(); return { insights: [] }; }
    const qs = new URLSearchParams({ practices: names.join(','), ...params }).toString();
    const response = await fetch(`${BASE_URL}/reporting/practice-comparison-insights?${qs}`, { headers: getHeaders() });
    return checked(response, 'Failed to fetch comparison insights');
  },
};
