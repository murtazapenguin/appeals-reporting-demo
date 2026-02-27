import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, Tabs, Tab, CircularProgress } from '@mui/material';
import ReportFilters from './reporting/ReportFilters';
import ExecutiveSummary from './reporting/ExecutiveSummary';
import DenialAnalysis from './reporting/DenialAnalysis';
import OverturnRates from './reporting/OverturnRates';
import PatternIntelligence from './reporting/PatternIntelligence';
import OperationalKPIs from './reporting/OperationalKPIs';
import { reportingAPI } from '../services/api';

const TABS = [
  { id: 'summary', label: 'Executive Summary' },
  { id: 'denial', label: 'Denial Analysis' },
  { id: 'overturn', label: 'Overturn Rates' },
  { id: 'patterns', label: 'Pattern Intelligence' },
  { id: 'operational', label: 'Operational KPIs' },
];

const Reporting = () => {
  const [activeTab, setActiveTab] = useState('summary');
  const [filters, setFilters] = useState({
    date_from: '',
    date_to: '',
    payers: '',
    practices: '',
    categories: '',
    denial_type: 'all',
  });

  const [summaryData, setSummaryData] = useState(null);
  const [denialData, setDenialData] = useState(null);
  const [overturnData, setOverturnData] = useState(null);
  const [patternData, setPatternData] = useState(null);
  const [operationalData, setOperationalData] = useState(null);
  const [overturnGroupBy, setOverturnGroupBy] = useState('payer');
  const [isLoading, setIsLoading] = useState(false);

  const buildParams = useCallback(() => {
    const params = {};
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    if (filters.payers) params.payers = filters.payers;
    if (filters.practices) params.practices = filters.practices;
    if (filters.categories) params.categories = filters.categories;
    if (filters.denial_type && filters.denial_type !== 'all') params.denial_type = filters.denial_type;
    return params;
  }, [filters]);

  const loadTab = useCallback(async (tab, params) => {
    try {
      switch (tab) {
        case 'summary':
          setSummaryData(await reportingAPI.getExecutiveSummary(params));
          break;
        case 'denial':
          setDenialData(await reportingAPI.getDenialAnalysis(params));
          break;
        case 'overturn':
          setOverturnData(await reportingAPI.getOverturnRates({ ...params, group_by: overturnGroupBy }));
          break;
        case 'patterns':
          setPatternData(await reportingAPI.getPatterns(params));
          break;
        case 'operational':
          setOperationalData(await reportingAPI.getOperationalKPIs(params));
          break;
      }
    } catch (err) {
      console.error(`Failed to load ${tab}:`, err);
    }
  }, [overturnGroupBy]);

  useEffect(() => {
    setIsLoading(true);
    const params = buildParams();
    loadTab(activeTab, params).finally(() => setIsLoading(false));
  }, [activeTab, filters, buildParams, loadTab]);

  useEffect(() => {
    if (activeTab === 'overturn') {
      setIsLoading(true);
      const params = buildParams();
      loadTab('overturn', params).finally(() => setIsLoading(false));
    }
  }, [overturnGroupBy]);

  const handleTabChange = (_event, newValue) => {
    setActiveTab(newValue);
  };

  return (
    <Box p={3}>
      <Box mb={3}>
        <Typography variant="h4" gutterBottom>Reporting &amp; Analytics</Typography>
        <Typography variant="body2" color="text.secondary">
          Denial insights, overturn analysis, and operational metrics
        </Typography>
      </Box>

      <ReportFilters filters={filters} onChange={setFilters} />

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="scrollable"
          scrollButtons="auto"
        >
          {TABS.map((tab) => (
            <Tab key={tab.id} value={tab.id} label={tab.label} />
          ))}
        </Tabs>
      </Box>

      {isLoading ? (
        <Box display="flex" justifyContent="center" py={10}>
          <CircularProgress color="primary" />
        </Box>
      ) : (
        <>
          {activeTab === 'summary' && <ExecutiveSummary data={summaryData} />}
          {activeTab === 'denial' && <DenialAnalysis data={denialData} />}
          {activeTab === 'overturn' && (
            <OverturnRates
              data={overturnData}
              groupBy={overturnGroupBy}
              onGroupByChange={setOverturnGroupBy}
            />
          )}
          {activeTab === 'patterns' && <PatternIntelligence data={patternData} />}
          {activeTab === 'operational' && <OperationalKPIs data={operationalData} />}
        </>
      )}
    </Box>
  );
};

export default Reporting;
