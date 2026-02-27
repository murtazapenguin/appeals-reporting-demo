import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Avatar, Button,
  Table, TableHead, TableBody, TableRow, TableCell,
  Chip, CircularProgress, Paper, Stack,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import {
  CurrencyDollarIcon, ClockIcon,
  CheckCircleIcon, ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
import { metricsAPI } from '../services/api';

const iconColor = {
  blue: { bg: '#eff6ff', fg: '#2563eb' },
  red: { bg: '#fef2f2', fg: '#dc2626' },
  green: { bg: '#f0fdf4', fg: '#16a34a' },
  purple: { bg: '#f5f3ff', fg: '#7c3aed' },
  pink: { bg: '#fdf2f8', fg: '#fc459d' },
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [payerMetrics, setPayerMetrics] = useState([]);
  const [categoryMetrics, setCategoryMetrics] = useState([]);
  const [trends, setTrends] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [dashboardData, payerData, categoryData, trendsData] = await Promise.all([
        metricsAPI.getDashboard(),
        metricsAPI.getByPayer(),
        metricsAPI.getByCategory(),
        metricsAPI.getTrends(12),
      ]);
      setMetrics(dashboardData);
      setPayerMetrics(payerData);
      setCategoryMetrics(categoryData);
      setTrends(trendsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Box display="flex" alignItems="center" justifyContent="center" height="80vh">
        <CircularProgress color="primary" />
      </Box>
    );
  }

  const metricCards = [
    {
      title: 'Total Open Denials',
      value: metrics?.total_open_denials || 0,
      amount: `$${(metrics?.total_at_risk || 0).toLocaleString()}`,
      subtitle: 'at risk',
      Icon: CurrencyDollarIcon,
      palette: iconColor.blue,
    },
    {
      title: 'Urgent Appeals',
      value: metrics?.urgent_appeals || 0,
      subtitle: '≤7 days deadline',
      Icon: ClockIcon,
      palette: iconColor.red,
    },
    {
      title: 'High Probability',
      value: metrics?.high_probability_count || 0,
      subtitle: '≥70% win rate',
      Icon: CheckCircleIcon,
      palette: iconColor.green,
    },
    {
      title: 'Recovered This Month',
      value: `$${(metrics?.recovered_this_month || 0).toLocaleString()}`,
      subtitle: `${metrics?.recovery_rate_this_month || 0}% success rate`,
      Icon: ArrowTrendingUpIcon,
      palette: iconColor.purple,
    },
    {
      title: 'Total Recovered (YTD)',
      value: `$${(metrics?.total_recovered_ytd || 0).toLocaleString()}`,
      subtitle: `${metrics?.total_claims_recovered || 0} claims`,
      Icon: ArrowTrendingUpIcon,
      palette: iconColor.pink,
    },
  ];

  const rateChipColor = (rate) => {
    if (rate >= 70) return 'success';
    if (rate >= 50) return 'warning';
    return 'error';
  };

  return (
    <Box p={3}>
      <Box mb={4}>
        <Typography variant="h4" gutterBottom>Dashboard</Typography>
        <Typography variant="body2" color="text.secondary">
          Monitor your denial management and revenue recovery
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} mb={4}>
        {metricCards.map((card, i) => (
          <Grid key={i} size={{ xs: 12, sm: 6, md: 4, xl: 2.4 }}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Avatar
                  sx={{ bgcolor: card.palette.bg, width: 44, height: 44, mb: 2 }}
                  variant="rounded"
                >
                  <card.Icon style={{ width: 22, height: 22, color: card.palette.fg }} />
                </Avatar>
                <Typography variant="caption" color="text.secondary" display="block">
                  {card.title}
                </Typography>
                <Stack direction="row" alignItems="baseline" spacing={1} mt={0.5}>
                  <Typography variant="h5">{card.value}</Typography>
                  {card.amount && (
                    <Typography variant="body2" color="text.secondary">{card.amount}</Typography>
                  )}
                </Stack>
                <Typography variant="caption" color="text.secondary">{card.subtitle}</Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={3}>Recovery Trends</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip formatter={(v) => `$${v.toLocaleString()}`} />
                <Legend />
                <Line type="monotone" dataKey="recovered_amount" stroke="#fc459d" strokeWidth={2} name="Recovered Amount" />
                <Line type="monotone" dataKey="submitted_appeals" stroke="#38bdf8" strokeWidth={2} name="Appeals Submitted" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" mb={3}>Success Rate by Payer</Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={payerMetrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="payer_name" />
                <YAxis />
                <Tooltip formatter={(v) => `${v}%`} />
                <Legend />
                <Bar dataKey="success_rate" fill="#fc459d" name="Success Rate (%)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Category Table */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" mb={2}>Performance by Denial Category</Typography>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell>Total Denials</TableCell>
              <TableCell>Appeals Submitted</TableCell>
              <TableCell>Success Rate</TableCell>
              <TableCell>Recovered Amount</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {categoryMetrics.map((cat, i) => (
              <TableRow key={i} hover>
                <TableCell>{cat.category}</TableCell>
                <TableCell>{cat.total_denials}</TableCell>
                <TableCell>{cat.appeals_submitted}</TableCell>
                <TableCell>
                  <Chip
                    label={`${cat.success_rate}%`}
                    size="small"
                    color={rateChipColor(cat.success_rate)}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>${(cat.recovered_amount || 0).toLocaleString()}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      {/* Quick Actions */}
      <Stack direction="row" spacing={2}>
        <Button variant="contained" onClick={() => navigate('/denials/new')}>
          Add New Denial
        </Button>
        <Button variant="outlined" onClick={() => navigate('/denials')}>
          View All Denials
        </Button>
      </Stack>
    </Box>
  );
};

export default Dashboard;
