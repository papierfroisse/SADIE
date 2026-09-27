import React from 'react';
import {
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Switch,
  Typography,
  Box,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Settings as SettingsIcon } from '@mui/icons-material';
import { TechnicalIndicator } from '../../types';

interface IndicatorPanelProps {
  indicators: TechnicalIndicator[];
  onToggleIndicator: (name: string) => void;
  onConfigureIndicator: (name: string) => void;
}

const IndicatorPanel: React.FC<IndicatorPanelProps> = ({
  indicators,
  onToggleIndicator,
  onConfigureIndicator,
}) => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Technical Indicators
      </Typography>
      <List>
        {indicators.map(indicator => (
          <ListItem key={indicator.name}>
            <ListItemText
              primary={indicator.name}
              secondary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" component="span" sx={{ color: indicator.color }}>
                    {indicator.value.toFixed(2)}
                  </Typography>
                  {indicator.signal && (
                    <Typography
                      variant="caption"
                      sx={{
                        color:
                          indicator.signal === 'buy'
                            ? 'success.main'
                            : indicator.signal === 'sell'
                              ? 'error.main'
                              : 'text.secondary',
                      }}
                    >
                      {indicator.signal.toUpperCase()}
                    </Typography>
                  )}
                </Box>
              }
            />
            <ListItemSecondaryAction sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="Configure">
                <IconButton
                  edge="end"
                  onClick={() => onConfigureIndicator(indicator.name)}
                  size="small"
                >
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Switch
                edge="end"
                onChange={() => onToggleIndicator(indicator.name)}
                checked={true}
              />
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default IndicatorPanel;
