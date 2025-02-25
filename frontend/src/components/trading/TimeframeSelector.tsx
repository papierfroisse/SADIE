import React from 'react';
import { ToggleButton, ToggleButtonGroup } from '@mui/material';

interface TimeframeSelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export const TimeframeSelector: React.FC<TimeframeSelectorProps> = ({ value, onChange }) => {
  const handleChange = (
    _event: React.MouseEvent<HTMLElement>,
    newValue: string | null
  ) => {
    if (newValue !== null) {
      onChange(newValue);
    }
  };

  return (
    <ToggleButtonGroup
      value={value}
      exclusive
      onChange={handleChange}
      aria-label="timeframe"
      size="small"
      sx={{ mb: 2 }}
    >
      <ToggleButton value="1m" aria-label="1 minute">
        1m
      </ToggleButton>
      <ToggleButton value="5m" aria-label="5 minutes">
        5m
      </ToggleButton>
      <ToggleButton value="15m" aria-label="15 minutes">
        15m
      </ToggleButton>
      <ToggleButton value="1h" aria-label="1 hour">
        1h
      </ToggleButton>
      <ToggleButton value="4h" aria-label="4 hours">
        4h
      </ToggleButton>
      <ToggleButton value="1d" aria-label="1 day">
        1d
      </ToggleButton>
    </ToggleButtonGroup>
  );
};

export default TimeframeSelector; 
