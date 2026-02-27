import {
  Box, Card, CardContent, Typography, Chip, Paper, Stack, Avatar,
  Table, TableHead, TableBody, TableRow, TableCell, Alert,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import {
  LightBulbIcon, ArrowTrendingUpIcon,
  ArrowTrendingDownIcon, MinusIcon,
} from '@heroicons/react/24/outline';

const TrendIcon = ({ trend }) => {
  if (trend === 'up') return <ArrowTrendingUpIcon style={{ width: 16, height: 16, color: '#ef4444' }} />;
  if (trend === 'down') return <ArrowTrendingDownIcon style={{ width: 16, height: 16, color: '#22c55e' }} />;
  return <MinusIcon style={{ width: 16, height: 16, color: '#9ca3af' }} />;
};

const PatternIntelligence = ({ data }) => {
  if (!data) return null;

  return (
    <Stack spacing={3}>
      {/* Actionable Insights Banner */}
      <Paper
        sx={{
          p: 3,
          background: 'linear-gradient(135deg, rgba(252,69,157,0.05) 0%, rgba(124,58,237,0.08) 100%)',
          borderColor: 'rgba(252,69,157,0.2)',
        }}
      >
        <Stack direction="row" alignItems="center" spacing={1} mb={2}>
          <LightBulbIcon style={{ width: 24, height: 24, color: '#fc459d' }} />
          <Typography variant="h6">Actionable Insights</Typography>
        </Stack>
        <Stack spacing={1.5}>
          {data.actionable_insights.map((insight, i) => (
            <Stack key={i} direction="row" spacing={1.5} alignItems="flex-start">
              <Avatar sx={{ bgcolor: '#fc459d', width: 24, height: 24, fontSize: 12, fontWeight: 700, flexShrink: 0 }}>
                {i + 1}
              </Avatar>
              <Typography variant="body2" color="text.secondary">{insight}</Typography>
            </Stack>
          ))}
        </Stack>
      </Paper>

      {/* Preventability Trend Chart */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Preventability Breakdown Over Time</Typography>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={data.preventability_trend}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Area type="monotone" dataKey="high" stackId="1" stroke="#ef4444" fill="#ef4444" fillOpacity={0.6} name="Highly Preventable" />
            <Area type="monotone" dataKey="medium" stackId="1" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.6} name="Potentially Preventable" />
            <Area type="monotone" dataKey="low" stackId="1" stroke="#22c55e" fill="#22c55e" fillOpacity={0.4} name="Low Preventability" />
          </AreaChart>
        </ResponsiveContainer>
      </Paper>

      {/* Recurring Patterns Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" mb={2}>Recurring Denial Patterns</Typography>
        {data.recurring_patterns.length === 0 ? (
          <Typography variant="body2" color="text.secondary" py={2}>
            No recurring patterns found (minimum 3 occurrences required).
          </Typography>
        ) : (
          <Box sx={{ overflowX: 'auto' }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Code</TableCell>
                  <TableCell>Frequency</TableCell>
                  <TableCell>Trend</TableCell>
                  <TableCell>Common Payer</TableCell>
                  <TableCell>Common Practice</TableCell>
                  <TableCell>Suggested Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.recurring_patterns.map((row, i) => (
                  <TableRow key={i} hover>
                    <TableCell sx={{ fontWeight: 600 }}>{row.code}</TableCell>
                    <TableCell>{row.frequency}</TableCell>
                    <TableCell>
                      <Stack direction="row" alignItems="center" spacing={0.5}>
                        <TrendIcon trend={row.trend} />
                        <Typography variant="caption" color="text.secondary" textTransform="capitalize">
                          {row.trend}
                        </Typography>
                      </Stack>
                    </TableCell>
                    <TableCell>{row.common_payer}</TableCell>
                    <TableCell>{row.common_practice}</TableCell>
                    <TableCell sx={{ maxWidth: 280 }}>{row.suggested_action}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        )}
      </Paper>

      {/* Practice & Payer Insights */}
      <Grid container spacing={3}>
        {/* Practice Insights */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" mb={2}>Practice-Level Insights</Typography>
            {data.practice_insights.length === 0 ? (
              <Typography variant="body2" color="text.secondary" py={2}>No practice data available.</Typography>
            ) : (
              <Stack spacing={1.5}>
                {data.practice_insights.map((p, i) => (
                  <Card key={i} variant="outlined">
                    <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={0.5}>
                        <Typography variant="subtitle2">{p.practice}</Typography>
                        <Chip
                          label={`${p.preventable_rate}% preventable`}
                          size="small"
                          color={p.preventable_rate >= 70 ? 'error' : p.preventable_rate >= 50 ? 'warning' : 'success'}
                          variant="outlined"
                        />
                      </Stack>
                      <Typography variant="caption" color="text.secondary">
                        {p.total_denials} denials &middot; {p.preventable_count} preventable
                      </Typography>
                      {p.top_codes.length > 0 && (
                        <Stack direction="row" spacing={0.5} mt={1} flexWrap="wrap" useFlexGap>
                          {p.top_codes.map((c, j) => (
                            <Chip key={j} label={c} size="small" variant="outlined" />
                          ))}
                        </Stack>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            )}
          </Paper>
        </Grid>

        {/* Payer Behavior */}
        <Grid size={{ xs: 12, lg: 6 }}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" mb={2}>Payer Behavior Analysis</Typography>
            {data.payer_behavior.length === 0 ? (
              <Typography variant="body2" color="text.secondary" py={2}>No payer data available.</Typography>
            ) : (
              <Stack spacing={1.5}>
                {data.payer_behavior.map((p, i) => (
                  <Card key={i} variant="outlined">
                    <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={0.5}>
                        <Typography variant="subtitle2">{p.payer}</Typography>
                        <Chip
                          label={`${p.overturn_rate}% overturn`}
                          size="small"
                          color={p.overturn_rate >= 70 ? 'success' : p.overturn_rate >= 50 ? 'warning' : 'error'}
                          variant="outlined"
                        />
                      </Stack>
                      <Typography variant="caption" color="text.secondary">
                        {p.total_denials} total denials
                      </Typography>
                      {p.top_codes.length > 0 && (
                        <Stack direction="row" spacing={0.5} mt={1} flexWrap="wrap" useFlexGap>
                          {p.top_codes.map((c, j) => (
                            <Chip key={j} label={c} size="small" variant="outlined" />
                          ))}
                        </Stack>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </Stack>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Stack>
  );
};

export default PatternIntelligence;
