import React, { useEffect, useState } from 'react';
import { 
  Button, 
  IconButton, 
  List, 
  ListItem, 
  ListItemText, 
  Paper, 
  Typography,
  Box,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import { apiService } from '../services/api';
import { format } from 'date-fns';
import { Alert } from '../types';

export const AlertList: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [open, setOpen] = useState(false);
  const [newAlert, setNewAlert] = useState<Partial<Alert>>({
    symbol: '',
    type: 'price',
    condition: 'above',
    value: 0,
    notificationType: 'browser'
  });

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const response = await apiService.getAlerts();
      if (response.success) {
        setAlerts(response.data);
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  };

  const handleCreateAlert = async () => {
    try {
      const response = await apiService.createAlert({
        symbol: newAlert.symbol as string,
        type: newAlert.type as 'price' | 'volume' | 'indicator',
        condition: newAlert.condition as 'above' | 'below',
        value: Number(newAlert.value),
        notificationType: newAlert.notificationType as 'browser' | 'email'
      });
      
      if (response.success) {
        setOpen(false);
        loadAlerts();
        resetForm();
      }
    } catch (error) {
      console.error('Error creating alert:', error);
    }
  };

  const handleDeleteAlert = async (id: string) => {
    try {
      const response = await apiService.deleteAlert(id);
      if (response.success) {
        loadAlerts();
      }
    } catch (error) {
      console.error('Error deleting alert:', error);
    }
  };

  const resetForm = () => {
    setNewAlert({
      symbol: '',
      type: 'price',
      condition: 'above',
      value: 0,
      notificationType: 'browser'
    });
  };

  const getNotificationIcon = (type: 'browser' | 'email') => {
    // Implement the logic to return the appropriate icon based on the notification type
    return null;
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Alertes</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setOpen(true)}
        >
          Nouvelle Alerte
        </Button>
      </Box>

      <Paper>
        <List>
          {alerts.map((alert) => (
            <ListItem key={alert.id}>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs>
                  <ListItemText
                    primary={alert.symbol}
                    secondary={
                      <Grid container spacing={1}>
                        <Grid item>
                          <Typography variant="body2" color="text.secondary">
                            {alert.type === 'price' ? 'Prix' : 'Volume'}{' '}
                            {alert.condition === 'above' ? 'supérieur' : 'inférieur'} à{' '}
                            {alert.value}
                          </Typography>
                        </Grid>
                        <Grid item>
                          <Chip
                            icon={getNotificationIcon(alert.notificationType)}
                            label={alert.notificationType === 'browser' ? 'Navigateur' : 'Email'}
                            size="small"
                            color={alert.triggered ? 'success' : 'default'}
                          />
                        </Grid>
                        <Grid item>
                          <Typography variant="caption" color="text.secondary">
                            Créée le {format(new Date(alert.createdAt), 'dd/MM/yyyy HH:mm')}
                          </Typography>
                        </Grid>
                      </Grid>
                    }
                  />
                </Grid>
                <Grid item>
                  <IconButton 
                    onClick={() => handleDeleteAlert(alert.id)}
                    data-testid={`delete-alert-${alert.id}`}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Grid>
              </Grid>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Créer une Alerte</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="Symbole"
              value={newAlert.symbol}
              onChange={(e) => setNewAlert({ ...newAlert, symbol: e.target.value })}
            />
            <FormControl>
              <InputLabel>Type</InputLabel>
              <Select
                value={newAlert.type}
                label="Type"
                onChange={(e) => setNewAlert({ ...newAlert, type: e.target.value as 'price' | 'volume' | 'indicator' })}
              >
                <MenuItem value="price">Prix</MenuItem>
                <MenuItem value="volume">Volume</MenuItem>
                <MenuItem value="indicator">Indicateur</MenuItem>
              </Select>
            </FormControl>
            <FormControl>
              <InputLabel>Condition</InputLabel>
              <Select
                value={newAlert.condition}
                label="Condition"
                onChange={(e) => setNewAlert({ ...newAlert, condition: e.target.value as 'above' | 'below' })}
              >
                <MenuItem value="above">Supérieur à</MenuItem>
                <MenuItem value="below">Inférieur à</MenuItem>
              </Select>
            </FormControl>
            <TextField
              label="Valeur"
              type="number"
              value={newAlert.value}
              onChange={(e) => setNewAlert({ ...newAlert, value: Number(e.target.value) })}
            />
            <FormControl>
              <InputLabel>Type de notification</InputLabel>
              <Select
                value={newAlert.notificationType}
                label="Type de notification"
                onChange={(e) => setNewAlert({ ...newAlert, notificationType: e.target.value as 'browser' | 'email' })}
              >
                <MenuItem value="browser">Navigateur</MenuItem>
                <MenuItem value="email">Email</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Annuler</Button>
          <Button onClick={handleCreateAlert} variant="contained" color="primary">
            Créer
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 
