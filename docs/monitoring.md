# Monitoring SADIE

## Architecture

Le système de monitoring de SADIE est basé sur la stack suivante :
- **Prometheus** : Collecte et stockage des métriques
- **Grafana** : Visualisation et alerting
- **Node Exporter** : Métriques système
- **Redis Exporter** : Métriques Redis

## Métriques Collectées

### Métriques de Trading

1. **Trades Traités**
   - Métrique : `sadie_trades_processed_total`
   - Type : Counter
   - Labels : `exchange`, `symbol`
   - Description : Nombre total de trades traités

2. **Latence de Traitement**
   - Métrique : `sadie_trade_processing_seconds`
   - Type : Histogram
   - Labels : `exchange`, `symbol`
   - Buckets : [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
   - Description : Temps de traitement des trades

3. **Taille des Buffers**
   - Métrique : `sadie_trade_buffer_size`
   - Type : Gauge
   - Labels : `exchange`, `symbol`
   - Description : Nombre de trades en attente de traitement

### Métriques Réseau

1. **Latence Réseau**
   - Métrique : `sadie_network_latency_seconds`
   - Type : Gauge
   - Labels : `exchange`
   - Description : Latence des requêtes vers les exchanges

2. **Erreurs Réseau**
   - Métrique : `sadie_network_errors_total`
   - Type : Counter
   - Labels : `exchange`, `type`
   - Description : Nombre d'erreurs réseau par type

### Métriques Cache

1. **Cache Hits/Misses**
   - Métriques : 
     - `sadie_cache_hits_total`
     - `sadie_cache_misses_total`
   - Type : Counter
   - Labels : `type`
   - Description : Performance du cache

2. **Taille du Cache**
   - Métrique : `sadie_cache_size_bytes`
   - Type : Gauge
   - Labels : `type`
   - Description : Utilisation mémoire du cache

### Métriques Système

1. **Utilisation Mémoire**
   - Métrique : `sadie_memory_usage_bytes`
   - Type : Gauge
   - Description : Utilisation mémoire du processus

2. **Utilisation CPU**
   - Métrique : `sadie_cpu_usage_percent`
   - Type : Gauge
   - Description : Utilisation CPU du processus

## Dashboards Grafana

### 1. Vue d'Ensemble (Overview)
- Trades par seconde
- Latence de traitement (P95)
- Taille des buffers
- Erreurs par seconde
- Utilisation ressources

### 2. Performance Cache
- Taux de hit/miss
- Ratio de hit
- Taille du cache
- Erreurs cache

### 3. Trades Détaillés
- Métriques par exchange/symbol
- Latence réseau
- Erreurs réseau
- Erreurs de traitement

## Configuration Alertes

### Alertes Critiques
1. **Latence Élevée**
   ```yaml
   alert: HighTradeProcessingLatency
   expr: histogram_quantile(0.95, rate(sadie_trade_processing_seconds_bucket[5m])) > 0.1
   for: 2m
   ```

2. **Buffer Plein**
   ```yaml
   alert: TradeBufferNearCapacity
   expr: sadie_trade_buffer_size > 8000
   for: 1m
   ```

3. **Erreurs Réseau**
   ```yaml
   alert: HighNetworkErrorRate
   expr: rate(sadie_network_errors_total[5m]) > 1
   for: 5m
   ```

### Alertes Warning
1. **Cache Performance**
   ```yaml
   alert: LowCacheHitRatio
   expr: rate(sadie_cache_hits_total[5m]) / (rate(sadie_cache_hits_total[5m]) + rate(sadie_cache_misses_total[5m])) < 0.7
   for: 10m
   ```

2. **Mémoire**
   ```yaml
   alert: HighMemoryUsage
   expr: sadie_memory_usage_bytes > 1e9
   for: 5m
   ```

## Maintenance

### Rétention des Données
- Prometheus : 15 jours
- Grafana : Agrégation après 24h

### Backup
- Snapshots Grafana quotidiens
- Backup Prometheus hebdomadaire

### Bonnes Pratiques
1. **Labels**
   - Limitez le nombre de labels
   - Évitez les labels à haute cardinalité

2. **Métriques**
   - Préfixez toutes les métriques avec `sadie_`
   - Utilisez des unités SI (secondes, bytes)

3. **Alertes**
   - Configurez des délais appropriés
   - Évitez les faux positifs
   - Documentez les actions de remédiation 