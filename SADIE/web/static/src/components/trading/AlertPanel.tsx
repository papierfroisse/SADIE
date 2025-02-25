import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';
import { Alert } from '../../types';

interface AlertPanelProps {
  symbol: string;
  currentPrice: number;
  onCreateAlert: (alert: Omit<Alert, 'id'>) => Promise<void>;
}

const AlertPanel: React.FC<AlertPanelProps> = ({ symbol, currentPrice, onCreateAlert }) => {
  const [type, setType] = useState<'price' | 'indicator'>('price');
  const [condition, setCondition] = useState<'above' | 'below'>('above');
  const [value, setValue] = useState<string>('');
  const [notificationType, setNotificationType] = useState<'browser' | 'email'>('browser');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newAlert: Omit<Alert, 'id'> = {
        symbol,
        type: 'alert' as const,
        alertType: type,
        condition,
        value: currentPrice * (1 + Number(value) / 100),
        notification_type: notificationType,
        created_at: Date.now(),
        triggered: false,
      };
      await onCreateAlert(newAlert);
      // Reset form
      setValue('');
    } catch (err) {
      console.error('Failed to create alert:', err);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Create Alert
      </Typography>
      <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Alert Type</InputLabel>
              <Select
                value={type}
                label="Alert Type"
                onChange={e => setType(e.target.value as 'price' | 'indicator')}
              >
                <MenuItem value="price">Price</MenuItem>
                <MenuItem value="indicator">Indicator</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Condition</InputLabel>
              <Select
                value={condition}
                label="Condition"
                onChange={e => setCondition(e.target.value as 'above' | 'below')}
              >
                <MenuItem value="above">Above</MenuItem>
                <MenuItem value="below">Below</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Value"
              type="number"
              value={value}
              onChange={e => setValue(e.target.value)}
              inputProps={{ step: 'any' }}
            />
          </Grid>

          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Notification Type</InputLabel>
              <Select
                value={notificationType}
                label="Notification Type"
                onChange={e => setNotificationType(e.target.value as 'browser' | 'email')}
              >
                <MenuItem value="browser">Browser</MenuItem>
                <MenuItem value="email">Email</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Current Price: ${currentPrice.toFixed(2)}
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Button fullWidth variant="contained" color="primary" type="submit" disabled={!value}>
              Create Alert
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Paper>
  );
};

export default AlertPanel;
