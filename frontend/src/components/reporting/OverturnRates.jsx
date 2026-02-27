import {
  Box, Card, CardContent, Typography, Chip, Paper, Stack,
  Table, TableHead, TableBody, TableRow, TableCell,
  ToggleButtonGroup, ToggleButton,
} from '@mui/material';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';

const GROUP_OPTIONS = [
  { value: 'payer', label: 'By Payer' },
  { value: 'practice', label: 'By Practice' },
  { value: 'category', label: 'By Category' },
  { value: 'code', label: 'By Denial Code' },
];

const EXTRA_HEADERS = {
  payer: 'Avg Days to Decision',
  practice: 'Most Common Code',
  category: 'Predicted vs Actual',
  code: 'Classification',
};

const rateColor = (r) => (r >= 70 ? 'success' : r >= 50 ? 'warning' : 'error');

const OverturnRates = ({ data, groupBy, onGroupByChange }) => {
  if (!data) return null;

  return (
    <Stack spacing={3}>
      {/* Overall KPI + Group Toggle */}
      <Stack direction={{ xs: 'column', sm: 'row' }} alignItems={{ sm: 'center' }} justifyContent="space-between" spacing={2}>
        <Card sx={{ display: 'inline-flex' }}>
          <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
            <Typography variant="caption" color="text.secondary">Overall Overturn Rate</Typography>
            <Typography variant="h4" fontWeight={700} color={`${rateColor(data.overall_overturn_rate)}.main`}>
              {data.overall_overturn_rate}%
            </Typography>
          </CardContent>
        </Card>

        <ToggleButtonGroup
          value={groupBy}
          exclusive
          onChange={(_e, val) => val && onGroupByChange(val)}
          size="small"
        >
          {GROUP_OPTIONS.map((opt) => (
            <ToggleButton key={opt.value} value={opt.value}>{opt.label}</ToggleButton>
          ))}
        </ToggleButtonGroup>
      </Stack>

      {/* Trend Chart */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Monthly Overturn Rate Trend</Typography>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data.trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} tickFormatter={(v) => `${v}%`} />
            <Tooltip formatter={(v, name) => name === 'overturn_rate' ? `${v}%` : v} />
            <Legend />
            <Line type="monotone" dataKey="overturn_rate" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} name="Overturn Rate %" />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Bar Chart Comparison */}
      {data.rows.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" mb={2}>
            Overturn Rate {GROUP_OPTIONS.find((o) => o.value === groupBy)?.label || ''}
          </Typography>
          <ResponsiveContainer width="100%" height={Math.max(200, data.rows.length * 40)}>
            <BarChart data={data.rows} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} tickFormatter={(v) => `${v}%`} />
              <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(v) => `${v}%`} />
              <Bar dataKey="overturn_rate" fill="#fc459d" radius={[0, 6, 6, 0]} name="Overturn Rate %" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
      )}

      {/* Detail Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Detailed Breakdown</Typography>
        <Box sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Total Appeals</TableCell>
                <TableCell>Overturned</TableCell>
                <TableCell>Overturn Rate</TableCell>
                <TableCell>{EXTRA_HEADERS[groupBy] || ''}</TableCell>
                <TableCell>Recovered</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {data.rows.map((row, i) => (
                <TableRow key={i} hover>
                  <TableCell sx={{ fontWeight: 600 }}>{row.name}</TableCell>
                  <TableCell>{row.total_appeals}</TableCell>
                  <TableCell>{row.overturned}</TableCell>
                  <TableCell>
                    <Chip
                      label={`${row.overturn_rate}%`}
                      size="small"
                      color={rateColor(row.overturn_rate)}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell sx={{ color: 'text.secondary' }}>
                    {row.extra || (row.avg_days_to_decision != null ? `${row.avg_days_to_decision} days` : '—')}
                  </TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>${row.recovered_amount.toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </Paper>
    </Stack>
  );
};

export default OverturnRates;
