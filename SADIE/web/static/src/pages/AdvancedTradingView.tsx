import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Chip,
  Divider,
  CircularProgress,
  Alert,
  Snackbar,
  Autocomplete,
  ToggleButton,
  ToggleButtonGroup,
  Card,
  CardContent,
  Slider,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tabs,
  Tab
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AddIcon from '@mui/icons-material/Add';
import RemoveIcon from '@mui/icons-material/Remove';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TimelineIcon from '@mui/icons-material/Timeline';
import SettingsIcon from '@mui/icons-material/Settings';
import SaveIcon from '@mui/icons-material/Save';
import DownloadIcon from '@mui/icons-material/Download';
import VisibilityIcon from '@mui/icons-material/Visibility';
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff';
import { styled } from '@mui/material/styles';
import { isAuthenticated } from '../services/api';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

// Types pour les données de trading
interface PriceData {
  timestamp: number;
  open: number;
  high: number;
  close: number;
  low: number;
  volume: number;
}

// Interface pour la réponse API
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Types pour les indicateurs techniques
interface Indicator {
  id: string;
  name: string;
  type: string;
  parameters: IndicatorParameter[];
  color: string;
  visible: boolean;
}

interface IndicatorParameter {
  name: string;
  type: 'number' | 'select' | 'boolean';
  value: any;
  options?: string[];
  min?: number;
  max?: number;
}

// Constantes pour les indicateurs disponibles
const AVAILABLE_INDICATORS = [
  {
    id: 'sma',
    name: 'Moyenne Mobile Simple',
    type: 'overlay',
    parameters: [
      { name: 'période', type: 'number', value: 20, min: 1, max: 200 }
    ],
    defaultColor: '#2196F3'
  },
  {
    id: 'ema',
    name: 'Moyenne Mobile Exponentielle',
    type: 'overlay',
    parameters: [
      { name: 'période', type: 'number', value: 20, min: 1, max: 200 }
    ],
    defaultColor: '#FF5722'
  },
  {
    id: 'bollinger',
    name: 'Bandes de Bollinger',
    type: 'overlay',
    parameters: [
      { name: 'période', type: 'number', value: 20, min: 1, max: 200 },
      { name: 'écart-type', type: 'number', value: 2, min: 0.1, max: 5 }
    ],
    defaultColor: '#4CAF50'
  },
  {
    id: 'rsi',
    name: 'RSI',
    type: 'oscillator',
    parameters: [
      { name: 'période', type: 'number', value: 14, min: 1, max: 100 }
    ],
    defaultColor: '#9C27B0'
  },
  {
    id: 'macd',
    name: 'MACD',
    type: 'oscillator',
    parameters: [
      { name: 'période rapide', type: 'number', value: 12, min: 1, max: 100 },
      { name: 'période lente', type: 'number', value: 26, min: 1, max: 100 },
      { name: 'période signal', type: 'number', value: 9, min: 1, max: 100 }
    ],
    defaultColor: '#E91E63'
  },
  {
    id: 'stochastic',
    name: 'Stochastique',
    type: 'oscillator',
    parameters: [
      { name: 'période K', type: 'number', value: 14, min: 1, max: 100 },
      { name: 'période D', type: 'number', value: 3, min: 1, max: 100 },
      { name: 'lissage', type: 'number', value: 3, min: 1, max: 100 }
    ],
    defaultColor: '#FFC107'
  },
  {
    id: 'atr',
    name: 'ATR',
    type: 'oscillator',
    parameters: [
      { name: 'période', type: 'number', value: 14, min: 1, max: 100 }
    ],
    defaultColor: '#607D8B'
  }
];

// Constantes pour les périodes disponibles
const AVAILABLE_TIMEFRAMES = [
  { value: '1m', label: '1 minute' },
  { value: '5m', label: '5 minutes' },
  { value: '15m', label: '15 minutes' },
  { value: '30m', label: '30 minutes' },
  { value: '1h', label: '1 heure' },
  { value: '4h', label: '4 heures' },
  { value: '1d', label: 'Journalier' },
  { value: '1w', label: 'Hebdomadaire' }
];

const AVAILABLE_EXCHANGES = [
  { value: 'binance', label: 'Binance' },
  { value: 'kraken', label: 'Kraken' }
];

// Pairs de trading populaires
const POPULAR_PAIRS = [
  'BTC/USDT',
  'ETH/USDT',
  'BNB/USDT',
  'XRP/USDT',
  'ADA/USDT',
  'SOL/USDT',
  'DOT/USDT',
  'DOGE/USDT'
];

// Styles personnalisés
const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  margin: theme.spacing(2, 0),
  borderRadius: theme.spacing(1),
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
}));

const ChartContainer = styled(Box)(({ theme }) => ({
  height: 500,
  background: theme.palette.mode === 'dark' ? '#1E1E1E' : '#F5F5F5',
  borderRadius: theme.spacing(1),
  overflow: 'hidden',
  position: 'relative',
  marginBottom: theme.spacing(2)
}));

const IndicatorChip = styled(Chip)<{ indicatorcolor: string }>(({ theme, indicatorcolor }) => ({
  margin: theme.spacing(0.5),
  backgroundColor: indicatorcolor,
  '&:hover': {
    backgroundColor: indicatorcolor,
    opacity: 0.8
  },
  '& .MuiChip-label': {
    color: theme.palette.getContrastText(indicatorcolor)
  }
}));

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`indicator-tabpanel-${index}`}
      aria-labelledby={`indicator-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

const a11yProps = (index: number) => {
  return {
    id: `indicator-tab-${index}`,
    'aria-controls': `indicator-tabpanel-${index}`,
  };
};

const AdvancedTradingView: React.FC = () => {
  const navigate = useNavigate();
  const chartRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [exchange, setExchange] = useState('binance');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [timeframe, setTimeframe] = useState('1h');
  const [chartType, setChartType] = useState('candlestick');
  const [indicators, setIndicators] = useState<Indicator[]>([]);
  const [availableSymbols, setAvailableSymbols] = useState<string[]>(POPULAR_PAIRS);
  const [tabValue, setTabValue] = useState(0);
  const [chartData, setChartData] = useState<PriceData[]>([]);

  // Vérifier l'authentification au chargement
  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    } else {
      // Charger les symboles disponibles depuis la base de données
      fetchAvailableSymbols();
      // Charger les données initiales
      fetchChartData();
    }
  }, [navigate]);

  // Récupérer les symboles disponibles depuis la base de données
  const fetchAvailableSymbols = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get<ApiResponse<string[]>>(`/api/market/symbols?exchange=${exchange}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (response.data.success && response.data.data) {
        setAvailableSymbols(response.data.data);
      }
    } catch (err) {
      console.error('Erreur lors de la récupération des symboles disponibles:', err);
    }
  };

  // Récupérer les données du graphique depuis la base de données
  const fetchChartData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      // Formater le symbole pour l'API backend
      const formattedSymbol = symbol.replace('/', '');
      
      // Appel à notre API backend pour récupérer les données historiques
      const response = await axios.get<ApiResponse<PriceData[]>>(
        `/api/market/${exchange}/${formattedSymbol}/klines`, 
        {
          params: {
            interval: timeframe,
            limit: 500  // Nombre de chandeliers à récupérer
          },
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      if (response.data.success && response.data.data) {
        setChartData(response.data.data);
        setSuccess('Données chargées avec succès');
        setTimeout(() => setSuccess(null), 3000);
        
        // Appliquer les indicateurs techniques aux données
        applyIndicators(response.data.data);
      } else {
        setError(response.data.error || 'Erreur lors du chargement des données');
      }
    } catch (err: any) {
      setError(`Erreur lors du chargement des données: ${err.message || 'Erreur inconnue'}`);
      console.error('Erreur lors du chargement des données:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Appliquer les indicateurs techniques aux données du graphique
  const applyIndicators = (data: PriceData[]) => {
    // Dans une implémentation réelle, cette fonction calculerait les valeurs des indicateurs
    // et les ajouterait aux données du graphique pour affichage
    console.log('Application des indicateurs aux données:', indicators);
    
    // Exemple de calcul pour un indicateur SMA
    indicators.forEach(indicator => {
      if (indicator.visible) {
        if (indicator.id.startsWith('sma')) {
          const period = indicator.parameters.find(p => p.name === 'période')?.value || 20;
          // Calcul du SMA (Simple Moving Average)
          calculateSMA(data, period, indicator.color);
        }
        // Ajoutez d'autres calculs d'indicateurs ici...
      }
    });
  };

  // Exemple de calcul d'un SMA (Simple Moving Average)
  const calculateSMA = (data: PriceData[], period: number, color: string) => {
    // Implémentation simplifiée - dans un environnement de production, 
    // utilisez une bibliothèque comme technicalindicators
    console.log(`Calcul du SMA avec période ${period} et couleur ${color}`);
    
    // Le vrai calcul serait:
    // let smaValues = [];
    // for (let i = period - 1; i < data.length; i++) {
    //   const sum = data.slice(i - period + 1, i + 1).reduce((acc, candle) => acc + candle.close, 0);
    //   smaValues.push({ timestamp: data[i].timestamp, value: sum / period });
    // }
    // return smaValues;
  };

  // Gérer le changement de symbole
  const handleSymbolChange = (_event: React.SyntheticEvent, newValue: string | null) => {
    if (newValue) {
      setSymbol(newValue);
    }
  };

  // Gérer le changement de période
  const handleTimeframeChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setTimeframe(event.target.value as string);
  };

  // Gérer le changement d'exchange
  const handleExchangeChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setExchange(event.target.value as string);
    // Mettre à jour les symboles disponibles pour le nouvel exchange
    fetchAvailableSymbols();
  };

  // Gérer le changement de type de graphique
  const handleChartTypeChange = (_event: React.MouseEvent<HTMLElement>, newChartType: string | null) => {
    if (newChartType) {
      setChartType(newChartType);
    }
  };

  // Ajouter un indicateur
  const handleAddIndicator = (indicatorId: string) => {
    const indicatorTemplate = AVAILABLE_INDICATORS.find(ind => ind.id === indicatorId);
    
    if (indicatorTemplate) {
      const newIndicator: Indicator = {
        id: `${indicatorId}-${Date.now()}`,
        name: indicatorTemplate.name,
        type: indicatorTemplate.type,
        parameters: JSON.parse(JSON.stringify(indicatorTemplate.parameters)),
        color: indicatorTemplate.defaultColor,
        visible: true
      };
      
      setIndicators([...indicators, newIndicator]);
      setSuccess(`Indicateur ${indicatorTemplate.name} ajouté`);
      setTimeout(() => setSuccess(null), 3000);
      
      // Appliquer immédiatement si des données sont déjà chargées
      if (chartData.length > 0) {
        applyIndicators(chartData);
      }
    }
  };

  // Supprimer un indicateur
  const handleRemoveIndicator = (indicatorId: string) => {
    setIndicators(indicators.filter(ind => ind.id !== indicatorId));
    
    // Réappliquer les indicateurs restants
    if (chartData.length > 0) {
      applyIndicators(chartData);
    }
  };

  // Modifier la visibilité d'un indicateur
  const toggleIndicatorVisibility = (indicatorId: string) => {
    setIndicators(indicators.map(ind => 
      ind.id === indicatorId ? { ...ind, visible: !ind.visible } : ind
    ));
    
    // Réappliquer les indicateurs avec la nouvelle visibilité
    if (chartData.length > 0) {
      applyIndicators(chartData);
    }
  };

  // Modifier un paramètre d'indicateur
  const handleParameterChange = (indicatorId: string, paramName: string, value: any) => {
    setIndicators(indicators.map(ind => {
      if (ind.id === indicatorId) {
        return {
          ...ind,
          parameters: ind.parameters.map(param => 
            param.name === paramName ? { ...param, value } : param
          )
        };
      }
      return ind;
    }));
  };

  // Appliquer les changements et mettre à jour le graphique
  const applyChanges = () => {
    fetchChartData();
  };

  // Gérer le changement d'onglet
  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Sauvegarder la configuration des indicateurs
  const saveConfiguration = async () => {
    try {
      const token = localStorage.getItem('token');
      const config = {
        exchange,
        symbol,
        timeframe,
        chartType,
        indicators
      };
      
      const response = await axios.post<ApiResponse<any>>(
        '/api/user/chart-config',
        config,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      if (response.data.success) {
        setSuccess('Configuration sauvegardée avec succès');
      } else {
        setError(response.data.error || 'Erreur lors de la sauvegarde');
      }
    } catch (err: any) {
      setError(`Erreur lors de la sauvegarde: ${err.message || 'Erreur inconnue'}`);
    }
  };

  // Exporter le graphique en image
  const exportChart = () => {
    // Implémentation simplifiée
    setSuccess('Fonction d\'exportation à implémenter');
    // Dans une implémentation réelle, on pourrait utiliser html2canvas ou un autre outil
    // pour capturer le graphique en image
  };

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" component="h1" gutterBottom sx={{ mt: 3 }}>
        Analyse Technique Avancée
      </Typography>
      
      {/* Contrôles de trading */}
      <StyledPaper>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel id="exchange-select-label">Exchange</InputLabel>
              <Select
                labelId="exchange-select-label"
                id="exchange-select"
                value={exchange}
                label="Exchange"
                onChange={handleExchangeChange as any}
              >
                {AVAILABLE_EXCHANGES.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Autocomplete
              id="symbol-select"
              options={availableSymbols}
              value={symbol}
              onChange={handleSymbolChange}
              renderInput={(params) => (
                <TextField {...params} label="Paire de trading" fullWidth />
              )}
            />
          </Grid>
          
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel id="timeframe-select-label">Période</InputLabel>
              <Select
                labelId="timeframe-select-label"
                id="timeframe-select"
                value={timeframe}
                label="Période"
                onChange={handleTimeframeChange as any}
              >
                {AVAILABLE_TIMEFRAMES.map(option => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <ToggleButtonGroup
              value={chartType}
              exclusive
              onChange={handleChartTypeChange}
              aria-label="Type de graphique"
              fullWidth
            >
              <ToggleButton value="candlestick" aria-label="chandelier">
                <Tooltip title="Graphique en chandeliers">
                  <ShowChartIcon />
                </Tooltip>
              </ToggleButton>
              <ToggleButton value="line" aria-label="ligne">
                <Tooltip title="Graphique en ligne">
                  <TimelineIcon />
                </Tooltip>
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>
        </Grid>

        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
          <Button 
            variant="contained" 
            onClick={applyChanges}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
          >
            {isLoading ? 'Chargement...' : 'Appliquer'}
          </Button>
        </Box>
      </StyledPaper>
      
      {/* Graphique principal */}
      <ChartContainer ref={chartRef}>
        {isLoading && (
          <Box 
            sx={{ 
              position: 'absolute', 
              top: 0, 
              left: 0, 
              width: '100%', 
              height: '100%', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              backgroundColor: 'rgba(0, 0, 0, 0.1)' 
            }}
          >
            <CircularProgress />
          </Box>
        )}
        
        {chartData.length > 0 ? (
          <Box sx={{ 
            p: 2, 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column', 
            justifyContent: 'center', 
            alignItems: 'center' 
          }}>
            <Typography variant="body1" color="textSecondary">
              {chartData.length} points de données chargés pour {symbol} sur {exchange}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Période: {timeframe} | Type: {chartType === 'candlestick' ? 'Chandeliers' : 'Ligne'}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Une bibliothèque comme TradingView, Chart.js ou Highcharts serait utilisée ici
            </Typography>
          </Box>
        ) : (
          <Box sx={{ 
            p: 2, 
            height: '100%', 
            display: 'flex', 
            flexDirection: 'column', 
            justifyContent: 'center', 
            alignItems: 'center' 
          }}>
            <Typography variant="body1" color="textSecondary">
              Aucune donnée chargée. Veuillez sélectionner un symbol et cliquer sur Appliquer.
            </Typography>
          </Box>
        )}
      </ChartContainer>
      
      {/* Gestion des indicateurs */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Ajouter des indicateurs
            </Typography>
            
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              variant="scrollable"
              scrollButtons="auto"
              aria-label="indicator tabs"
            >
              <Tab label="Superposés" {...a11yProps(0)} />
              <Tab label="Oscillateurs" {...a11yProps(1)} />
              <Tab label="Tous" {...a11yProps(2)} />
            </Tabs>
            
            <TabPanel value={tabValue} index={0}>
              <Grid container spacing={1}>
                {AVAILABLE_INDICATORS.filter(ind => ind.type === 'overlay').map(indicator => (
                  <Grid item xs={12} key={indicator.id}>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => handleAddIndicator(indicator.id)}
                      fullWidth
                      sx={{ justifyContent: 'flex-start', mb: 1 }}
                    >
                      {indicator.name}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>
            
            <TabPanel value={tabValue} index={1}>
              <Grid container spacing={1}>
                {AVAILABLE_INDICATORS.filter(ind => ind.type === 'oscillator').map(indicator => (
                  <Grid item xs={12} key={indicator.id}>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => handleAddIndicator(indicator.id)}
                      fullWidth
                      sx={{ justifyContent: 'flex-start', mb: 1 }}
                    >
                      {indicator.name}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>
            
            <TabPanel value={tabValue} index={2}>
              <Grid container spacing={1}>
                {AVAILABLE_INDICATORS.map(indicator => (
                  <Grid item xs={12} key={indicator.id}>
                    <Button
                      variant="outlined"
                      startIcon={<AddIcon />}
                      onClick={() => handleAddIndicator(indicator.id)}
                      fullWidth
                      sx={{ justifyContent: 'flex-start', mb: 1 }}
                    >
                      {indicator.name}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </TabPanel>
          </StyledPaper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Indicateurs actifs
            </Typography>
            
            {indicators.length === 0 ? (
              <Alert severity="info" sx={{ mt: 2 }}>
                Aucun indicateur actif. Ajoutez des indicateurs depuis le panneau de gauche.
              </Alert>
            ) : (
              <Box sx={{ mt: 1 }}>
                {indicators.map((indicator) => (
                  <Accordion key={indicator.id} sx={{ mb: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <IndicatorChip 
                            label={indicator.name}
                            indicatorcolor={indicator.color}
                            size="medium"
                          />
                          {!indicator.visible && (
                            <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                              (Masqué)
                            </Typography>
                          )}
                        </Box>
                        <Box>
                          <Tooltip title={indicator.visible ? "Masquer" : "Afficher"}>
                            <Button 
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleIndicatorVisibility(indicator.id);
                              }}
                              size="small"
                            >
                              {indicator.visible ? <VisibilityIcon /> : <VisibilityOffIcon />}
                            </Button>
                          </Tooltip>
                          <Tooltip title="Supprimer">
                            <Button 
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRemoveIndicator(indicator.id);
                              }}
                              size="small"
                              color="error"
                            >
                              <RemoveIcon />
                            </Button>
                          </Tooltip>
                        </Box>
                      </Box>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Grid container spacing={2}>
                        {indicator.parameters.map((param, index) => (
                          <Grid item xs={12} sm={6} key={index}>
                            {param.type === 'number' ? (
                              <Box>
                                <Typography gutterBottom>
                                  {param.name}: {param.value}
                                </Typography>
                                <Slider
                                  value={param.value}
                                  min={param.min || 1}
                                  max={param.max || 100}
                                  onChange={(_e, newValue) => 
                                    handleParameterChange(indicator.id, param.name, newValue as number)
                                  }
                                  valueLabelDisplay="auto"
                                />
                              </Box>
                            ) : param.type === 'select' && param.options ? (
                              <FormControl fullWidth>
                                <InputLabel>{param.name}</InputLabel>
                                <Select
                                  value={param.value}
                                  onChange={(e) => 
                                    handleParameterChange(indicator.id, param.name, e.target.value)
                                  }
                                >
                                  {param.options.map(option => (
                                    <MenuItem key={option} value={option}>
                                      {option}
                                    </MenuItem>
                                  ))}
                                </Select>
                              </FormControl>
                            ) : null}
                          </Grid>
                        ))}
                      </Grid>
                    </AccordionDetails>
                  </Accordion>
                ))}
                
                <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
                  <Button 
                    variant="contained" 
                    color="primary"
                    onClick={saveConfiguration}
                    disabled={isLoading}
                    startIcon={<SaveIcon />}
                    sx={{ mr: 1 }}
                  >
                    Sauvegarder configuration
                  </Button>
                  <Button 
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={exportChart}
                  >
                    Exporter graphique
                  </Button>
                </Box>
              </Box>
            )}
          </StyledPaper>
        </Grid>
      </Grid>
      
      {/* Messages de notification */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
      
      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setSuccess(null)} severity="success">
          {success}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default AdvancedTradingView; 