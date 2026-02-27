import {
  Box, Card, CardContent, Typography, Chip, Paper, Stack, Alert, Avatar,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
  ClockIcon, BoltIcon, CpuChipIcon,
  UserGroupIcon, DocumentMagnifyingGlassIcon, ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';

const OperationalKPIs = ({ data }) => {
  if (!data) return null;

  const metrics = [
    {
      title: 'Avg Processing Time',
      value: data.avg_processing_days != null ? `${data.avg_processing_days} days` : '—',
      subtitle: 'Denial creation to appeal submission',
      Icon: ClockIcon,
      available: data.avg_processing_days != null,
    },
    {
      title: 'Avg Letter Generation',
      value: data.avg_letter_generation_seconds != null ? `${data.avg_letter_generation_seconds}s` : '—',
      subtitle: 'AI draft generation time',
      Icon: BoltIcon,
      available: data.avg_letter_generation_seconds != null,
    },
    {
      title: 'AI Auto-Approval Rate',
      value: data.ai_auto_approval_rate != null ? `${data.ai_auto_approval_rate}%` : '—',
      subtitle: 'Letters accepted without edits',
      Icon: CpuChipIcon,
      available: data.ai_auto_approval_rate != null,
    },
    {
      title: 'Appeals per Week',
      value: data.appeals_per_week != null ? data.appeals_per_week : '—',
      subtitle: 'Average throughput',
      Icon: UserGroupIcon,
      available: data.appeals_per_week != null,
    },
    {
      title: 'Avg Review Time',
      value: data.avg_review_hours != null ? `${data.avg_review_hours}h` : '—',
      subtitle: 'Per appeal review duration',
      Icon: DocumentMagnifyingGlassIcon,
      available: data.avg_review_hours != null,
    },
    {
      title: 'FTE Capacity Gain',
      value: data.fte_capacity_gain != null ? `${data.fte_capacity_gain}x` : '—',
      subtitle: 'Estimated AI efficiency multiplier',
      Icon: ArrowTrendingUpIcon,
      available: data.fte_capacity_gain != null,
    },
  ];

  return (
    <Stack spacing={3}>
      {/* Metric Cards */}
      <Grid container spacing={2}>
        {metrics.map((m, i) => (
          <Grid key={i} size={{ xs: 12, sm: 6, lg: 4, xl: 2 }}>
            <Card sx={{ height: '100%', opacity: m.available ? 1 : 0.6 }}>
              <CardContent>
                <Stack direction="row" alignItems="flex-start" justifyContent="space-between" mb={1.5}>
                  <Avatar variant="rounded" sx={{ bgcolor: '#f9fafb', width: 40, height: 40 }}>
                    <m.Icon style={{ width: 20, height: 20, color: '#4b5563' }} />
                  </Avatar>
                  {!m.available && (
                    <Chip label="Coming Soon" size="small" variant="outlined" sx={{ fontSize: '0.65rem' }} />
                  )}
                </Stack>
                <Typography variant="caption" color="text.secondary" display="block">{m.title}</Typography>
                <Typography variant="h5" mt={0.5}>{m.value}</Typography>
                {m.subtitle && (
                  <Typography variant="caption" color="text.secondary">{m.subtitle}</Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Processing Time Trend</Typography>
            {data.processing_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={data.processing_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} label={{ value: 'Days', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }} />
                  <Tooltip formatter={(v) => `${v} days`} />
                  <Line type="monotone" dataKey="avg_days" stroke="#fc459d" strokeWidth={2} dot={{ r: 3 }} name="Avg Days" />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <Box display="flex" alignItems="center" justifyContent="center" height={280}>
                <Typography variant="body2" color="text.secondary">
                  No processing time data available yet.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Weekly Throughput</Typography>
            {data.throughput_trend.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data.throughput_trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#7c3aed" radius={[4, 4, 0, 0]} name="Appeals" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <Box display="flex" alignItems="center" justifyContent="center" height={280}>
                <Typography variant="body2" color="text.secondary">
                  No throughput data available yet.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Info Banner */}
      <Alert severity="info" variant="outlined">
        <strong>Note:</strong> Some operational metrics (AI letter generation time, auto-approval rate, review time, FTE capacity gain)
        require timing instrumentation that will be added in a future update. Currently available metrics are computed from
        existing timestamp data in the system.
      </Alert>
    </Stack>
  );
};

export default OperationalKPIs;
