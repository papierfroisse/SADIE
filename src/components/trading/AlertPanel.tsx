import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography
} from '@mui/material';
import { Alert } from '../../types';

interface AlertPanelProps {
  symbol: string;
  currentPrice: number;
  onCreateAlert: (alert: Omit<Alert, 'id' | 'triggered' | 'createdAt' | 'triggeredAt'>) => void;
}

export const AlertPanel: React.FC<AlertPanelProps> = ({
  symbol,
  currentPrice,
  onCreateAlert
}) => {
  const [value, setValue] = useState<number>(0);
  const [condition, setCondition] = useState<'>' | '<'>('<');

  const handleCreateAlert = () => {
    const newAlert: Omit<Alert, 'id' | 'triggered' | 'createdAt' | 'triggeredAt'> = {
      symbol,
      type: 'price',
      condition,
      value: currentPrice * (1 + Number(value) / 100),
      notificationType: 'browser'
    };
    onCreateAlert(newAlert);
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Créer une alerte
      </Typography>
      <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 2 }}>
        <TextField
          label="Variation (%)"
          type="number"
          value={value}
          onChange={(e) => setValue(Number(e.target.value))}
          size="small"
        />
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Condition</InputLabel>
          <Select
            value={condition}
            label="Condition"
            onChange={(e) => setCondition(e.target.value as '>' | '<')}
          >
            <MenuItem value=">">Au-dessus</MenuItem>
            <MenuItem value="<">En-dessous</MenuItem>
          </Select>
        </FormControl>
        <Button
          variant="contained"
          onClick={handleCreateAlert}
          size="small"
        >
          Créer
        </Button>
      </Box>
      <Typography variant="body2" color="text.secondary">
        Prix actuel: {currentPrice.toFixed(2)}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Prix d'alerte: {(currentPrice * (1 + Number(value) / 100)).toFixed(2)}
      </Typography>
    </Box>
  );
}; 