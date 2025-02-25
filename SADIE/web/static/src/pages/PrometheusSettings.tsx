import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Switch, 
  FormControlLabel,
  TextField,
  Button,
  CircularProgress,
  Snackbar,
  Alert,
  Paper,
  Divider,
  List,
  ListItem,
  ListItemText,
  Link
} from '@mui/material';

interface PrometheusStatusResponse {
  enabled: boolean;
  port: number | null;
}

const PrometheusSettings: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [enabled, setEnabled] = useState<boolean>(false);
  const [port, setPort] = useState<string>("9090");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/prometheus/status', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la récupération du statut');
      }

      const data: PrometheusStatusResponse = await response.json();
      setEnabled(data.enabled);
      if (data.port) {
        setPort(data.port.toString());
      }
    } catch (error) {
      setErrorMessage('Erreur lors de la récupération des paramètres Prometheus');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const response = await fetch('/api/prometheus/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          enabled,
          port: parseInt(port, 10)
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de la mise à jour des paramètres');
      }

      const data: PrometheusStatusResponse = await response.json();
      setEnabled(data.enabled);
      if (data.port) {
        setPort(data.port.toString());
      }
      
      setSuccessMessage('Paramètres Prometheus mis à jour avec succès');
    } catch (error) {
      if (error instanceof Error) {
        setErrorMessage(error.message);
      } else {
        setErrorMessage('Erreur lors de la mise à jour des paramètres Prometheus');
      }
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const handlePortChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // Autoriser uniquement les nombres
    if (/^\d*$/.test(value)) {
      setPort(value);
    }
  };

  const handleCloseError = () => {
    setErrorMessage(null);
  };

  const handleCloseSuccess = () => {
    setSuccessMessage(null);
  };

  const getMetricsUrl = () => {
    return `http://${window.location.hostname}:${port}/metrics`;
  };

  const getGrafanaDashboardConfigExample = () => {
    return `
{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "auto",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "ops"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "editorMode": "code",
          "expr": "sadie_collector_throughput",
          "legendFormat": "{{collector_name}} - {{exchange}} - {{symbol}}",
          "range": true,
          "refId": "A"
        }
      ],
      "title": "Débit des collecteurs",
      "type": "timeseries"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": ["sadie", "monitoring"],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "SADIE - Performance des collecteurs",
  "version": 1,
  "weekStart": ""
}
    `;
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, mx: 'auto' }}>
      <Typography variant="h4" gutterBottom>
        Paramètres d'exportation Prometheus
      </Typography>
      
      <Paper elevation={3} sx={{ mb: 4, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Configuration de l'exportateur
        </Typography>
        <Box sx={{ mt: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
              />
            }
            label={enabled ? "Activé" : "Désactivé"}
          />
          
          <TextField
            label="Port"
            variant="outlined"
            size="small"
            value={port}
            onChange={handlePortChange}
            sx={{ ml: 2, width: 120 }}
            disabled={!enabled}
          />
          
          <Button
            variant="contained"
            color="primary"
            onClick={handleSave}
            disabled={saving}
            sx={{ ml: 2 }}
          >
            {saving ? <CircularProgress size={24} color="inherit" /> : "Enregistrer"}
          </Button>
        </Box>
        
        {enabled && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1">
              URL des métriques: <Link href={getMetricsUrl()} target="_blank">{getMetricsUrl()}</Link>
            </Typography>
          </Box>
        )}
      </Paper>
      
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Métriques disponibles
          </Typography>
          <List>
            <ListItem>
              <ListItemText 
                primary="sadie_collector_throughput" 
                secondary="Débit du collecteur en messages par seconde"
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText 
                primary="sadie_collector_latency" 
                secondary="Latence du collecteur en millisecondes"
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText 
                primary="sadie_collector_error_rate" 
                secondary="Taux d'erreurs du collecteur en pourcentage"
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText 
                primary="sadie_collector_health" 
                secondary="Santé du collecteur (1: sain, 0: défaillant)"
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText 
                primary="sadie_collector_total_messages" 
                secondary="Nombre total de messages traités par le collecteur"
              />
            </ListItem>
            <Divider />
            <ListItem>
              <ListItemText 
                primary="sadie_collector_total_errors" 
                secondary="Nombre total d'erreurs rencontrées par le collecteur"
              />
            </ListItem>
          </List>
        </CardContent>
      </Card>
      
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Configuration Grafana
        </Typography>
        <Typography variant="body1" paragraph>
          Pour visualiser les métriques SADIE dans Grafana, suivez ces étapes:
        </Typography>
        <List sx={{ mb: 2 }}>
          <ListItem>
            <ListItemText primary="1. Configurez une source de données Prometheus dans Grafana pointant vers votre instance Prometheus" />
          </ListItem>
          <ListItem>
            <ListItemText primary="2. Configurez Prometheus pour scraper le endpoint des métriques SADIE" />
          </ListItem>
          <ListItem>
            <ListItemText primary="3. Importez ou créez un tableau de bord Grafana utilisant les métriques SADIE" />
          </ListItem>
        </List>
        
        <Typography variant="subtitle1">
          Exemple de configuration Prometheus (prometheus.yml):
        </Typography>
        <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, mb: 2, overflow: 'auto' }}>
          <pre style={{ margin: 0 }}>
{`scrape_configs:
  - job_name: 'sadie'
    static_configs:
      - targets: ['localhost:${port}']
    scrape_interval: 15s`}
          </pre>
        </Box>
        
        <Typography variant="subtitle1">
          Exemple de configuration de tableau de bord Grafana:
        </Typography>
        <Box sx={{ bgcolor: 'background.paper', p: 2, borderRadius: 1, overflow: 'auto' }}>
          <pre style={{ margin: 0 }}>
            {getGrafanaDashboardConfigExample()}
          </pre>
        </Box>
      </Paper>
      
      <Snackbar open={!!errorMessage} autoHideDuration={6000} onClose={handleCloseError}>
        <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
          {errorMessage}
        </Alert>
      </Snackbar>
      
      <Snackbar open={!!successMessage} autoHideDuration={6000} onClose={handleCloseSuccess}>
        <Alert onClose={handleCloseSuccess} severity="success" sx={{ width: '100%' }}>
          {successMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default PrometheusSettings; 