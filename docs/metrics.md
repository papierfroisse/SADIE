# Documentation des Métriques de Performance

## Aperçu

Le système de métriques de SADIE permet de surveiller les performances des collecteurs de données en temps réel. Il offre une visibilité complète sur le fonctionnement de l'application et facilite l'identification des problèmes potentiels.

## Architecture

Le système de métriques est composé de trois éléments principaux :

1. **CollectorMetric** : Structure de données représentant une métrique individuelle
2. **CollectorPerformanceMonitor** : Surveille les performances d'un collecteur spécifique
3. **CollectorMetricsManager** : Gestionnaire global qui centralise toutes les métriques

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Collecteur 1   │     │  Collecteur 2   │     │  Collecteur N   │
│  avec Monitor   │     │  avec Monitor   │     │  avec Monitor   │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                       │
         │                       │                       │
         └───────────────┬───────┴───────────────┬───────┘
                         │                       │
                ┌────────▼────────┐     ┌────────▼────────┐
                │ Metrics Manager │     │     API Web     │
                └────────┬────────┘     └────────┬────────┘
                         │                       │
                         └───────────┬───────────┘
                                     │
                            ┌────────▼────────┐
                            │ Interface Web   │
                            └─────────────────┘
```

## Types de Métriques

Le système collecte plusieurs types de métriques :

| Catégorie   | Description                                    | Unité              |
|-------------|------------------------------------------------|--------------------|
| Throughput  | Débit de traitement des messages               | messages/seconde   |
| Latency     | Temps de traitement moyen d'un message         | millisecondes      |
| Error Rate  | Taux d'erreurs                                 | pourcentage        |
| Health      | État de santé global du collecteur             | healthy/degraded/unhealthy |
| Trades      | Nombre de trades traités par symbole           | count              |

## Utilisation dans le Code

### Activation des Métriques dans un Collecteur

Les métriques sont activées par défaut dans tous les collecteurs qui héritent de `BaseCollector`. Pour désactiver les métriques :

```python
collector = BinanceTradeCollector(
    name="binance_collector",
    symbols=["BTCUSDT"],
    enable_metrics=False  # Désactivation des métriques
)
```

### Enregistrement Manuel de Métriques

Pour enregistrer manuellement des métriques dans un collecteur personnalisé :

```python
# Dans la méthode de traitement
start_time = time.time()
await process_message(message)
processing_time = (time.time() - start_time) * 1000  # en ms

# Enregistrement des métriques
self._performance_monitor.record_processing_time(processing_time)
self._performance_monitor.messages_received += 1
self._performance_monitor.increment_trades(symbol, 1)

# En cas d'erreur
self._performance_monitor.record_error()
```

### Récupération des Métriques de Performance

Pour obtenir un rapport de performance d'un collecteur :

```python
performance_report = await collector.get_performance_metrics()

# Affichage des métriques
print(f"Messages traités : {performance_report['metrics']['messages_received']}")
print(f"Temps de traitement moyen : {performance_report['metrics']['avg_processing_time']} ms")
print(f"Taux d'erreur : {performance_report['metrics']['error_rate']}%")
```

## API Endpoints

Le système expose plusieurs endpoints API pour accéder aux métriques :

### Métriques Agrégées

```
GET /api/metrics/collectors?collector_name=&exchange=&metric_type=&symbol=&timeframe=&aggregation=
```

Paramètres :
- `collector_name` : Filtrer par nom de collecteur
- `exchange` : Filtrer par exchange (binance, kraken, etc.)
- `metric_type` : Type de métrique (throughput, latency, health, error_rate)
- `symbol` : Symbole spécifique
- `timeframe` : Fenêtre temporelle (5m, 15m, 1h, 6h, 24h, 7d)
- `aggregation` : Type d'agrégation (avg, min, max, sum, count)

### Métriques Brutes (Administrateurs Uniquement)

```
GET /api/metrics/collectors/raw?collector_name=&exchange=&metric_type=&symbol=&timeframe=&limit=
```

### État de Santé des Collecteurs

```
GET /api/metrics/collectors/health?collector_name=&exchange=
```

### Résumé des Métriques

```
GET /api/metrics/collectors/summary
```

## Interface Web

L'interface web des métriques est accessible à l'adresse `/metrics` et permet de visualiser :

1. **Tableau de bord** : Vue d'ensemble des performances de tous les collecteurs
2. **Graphiques en temps réel** : Visualisation des métriques clés
3. **État de santé** : Statut de tous les collecteurs
4. **Alertes** : Notification en cas de problème

## Surveillance et Alertes

Le système de métriques peut être intégré à des solutions de surveillance externes :

- **Prometheus** : Exposition des métriques au format Prometheus
- **Grafana** : Visualisation avancée et configuration d'alertes
- **Alertmanager** : Gestion des notifications (email, Slack, etc.)

## Configuration Avancée

Le comportement du système de métriques peut être configuré via les variables d'environnement :

```
# Activation/désactivation globale
METRICS_ENABLED=true

# Intervalle d'enregistrement des métriques (en secondes)
METRICS_RECORDING_INTERVAL=10

# Période de conservation des métriques (en heures)
METRICS_RETENTION_PERIOD=24

# Seuils d'alerte pour le statut de santé
METRICS_DEGRADED_ERROR_THRESHOLD=3
METRICS_UNHEALTHY_ERROR_THRESHOLD=10
```

## Performance

Le système de métriques est conçu pour avoir un impact minimal sur les performances de l'application :

- Stockage en mémoire avec nettoyage périodique des données obsolètes
- Échantillonnage adaptatif pour limiter la fréquence d'enregistrement
- Traitement asynchrone pour éviter de bloquer les opérations principales

## Tests

Des tests unitaires et d'intégration complets sont disponibles pour vérifier le bon fonctionnement du système de métriques :

```bash
# Exécution des tests unitaires
pytest tests/unit/test_metrics.py

# Exécution des tests d'intégration
pytest tests/integration/test_metrics_integration.py
```

## Dépannage

### Problèmes Courants

1. **Métriques manquantes** : Vérifier que `enable_metrics=True` est défini pour le collecteur
2. **Latence élevée** : Surveiller le nombre de métriques collectées et ajuster la fréquence d'enregistrement
3. **Erreurs d'API** : Vérifier les autorisations de l'utilisateur 