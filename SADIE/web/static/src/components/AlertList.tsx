import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Stack,
  Grid,
  useTheme,
  Tooltip,
  Divider,
  Alert as MuiAlert,
  CircularProgress,
  Snackbar,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Add as AddIcon,
  Notifications as NotificationsIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Email as EmailIcon,
  NotificationsActive as NotificationsActiveIcon,
  NotificationsOff as NotificationsOffIcon,
  FilterList as FilterListIcon,
  AttachMoney as AttachMoneyIcon,
  BarChart as BarChartIcon,
  ShowChart as ShowChartIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';
import { Alert } from '../types';
import { api } from '../services/api';
import { useWebSocket } from '../context/WebSocketContext';

export const AlertList: React.FC = () => {
  const theme = useTheme();
  const { lastAlert, isConnected, error: wsError } = useWebSocket();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notificationsEnabled, setNotificationsEnabled] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'info' | 'warning' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'info',
  });
  const [newAlert, setNewAlert] = useState<Partial<Alert>>({
    symbol: '',
    type: 'price',
    condition: 'above',
    value: 0,
    notificationType: 'browser',
  });

  const loadAlerts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.getAlerts();
      if (response.success && response.data) {
        setAlerts(response.data);
      } else {
        setError('Erreur lors du chargement des alertes');
      }
    } catch (err) {
      setError('Erreur lors du chargement des alertes');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  useEffect(() => {
    const checkNotificationPermission = async () => {
      if ('Notification' in window) {
        const permission = await Notification.requestPermission();
        setNotificationsEnabled(permission === 'granted');
      }
    };
    checkNotificationPermission();
  }, []);

  useEffect(() => {
    if (lastAlert) {
      setAlerts(prev => prev.map(alert => (alert.id === lastAlert.id ? lastAlert : alert)));

      if (lastAlert.triggered && notificationsEnabled) {
        const notificationTitle = `Alerte ${lastAlert.symbol}`;
        const notificationBody = `Condition ${lastAlert.condition} ${lastAlert.value} atteinte`;

        new Notification(notificationTitle, { body: notificationBody });
      }
    }
  }, [lastAlert, notificationsEnabled]);

  useEffect(() => {
    if (wsError) {
      setSnackbar({
        open: true,
        message: 'Problème de connexion au serveur de notifications',
        severity: 'warning',
      });
    }
  }, [wsError]);

  const handleCreateAlert = async () => {
    if (newAlert.symbol && newAlert.value !== undefined) {
      try {
        setError(null);
        const alertToCreate = {
          ...newAlert,
          createdAt: Date.now(),
          triggered: false,
        } as Omit<Alert, 'id'>;

        const response = await api.createAlert(alertToCreate);
        if (response.success && response.data) {
          setAlerts([...alerts, response.data]);
          setOpenDialog(false);
          setNewAlert({
            symbol: '',
            type: 'price',
            condition: 'above',
            value: 0,
            notificationType: 'browser',
          });
        } else {
          setError("Erreur lors de la création de l'alerte");
        }
      } catch (err) {
        setError("Erreur lors de la création de l'alerte");
      }
    }
  };

  const handleDeleteAlert = async (id: string) => {
    try {
      setError(null);
      const response = await api.deleteAlert(id);
      if (response.success) {
        setAlerts(alerts.filter(alert => alert.id !== id));
      } else {
        setError("Erreur lors de la suppression de l'alerte");
      }
    } catch (err) {
      setError("Erreur lors de la suppression de l'alerte");
    }
  };

  const getAlertIcon = (alert: Alert) => {
    switch (alert.type) {
      case 'price':
        return <AttachMoneyIcon />;
      case 'volume':
        return <BarChartIcon />;
      case 'indicator':
        return <ShowChartIcon />;
      default:
        return <NotificationsIcon />;
    }
  };

  const getNotificationIcon = (type: string) => {
    return type === 'browser' ? (
      <NotificationsActiveIcon fontSize="small" />
    ) : (
      <EmailIcon fontSize="small" />
    );
  };

  const handleNotificationToggle = async () => {
    if ('Notification' in window) {
      if (notificationsEnabled) {
        setNotificationsEnabled(false);
        setSnackbar({
          open: true,
          message: 'Notifications désactivées',
          severity: 'info',
        });
      } else {
        const permission = await Notification.requestPermission();
        setNotificationsEnabled(permission === 'granted');
        setSnackbar({
          open: true,
          message:
            permission === 'granted'
              ? 'Notifications activées'
              : 'Permission refusée pour les notifications',
          severity: permission === 'granted' ? 'success' : 'warning',
        });
      }
    } else {
      setSnackbar({
        open: true,
        message: 'Les notifications ne sont pas supportées par votre navigateur',
        severity: 'error',
      });
    }
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5">Alertes</Typography>
        <Box>
          <Tooltip
            title={
              !isConnected
                ? 'Connexion perdue'
                : notificationsEnabled
                  ? 'Désactiver les notifications'
                  : 'Activer les notifications'
            }
          >
            <span>
              <IconButton
                onClick={handleNotificationToggle}
                color={!isConnected ? 'error' : notificationsEnabled ? 'primary' : 'default'}
                disabled={!isConnected}
                data-testid="notification-toggle"
              >
                {!isConnected ? (
                  <NotificationsOffIcon />
                ) : notificationsEnabled ? (
                  <NotificationsActiveIcon />
                ) : (
                  <NotificationsOffIcon />
                )}
              </IconButton>
            </span>
          </Tooltip>
          <Box component="span" sx={{ ml: 1 }}>
            <Typography variant="caption" color="text.secondary" data-testid="notification-status">
              {notificationsEnabled ? 'Notifications activées' : 'Notifications désactivées'}
            </Typography>
          </Box>
          <Button
            variant="contained"
            onClick={() => setOpenDialog(true)}
            startIcon={<AddIcon />}
            data-testid="new-alert-button"
            sx={{ ml: 1 }}
          >
            Nouvelle Alerte
          </Button>
        </Box>
      </Box>

      <Grid container spacing={2} alignItems="center" sx={{ mb: 3 }}>
        <Grid item xs>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <NotificationsIcon color="primary" />
            <Typography variant="h6">Alertes de Trading</Typography>
            <Chip
              label={`${alerts.length} ${alerts.length > 1 ? 'alertes' : 'alerte'}`}
              color="primary"
              size="small"
            />
          </Box>
        </Grid>
        <Grid item>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Filtrer">
              <IconButton size="small">
                <FilterListIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Grid>
      </Grid>

      {wsError && (
        <MuiAlert severity="warning" sx={{ mb: 2 }}>
          Problème de connexion au serveur de notifications. Les alertes peuvent être retardées.
        </MuiAlert>
      )}

      {error && (
        <MuiAlert severity="error" sx={{ mb: 2 }}>
          {error}
        </MuiAlert>
      )}

      <Paper sx={{ position: 'relative' }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : alerts.length === 0 ? (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <NotificationsIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Aucune alerte
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Créez votre première alerte en cliquant sur le bouton &quot;Nouvelle Alerte&quot;
            </Typography>
          </Box>
        ) : (
          <List data-testid="alerts-list">
            {alerts.map((alert, index) => (
              <React.Fragment key={alert.id}>
                {index > 0 && <Divider />}
                <ListItem
                  data-testid="alert-item"
                  sx={{
                    '&:hover': {
                      backgroundColor: theme.palette.action.hover,
                    },
                  }}
                  secondaryAction={
                    <IconButton
                      edge="end"
                      onClick={() => handleDeleteAlert(alert.id)}
                      data-testid="delete-alert-button"
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                >
                  <ListItemText
                    primary={
                      <div>
                        <Grid container spacing={1} alignItems="center">
                          <Grid item>{getAlertIcon(alert)}</Grid>
                          <Grid item>
                            <Typography variant="body1">{alert.symbol}</Typography>
                          </Grid>
                        </Grid>
                        <Grid container spacing={1} alignItems="center">
                          <Grid item>
                            <Typography variant="body2" color="text.secondary">
                              {alert.type === 'price' ? 'Prix' : alert.type === 'volume' ? 'Volume' : 'Indicateur'}{' '}
                              {alert.condition === 'above' ? 'supérieur' : 'inférieur'} à{' '}
                              {alert.value}
                            </Typography>
                          </Grid>
                          <Grid item>
                            <Divider orientation="vertical" flexItem />
                          </Grid>
                          <Grid item>
                            <Chip
                              icon={getNotificationIcon(alert.notificationType)}
                              label={alert.notificationType === 'browser' ? 'Navigateur' : 'Email'}
                              size="small"
                              color={alert.triggered ? 'success' : 'default'}
                            />
                          </Grid>
                        </Grid>
                      </div>
                    }
                    secondary={
                      <Typography variant="caption" color="text.secondary">
                        Créée le {format(new Date(alert.createdAt), 'dd/MM/yyyy HH:mm')}
                      </Typography>
                    }
                  />
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        )}
      </Paper>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Stack direction="row" spacing={1} alignItems="center">
            <AddIcon color="primary" />
            <Typography variant="h6">Nouvelle Alerte</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12}>
                <TextField
                  id="symbol"
                  label="Symbole"
                  fullWidth
                  value={newAlert.symbol}
                  onChange={e => setNewAlert({ ...newAlert, symbol: e.target.value })}
                  data-testid="symbol-input"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="type-label">Type</InputLabel>
                  <Select
                    labelId="type-label"
                    id="type"
                    value={newAlert.type}
                    label="Type"
                    data-testid="type-select"
                    onChange={e =>
                      setNewAlert({ 
                        ...newAlert, 
                        type: e.target.value as 'price' | 'volume' | 'indicator' 
                      })
                    }
                  >
                    <MenuItem value="price">Prix</MenuItem>
                    <MenuItem value="volume">Volume</MenuItem>
                    <MenuItem value="indicator">Indicateur</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="condition-label">Condition</InputLabel>
                  <Select
                    labelId="condition-label"
                    id="condition"
                    value={newAlert.condition}
                    label="Condition"
                    data-testid="condition-select"
                    onChange={e =>
                      setNewAlert({ ...newAlert, condition: e.target.value as 'above' | 'below' })
                    }
                  >
                    <MenuItem value="above">Au-dessus de</MenuItem>
                    <MenuItem value="below">En-dessous de</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField
                  id="value"
                  label="Valeur"
                  type="number"
                  fullWidth
                  value={newAlert.value}
                  onChange={e => setNewAlert({ ...newAlert, value: parseFloat(e.target.value) })}
                  data-testid="price-input"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                  <InputLabel id="notification-type-label">Type de notification</InputLabel>
                  <Select
                    labelId="notification-type-label"
                    id="notification-type"
                    value={newAlert.notificationType}
                    label="Type de notification"
                    data-testid="notification-type-select"
                    onChange={e =>
                      setNewAlert({
                        ...newAlert,
                        notificationType: e.target.value as 'browser' | 'email',
                      })
                    }
                  >
                    <MenuItem value="browser">Navigateur</MenuItem>
                    <MenuItem value="email">Email</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setOpenDialog(false)}>Annuler</Button>
          <Button
            onClick={handleCreateAlert}
            variant="contained"
            color="primary"
            data-testid="create-alert-button"
            disabled={!newAlert.symbol || newAlert.value === undefined}
          >
            Créer
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <MuiAlert
          elevation={6}
          variant="filled"
          severity={snackbar.severity}
          onClose={handleCloseSnackbar}
        >
          {snackbar.message}
        </MuiAlert>
      </Snackbar>
    </Box>
  );
};
