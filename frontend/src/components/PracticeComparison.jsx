import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, Stack, Chip, Avatar,
  CircularProgress, Button, FormControl, InputLabel, Select, MenuItem,
  Table, TableHead, TableBody, TableRow, TableCell, IconButton, Alert,
} from '@mui/material';
import {
  ArrowLeftIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ClockIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RTooltip, ResponsiveContainer, Legend } from 'recharts';
import { reportingAPI } from '../services/api';
import { mockProviders } from '../services/mockData';

const COLORS = ['#fc459d', '#7c3aed', '#0284c7'];

const PracticeComparison = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [allPractices, setAllPractices] = useState([]);
  const [selected, setSelected] = useState([]);
  const [data, setData] = useState([]);
  const [comparisonInsights, setComparisonInsights] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const DEMO = import.meta.env.VITE_DEMO_MODE === 'true';
    if (DEMO) {
      setAllPractices(mockProviders);
    } else {
      reportingAPI.getPracticeSummaries()
        .then((res) => setAllPractices(Array.isArray(res) ? res.map((p) => (typeof p === 'string' ? p : p.name)) : []))
        .catch(() => setAllPractices([]));
    }
  }, []);

  useEffect(() => {
    const fromUrl = searchParams.get('practices');
    if (fromUrl) {
      setSelected(fromUrl.split(',').map(decodeURIComponent).filter(Boolean).slice(0, 3));
    }
  }, [searchParams]);

  useEffect(() => {
    if (selected.length < 2) { setData([]); setComparisonInsights([]); return; }
    setLoading(true);
    setComparisonInsights([]);
    reportingAPI.getPracticeComparison(selected)
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [selected]);

  useEffect(() => {
    if (selected.length < 2 || data.length < 2) { setComparisonInsights([]); return; }
    reportingAPI.getPracticeComparisonInsights(selected)
      .then((res) => setComparisonInsights(res.insights || []))
      .catch(() => setComparisonInsights([]));
  }, [selected, data.length]);

  const handleSelect = (idx, value) => {
    setSelected((prev) => {
      const next = [...prev];
      next[idx] = value;
      return next.filter(Boolean);
    });
  };

  const addSlot = () => setSelected((p) => (p.length < 3 ? [...p, ''] : p));
  const removeSlot = (idx) => setSelected((p) => p.filter((_, i) => i !== idx));

  const rateColor = (r) => (r >= 65 ? 'success' : r >= 45 ? 'warning' : 'error');

  const kpiDefs = [
    { key: 'total_denials', label: 'Total Denials', fmt: (v) => v.toLocaleString(), Icon: ExclamationTriangleIcon, palette: { bg: '#fef3c7', fg: '#d97706' } },
    { key: 'total_denied', label: 'Total Denied', fmt: (v) => `$${v.toLocaleString()}`, Icon: CurrencyDollarIcon, palette: { bg: '#fee2e2', fg: '#ef4444' } },
    { key: 'total_recovered', label: 'Recovered', fmt: (v) => `$${v.toLocaleString()}`, Icon: CurrencyDollarIcon, palette: { bg: '#d1fae5', fg: '#10b981' } },
    { key: 'overturn_rate', label: 'Overturn Rate', fmt: (v) => `${v}%`, Icon: ShieldCheckIcon, palette: { bg: '#ede9fe', fg: '#7c3aed' } },
    { key: 'preventable_rate', label: 'Preventable', fmt: (v) => `${v}%`, Icon: ChartBarIcon, palette: { bg: '#fce4ec', fg: '#fc459d' } },
    { key: 'avg_resolution_days', label: 'Avg Resolution', fmt: (v) => (v != null ? `${v}d` : 'N/A'), Icon: ClockIcon, palette: { bg: '#e0f2fe', fg: '#0284c7' } },
  ];

  const allCodes = useMemo(() => {
    if (!data.length) return [];
    const codeMap = {};
    data.forEach((d) => {
      (d.top_denial_codes || []).forEach((c) => {
        if (!codeMap[c.code]) codeMap[c.code] = { code: c.code, description: c.description };
        codeMap[c.code][d.practice_name] = c.count;
      });
    });
    return Object.values(codeMap).sort((a, b) => {
      const sumA = data.reduce((s, d) => s + (a[d.practice_name] || 0), 0);
      const sumB = data.reduce((s, d) => s + (b[d.practice_name] || 0), 0);
      return sumB - sumA;
    }).slice(0, 10);
  }, [data]);

  const denialTypeMixData = useMemo(() => {
    if (!data.length) return [];
    return data.map((d) => {
      const admin = d.admin_split?.count ?? 0;
      const clinical = d.clinical_split?.count ?? 0;
      const total = d.total_denials ?? 0;
      const other = Math.max(0, total - admin - clinical);
      return {
        name: d.practice_name,
        administrative: admin,
        clinical,
        other,
      };
    });
  }, [data]);

  const payerComparisonRows = useMemo(() => {
    if (!data.length) return [];
    const payerSet = new Set();
    data.forEach((d) => {
      (d.payer_breakdown || []).forEach((p) => payerSet.add(p.name));
    });
    const payers = Array.from(payerSet).sort();
    return payers.map((payerName) => {
      const row = { payer: payerName };
      data.forEach((d) => {
        const found = (d.payer_breakdown || []).find((p) => p.name === payerName);
        row[d.practice_name] = found != null ? found.overturn_rate : null;
      });
      return row;
    });
  }, [data]);

  const frontendInsights = useMemo(() => {
    if (!data.length || data.length < 2) return [];
    const bullets = [];
    const best = data.reduce((a, b) => ((a.overturn_rate ?? 0) >= (b.overturn_rate ?? 0) ? a : b));
    const worst = data.reduce((a, b) => ((a.overturn_rate ?? 0) <= (b.overturn_rate ?? 0) ? a : b));
    if (best.practice_name !== worst.practice_name && (best.overturn_rate ?? 0) > (worst.overturn_rate ?? 0)) {
      bullets.push({ type: 'internal', message: `${best.practice_name} has a higher overturn rate (${best.overturn_rate}% vs ${worst.overturn_rate}%). Compare denial type mix and payer table to see why.` });
    }
    data.forEach((d) => {
      const total = d.total_denials ?? 0;
      if (total === 0) return;
      const admin = d.admin_split?.count ?? 0;
      const adminPct = Math.round(admin / total * 100);
      if (adminPct >= 50 && (d.admin_split?.overturn_rate ?? 0) >= 60) {
        bullets.push({ type: 'internal', message: `${d.practice_name} has a high share of administrative denials (${adminPct}%); administrative denials often overturn more — consider prioritizing admin appeals at other practices.` });
      }
    });
    const highPrev = data.find((d) => (d.preventable_rate ?? 0) >= 50);
    if (highPrev) {
      bullets.push({ type: 'action', message: `${highPrev.practice_name} has a high preventable rate (${highPrev.preventable_rate}%); focus on prior authorization and coding to reduce denials.` });
    }
    const withPriorAuthCode = data.find((d) => {
      const top = (d.top_denial_codes || [])[0];
      return top && (top.code === 'CO-197' || (top.preventability === 'high' && (top.description || '').toLowerCase().includes('prior')));
    });
    if (withPriorAuthCode) {
      const top = withPriorAuthCode.top_denial_codes[0];
      bullets.push({ type: 'action', message: `${withPriorAuthCode.practice_name}'s top code is ${top.code} (prior auth) — consider strengthening pre-authorization workflow.` });
    }
    return bullets.slice(0, 5);
  }, [data]);

  const insightsToShow = comparisonInsights.length > 0 ? comparisonInsights : frontendInsights;

  return (
    <Box p={3}>
      <Stack direction="row" spacing={1} alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/practices')} size="small">
          <ArrowLeftIcon style={{ width: 20, height: 20 }} />
        </IconButton>
        <Box>
          <Typography variant="h4">Practice Comparison</Typography>
          <Typography variant="body2" color="text.secondary">Side-by-side performance analysis</Typography>
        </Box>
      </Stack>

      {/* Practice selectors */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} alignItems={{ sm: 'center' }}>
            {selected.map((val, idx) => (
              <Stack key={idx} direction="row" spacing={1} alignItems="center" flex={1}>
                <Box sx={{ width: 6, height: 32, borderRadius: 1, bgcolor: COLORS[idx] }} />
                <FormControl size="small" fullWidth>
                  <InputLabel>Practice {idx + 1}</InputLabel>
                  <Select value={val} label={`Practice ${idx + 1}`} onChange={(e) => handleSelect(idx, e.target.value)}>
                    {allPractices.map((p) => (
                      <MenuItem key={p} value={p} disabled={selected.includes(p) && p !== val}>{p}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                {selected.length > 2 && (
                  <Button size="small" color="error" onClick={() => removeSlot(idx)} sx={{ minWidth: 0 }}>X</Button>
                )}
              </Stack>
            ))}
            {selected.length < 3 && (
              <Button size="small" variant="outlined" onClick={addSlot}>+ Add</Button>
            )}
          </Stack>
          {selected.length < 2 && (
            <Typography variant="caption" color="text.secondary" mt={1} display="block">
              Select at least 2 practices to compare.
            </Typography>
          )}
        </CardContent>
      </Card>

      {loading && (
        <Box display="flex" justifyContent="center" py={10}><CircularProgress /></Box>
      )}

      {!loading && data.length >= 2 && (
        <>
          {/* Key metrics comparison table */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>Key metrics</Typography>
              <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Metric</TableCell>
                      {data.map((d, i) => (
                        <TableCell key={d.practice_name}>
                          <Stack direction="row" spacing={0.5} alignItems="center">
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: COLORS[i] }} />
                            <Typography variant="body2" fontWeight={600} noWrap>{d.practice_name}</Typography>
                          </Stack>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {kpiDefs.map((kpi) => (
                      <TableRow key={kpi.key} hover>
                        <TableCell sx={{ minWidth: 140 }}>
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Avatar variant="rounded" sx={{ bgcolor: kpi.palette.bg, width: 24, height: 24 }}>
                              <kpi.Icon style={{ width: 12, height: 12, color: kpi.palette.fg }} />
                            </Avatar>
                            <Typography variant="body2">{kpi.label}</Typography>
                          </Stack>
                        </TableCell>
                        {data.map((d, i) => {
                          const value = d[kpi.key];
                          const isRate = kpi.key === 'overturn_rate' || kpi.key === 'preventable_rate';
                          return (
                            <TableCell key={d.practice_name}>
                              {isRate && typeof value === 'number' ? (
                                <Chip label={kpi.fmt(value)} size="small" color={rateColor(value)} sx={{ fontWeight: 600 }} />
                              ) : (
                                <Typography variant="body2" fontWeight={600}>{kpi.fmt(value)}</Typography>
                              )}
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            </CardContent>
          </Card>

          {/* Denial type mix */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>Denial type mix</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Composition of denials by type. Different mixes can explain different overturn rates.
              </Typography>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={denialTypeMixData} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis type="number" tick={{ fontSize: 12 }} />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={160} />
                  <RTooltip />
                  <Legend />
                  <Bar dataKey="administrative" name="Administrative" stackId="stack" fill="#7c3aed" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="clinical" name="Clinical" stackId="stack" fill="#0284c7" radius={[0, 0, 0, 0]} />
                  <Bar dataKey="other" name="Other" stackId="stack" fill="#94a3b8" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Overturn rate by payer */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>Overturn rate by payer</Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Compare performance with the same payers (internal) vs different payer mix (external).
              </Typography>
              <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 600 }}>Payer</TableCell>
                      {data.map((d, i) => (
                        <TableCell key={d.practice_name}>
                          <Stack direction="row" spacing={0.5} alignItems="center">
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: COLORS[i] }} />
                            <Typography variant="body2" fontWeight={600} noWrap>{d.practice_name}</Typography>
                          </Stack>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {payerComparisonRows.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={data.length + 1} align="center" color="text.secondary">
                          No payer breakdown data for selected practices.
                        </TableCell>
                      </TableRow>
                    ) : (
                      payerComparisonRows.map((row) => (
                        <TableRow key={row.payer} hover>
                          <TableCell sx={{ fontWeight: 500 }}>{row.payer}</TableCell>
                          {data.map((d) => (
                            <TableCell key={d.practice_name}>
                              {row[d.practice_name] != null ? (
                                <Chip label={`${row[d.practice_name]}%`} size="small" color={rateColor(row[d.practice_name])} />
                              ) : (
                                '—'
                              )}
                            </TableCell>
                          ))}
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </Box>
            </CardContent>
          </Card>

          {/* Insights */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" mb={1.5}>
                <LightBulbIcon style={{ width: 22, height: 22, color: '#d97706' }} />
                <Typography variant="subtitle1" fontWeight={700}>Insights</Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Why practices differ — external factors (e.g. payer mix) vs changes you can make (process, documentation).
              </Typography>
              {insightsToShow.length === 0 ? (
                <Typography variant="body2" color="text.secondary">No specific insights for this comparison. Use the denial type mix and payer table above to spot differences.</Typography>
              ) : (
                <Stack spacing={1.5}>
                  {insightsToShow.map((insight, idx) => (
                    <Stack key={idx} direction="row" spacing={1.5} alignItems="flex-start">
                      <Chip
                        size="small"
                        label={insight.type === 'external' ? 'External' : insight.type === 'action' ? 'Action' : 'Internal'}
                        color={insight.type === 'external' ? 'default' : insight.type === 'action' ? 'primary' : 'secondary'}
                        sx={{ flexShrink: 0, mt: 0.25 }}
                      />
                      <Typography variant="body2">{insight.message}</Typography>
                    </Stack>
                  ))}
                </Stack>
              )}
            </CardContent>
          </Card>

          {/* Denial Code Comparison Table */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>Top Denial Codes Comparison</Typography>
              <Box sx={{ overflowX: 'auto' }}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Code</TableCell>
                      <TableCell>Description</TableCell>
                      {data.map((d, i) => (
                        <TableCell key={d.practice_name}>
                          <Stack direction="row" spacing={0.5} alignItems="center">
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: COLORS[i] }} />
                            <Typography variant="caption" fontWeight={600} noWrap>{d.practice_name}</Typography>
                          </Stack>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {allCodes.map((row) => (
                      <TableRow key={row.code} hover>
                        <TableCell sx={{ fontWeight: 600 }}>{row.code}</TableCell>
                        <TableCell sx={{ maxWidth: 200, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {row.description}
                        </TableCell>
                        {data.map((d) => (
                          <TableCell key={d.practice_name}>{row[d.practice_name] || '—'}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Box>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
};

export default PracticeComparison;
