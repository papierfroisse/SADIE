import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Grid, 
  Card, 
  CardContent,
  CardHeader,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Snackbar,
  Alert,
  CircularProgress,
  Divider
} from '@mui/material';
import { 
  Add as AddIcon, 
  Delete as DeleteIcon, 
  Edit as EditIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  BarChart as BarChartIcon,
  ShowChart as LineChartIcon,
  PieChart as PieChartIcon,
  TableChart as TableChartIcon,
  Download as DownloadIcon
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';

// Définition des types
interface Widget {
  id: string;
  title: string;
  type: 'line' | 'bar' | 'pie' | 'table' | 'value';
  size: 'small' | 'medium' | 'large';
  collector?: string;
  exchange?: string;
  metricType: string;
  symbol?: string;
  timeframe: string;
  aggregation: string;
  position: {
    x: number;
    y: number;
  };
  data?: any[];
}

interface Dashboard {
  id: string;
  name: string;
  description?: string;
  widgets: Widget[];
  isDefault?: boolean;
}

// Couleurs pour les graphiques
const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// Configuration des tailles de widgets
const sizeMap = {
  small: 4,  // 1/3 de la largeur
  medium: 6, // 1/2 de la largeur
  large: 12  // Largeur complète
};

// Composant principal
const DashboardPage: React.FC = () => {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [currentDashboard, setCurrentDashboard] = useState<Dashboard | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshInterval, setRefreshInterval] = useState(30); // secondes
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  
  // États pour les dialogues
  const [openAddWidgetDialog, setOpenAddWidgetDialog] = useState(false);
  const [openEditDashboardDialog, setOpenEditDashboardDialog] = useState(false);
  const [openLoginDialog, setOpenLoginDialog] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  // États pour la création/édition de widget
  const [newWidget, setNewWidget] = useState<Partial<Widget>>({
    title: '',
    type: 'line',
    size: 'medium',
    metricType: 'throughput',
    timeframe: '1h',
    aggregation: 'avg'
  });
  
  // États pour la création/édition de dashboard
  const [editingDashboard, setEditingDashboard] = useState<Partial<Dashboard>>({
    name: '',
    description: '',
    widgets: []
  });
  
  // Effet pour charger les dashboards au démarrage
  useEffect(() => {
    if (token) {
      loadDashboards();
    } else {
      setOpenLoginDialog(true);
    }
  }, [token]);
  
  // Effet pour rafraîchir automatiquement les données
  useEffect(() => {
    const interval = setInterval(() => {
      if (currentDashboard && token) {
        refreshDashboardData();
      }
    }, refreshInterval * 1000);
    
    return () => clearInterval(interval);
  }, [currentDashboard, refreshInterval, token]);
  
  // Fonction de connexion
  const handleLogin = async () => {
    try {
      setIsLoading(true);
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await fetch('/api/token', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        setToken(data.access_token);
        setOpenLoginDialog(false);
        loadDashboards();
      } else {
        setError('Identifiants incorrects');
      }
    } catch (err) {
      setError('Erreur de connexion au serveur');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Fonction de déconnexion
  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setOpenLoginDialog(true);
  };
  
  // Fonction pour charger la liste des dashboards
  const loadDashboards = async () => {
    try {
      setIsLoading(true);
      
      // Si pas de dashboards en localStorage, créer un par défaut
      const savedDashboards = localStorage.getItem('dashboards');
      
      if (savedDashboards) {
        const dashboardsList = JSON.parse(savedDashboards);
        setDashboards(dashboardsList);
        
        // Sélectionner le dashboard par défaut ou le premier
        const defaultDashboard = dashboardsList.find((d: Dashboard) => d.isDefault) || dashboardsList[0];
        setCurrentDashboard(defaultDashboard);
        
        // Charger les données pour le dashboard sélectionné
        if (defaultDashboard) {
          await loadDashboardData(defaultDashboard);
        }
      } else {
        // Créer un dashboard par défaut
        const defaultDashboard: Dashboard = {
          id: 'default',
          name: 'Tableau de bord principal',
          description: 'Métriques principales des collecteurs',
          isDefault: true,
          widgets: [
            {
              id: 'throughput',
              title: 'Débit des collecteurs',
              type: 'line',
              size: 'medium',
              metricType: 'throughput',
              timeframe: '1h',
              aggregation: 'avg',
              position: { x: 0, y: 0 }
            },
            {
              id: 'latency',
              title: 'Latence des collecteurs',
              type: 'bar',
              size: 'medium',
              metricType: 'latency',
              timeframe: '1h',
              aggregation: 'avg',
              position: { x: 1, y: 0 }
            },
            {
              id: 'errors',
              title: 'Taux d\'erreurs',
              type: 'pie',
              size: 'small',
              metricType: 'error_rate',
              timeframe: '1h',
              aggregation: 'avg',
              position: { x: 0, y: 1 }
            },
            {
              id: 'health',
              title: 'Santé des collecteurs',
              type: 'table',
              size: 'small',
              metricType: 'health',
              timeframe: '1h',
              aggregation: 'avg',
              position: { x: 1, y: 1 }
            }
          ]
        };
        
        setDashboards([defaultDashboard]);
        setCurrentDashboard(defaultDashboard);
        localStorage.setItem('dashboards', JSON.stringify([defaultDashboard]));
        
        // Charger les données pour le dashboard par défaut
        await loadDashboardData(defaultDashboard);
      }
    } catch (err) {
      setError('Erreur lors du chargement des tableaux de bord');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Fonction pour charger les données d'un dashboard
  const loadDashboardData = async (dashboard: Dashboard) => {
    try {
      const dashboardWithData = { ...dashboard };
      
      // Charger les données pour chaque widget
      for (let i = 0; i < dashboardWithData.widgets.length; i++) {
        const widget = dashboardWithData.widgets[i];
        const data = await fetchMetricsData(widget);
        dashboardWithData.widgets[i] = { ...widget, data };
      }
      
      setCurrentDashboard(dashboardWithData);
    } catch (err) {
      setError('Erreur lors du chargement des données');
    }
  };
  
  // Fonction pour rafraîchir les données du dashboard actuel
  const refreshDashboardData = async () => {
    if (currentDashboard) {
      await loadDashboardData(currentDashboard);
    }
  };
  
  // Fonction pour récupérer les données de métriques pour un widget
  const fetchMetricsData = async (widget: Widget) => {
    try {
      if (!token) return [];
      
      const params = new URLSearchParams();
      if (widget.collector) params.append('collector_name', widget.collector);
      if (widget.exchange) params.append('exchange', widget.exchange);
      if (widget.symbol) params.append('symbol', widget.symbol);
      params.append('metric_type', widget.metricType);
      params.append('timeframe', widget.timeframe);
      params.append('aggregation', widget.aggregation);
      
      const response = await fetch(`/api/metrics/collectors?${params.toString()}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Erreur lors de la récupération des données');
      }
      
      const data = await response.json();
      
      // Transformer les données pour les graphiques
      return transformMetricsData(data, widget.type);
    } catch (err) {
      console.error('Erreur lors de la récupération des métriques:', err);
      return [];
    }
  };
  
  // Fonction pour transformer les données de métriques selon le type de widget
  const transformMetricsData = (data: any, type: string) => {
    if (!data || !data.metrics) return [];
    
    switch (type) {
      case 'line':
      case 'bar':
        // Transformer pour les graphiques temporels
        const chartData = [];
        for (const [timestamp, values] of Object.entries(data.metrics)) {
          chartData.push({
            timestamp,
            ...values
          });
        }
        return chartData.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
        
      case 'pie':
        // Transformer pour les graphiques circulaires
        return Object.entries(data.metrics).map(([name, value]: [string, any]) => ({
          name,
          value: Object.values(value)[0]
        }));
        
      case 'table':
      case 'value':
      default:
        // Retourner les données telles quelles
        return data.metrics;
    }
  };
  
  // Fonction pour ajouter un nouveau widget
  const handleAddWidget = async () => {
    if (!currentDashboard || !newWidget.title || !newWidget.metricType) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }
    
    const widget: Widget = {
      id: `widget-${Date.now()}`,
      title: newWidget.title || '',
      type: newWidget.type as 'line',
      size: newWidget.size as 'medium',
      collector: newWidget.collector,
      exchange: newWidget.exchange,
      metricType: newWidget.metricType || 'throughput',
      symbol: newWidget.symbol,
      timeframe: newWidget.timeframe || '1h',
      aggregation: newWidget.aggregation || 'avg',
      position: {
        x: currentDashboard.widgets.length % 2,
        y: Math.floor(currentDashboard.widgets.length / 2)
      }
    };
    
    // Récupérer les données pour le widget
    const data = await fetchMetricsData(widget);
    const widgetWithData = { ...widget, data };
    
    // Mettre à jour le dashboard
    const updatedDashboard = {
      ...currentDashboard,
      widgets: [...currentDashboard.widgets, widgetWithData]
    };
    
    // Mettre à jour le state
    setCurrentDashboard(updatedDashboard);
    
    // Mettre à jour la liste des dashboards
    const updatedDashboards = dashboards.map(d => 
      d.id === currentDashboard.id ? updatedDashboard : d
    );
    setDashboards(updatedDashboards);
    
    // Sauvegarder en localStorage
    localStorage.setItem('dashboards', JSON.stringify(updatedDashboards));
    
    // Fermer le dialogue
    setOpenAddWidgetDialog(false);
    
    // Réinitialiser le formulaire
    setNewWidget({
      title: '',
      type: 'line',
      size: 'medium',
      metricType: 'throughput',
      timeframe: '1h',
      aggregation: 'avg'
    });
  };
  
  // Fonction pour supprimer un widget
  const handleDeleteWidget = (widgetId: string) => {
    if (!currentDashboard) return;
    
    // Filtrer les widgets
    const updatedWidgets = currentDashboard.widgets.filter(w => w.id !== widgetId);
    
    // Mettre à jour le dashboard
    const updatedDashboard = {
      ...currentDashboard,
      widgets: updatedWidgets
    };
    
    // Mettre à jour le state
    setCurrentDashboard(updatedDashboard);
    
    // Mettre à jour la liste des dashboards
    const updatedDashboards = dashboards.map(d => 
      d.id === currentDashboard.id ? updatedDashboard : d
    );
    setDashboards(updatedDashboards);
    
    // Sauvegarder en localStorage
    localStorage.setItem('dashboards', JSON.stringify(updatedDashboards));
  };
  
  // Fonction pour créer un nouveau dashboard
  const handleCreateDashboard = () => {
    if (!editingDashboard.name) {
      setError('Veuillez saisir un nom pour le tableau de bord');
      return;
    }
    
    const newDashboard: Dashboard = {
      id: `dashboard-${Date.now()}`,
      name: editingDashboard.name || '',
      description: editingDashboard.description || '',
      widgets: [],
      isDefault: dashboards.length === 0
    };
    
    // Mettre à jour la liste des dashboards
    const updatedDashboards = [...dashboards, newDashboard];
    setDashboards(updatedDashboards);
    
    // Sélectionner le nouveau dashboard
    setCurrentDashboard(newDashboard);
    
    // Sauvegarder en localStorage
    localStorage.setItem('dashboards', JSON.stringify(updatedDashboards));
    
    // Fermer le dialogue
    setOpenEditDashboardDialog(false);
    
    // Réinitialiser le formulaire
    setEditingDashboard({
      name: '',
      description: '',
      widgets: []
    });
  };
  
  // Fonction pour exportation en JSON
  const handleExportJSON = () => {
    if (!currentDashboard) return;
    
    const dataStr = JSON.stringify(currentDashboard, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `${currentDashboard.name.replace(/\s+/g, '_')}_dashboard.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };
  
  // Fonction pour exportation en CSV
  const handleExportCSV = () => {
    if (!currentDashboard) return;
    
    let csvContent = "data:text/csv;charset=utf-8,";
    
    // En-tête pour toutes les métriques
    const allMetrics = new Set<string>();
    currentDashboard.widgets.forEach(widget => {
      if (widget.data && Array.isArray(widget.data)) {
        widget.data.forEach(item => {
          Object.keys(item).forEach(key => {
            if (key !== 'timestamp') {
              allMetrics.add(key);
            }
          });
        });
      }
    });
    
    // Créer l'en-tête
    csvContent += `"Timestamp",${Array.from(allMetrics).map(m => `"${m}"`).join(',')}\n`;
    
    // Fusionner les données de tous les widgets
    const mergedData: {[key: string]: {[metric: string]: number}} = {};
    
    currentDashboard.widgets.forEach(widget => {
      if (widget.data && Array.isArray(widget.data)) {
        widget.data.forEach(item => {
          const timestamp = item.timestamp;
          if (!mergedData[timestamp]) {
            mergedData[timestamp] = {};
          }
          
          Object.entries(item).forEach(([key, value]) => {
            if (key !== 'timestamp' && typeof value === 'number') {
              mergedData[timestamp][key] = value;
            }
          });
        });
      }
    });
    
    // Ajouter les lignes
    Object.entries(mergedData).forEach(([timestamp, values]) => {
      const row = [timestamp];
      
      allMetrics.forEach(metric => {
        row.push(values[metric] !== undefined ? String(values[metric]) : '');
      });
      
      csvContent += row.join(',') + '\n';
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `${currentDashboard.name.replace(/\s+/g, '_')}_dashboard.csv`);
    document.body.appendChild(link);
    link.click();
  };
  
  // Rendu des widgets selon leur type
  const renderWidget = (widget: Widget) => {
    if (!widget.data) return <CircularProgress />;
    
    const sizeMap = {
      small: 4,
      medium: 6,
      large: 12
    };
    
    switch (widget.type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={widget.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              {Object.keys(widget.data[0] || {})
                .filter(key => key !== 'timestamp')
                .map((key, index) => (
                  <Line 
                    key={key}
                    type="monotone" 
                    dataKey={key} 
                    stroke={COLORS[index % COLORS.length]} 
                    activeDot={{ r: 8 }}
                  />
                ))}
            </LineChart>
          </ResponsiveContainer>
        );
        
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={widget.data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              {Object.keys(widget.data[0] || {})
                .filter(key => key !== 'timestamp')
                .map((key, index) => (
                  <Bar 
                    key={key}
                    dataKey={key} 
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
            </BarChart>
          </ResponsiveContainer>
        );
        
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={widget.data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value.toFixed(2)}`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {widget.data.map((entry: any, index: number) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );
        
      case 'table':
        return (
          <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ border: '1px solid #ddd', padding: 8, textAlign: 'left' }}>Métrique</th>
                  <th style={{ border: '1px solid #ddd', padding: 8, textAlign: 'left' }}>Valeur</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(widget.data).map(([key, value]: [string, any], index) => (
                  <tr key={index}>
                    <td style={{ border: '1px solid #ddd', padding: 8 }}>{key}</td>
                    <td style={{ border: '1px solid #ddd', padding: 8 }}>
                      {typeof value === 'object' 
                        ? Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(', ')
                        : value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Box>
        );
        
      case 'value':
      default:
        // Afficher une valeur unique
        const value = widget.data && typeof widget.data === 'object' 
          ? Object.values(widget.data)[0] 
          : widget.data;
          
        return (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            height: '100%',
            minHeight: 150
          }}>
            <Typography variant="h3">
              {typeof value === 'number' ? value.toFixed(2) : value}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {widget.metricType}
            </Typography>
          </Box>
        );
    }
  };
  
  // Affichage de la page de chargement
  if (isLoading && !currentDashboard) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }
  
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Barre d'outils */}
      <Paper sx={{ mb: 2, p: 2 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <Typography variant="h6" component="div">
              {currentDashboard?.name || 'Tableau de bord'}
            </Typography>
          </Grid>
          
          {token && (
            <>
              <Grid item xs={12} md={8} sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenAddWidgetDialog(true)}
                >
                  Ajouter un widget
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={refreshDashboardData}
                >
                  Actualiser
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  onClick={() => setOpenEditDashboardDialog(true)}
                >
                  Nouveau tableau
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportJSON}
                >
                  Exporter JSON
                </Button>
                
                <Button
                  variant="outlined"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportCSV}
                >
                  Exporter CSV
                </Button>
              </Grid>
            </>
          )}
        </Grid>
      </Paper>
      
      {/* Grille de widgets */}
      {currentDashboard && (
        <Grid container spacing={2}>
          {currentDashboard.widgets.map(widget => (
            <Grid item key={widget.id} xs={12} sm={sizeMap[widget.size]} md={sizeMap[widget.size]}>
              <Card sx={{ height: '100%' }}>
                <CardHeader
                  title={widget.title}
                  action={
                    <IconButton onClick={() => handleDeleteWidget(widget.id)}>
                      <DeleteIcon />
                    </IconButton>
                  }
                />
                <Divider />
                <CardContent>
                  {renderWidget(widget)}
                </CardContent>
              </Card>
            </Grid>
          ))}
          
          {currentDashboard.widgets.length === 0 && (
            <Grid item xs={12}>
              <Paper sx={{ p: 3, textAlign: 'center' }}>
                <Typography variant="h6">
                  Aucun widget dans ce tableau de bord
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setOpenAddWidgetDialog(true)}
                  sx={{ mt: 2 }}
                >
                  Ajouter un widget
                </Button>
              </Paper>
            </Grid>
          )}
        </Grid>
      )}
      
      {/* Dialog pour l'ajout de widget */}
      <Dialog open={openAddWidgetDialog} onClose={() => setOpenAddWidgetDialog(false)}>
        <DialogTitle>Ajouter un widget</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 400 }}>
            <TextField
              fullWidth
              label="Titre du widget"
              value={newWidget.title || ''}
              onChange={(e) => setNewWidget({ ...newWidget, title: e.target.value })}
              margin="normal"
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Type de graphique</InputLabel>
              <Select
                value={newWidget.type || 'line'}
                onChange={(e) => setNewWidget({ ...newWidget, type: e.target.value })}
              >
                <MenuItem value="line">Ligne</MenuItem>
                <MenuItem value="bar">Barre</MenuItem>
                <MenuItem value="pie">Circulaire</MenuItem>
                <MenuItem value="table">Tableau</MenuItem>
                <MenuItem value="value">Valeur unique</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Taille</InputLabel>
              <Select
                value={newWidget.size || 'medium'}
                onChange={(e) => setNewWidget({ ...newWidget, size: e.target.value })}
              >
                <MenuItem value="small">Petit</MenuItem>
                <MenuItem value="medium">Moyen</MenuItem>
                <MenuItem value="large">Large</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              label="Collecteur (optionnel)"
              value={newWidget.collector || ''}
              onChange={(e) => setNewWidget({ ...newWidget, collector: e.target.value })}
              margin="normal"
              placeholder="Laissez vide pour tous les collecteurs"
            />
            
            <TextField
              fullWidth
              label="Exchange (optionnel)"
              value={newWidget.exchange || ''}
              onChange={(e) => setNewWidget({ ...newWidget, exchange: e.target.value })}
              margin="normal"
              placeholder="Laissez vide pour tous les exchanges"
            />
            
            <TextField
              fullWidth
              label="Symbole (optionnel)"
              value={newWidget.symbol || ''}
              onChange={(e) => setNewWidget({ ...newWidget, symbol: e.target.value })}
              margin="normal"
              placeholder="Laissez vide pour tous les symboles"
            />
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Type de métrique</InputLabel>
              <Select
                value={newWidget.metricType || 'throughput'}
                onChange={(e) => setNewWidget({ ...newWidget, metricType: e.target.value })}
              >
                <MenuItem value="throughput">Débit</MenuItem>
                <MenuItem value="latency">Latence</MenuItem>
                <MenuItem value="error_rate">Taux d'erreur</MenuItem>
                <MenuItem value="health">Santé</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Période</InputLabel>
              <Select
                value={newWidget.timeframe || '1h'}
                onChange={(e) => setNewWidget({ ...newWidget, timeframe: e.target.value })}
              >
                <MenuItem value="5m">5 minutes</MenuItem>
                <MenuItem value="15m">15 minutes</MenuItem>
                <MenuItem value="1h">1 heure</MenuItem>
                <MenuItem value="6h">6 heures</MenuItem>
                <MenuItem value="24h">24 heures</MenuItem>
                <MenuItem value="7d">7 jours</MenuItem>
              </Select>
            </FormControl>
            
            <FormControl fullWidth margin="normal">
              <InputLabel>Agrégation</InputLabel>
              <Select
                value={newWidget.aggregation || 'avg'}
                onChange={(e) => setNewWidget({ ...newWidget, aggregation: e.target.value })}
              >
                <MenuItem value="avg">Moyenne</MenuItem>
                <MenuItem value="min">Minimum</MenuItem>
                <MenuItem value="max">Maximum</MenuItem>
                <MenuItem value="sum">Somme</MenuItem>
                <MenuItem value="count">Nombre</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddWidgetDialog(false)}>Annuler</Button>
          <Button onClick={handleAddWidget} variant="contained">Ajouter</Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog pour l'édition/création de dashboard */}
      <Dialog open={openEditDashboardDialog} onClose={() => setOpenEditDashboardDialog(false)}>
        <DialogTitle>Nouveau tableau de bord</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 400 }}>
            <TextField
              fullWidth
              label="Nom du tableau de bord"
              value={editingDashboard.name || ''}
              onChange={(e) => setEditingDashboard({ ...editingDashboard, name: e.target.value })}
              margin="normal"
            />
            
            <TextField
              fullWidth
              label="Description (optionnel)"
              value={editingDashboard.description || ''}
              onChange={(e) => setEditingDashboard({ ...editingDashboard, description: e.target.value })}
              margin="normal"
              multiline
              rows={3}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditDashboardDialog(false)}>Annuler</Button>
          <Button onClick={handleCreateDashboard} variant="contained">Créer</Button>
        </DialogActions>
      </Dialog>
      
      {/* Dialog de connexion */}
      <Dialog open={openLoginDialog} onClose={() => {}} disableEscapeKeyDown>
        <DialogTitle>Connexion requise</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, minWidth: 300 }}>
            <TextField
              fullWidth
              label="Nom d'utilisateur"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
            />
            
            <TextField
              fullWidth
              label="Mot de passe"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleLogin} variant="contained" disabled={isLoading}>
            {isLoading ? <CircularProgress size={24} /> : 'Se connecter'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Snackbar pour les erreurs */}
      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert onClose={() => setError(null)} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DashboardPage; 