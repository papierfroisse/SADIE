import React, { useState, useEffect } from 'react';
import { Alert } from '../types';
import { api } from '../services/api';
import { Notifications as NotificationsIcon, Email as EmailIcon } from '@mui/icons-material';
import { 
  Box,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  Grid,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  MenuItem,
  Select,
  TextField,
  Typography
} from '@mui/material';
import { format } from 'date-fns';

const AlertList: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [open, setOpen] = useState(false);
  const [newAlert, setNewAlert] = useState<Partial<Alert>>({
    symbol: '',
    type: 'price',
    condition: 'above',
    value: 0,
    notification_type: 'browser'
  });

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const response = await api.getAlerts();
      if (response.success && response.data) {
        setAlerts(response.data);
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
    }
  };

  const handleCreateAlert = async () => {
    try {
      const response = await api.createAlert({
        symbol: newAlert.symbol as string,
        type: newAlert.type as 'price' | 'indicator',
        condition: newAlert.condition as 'above' | 'below',
        value: Number(newAlert.value),
        notification_type: newAlert.notification_type as 'browser' | 'email',
        triggered: false,
        created_at: new Date().getTime()
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

  const resetForm = () => {
    setNewAlert({
      symbol: '',
      type: 'price',
      condition: 'above',
      value: 0,
      notification_type: 'browser'
    });
  };

  const getNotificationIcon = (type: 'browser' | 'email') => {
    switch (type) {
      case 'browser':
        return <NotificationsIcon />;
      case 'email':
        return <EmailIcon />;
      default:
        return <NotificationsIcon />;
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Alertes</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setOpen(true)}
        >
          Nouvelle Alerte
        </Button>
      </Box>

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
                          {alert.type === 'price' ? 'Prix' : 'Indicateur'}{' '}
                          {alert.condition === 'above' ? 'supérieur' : 'inférieur'} à{' '}
                          {alert.value}
                        </Typography>
                      </Grid>
                      <Grid item>
                        <Chip
                          icon={getNotificationIcon(alert.notification_type)}
                          label={alert.notification_type === 'browser' ? 'Navigateur' : 'Email'}
                          size="small"
                          color={alert.triggered ? 'success' : 'default'}
                        />
                      </Grid>
                      <Grid item>
                        <Typography variant="caption" color="text.secondary">
                          Créée le {format(new Date(alert.created_at), 'dd/MM/yyyy HH:mm')}
                        </Typography>
                      </Grid>
                    </Grid>
                  }
                />
              </Grid>
            </Grid>
          </ListItem>
        ))}
      </List>

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
                onChange={(e) => setNewAlert({ ...newAlert, type: e.target.value as 'price' | 'indicator' })}
              >
                <MenuItem value="price">Prix</MenuItem>
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
                value={newAlert.notification_type}
                label="Type de notification"
                onChange={(e) => setNewAlert({ ...newAlert, notification_type: e.target.value as 'browser' | 'email' })}
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

export default AlertList; 
