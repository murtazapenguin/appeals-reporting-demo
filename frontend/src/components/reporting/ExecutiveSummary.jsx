import {
  Box, Card, CardContent, Typography, Avatar, Paper, Stack,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  AreaChart, Area, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import {
  DocumentTextIcon, ArrowPathIcon, CurrencyDollarIcon,
  ClockIcon, ShieldExclamationIcon,
} from '@heroicons/react/24/outline';

const palette = {
  blue: { bg: '#eff6ff', fg: '#2563eb' },
  green: { bg: '#f0fdf4', fg: '#16a34a' },
  purple: { bg: '#f5f3ff', fg: '#7c3aed' },
  orange: { bg: '#fff7ed', fg: '#ea580c' },
  red: { bg: '#fef2f2', fg: '#dc2626' },
};

const ExecutiveSummary = ({ data }) => {
  if (!data) return null;

  const cards = [
    {
      title: 'Total Denials',
      value: data.total_denials.toLocaleString(),
      Icon: DocumentTextIcon,
      color: palette.blue,
    },
    {
      title: 'Overall Overturn Rate',
      value: `${data.overall_overturn_rate}%`,
      subtitle: 'of appealed claims overturned',
      Icon: ArrowPathIcon,
      color: palette.green,
    },
    {
      title: 'Total Recovered',
      value: `$${data.total_recovered.toLocaleString()}`,
      Icon: CurrencyDollarIcon,
      color: palette.purple,
    },
    {
      title: 'Avg Resolution Time',
      value: data.avg_resolution_days != null ? `${data.avg_resolution_days} days` : '—',
      subtitle: 'from denial to outcome',
      Icon: ClockIcon,
      color: palette.orange,
    },
    {
      title: 'Preventable Rate',
      value: `${data.preventable_rate}%`,
      subtitle: 'of denials are preventable',
      Icon: ShieldExclamationIcon,
      color: palette.red,
    },
  ];

  return (
    <Stack spacing={3}>
      {/* KPI Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(5, 1fr)' },
          gap: 2,
        }}
      >
        {cards.map((c, i) => (
          <Card key={i} sx={{ height: '100%' }}>
            <CardContent>
              <Avatar
                variant="rounded"
                sx={{ bgcolor: c.color.bg, width: 40, height: 40, mb: 1.5 }}
              >
                <c.Icon style={{ width: 20, height: 20, color: c.color.fg }} />
              </Avatar>
              <Typography variant="caption" color="text.secondary" display="block">
                {c.title}
              </Typography>
              <Typography variant="h5" mt={0.5}>{c.value}</Typography>
              {c.subtitle && (
                <Typography variant="caption" color="text.secondary">{c.subtitle}</Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* Charts Row 1 */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Denial Volume by Type</Typography>
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={data.volume_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="clinical" stackId="1" stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.6} name="Clinical" />
                <Area type="monotone" dataKey="administrative" stackId="1" stroke="#fc459d" fill="#fc459d" fillOpacity={0.6} name="Administrative" />
                <Area type="monotone" dataKey="other" stackId="1" stroke="#94a3b8" fill="#94a3b8" fillOpacity={0.4} name="Other" />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Recovery Trend</Typography>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.recovery_trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`} />
                <Tooltip formatter={(v) => `$${v.toLocaleString()}`} />
                <Line type="monotone" dataKey="recovered_amount" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} name="Recovered" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Charts Row 2 */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Top 5 Denial Codes</Typography>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={data.top_denial_codes} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="name" width={70} tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#fc459d" radius={[0, 6, 6, 0]} name="Count" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={2}>Top 5 Payers by Denial Volume</Typography>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={data.top_payers} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" tick={{ fontSize: 12 }} />
                <YAxis type="category" dataKey="name" width={120} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="count" fill="#7c3aed" radius={[0, 6, 6, 0]} name="Denials" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
};

export default ExecutiveSummary;
