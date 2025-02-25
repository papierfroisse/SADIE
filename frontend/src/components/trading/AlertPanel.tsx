import React, { useState } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { Alert } from '../../types';
import { api } from '../../services/api';

export const AlertPanel: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  React.useEffect(() => {
    const loadAlerts = async () => {
      const response = await api.getAlerts();
      if (response.success && response.data) {
        setAlerts(response.data);
      }
    };
    loadAlerts();
  }, []);

  const handleDeleteAlert = async (id: string) => {
    const response = await api.deleteAlert(id);
    if (response.success) {
      setAlerts(alerts.filter(alert => alert.id !== id));
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Trading Alerts
      </Typography>
      <List>
        {alerts.length === 0 ? (
          <ListItem>
            <ListItemText
              primary="Aucune alerte active"
              secondary="Créez une nouvelle alerte pour commencer"
            />
          </ListItem>
        ) : (
          alerts.map((alert, index) => (
            <React.Fragment key={alert.id}>
              {index > 0 && <Divider />}
              <ListItem>
                <ListItemText
                  primary={`${alert.symbol} ${alert.condition} ${alert.value}`}
                  secondary={`Type: ${alert.type}`}
                />
                <ListItemSecondaryAction>
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => handleDeleteAlert(alert.id)}
                  >
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            </React.Fragment>
          ))
        )}
      </List>
      <Box sx={{ mt: 2 }}>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ mt: 1 }}
        >
          New Alert
        </Button>
      </Box>
    </Paper>
  );
};

export default AlertPanel; 