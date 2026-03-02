import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, CardActionArea, Stack,
  CircularProgress, Chip, Avatar, Button, TextField, InputAdornment,
} from '@mui/material';
import {
  BuildingOffice2Icon,
  MagnifyingGlassIcon,
  ArrowsRightLeftIcon,
} from '@heroicons/react/24/outline';
import { reportingAPI } from '../services/api';

const PracticeSelector = () => {
  const navigate = useNavigate();
  const [practices, setPractices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    reportingAPI.getPracticeSummaries()
      .then(setPractices)
      .catch(() => setPractices([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = practices.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  const rateColor = (rate) => {
    if (rate >= 65) return 'success';
    if (rate >= 45) return 'warning';
    return 'error';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" py={12}>
        <CircularProgress color="primary" />
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems={{ sm: 'center' }} spacing={2} mb={3}>
        <Box>
          <Typography variant="h4" gutterBottom>Practice Reports</Typography>
          <Typography variant="body2" color="text.secondary">
            Select a practice to view its full performance scorecard, or compare practices side-by-side
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<ArrowsRightLeftIcon style={{ width: 18, height: 18 }} />}
          onClick={() => navigate('/practices/compare')}
          sx={{ whiteSpace: 'nowrap' }}
        >
          Compare Practices
        </Button>
      </Stack>

      <TextField
        fullWidth
        size="small"
        placeholder="Search practices..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        sx={{ mb: 3, maxWidth: 400 }}
        slotProps={{
          input: {
            startAdornment: (
              <InputAdornment position="start">
                <MagnifyingGlassIcon style={{ width: 18, height: 18, color: '#9ca3af' }} />
              </InputAdornment>
            ),
          },
        }}
      />

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' },
          gap: 3,
        }}
      >
        {filtered.map((p) => (
          <Card key={p.name} sx={{ '&:hover': { borderColor: 'primary.main' }, transition: 'border-color 0.2s' }}>
            <CardActionArea onClick={() => navigate(`/practices/${encodeURIComponent(p.name)}`)}>
              <CardContent>
                <Stack direction="row" spacing={2} alignItems="flex-start" mb={2}>
                  <Avatar variant="rounded" sx={{ bgcolor: '#fce4ec', width: 44, height: 44 }}>
                    <BuildingOffice2Icon style={{ width: 22, height: 22, color: '#fc459d' }} />
                  </Avatar>
                  <Box flex={1} minWidth={0}>
                    <Typography variant="subtitle1" fontWeight={700} noWrap>{p.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {p.total_denials} denials
                    </Typography>
                  </Box>
                </Stack>

                <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                  <Box>
                    <Typography variant="caption" color="text.secondary">Denied</Typography>
                    <Typography variant="body2" fontWeight={600}>${p.total_denied.toLocaleString()}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">Recovered</Typography>
                    <Typography variant="body2" fontWeight={600} color="success.main">
                      ${p.total_recovered.toLocaleString()}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary" display="block" mb={0.75}>Overturn</Typography>
                    <Chip label={`${p.overturn_rate}%`} size="small" color={rateColor(p.overturn_rate)} />
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary">Preventable</Typography>
                    <Typography variant="body2" fontWeight={600}>{p.preventable_rate}%</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </CardActionArea>
          </Card>
        ))}
      </Box>

      {filtered.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography color="text.secondary">No practices match your search.</Typography>
        </Box>
      )}
    </Box>
  );
};

export default PracticeSelector;
