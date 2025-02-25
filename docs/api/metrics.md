# API Métriques Avancées

Cette documentation détaille les endpoints API disponibles pour les fonctionnalités avancées du système de métriques SADIE.

## Endpoints pour les Alertes

### Obtenir toutes les alertes

```
GET /api/v1/alerts
```

Récupère la liste de toutes les alertes de performance configurées.

**Paramètres de requête :**
- `collector_id` (optionnel) : Filtre les alertes par ID de collecteur
- `severity` (optionnel) : Filtre les alertes par sévérité (warning, critical)

**Exemple de réponse :**
```json
{
  "alerts": [
    {
      "id": "a1b2c3d4",
      "name": "Latence élevée Binance",
      "description": "Alerte lorsque la latence dépasse 200ms",
      "collector_id": "binance_collector",
      "threshold": {
        "metric": "latency",
        "operator": ">",
        "value": 200
      },
      "severity": "warning",
      "created_at": "2024-05-01T12:00:00Z"
    },
    {
      "id": "e5f6g7h8",
      "name": "Utilisation CPU critique",
      "description": "Alerte lorsque l'utilisation CPU dépasse 90%",
      "collector_id": "*",
      "threshold": {
        "metric": "cpu_usage",
        "operator": ">",
        "value": 90
      },
      "severity": "critical",
      "created_at": "2024-05-01T12:30:00Z"
    }
  ],
  "count": 2
}
```

### Créer une alerte

```
POST /api/v1/alerts
```

Crée une nouvelle alerte de performance.

**Corps de la requête :**
```json
{
  "name": "Mémoire élevée Kraken",
  "description": "Alerte lorsque l'utilisation mémoire dépasse 500MB",
  "collector_id": "kraken_collector",
  "threshold": {
    "metric": "memory_usage",
    "operator": ">",
    "value": 500
  },
  "severity": "warning"
}
```

**Exemple de réponse :**
```json
{
  "id": "i9j0k1l2",
  "name": "Mémoire élevée Kraken",
  "description": "Alerte lorsque l'utilisation mémoire dépasse 500MB",
  "collector_id": "kraken_collector",
  "threshold": {
    "metric": "memory_usage",
    "operator": ">",
    "value": 500
  },
  "severity": "warning",
  "created_at": "2024-05-01T14:00:00Z"
}
```

### Obtenir une alerte spécifique

```
GET /api/v1/alerts/{alert_id}
```

Récupère les détails d'une alerte spécifique.

**Exemple de réponse :**
```json
{
  "id": "a1b2c3d4",
  "name": "Latence élevée Binance",
  "description": "Alerte lorsque la latence dépasse 200ms",
  "collector_id": "binance_collector",
  "threshold": {
    "metric": "latency",
    "operator": ">",
    "value": 200
  },
  "severity": "warning",
  "created_at": "2024-05-01T12:00:00Z"
}
```

### Mettre à jour une alerte

```
PUT /api/v1/alerts/{alert_id}
```

Met à jour une alerte existante.

**Corps de la requête :**
```json
{
  "name": "Latence élevée Binance",
  "description": "Alerte lorsque la latence dépasse 300ms",
  "collector_id": "binance_collector",
  "threshold": {
    "metric": "latency",
    "operator": ">",
    "value": 300
  },
  "severity": "critical"
}
```

**Exemple de réponse :**
```json
{
  "id": "a1b2c3d4",
  "name": "Latence élevée Binance",
  "description": "Alerte lorsque la latence dépasse 300ms",
  "collector_id": "binance_collector",
  "threshold": {
    "metric": "latency",
    "operator": ">",
    "value": 300
  },
  "severity": "critical",
  "created_at": "2024-05-01T12:00:00Z",
  "updated_at": "2024-05-01T15:00:00Z"
}
```

### Supprimer une alerte

```
DELETE /api/v1/alerts/{alert_id}
```

Supprime une alerte existante.

**Exemple de réponse :**
```json
{
  "success": true,
  "message": "Alerte supprimée avec succès"
}
```

### Consulter l'historique des alertes déclenchées

```
GET /api/v1/alerts/history
```

Récupère l'historique des alertes déclenchées.

**Paramètres de requête :**
- `collector_id` (optionnel) : Filtre par ID de collecteur
- `severity` (optionnel) : Filtre par sévérité
- `start_date` (optionnel) : Date de début (format ISO)
- `end_date` (optionnel) : Date de fin (format ISO)
- `limit` (optionnel) : Nombre maximum d'événements à retourner (défaut: 100)
- `offset` (optionnel) : Décalage pour la pagination (défaut: 0)

**Exemple de réponse :**
```json
{
  "history": [
    {
      "id": "h1i2j3k4",
      "alert_id": "a1b2c3d4",
      "alert_name": "Latence élevée Binance",
      "collector_id": "binance_collector",
      "triggered_at": "2024-05-01T13:15:00Z",
      "metric_value": 312,
      "threshold_value": 200,
      "severity": "warning"
    },
    {
      "id": "l5m6n7o8",
      "alert_id": "e5f6g7h8",
      "alert_name": "Utilisation CPU critique",
      "collector_id": "binance_collector",
      "triggered_at": "2024-05-01T14:20:00Z",
      "metric_value": 95,
      "threshold_value": 90,
      "severity": "critical"
    }
  ],
  "count": 2,
  "total": 245
}
```

## Endpoints pour les Tableaux de Bord

### Obtenir tous les tableaux de bord

```
GET /api/v1/dashboards
```

Récupère la liste de tous les tableaux de bord configurés.

**Paramètres de requête :**
- `collector_id` (optionnel) : Filtre par ID de collecteur

**Exemple de réponse :**
```json
{
  "dashboards": [
    {
      "id": "d1e2f3g4",
      "name": "Vue générale Binance",
      "description": "Vue d'ensemble des performances Binance",
      "collector_id": "binance_collector",
      "created_at": "2024-05-01T10:00:00Z",
      "widget_count": 4
    },
    {
      "id": "h5i6j7k8",
      "name": "Monitoring global",
      "description": "Vue d'ensemble de tous les collecteurs",
      "collector_id": "*",
      "created_at": "2024-05-01T11:00:00Z",
      "widget_count": 3
    }
  ],
  "count": 2
}
```

### Créer un tableau de bord

```
POST /api/v1/dashboards
```

Crée un nouveau tableau de bord.

**Corps de la requête :**
```json
{
  "name": "Performance Kraken",
  "description": "Tableau de bord pour suivre les performances du collecteur Kraken",
  "collector_id": "kraken_collector"
}
```

**Exemple de réponse :**
```json
{
  "id": "l9m0n1o2",
  "name": "Performance Kraken",
  "description": "Tableau de bord pour suivre les performances du collecteur Kraken",
  "collector_id": "kraken_collector",
  "created_at": "2024-05-01T16:00:00Z",
  "widget_count": 0
}
```

### Obtenir un tableau de bord spécifique

```
GET /api/v1/dashboards/{dashboard_id}
```

Récupère les détails d'un tableau de bord spécifique, incluant ses widgets.

**Exemple de réponse :**
```json
{
  "id": "d1e2f3g4",
  "name": "Vue générale Binance",
  "description": "Vue d'ensemble des performances Binance",
  "collector_id": "binance_collector",
  "created_at": "2024-05-01T10:00:00Z",
  "updated_at": "2024-05-01T12:30:00Z",
  "widgets": [
    {
      "id": "w1x2y3z4",
      "name": "Latence",
      "widget_type": "line_chart",
      "metric": "latency",
      "time_range": "24h",
      "refresh_interval": 60
    },
    {
      "id": "a5b6c7d8",
      "name": "Utilisation CPU",
      "widget_type": "gauge",
      "metric": "cpu_usage",
      "min_value": 0,
      "max_value": 100,
      "thresholds": [
        {"value": 70, "color": "yellow"},
        {"value": 90, "color": "red"}
      ]
    }
  ]
}
```

### Mettre à jour un tableau de bord

```
PUT /api/v1/dashboards/{dashboard_id}
```

Met à jour les informations d'un tableau de bord existant.

**Corps de la requête :**
```json
{
  "name": "Vue détaillée Binance",
  "description": "Vue détaillée des performances du collecteur Binance"
}
```

**Exemple de réponse :**
```json
{
  "id": "d1e2f3g4",
  "name": "Vue détaillée Binance",
  "description": "Vue détaillée des performances du collecteur Binance",
  "collector_id": "binance_collector",
  "created_at": "2024-05-01T10:00:00Z",
  "updated_at": "2024-05-01T17:00:00Z",
  "widget_count": 4
}
```

### Supprimer un tableau de bord

```
DELETE /api/v1/dashboards/{dashboard_id}
```

Supprime un tableau de bord existant et tous ses widgets.

**Exemple de réponse :**
```json
{
  "success": true,
  "message": "Tableau de bord supprimé avec succès"
}
```

### Ajouter un widget à un tableau de bord

```
POST /api/v1/dashboards/{dashboard_id}/widgets
```

Ajoute un nouveau widget à un tableau de bord.

**Corps de la requête :**
```json
{
  "name": "Requêtes par minute",
  "widget_type": "counter",
  "metric": "requests_per_minute",
  "time_range": "5m"
}
```

**Exemple de réponse :**
```json
{
  "id": "e9f0g1h2",
  "name": "Requêtes par minute",
  "widget_type": "counter",
  "metric": "requests_per_minute",
  "time_range": "5m",
  "dashboard_id": "d1e2f3g4",
  "created_at": "2024-05-01T17:30:00Z"
}
```

### Mettre à jour un widget

```
PUT /api/v1/dashboards/{dashboard_id}/widgets/{widget_id}
```

Met à jour un widget existant dans un tableau de bord.

**Corps de la requête :**
```json
{
  "name": "Requêtes par minute (en temps réel)",
  "time_range": "1m",
  "refresh_interval": 10
}
```

**Exemple de réponse :**
```json
{
  "id": "e9f0g1h2",
  "name": "Requêtes par minute (en temps réel)",
  "widget_type": "counter",
  "metric": "requests_per_minute",
  "time_range": "1m",
  "refresh_interval": 10,
  "dashboard_id": "d1e2f3g4",
  "created_at": "2024-05-01T17:30:00Z",
  "updated_at": "2024-05-01T18:00:00Z"
}
```

### Supprimer un widget

```
DELETE /api/v1/dashboards/{dashboard_id}/widgets/{widget_id}
```

Supprime un widget d'un tableau de bord.

**Exemple de réponse :**
```json
{
  "success": true,
  "message": "Widget supprimé avec succès"
}
```

## Endpoints pour l'Exportation des Données

### Exporter des métriques au format JSON

```
GET /api/v1/metrics/export/json
```

Exporte des métriques au format JSON selon les critères spécifiés.

**Paramètres de requête :**
- `collector_id` (obligatoire) : ID du collecteur
- `start_time` (obligatoire) : Horodatage de début (format ISO)
- `end_time` (obligatoire) : Horodatage de fin (format ISO)
- `metrics` (optionnel) : Liste des métriques à inclure, séparées par des virgules (par défaut : toutes)

**Exemple de réponse :**
```json
{
  "collector_id": "binance_collector",
  "start_time": "2024-05-01T10:00:00Z",
  "end_time": "2024-05-01T11:00:00Z",
  "metrics": [
    {
      "timestamp": "2024-05-01T10:00:00Z",
      "latency": 120,
      "memory_usage": 350,
      "cpu_usage": 15,
      "requests_per_minute": 142
    },
    {
      "timestamp": "2024-05-01T10:01:00Z",
      "latency": 115,
      "memory_usage": 355,
      "cpu_usage": 14,
      "requests_per_minute": 138
    }
  ]
}
```

### Exporter des métriques au format CSV

```
GET /api/v1/metrics/export/csv
```

Exporte des métriques au format CSV selon les critères spécifiés.

**Paramètres de requête :**
- `collector_id` (obligatoire) : ID du collecteur
- `start_time` (obligatoire) : Horodatage de début (format ISO)
- `end_time` (obligatoire) : Horodatage de fin (format ISO)
- `metrics` (optionnel) : Liste des métriques à inclure, séparées par des virgules (par défaut : toutes)

**Exemple de réponse :**
```
timestamp,latency,memory_usage,cpu_usage,requests_per_minute
2024-05-01T10:00:00Z,120,350,15,142
2024-05-01T10:01:00Z,115,355,14,138
```

## Endpoints pour l'Intégration Prometheus

### Exposition des métriques au format Prometheus

```
GET /metrics
```

Expose toutes les métriques des collecteurs au format Prometheus.

**Exemple de réponse :**
```
# HELP sadie_collector_latency_milliseconds Latence du collecteur en millisecondes
# TYPE sadie_collector_latency_milliseconds gauge
sadie_collector_latency_milliseconds{collector="binance_collector"} 120
sadie_collector_latency_milliseconds{collector="kraken_collector"} 140

# HELP sadie_collector_memory_usage_bytes Utilisation mémoire du collecteur en bytes
# TYPE sadie_collector_memory_usage_bytes gauge
sadie_collector_memory_usage_bytes{collector="binance_collector"} 358400
sadie_collector_memory_usage_bytes{collector="kraken_collector"} 286720

# HELP sadie_collector_cpu_usage_percent Utilisation CPU du collecteur en pourcentage
# TYPE sadie_collector_cpu_usage_percent gauge
sadie_collector_cpu_usage_percent{collector="binance_collector"} 12
sadie_collector_cpu_usage_percent{collector="kraken_collector"} 18

# HELP sadie_collector_requests_total Nombre total de requêtes effectuées par le collecteur
# TYPE sadie_collector_requests_total counter
sadie_collector_requests_total{collector="binance_collector"} 1520
sadie_collector_requests_total{collector="kraken_collector"} 960
``` 