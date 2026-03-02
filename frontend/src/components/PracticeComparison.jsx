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
    if (selected.length < 2) { setData([]); return; }
    setLoading(true);
    reportingAPI.getPracticeComparison(selected)
      .then(setData)
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [selected]);

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

  const overturnChartData = useMemo(() => {
    if (!data.length) return [];
    return data.map((d) => ({ name: d.practice_name, overturn_rate: d.overturn_rate }));
  }, [data]);

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

  const recoveredChartData = useMemo(() => {
    if (!data.length) return [];
    return data.map((d) => ({ name: d.practice_name, recovered: d.total_recovered, denied: d.total_denied }));
  }, [data]);

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
          {/* KPI Comparison */}
          {kpiDefs.map((kpi) => (
            <Card key={kpi.key} sx={{ mb: 2 }}>
              <CardContent>
                <Stack direction="row" spacing={1} alignItems="center" mb={1.5}>
                  <Avatar variant="rounded" sx={{ bgcolor: kpi.palette.bg, width: 28, height: 28 }}>
                    <kpi.Icon style={{ width: 14, height: 14, color: kpi.palette.fg }} />
                  </Avatar>
                  <Typography variant="subtitle2">{kpi.label}</Typography>
                </Stack>
                <Stack direction="row" spacing={3}>
                  {data.map((d, i) => (
                    <Box key={d.practice_name} flex={1}>
                      <Typography variant="caption" color="text.secondary" display="block" noWrap>
                        <Box component="span" sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: COLORS[i], display: 'inline-block', mr: 0.5 }} />
                        {d.practice_name}
                      </Typography>
                      <Typography variant="h5" fontWeight={700}>{kpi.fmt(d[kpi.key])}</Typography>
                    </Box>
                  ))}
                </Stack>
              </CardContent>
            </Card>
          ))}

          {/* Overturn Rate Bar Chart */}
          <Card sx={{ mb: 3, mt: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>Overturn Rate Comparison</Typography>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={overturnChartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 12 }} unit="%" />
                  <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={160} />
                  <RTooltip formatter={(v) => `${v}%`} />
                  <Bar dataKey="overturn_rate" name="Overturn Rate" radius={[0, 6, 6, 0]}>
                    {overturnChartData.map((_, i) => (
                      <rect key={i} fill={COLORS[i]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Recovered vs Denied */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={700} gutterBottom>Denied vs Recovered ($)</Typography>
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={recoveredChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${(v / 1000).toFixed(0)}K`} />
                  <RTooltip formatter={(v) => `$${v.toLocaleString()}`} />
                  <Legend />
                  <Bar dataKey="denied" name="Total Denied" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="recovered" name="Recovered" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
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
