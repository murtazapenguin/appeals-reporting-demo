import { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Stack, Chip, Paper,
  Table, TableHead, TableBody, TableRow, TableCell, TableSortLabel,
} from '@mui/material';
import { ShieldCheckIcon, ExclamationTriangleIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

const SplitCard = ({ label, count, totalDenied, overturnRate, recovered, Icon, iconColor }) => {
  const rateColor = overturnRate >= 65 ? 'success' : overturnRate >= 45 ? 'warning' : 'error';
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Stack direction="row" spacing={1} alignItems="center" mb={1.5}>
          <Icon style={{ width: 20, height: 20, color: iconColor }} />
          <Typography variant="subtitle2">{label}</Typography>
        </Stack>
        <Stack direction="row" spacing={3} flexWrap="wrap" useFlexGap>
          <Box sx={{ minWidth: 70 }}>
            <Typography variant="caption" color="text.secondary">Count</Typography>
            <Typography variant="h6">{count.toLocaleString()}</Typography>
          </Box>
          <Box sx={{ minWidth: 90 }}>
            <Typography variant="caption" color="text.secondary">Total Denied</Typography>
            <Typography variant="h6">${totalDenied.toLocaleString()}</Typography>
          </Box>
          <Box sx={{ minWidth: 90 }}>
            <Typography variant="caption" color="text.secondary">Recovered</Typography>
            <Typography variant="h6" color="success.main">${(recovered || 0).toLocaleString()}</Typography>
          </Box>
          <Box sx={{ minWidth: 70 }}>
            <Typography variant="caption" color="text.secondary">Overturn Rate</Typography>
            <Chip label={`${overturnRate}%`} size="small" color={rateColor} sx={{ mt: 0.5 }} />
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

const COLUMNS = [
  { key: 'code', label: 'Code' },
  { key: 'description', label: 'Description' },
  { key: 'count', label: 'Count' },
  { key: 'total_denied', label: 'Total Denied' },
  { key: 'recovered', label: 'Recovered' },
  { key: 'overturn_rate', label: 'Overturn Rate' },
  { key: 'classification', label: 'Type' },
  { key: 'preventability', label: 'Preventability' },
];

const DenialAnalysis = ({ data }) => {
  const [sortConfig, setSortConfig] = useState({ key: 'count', direction: 'desc' });

  if (!data) return null;

  const handleSort = (key) => {
    setSortConfig((prev) =>
      prev.key === key
        ? { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' }
        : { key, direction: 'desc' }
    );
  };

  const sorted = [...(data.code_breakdown || [])].sort((a, b) => {
    const m = sortConfig.direction === 'asc' ? 1 : -1;
    if (typeof a[sortConfig.key] === 'number') return (a[sortConfig.key] - b[sortConfig.key]) * m;
    return String(a[sortConfig.key] || '').localeCompare(String(b[sortConfig.key] || '')) * m;
  });

  const rateColor = (r) => (r >= 65 ? 'success' : r >= 45 ? 'warning' : 'error');
  const prevColor = (p) => (p === 'high' ? 'error' : p === 'medium' ? 'warning' : 'default');

  return (
    <Box>
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, gap: 2, mb: 3 }}>
        <SplitCard
          label="Administrative"
          count={data.admin_split?.count || 0}
          totalDenied={data.admin_split?.total_denied || 0}
          overturnRate={data.admin_split?.overturn_rate || 0}
          recovered={data.admin_split?.recovered || 0}
          Icon={ShieldCheckIcon}
          iconColor="#7c3aed"
        />
        <SplitCard
          label="Clinical"
          count={data.clinical_split?.count || 0}
          totalDenied={data.clinical_split?.total_denied || 0}
          overturnRate={data.clinical_split?.overturn_rate || 0}
          recovered={data.clinical_split?.recovered || 0}
          Icon={ExclamationTriangleIcon}
          iconColor="#ef4444"
        />
        <SplitCard
          label="Other"
          count={data.other_split?.count || 0}
          totalDenied={data.other_split?.total_denied || 0}
          overturnRate={data.other_split?.overturn_rate || 0}
          recovered={data.other_split?.recovered || 0}
          Icon={QuestionMarkCircleIcon}
          iconColor="#9ca3af"
        />
      </Box>

      <Card>
        <CardContent>
          <Typography variant="subtitle1" fontWeight={700} gutterBottom>Denial Code Breakdown</Typography>
          <Box sx={{ overflowX: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {COLUMNS.map((col) => (
                    <TableCell key={col.key}>
                      <TableSortLabel
                        active={sortConfig.key === col.key}
                        direction={sortConfig.key === col.key ? sortConfig.direction : 'desc'}
                        onClick={() => handleSort(col.key)}
                      >
                        {col.label}
                      </TableSortLabel>
                    </TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {sorted.map((row) => (
                  <TableRow key={row.code} hover>
                    <TableCell sx={{ fontWeight: 600 }}>{row.code}</TableCell>
                    <TableCell sx={{ maxWidth: 220, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {row.description}
                    </TableCell>
                    <TableCell>{row.count}</TableCell>
                    <TableCell>${row.total_denied.toLocaleString()}</TableCell>
                    <TableCell sx={{ color: 'success.main', fontWeight: 600 }}>
                      ${(row.recovered || 0).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Chip label={`${row.overturn_rate}%`} size="small" color={rateColor(row.overturn_rate)} />
                    </TableCell>
                    <TableCell>
                      <Chip label={row.classification} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Chip label={row.preventability} size="small" color={prevColor(row.preventability)} variant="outlined" />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DenialAnalysis;
