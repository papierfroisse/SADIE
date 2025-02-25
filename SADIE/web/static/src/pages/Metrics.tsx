import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CircularProgress, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  AlertTitle,
  Alert,
  Button
} from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Exemple de fonction pour formater les métriques
const formatMetric = (value: number, unit: string) => {
  if (unit === 'ms') {
    return `${value.toFixed(2)} ms`;
  } else if (unit === 'tps') {
    return `${value.toFixed(2)} tps`;
  } else if (unit === '%') {
    return `${value.toFixed(0)}%`;
  }
  return value.toString();
};

// Fonction pour déterminer la couleur selon l'état de santé
const getHealthColor = (health: string) => {
  switch (health) {
    case 'healthy':
      return '#4caf50'; // vert
    case 'degraded':
      return '#ff9800'; // orange
    case 'unhealthy':
      return '#f44336'; // rouge
    default:
      return '#9e9e9e'; // gris
  }
};

const Metrics: React.FC = () => {
  // États
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [metricsData, setMetricsData] = useState<any>(null);
  const [timeframe, setTimeframe] = useState<string>('1h');
  const [exchange, setExchange] = useState<string>('all');
  const [collector, setCollector] = useState<string>('all');
  const [healthData, setHealthData] = useState<any[]>([]);
  const [summaryData, setSummaryData] = useState<any>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');

  // Effet pour vérifier l'authentification au chargement
  useEffect(() => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      setAuthToken(token);
      setIsLoggedIn(true);
      fetchAllMetrics(token);
    }
  }, []);

  // Fonction pour s'authentifier
  const handleLogin = async () => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch('/api/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error('Authentification échouée');
      }
      
      const data = await response.json();
      const token = data.access_token;
      
      // Sauvegarde du token et mise à jour de l'état
      localStorage.setItem('auth_token', token);
      setAuthToken(token);
      setIsLoggedIn(true);
      
      // Récupération des métriques avec le token
      fetchAllMetrics(token);
      
    } catch (error) {
      setError('Erreur d\'authentification. Vérifiez vos identifiants.');
    }
  };

  // Fonction pour se déconnecter
  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setAuthToken(null);
    setIsLoggedIn(false);
    setMetricsData(null);
    setHealthData([]);
    setSummaryData(null);
  };

  // Fonction pour récupérer toutes les métriques
  const fetchAllMetrics = async (token: string) => {
    setLoading(true);
    setError(null);
    
    try {
      // Récupération en parallèle des différentes métriques
      const [metricsResponse, healthResponse, summaryResponse] = await Promise.all([
        fetch(`/api/metrics/collectors?timeframe=${timeframe}&exchange=${exchange !== 'all' ? exchange : ''}&collector_name=${collector !== 'all' ? collector : ''}`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch('/api/metrics/collectors/health', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }),
        fetch('/api/metrics/collectors/summary', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      ]);
      
      if (!metricsResponse.ok || !healthResponse.ok || !summaryResponse.ok) {
        throw new Error('Erreur lors de la récupération des métriques');
      }
      
      const metrics = await metricsResponse.json();
      const health = await healthResponse.json();
      const summary = await summaryResponse.json();
      
      setMetricsData(metrics);
      setHealthData(health.collectors || []);
      setSummaryData(summary.summary);
      
    } catch (error) {
      console.error('Erreur:', error);
      setError('Erreur lors de la récupération des métriques. Vérifiez votre connexion et vos permissions.');
    } finally {
      setLoading(false);
    }
  };

  // Effet pour recharger les métriques lors des changements de filtres
  useEffect(() => {
    if (authToken) {
      fetchAllMetrics(authToken);
    }
  }, [timeframe, exchange, collector]);

  // Si pas d'authentification, afficher le formulaire de connexion
  if (!isLoggedIn) {
    return (
      <Box sx={{ p: 4, maxWidth: 400, mx: 'auto', mt: 8 }}>
        <Typography variant="h4" gutterBottom>
          Authentification requise
        </Typography>
        <Box component="form" sx={{ mt: 2 }}>
          <FormControl fullWidth margin="normal">
            <InputLabel>Nom d'utilisateur</InputLabel>
            <Select
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            >
              <MenuItem value="admin">admin</MenuItem>
              <MenuItem value="analyst">analyst</MenuItem>
              <MenuItem value="operator">operator</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth margin="normal">
            <InputLabel>Mot de passe</InputLabel>
            <Select
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            >
              <MenuItem value="adminpassword">adminpassword</MenuItem>
              <MenuItem value="analystpassword">analystpassword</MenuItem>
              <MenuItem value="operatorpassword">operatorpassword</MenuItem>
            </Select>
          </FormControl>
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}
          <Button 
            variant="contained" 
            color="primary" 
            fullWidth 
            sx={{ mt: 2 }}
            onClick={handleLogin}
          >
            Se connecter
          </Button>
        </Box>
      </Box>
    );
  }

  // Affichage des métriques
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Métriques des Collecteurs</Typography>
        <Button variant="outlined" onClick={handleLogout}>
          Déconnexion
        </Button>
      </Box>
      
      {/* Filtres */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel>Période</InputLabel>
            <Select
              value={timeframe}
              label="Période"
              onChange={(e) => setTimeframe(e.target.value)}
            >
              <MenuItem value="5m">5 minutes</MenuItem>
              <MenuItem value="15m">15 minutes</MenuItem>
              <MenuItem value="1h">1 heure</MenuItem>
              <MenuItem value="6h">6 heures</MenuItem>
              <MenuItem value="24h">24 heures</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel>Exchange</InputLabel>
            <Select
              value={exchange}
              label="Exchange"
              onChange={(e) => setExchange(e.target.value)}
            >
              <MenuItem value="all">Tous</MenuItem>
              <MenuItem value="binance">Binance</MenuItem>
              <MenuItem value="kraken">Kraken</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel>Collecteur</InputLabel>
            <Select
              value={collector}
              label="Collecteur"
              onChange={(e) => setCollector(e.target.value)}
            >
              <MenuItem value="all">Tous</MenuItem>
              {healthData.map((item) => (
                <MenuItem key={item.name} value={item.name}>
                  {item.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 5 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">
          <AlertTitle>Erreur</AlertTitle>
          {error}
        </Alert>
      ) : (
        <>
          {/* Résumé des métriques */}
          {summaryData && (
            <Grid container spacing={2} sx={{ mb: 4 }}>
              <Grid item xs={12}>
                <Typography variant="h6" gutterBottom>
                  Résumé des dernières 24 heures
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary">
                      Débit moyen
                    </Typography>
                    <Typography variant="h5">
                      {formatMetric(summaryData.avg_throughput, 'tps')}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary">
                      Latence moyenne
                    </Typography>
                    <Typography variant="h5">
                      {formatMetric(summaryData.avg_latency, 'ms')}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary">
                      Taux d'erreur moyen
                    </Typography>
                    <Typography variant="h5">
                      {formatMetric(summaryData.avg_error_rate, '%')}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" color="text.secondary">
                      État de santé global
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: getHealthColor(summaryData.overall_status),
                          mr: 1
                        }}
                      />
                      <Typography variant="h5" sx={{ textTransform: 'capitalize' }}>
                        {summaryData.overall_status}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
          
          {/* Tableau de santé des collecteurs */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              État de santé des collecteurs
            </Typography>
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Nom</TableCell>
                    <TableCell>Exchange</TableCell>
                    <TableCell>Symboles</TableCell>
                    <TableCell>Santé</TableCell>
                    <TableCell>Statut</TableCell>
                    <TableCell>Dernière mise à jour</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {healthData.map((item) => (
                    <TableRow key={item.name}>
                      <TableCell>{item.name}</TableCell>
                      <TableCell>{item.exchange}</TableCell>
                      <TableCell>
                        {item.symbols.map((symbol: string) => (
                          <Chip key={symbol} label={symbol} size="small" sx={{ mr: 0.5 }} />
                        ))}
                      </TableCell>
                      <TableCell>{formatMetric(item.health, '%')}</TableCell>
                      <TableCell>
                        <Chip
                          label={item.status}
                          sx={{
                            bgcolor: getHealthColor(item.status),
                            color: 'white',
                            textTransform: 'capitalize'
                          }}
                        />
                      </TableCell>
                      <TableCell>
                        {new Date(item.timestamp).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
          
          {/* Graphiques des métriques */}
          {metricsData && metricsData.metrics && (
            <Grid container spacing={3}>
              {Object.keys(metricsData.metrics).map((metricType) => (
                <Grid item xs={12} md={6} key={metricType}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {metricType === 'throughput' 
                          ? 'Débit (trades/s)' 
                          : metricType === 'latency' 
                            ? 'Latence (ms)' 
                            : metricType === 'error_rate' 
                              ? 'Taux d\'erreur (%)' 
                              : metricType === 'health' 
                                ? 'Santé (%)' 
                                : metricType}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Valeur: {formatMetric(
                          metricsData.metrics[metricType].value, 
                          metricType === 'latency' ? 'ms' : metricType === 'throughput' ? 'tps' : '%'
                        )}
                      </Typography>
                      {metricsData.metrics[metricType].min !== undefined && (
                        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                          <Typography variant="body2" color="text.secondary">
                            Min: {formatMetric(
                              metricsData.metrics[metricType].min, 
                              metricType === 'latency' ? 'ms' : metricType === 'throughput' ? 'tps' : '%'
                            )}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Max: {formatMetric(
                              metricsData.metrics[metricType].max, 
                              metricType === 'latency' ? 'ms' : metricType === 'throughput' ? 'tps' : '%'
                            )}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Écart type: {formatMetric(
                              metricsData.metrics[metricType].std_dev, 
                              metricType === 'latency' ? 'ms' : metricType === 'throughput' ? 'tps' : '%'
                            )}
                          </Typography>
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </>
      )}
    </Box>
  );
};

export default Metrics; 