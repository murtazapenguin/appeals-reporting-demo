import { useState } from 'react';
import {
  Box, Card, CardContent, Typography, Stack, Chip, Paper,
  Table, TableHead, TableBody, TableRow, TableCell, TableSortLabel,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts';

const splitColors = {
  Administrative: '#fc459d',
  Clinical: '#7c3aed',
  Other: '#9ca3af',
};

const SplitCard = ({ label, count, totalDenied, overturnRate }) => {
  const rateColor =
    overturnRate >= 70 ? 'success' : overturnRate >= 50 ? 'warning' : 'error';

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <Box
            sx={{
              width: 12, height: 12, borderRadius: '50%',
              bgcolor: splitColors[label] || '#9ca3af',
            }}
          />
          <Typography variant="subtitle1" fontWeight={700}>{label}</Typography>
        </Stack>

        <Stack direction="row" spacing={4}>
          <Box sx={{ minWidth: 80 }}>
            <Typography variant="caption" color="text.secondary">Count</Typography>
            <Typography variant="h6">{count.toLocaleString()}</Typography>
          </Box>
          <Box sx={{ minWidth: 100 }}>
            <Typography variant="caption" color="text.secondary">Total Denied</Typography>
            <Typography variant="h6">${totalDenied.toLocaleString()}</Typography>
          </Box>
          <Box sx={{ minWidth: 80 }}>
            <Typography variant="caption" color="text.secondary">Overturn Rate</Typography>
            <Chip label={`${overturnRate}%`} size="small" color={rateColor} sx={{ mt: 0.5 }} />
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

const preventabilityChip = (p) => {
  const map = { high: 'error', medium: 'warning', low: 'success' };
  return <Chip label={p} size="small" color={map[p] || 'default'} variant="outlined" sx={{ textTransform: 'capitalize' }} />;
};

const classificationChip = (c) => {
  const colorMap = { administrative: '#fc459d', clinical: '#7c3aed' };
  return (
    <Chip
      label={c}
      size="small"
      variant="outlined"
      sx={{ textTransform: 'capitalize', borderColor: colorMap[c] || undefined, color: colorMap[c] || undefined }}
    />
  );
};

const heatChip = (v) => {
  if (v <= 0) return <Typography variant="body2" color="text.disabled">0</Typography>;
  const color = v >= 5 ? 'error' : v >= 3 ? 'warning' : 'default';
  return <Chip label={v} size="small" color={color} variant="outlined" />;
};

const COLUMNS = [
  { key: 'code', label: 'Code' },
  { key: 'description', label: 'Description' },
  { key: 'count', label: 'Count' },
  { key: 'total_denied', label: 'Total Denied' },
  { key: 'overturn_rate', label: 'Overturn Rate' },
  { key: 'classification', label: 'Type' },
  { key: 'preventability', label: 'Preventability' },
];

const DenialAnalysis = ({ data }) => {
  const [sortKey, setSortKey] = useState('count');
  const [sortDir, setSortDir] = useState('desc');

  if (!data) return null;

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  const sortedCodes = [...data.code_breakdown].sort((a, b) => {
    const av = a[sortKey] ?? 0;
    const bv = b[sortKey] ?? 0;
    return sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
  });

  return (
    <Stack spacing={3}>
      {/* Admin / Clinical / Other Split */}
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, lg: 4 }}>
          <SplitCard
            label="Administrative"
            count={data.admin_split.count}
            totalDenied={data.admin_split.total_denied}
            overturnRate={data.admin_split.overturn_rate}
          />
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <SplitCard
            label="Clinical"
            count={data.clinical_split.count}
            totalDenied={data.clinical_split.total_denied}
            overturnRate={data.clinical_split.overturn_rate}
          />
        </Grid>
        <Grid size={{ xs: 12, lg: 4 }}>
          <SplitCard
            label="Other"
            count={data.other_split.count}
            totalDenied={data.other_split.total_denied}
            overturnRate={data.other_split.overturn_rate}
          />
        </Grid>
      </Grid>

      {/* Denial Code Breakdown Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Denial Code Breakdown</Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                {COLUMNS.map((col) => (
                  <TableCell key={col.key}>
                    <TableSortLabel
                      active={sortKey === col.key}
                      direction={sortKey === col.key ? sortDir : 'asc'}
                      onClick={() => handleSort(col.key)}
                    >
                      {col.label}
                    </TableSortLabel>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {sortedCodes.map((row, i) => (
                <TableRow key={i} hover>
                  <TableCell sx={{ fontWeight: 600 }}>{row.code}</TableCell>
                  <TableCell sx={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {row.description || '—'}
                  </TableCell>
                  <TableCell>{row.count}</TableCell>
                  <TableCell>${row.total_denied.toLocaleString()}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${row.overturn_rate}%`}
                      size="small"
                      color={row.overturn_rate >= 70 ? 'success' : row.overturn_rate >= 50 ? 'warning' : 'error'}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>{classificationChip(row.classification)}</TableCell>
                  <TableCell>{preventabilityChip(row.preventability)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </Paper>

      {/* Procedure Code Matrix */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Procedure Code Denial Matrix</Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>CPT Code</TableCell>
                <TableCell>Total</TableCell>
                <TableCell>Medical Necessity</TableCell>
                <TableCell>Prior Auth</TableCell>
                <TableCell>Coding Error</TableCell>
                <TableCell>Documentation</TableCell>
                <TableCell>Other</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.procedure_matrix.map((row, i) => (
                <TableRow key={i} hover>
                  <TableCell sx={{ fontWeight: 600 }}>{row.procedure_code}</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>{row.total}</TableCell>
                  {[row.medical_necessity, row.prior_authorization, row.coding_error, row.documentation, row.other].map((v, j) => (
                    <TableCell key={j}>{heatChip(v)}</TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </Paper>

      {/* Diagnosis Codes Chart */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Top Diagnosis Codes in Denied Claims</Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data.top_diagnosis_codes} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tick={{ fontSize: 12 }} />
            <YAxis type="category" dataKey="code" width={100} tick={{ fontSize: 11 }} />
            <Tooltip />
            <Bar dataKey="count" fill="#7c3aed" radius={[0, 6, 6, 0]} name="Occurrences" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>
    </Stack>
  );
};

export default DenialAnalysis;
