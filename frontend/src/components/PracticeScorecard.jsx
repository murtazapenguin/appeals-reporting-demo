import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, Stack, Chip, Avatar,
  CircularProgress, Button, Paper, Table, TableHead, TableBody,
  TableRow, TableCell, TableSortLabel, Alert, IconButton, Tooltip,
} from '@mui/material';
import {
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  ArrowsRightLeftIcon,
  ExclamationTriangleIcon,
  ShieldCheckIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  DocumentCheckIcon,
} from '@heroicons/react/24/outline';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RTooltip, ResponsiveContainer, Legend } from 'recharts';
import { reportingAPI } from '../services/api';

const PracticeScorecard = () => {
  const { name } = useParams();
  const navigate = useNavigate();
  const printRef = useRef(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [codeSort, setCodeSort] = useState({ key: 'count', dir: 'desc' });

  const practiceName = decodeURIComponent(name);

  useEffect(() => {
    setLoading(true);
    reportingAPI.getPracticeScorecard(practiceName)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [practiceName]);

  const handlePDF = async () => {
    const el = printRef.current;
    if (!el) return;
    const { default: html2canvas } = await import('html2canvas');
    const { default: jsPDF } = await import('jspdf');
    const canvas = await html2canvas(el, { scale: 2, useCORS: true });
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const pW = pdf.internal.pageSize.getWidth();
    const pH = pdf.internal.pageSize.getHeight();
    const imgW = pW - 20;
    const imgH = (canvas.height * imgW) / canvas.width;
    let yOff = 10;
    if (imgH <= pH - 20) {
      pdf.addImage(imgData, 'PNG', 10, yOff, imgW, imgH);
    } else {
      let remaining = imgH;
      let srcY = 0;
      while (remaining > 0) {
        const sliceH = Math.min(remaining, pH - 20);
        const sliceCanvas = document.createElement('canvas');
        sliceCanvas.width = canvas.width;
        sliceCanvas.height = (sliceH / imgH) * canvas.height;
        const ctx = sliceCanvas.getContext('2d');
        ctx.drawImage(canvas, 0, srcY, canvas.width, sliceCanvas.height, 0, 0, canvas.width, sliceCanvas.height);
        pdf.addImage(sliceCanvas.toDataURL('image/png'), 'PNG', 10, 10, imgW, sliceH);
        remaining -= sliceH;
        srcY += sliceCanvas.height;
        if (remaining > 0) pdf.addPage();
      }
    }
    pdf.save(`${practiceName.replace(/\s+/g, '_')}_Scorecard.pdf`);
  };

  const rateColor = (r) => (r >= 65 ? 'success' : r >= 45 ? 'warning' : 'error');

  const sortedCodes = data?.top_denial_codes
    ? [...data.top_denial_codes].sort((a, b) => {
        const m = codeSort.dir === 'asc' ? 1 : -1;
        if (typeof a[codeSort.key] === 'number') return (a[codeSort.key] - b[codeSort.key]) * m;
        return String(a[codeSort.key] || '').localeCompare(String(b[codeSort.key] || '')) * m;
      })
    : [];

  const handleSort = (key) => {
    setCodeSort((prev) =>
      prev.key === key ? { key, dir: prev.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'desc' }
    );
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={12}>
        <CircularProgress color="primary" />
      </Box>
    );
  }

  if (!data) {
    return (
      <Box p={3}>
        <Alert severity="error">No data found for practice "{practiceName}".</Alert>
        <Button sx={{ mt: 2 }} onClick={() => navigate('/practices')}>Back to Practices</Button>
      </Box>
    );
  }

  const kpis = [
    { title: 'Total Denials', value: data.total_denials.toLocaleString(), Icon: ExclamationTriangleIcon, palette: { bg: '#fef3c7', fg: '#d97706' } },
    { title: 'Total Denied', value: `$${data.total_denied.toLocaleString()}`, Icon: CurrencyDollarIcon, palette: { bg: '#fee2e2', fg: '#ef4444' } },
    { title: 'Total Recovered', value: `$${data.total_recovered.toLocaleString()}`, Icon: CurrencyDollarIcon, palette: { bg: '#d1fae5', fg: '#10b981' } },
    { title: 'Overturn Rate', value: `${data.overturn_rate}%`, Icon: ShieldCheckIcon, palette: { bg: '#ede9fe', fg: '#7c3aed' } },
    { title: 'Preventable Rate', value: `${data.preventable_rate}%`, Icon: ChartBarIcon, palette: { bg: '#fce4ec', fg: '#fc459d' } },
    { title: 'Avg Resolution', value: data.avg_resolution_days != null ? `${data.avg_resolution_days}d` : 'N/A', Icon: ClockIcon, palette: { bg: '#e0f2fe', fg: '#0284c7' } },
  ];

  const CODE_COLS = [
    { key: 'code', label: 'Code' },
    { key: 'description', label: 'Description' },
    { key: 'count', label: 'Count' },
    { key: 'total_denied', label: 'Total Denied' },
    { key: 'recovered', label: 'Recovered' },
    { key: 'overturn_rate', label: 'Overturn Rate' },
    { key: 'classification', label: 'Type' },
    { key: 'preventability', label: 'Preventability' },
  ];

  return (
    <Box p={3}>
      {/* Header */}
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} mb={3}>
        <Stack direction="row" spacing={1} alignItems="center">
          <IconButton onClick={() => navigate('/practices')} size="small">
            <ArrowLeftIcon style={{ width: 20, height: 20 }} />
          </IconButton>
          <Box>
            <Typography variant="h4">Practice Scorecard</Typography>
            <Typography variant="body2" color="text.secondary">{practiceName}</Typography>
          </Box>
        </Stack>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<ArrowsRightLeftIcon style={{ width: 16, height: 16 }} />}
            onClick={() => navigate(`/practices/compare?practices=${encodeURIComponent(practiceName)}`)}
          >
            Compare
          </Button>
          <Button
            variant="contained"
            size="small"
            startIcon={<ArrowDownTrayIcon style={{ width: 16, height: 16 }} />}
            onClick={handlePDF}
          >
            Download PDF
          </Button>
        </Stack>
      </Stack>

      {/* Printable area */}
      <Box ref={printRef}>
        {/* KPI Row */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: 'repeat(2, 1fr)', sm: 'repeat(3, 1fr)', md: 'repeat(6, 1fr)' }, gap: 2, mb: 3 }}>
          {kpis.map((k, i) => (
            <Card key={i}>
              <CardContent sx={{ py: 2 }}>
                <Avatar variant="rounded" sx={{ bgcolor: k.palette.bg, width: 36, height: 36, mb: 1 }}>
                  <k.Icon style={{ width: 18, height: 18, color: k.palette.fg }} />
                </Avatar>
                <Typography variant="caption" color="text.secondary" display="block">{k.title}</Typography>
                <Typography variant="h6">{k.value}</Typography>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Admin vs Clinical Split */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2, mb: 3 }}>
          {[data.admin_split, data.clinical_split].map((split, i) => (
            <Card key={i}>
              <CardContent>
                <Typography variant="subtitle2" gutterBottom>{split.label || (i === 0 ? 'Administrative' : 'Clinical')}</Typography>
                <Stack direction="row" spacing={3} flexWrap="wrap" useFlexGap>
                  <Box sx={{ minWidth: 70 }}>
                    <Typography variant="caption" color="text.secondary">Count</Typography>
                    <Typography variant="h6">{split.count}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 90 }}>
                    <Typography variant="caption" color="text.secondary">Total Denied</Typography>
                    <Typography variant="h6">${split.total_denied.toLocaleString()}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 90 }}>
                    <Typography variant="caption" color="text.secondary">Recovered</Typography>
                    <Typography variant="h6" color="success.main">${(split.recovered || 0).toLocaleString()}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 80 }}>
                    <Typography variant="caption" color="text.secondary" display="block" mb={0.75}>Overturn</Typography>
                    <Chip label={`${split.overturn_rate}%`} size="small" color={rateColor(split.overturn_rate)} />
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          ))}
        </Box>

        {/* Top Denial Codes Table */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} gutterBottom>Top Denial Codes</Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    {CODE_COLS.map((col) => (
                      <TableCell key={col.key}>
                        <TableSortLabel
                          active={codeSort.key === col.key}
                          direction={codeSort.key === col.key ? codeSort.dir : 'desc'}
                          onClick={() => handleSort(col.key)}
                        >
                          {col.label}
                        </TableSortLabel>
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {sortedCodes.map((row) => (
                    <TableRow key={row.code} hover>
                      <TableCell sx={{ fontWeight: 600 }}>{row.code}</TableCell>
                      <TableCell sx={{ maxWidth: 220, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        <Tooltip title={row.description}><span>{row.description}</span></Tooltip>
                      </TableCell>
                      <TableCell>{row.count}</TableCell>
                      <TableCell>${row.total_denied.toLocaleString()}</TableCell>
                      <TableCell sx={{ color: 'success.main', fontWeight: 600 }}>${(row.recovered || 0).toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip label={`${row.overturn_rate}%`} size="small" color={rateColor(row.overturn_rate)} />
                      </TableCell>
                      <TableCell>
                        <Chip label={row.classification} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={row.preventability}
                          size="small"
                          color={row.preventability === 'high' ? 'error' : row.preventability === 'medium' ? 'warning' : 'default'}
                          variant="outlined"
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </CardContent>
        </Card>

        {/* Top Procedures */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} gutterBottom>Top Procedures Denied</Typography>
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
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(data.top_procedures || []).map((row) => (
                    <TableRow key={row.procedure_code} hover>
                      <TableCell sx={{ fontWeight: 600 }}>{row.procedure_code}</TableCell>
                      <TableCell>{row.total}</TableCell>
                      <TableCell>{row.medical_necessity}</TableCell>
                      <TableCell>{row.prior_authorization}</TableCell>
                      <TableCell>{row.coding_error}</TableCell>
                      <TableCell>{row.documentation}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </CardContent>
        </Card>

        {/* Payer Breakdown */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} gutterBottom>Payer Breakdown</Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Payer</TableCell>
                    <TableCell>Appeals</TableCell>
                    <TableCell>Overturn Rate</TableCell>
                    <TableCell>Recovered</TableCell>
                    <TableCell>Avg Days</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(data.payer_breakdown || []).map((row) => (
                    <TableRow key={row.name} hover>
                      <TableCell sx={{ fontWeight: 600 }}>{row.name}</TableCell>
                      <TableCell>{row.total_appeals}</TableCell>
                      <TableCell>
                        <Chip label={`${row.overturn_rate}%`} size="small" color={rateColor(row.overturn_rate)} />
                      </TableCell>
                      <TableCell sx={{ color: 'success.main', fontWeight: 600 }}>${row.recovered_amount.toLocaleString()}</TableCell>
                      <TableCell>{row.avg_days_to_decision != null ? `${row.avg_days_to_decision}d` : '—'}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </CardContent>
        </Card>

        {/* Denial Trend Chart */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} gutterBottom>Monthly Denial Trend</Typography>
            <ResponsiveContainer width="100%" height={260}>
              <AreaChart data={data.denial_trend || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <RTooltip />
                <Legend />
                <Area type="monotone" dataKey="clinical" stackId="1" stroke="#7c3aed" fill="#ede9fe" name="Clinical" />
                <Area type="monotone" dataKey="administrative" stackId="1" stroke="#fc459d" fill="#fce4ec" name="Administrative" />
                <Area type="monotone" dataKey="other" stackId="1" stroke="#9ca3af" fill="#f3f4f6" name="Other" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Actionable Insights */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Stack direction="row" spacing={1} alignItems="center" mb={2}>
              <Avatar variant="rounded" sx={{ bgcolor: '#ede9fe', width: 32, height: 32 }}>
                <DocumentCheckIcon style={{ width: 16, height: 16, color: '#7c3aed' }} />
              </Avatar>
              <Typography variant="subtitle1" fontWeight={700}>Actionable Insights</Typography>
            </Stack>
            <Stack spacing={1.5}>
              {(data.actionable_insights || []).map((insight, i) => (
                <Alert key={i} severity="info" variant="outlined" icon={false} sx={{ '& .MuiAlert-message': { fontSize: '0.875rem' } }}>
                  {insight}
                </Alert>
              ))}
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default PracticeScorecard;
