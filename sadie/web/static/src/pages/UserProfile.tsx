import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  TextField,
  Button,
  Divider,
  Alert,
  Snackbar,
  IconButton,
  Chip,
  Avatar,
  Card,
  CardContent,
  CardHeader,
  Switch,
  FormControlLabel,
  Tooltip
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { styled } from '@mui/material/styles';
import PersonIcon from '@mui/icons-material/Person';
import SecurityIcon from '@mui/icons-material/Security';
import ApiIcon from '@mui/icons-material/Api';
import SaveIcon from '@mui/icons-material/Save';
import { logoutUser } from '../services/api';
import { useNavigate } from 'react-router-dom';

// Interfaces pour les données du profil
interface ApiKey {
  exchange: string;
  apiKey: string;
  apiSecret: string;
  enabled: boolean;
}

interface UserPreferences {
  notifications: boolean;
  darkMode: boolean;
  autoRefresh: boolean;
  refreshInterval: number;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  margin: theme.spacing(2, 0),
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
  borderRadius: theme.spacing(1),
}));

const ApiKeyCard = styled(Card)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  borderLeft: `4px solid ${theme.palette.primary.main}`,
}));

const UserProfile: React.FC = () => {
  const navigate = useNavigate();
  const username = localStorage.getItem('username') || 'Utilisateur';
  
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([
    { exchange: 'Binance', apiKey: '', apiSecret: '', enabled: false },
    { exchange: 'Kraken', apiKey: '', apiSecret: '', enabled: false },
  ]);
  
  const [preferences, setPreferences] = useState<UserPreferences>({
    notifications: true,
    darkMode: true,
    autoRefresh: true,
    refreshInterval: 30,
  });
  
  const [showSecrets, setShowSecrets] = useState<{[key: string]: boolean}>({});
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // Effet pour charger les clés API depuis le stockage local
  useEffect(() => {
    // Dans un environnement réel, ces données viendraient d'une API
    const storedKeys = localStorage.getItem('api_keys');
    if (storedKeys) {
      try {
        setApiKeys(JSON.parse(storedKeys));
      } catch (e) {
        console.error('Erreur lors du chargement des clés API:', e);
      }
    }
    
    const storedPrefs = localStorage.getItem('user_preferences');
    if (storedPrefs) {
      try {
        setPreferences(JSON.parse(storedPrefs));
      } catch (e) {
        console.error('Erreur lors du chargement des préférences:', e);
      }
    }
  }, []);
  
  const handleApiKeyChange = (index: number, field: keyof ApiKey, value: string | boolean) => {
    const newKeys = [...apiKeys];
    newKeys[index] = { ...newKeys[index], [field]: value };
    setApiKeys(newKeys);
  };
  
  const handlePreferenceChange = (field: keyof UserPreferences, value: boolean | number) => {
    setPreferences(prev => ({ ...prev, [field]: value }));
  };
  
  const toggleShowSecret = (exchange: string) => {
    setShowSecrets(prev => ({ ...prev, [exchange]: !prev[exchange] }));
  };
  
  const handleSaveApiKeys = () => {
    try {
      // Dans un environnement réel, ces données seraient envoyées à une API
      localStorage.setItem('api_keys', JSON.stringify(apiKeys));
      setSuccessMessage('Clés API sauvegardées avec succès');
    } catch (e) {
      setErrorMessage('Erreur lors de la sauvegarde des clés API');
      console.error(e);
    }
  };
  
  const handleSavePreferences = () => {
    try {
      localStorage.setItem('user_preferences', JSON.stringify(preferences));
      setSuccessMessage('Préférences sauvegardées avec succès');
    } catch (e) {
      setErrorMessage('Erreur lors de la sauvegarde des préférences');
      console.error(e);
    }
  };
  
  const handleLogout = () => {
    logoutUser();
    navigate('/login');
  };
  
  const closeSuccessAlert = () => {
    setSuccessMessage('');
  };
  
  const closeErrorAlert = () => {
    setErrorMessage('');
  };
  
  return (
    <Container maxWidth="lg">
      <Box mt={4} mb={2}>
        <Typography variant="h4" component="h1" gutterBottom>
          Profil utilisateur
        </Typography>
        <Chip
          icon={<PersonIcon />}
          label={username}
          color="primary"
          variant="outlined"
          size="medium"
        />
      </Box>
      
      {/* Section profil utilisateur */}
      <StyledPaper>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5" component="h2">
            <PersonIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
            Informations personnelles
          </Typography>
          <Button variant="outlined" color="secondary" onClick={handleLogout}>
            Se déconnecter
          </Button>
        </Box>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Nom d'utilisateur"
              variant="outlined"
              value={username}
              disabled
              InputProps={{
                readOnly: true,
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Adresse email"
              variant="outlined"
              value="utilisateur@exemple.com"
              disabled
              InputProps={{
                readOnly: true,
              }}
            />
          </Grid>
        </Grid>
      </StyledPaper>
      
      {/* Section clés API */}
      <StyledPaper>
        <Typography variant="h5" component="h2" mb={3}>
          <ApiIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          Clés API des exchanges
        </Typography>
        
        <Alert severity="info" sx={{ mb: 3 }}>
          Les clés API sont stockées de manière sécurisée et sont utilisées uniquement pour récupérer vos données de trading. Elles ne sont jamais partagées.
        </Alert>
        
        {apiKeys.map((key, index) => (
          <ApiKeyCard key={key.exchange}>
            <CardHeader
              title={key.exchange}
              action={
                <FormControlLabel
                  control={
                    <Switch
                      checked={key.enabled}
                      onChange={(e) => handleApiKeyChange(index, 'enabled', e.target.checked)}
                      color="primary"
                    />
                  }
                  label={key.enabled ? "Activé" : "Désactivé"}
                />
              }
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Clé API"
                    variant="outlined"
                    value={key.apiKey}
                    onChange={(e) => handleApiKeyChange(index, 'apiKey', e.target.value)}
                    placeholder={`Entrez votre clé API ${key.exchange}`}
                    size="small"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Secret API"
                    variant="outlined"
                    type={showSecrets[key.exchange] ? 'text' : 'password'}
                    value={key.apiSecret}
                    onChange={(e) => handleApiKeyChange(index, 'apiSecret', e.target.value)}
                    placeholder={`Entrez votre secret API ${key.exchange}`}
                    size="small"
                    InputProps={{
                      endAdornment: (
                        <IconButton
                          onClick={() => toggleShowSecret(key.exchange)}
                          edge="end"
                        >
                          {showSecrets[key.exchange] ? <VisibilityOffIcon /> : <VisibilityIcon />}
                        </IconButton>
                      ),
                    }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </ApiKeyCard>
        ))}
        
        <Box display="flex" justifyContent="flex-end" mt={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<SaveIcon />}
            onClick={handleSaveApiKeys}
          >
            Sauvegarder les clés API
          </Button>
        </Box>
      </StyledPaper>
      
      {/* Section préférences */}
      <StyledPaper>
        <Typography variant="h5" component="h2" mb={3}>
          <SecurityIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          Préférences
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.notifications}
                  onChange={(e) => handlePreferenceChange('notifications', e.target.checked)}
                  color="primary"
                />
              }
              label="Recevoir des notifications"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.darkMode}
                  onChange={(e) => handlePreferenceChange('darkMode', e.target.checked)}
                  color="primary"
                />
              }
              label="Mode sombre"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={preferences.autoRefresh}
                  onChange={(e) => handlePreferenceChange('autoRefresh', e.target.checked)}
                  color="primary"
                />
              }
              label="Actualisation automatique des données"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Intervalle d'actualisation (secondes)"
              variant="outlined"
              type="number"
              value={preferences.refreshInterval}
              onChange={(e) => handlePreferenceChange('refreshInterval', parseInt(e.target.value, 10))}
              disabled={!preferences.autoRefresh}
              InputProps={{
                inputProps: { min: 10, max: 3600 }
              }}
            />
          </Grid>
        </Grid>
        
        <Box display="flex" justifyContent="flex-end" mt={3}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<SaveIcon />}
            onClick={handleSavePreferences}
          >
            Sauvegarder les préférences
          </Button>
        </Box>
      </StyledPaper>
      
      {/* Snackbars pour les notifications */}
      <Snackbar
        open={!!successMessage}
        autoHideDuration={6000}
        onClose={closeSuccessAlert}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={closeSuccessAlert} severity="success">
          {successMessage}
        </Alert>
      </Snackbar>
      
      <Snackbar
        open={!!errorMessage}
        autoHideDuration={6000}
        onClose={closeErrorAlert}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={closeErrorAlert} severity="error">
          {errorMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default UserProfile; 