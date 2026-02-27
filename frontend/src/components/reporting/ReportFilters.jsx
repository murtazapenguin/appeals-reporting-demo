import { useState, useEffect } from 'react';
import {
  Paper, Button, IconButton, Collapse, Stack, Box,
  FormControl, InputLabel, Select, MenuItem, TextField, Badge,
} from '@mui/material';
import { FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { referenceDataAPI } from '../../services/api';

const ReportFilters = ({ filters, onChange }) => {
  const [payers, setPayers] = useState([]);
  const [practices, setPractices] = useState([]);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    referenceDataAPI.getPayers().then(setPayers).catch(() => {});
    referenceDataAPI.getProviders().then(setPractices).catch(() => {});
  }, []);

  const update = (key, value) => {
    onChange({ ...filters, [key]: value });
  };

  const clearAll = () => {
    onChange({
      date_from: '',
      date_to: '',
      payers: '',
      practices: '',
      categories: '',
      denial_type: 'all',
    });
  };

  const hasFilters = filters.date_from || filters.date_to || filters.payers
    || filters.practices || filters.categories || filters.denial_type !== 'all';

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between">
        <Button
          startIcon={
            <Badge color="primary" variant="dot" invisible={!hasFilters}>
              <FunnelIcon style={{ width: 20, height: 20 }} />
            </Badge>
          }
          onClick={() => setExpanded(!expanded)}
          size="small"
          color="inherit"
        >
          Filters
        </Button>
        {hasFilters && (
          <IconButton size="small" onClick={clearAll} color="default">
            <XMarkIcon style={{ width: 18, height: 18 }} />
          </IconButton>
        )}
      </Stack>

      <Collapse in={expanded}>
        <Box
          sx={{
            mt: 2,
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr', xl: 'repeat(6, 1fr)' },
            gap: 2,
          }}
        >
          <TextField
            label="From"
            type="date"
            size="small"
            slotProps={{ inputLabel: { shrink: true } }}
            value={filters.date_from}
            onChange={(e) => update('date_from', e.target.value)}
          />
          <TextField
            label="To"
            type="date"
            size="small"
            slotProps={{ inputLabel: { shrink: true } }}
            value={filters.date_to}
            onChange={(e) => update('date_to', e.target.value)}
          />

          <FormControl size="small">
            <InputLabel>Payer</InputLabel>
            <Select
              value={filters.payers}
              label="Payer"
              onChange={(e) => update('payers', e.target.value)}
            >
              <MenuItem value="">All Payers</MenuItem>
              {payers.map((p) => (
                <MenuItem key={p} value={p}>{p}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small">
            <InputLabel>Practice</InputLabel>
            <Select
              value={filters.practices}
              label="Practice"
              onChange={(e) => update('practices', e.target.value)}
            >
              <MenuItem value="">All Practices</MenuItem>
              {practices.map((p) => (
                <MenuItem key={p} value={p}>{p}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl size="small">
            <InputLabel>Category</InputLabel>
            <Select
              value={filters.categories}
              label="Category"
              onChange={(e) => update('categories', e.target.value)}
            >
              <MenuItem value="">All Categories</MenuItem>
              <MenuItem value="Medical Necessity">Medical Necessity</MenuItem>
              <MenuItem value="Prior Authorization">Prior Authorization</MenuItem>
              <MenuItem value="Coding Error">Coding Error</MenuItem>
              <MenuItem value="Documentation">Documentation</MenuItem>
              <MenuItem value="Other">Other</MenuItem>
            </Select>
          </FormControl>

          <FormControl size="small">
            <InputLabel>Denial Type</InputLabel>
            <Select
              value={filters.denial_type}
              label="Denial Type"
              onChange={(e) => update('denial_type', e.target.value)}
            >
              <MenuItem value="all">All Types</MenuItem>
              <MenuItem value="administrative">Administrative</MenuItem>
              <MenuItem value="clinical">Clinical</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default ReportFilters;
