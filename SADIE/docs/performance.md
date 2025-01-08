# Tests de Performance SADIE

Ce document décrit le framework de tests de performance et de résilience pour le projet SADIE.

## Objectifs

Les tests de performance visent à :

1. Mesurer et valider les performances des collecteurs de données
2. Vérifier la résilience du système sous charge
3. Identifier les goulots d'étranglement potentiels
4. Établir des références de performance

## Métriques Mesurées

### Utilisation des Ressources

- **Mémoire**
  - Utilisation moyenne
  - Pics d'utilisation
  - Fuites mémoire potentielles

- **CPU**
  - Utilisation moyenne
  - Pics d'utilisation
  - Distribution de la charge

- **Réseau**
  - Bande passante utilisée
  - Latence des requêtes
  - Taux d'erreur

### Métriques Spécifiques

- **Latence des Collecteurs**
  - Temps de réponse moyen
  - 95e percentile
  - 99e percentile
  - Latence maximale

- **Débit**
  - Transactions par seconde
  - Messages WebSocket par seconde
  - Taux de mise à jour des order books

- **Fiabilité**
  - Taux de succès des requêtes
  - Taux de reconnexion
  - Temps moyen entre les erreurs

## Scénarios de Test

### 1. Tests de Charge Normale

```python
# Exemple de test de charge normale
async def test_normal_load():
    collector = OrderBookCollector(symbols=["BTCUSDT"])
    await collector.start()
    
    # Collecter les métriques pendant 1 heure
    metrics = await collect_metrics(duration=3600)
    assert metrics.avg_response_time < 0.1  # 100ms max
```

### 2. Tests de Charge Élevée

```python
# Exemple de test de charge élevée
async def test_high_load():
    collector = OrderBookCollector(symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"])
    await collector.start()
    
    # Simuler une charge élevée
    await generate_high_load(tps=1000, duration=300)
    
    metrics = await collect_metrics()
    assert metrics.error_rate < 0.01  # Max 1% d'erreurs
```

### 3. Tests de Résilience

```python
# Exemple de test de résilience
async def test_network_issues():
    collector = TransactionCollector(symbols=["BTCUSDT"])
    await collector.start()
    
    # Simuler des problèmes réseau
    await simulate_network_issues(duration=60)
    
    # Vérifier la récupération
    metrics = await collect_metrics()
    assert metrics.recovery_time < 5.0  # Récupération en moins de 5s
```

## Seuils de Performance

### Collecteur OrderBook

- Temps de réponse moyen < 100ms
- Utilisation CPU < 30%
- Utilisation mémoire < 200MB
- Taux d'erreur < 0.1%

### Collecteur de Transactions

- Latence de traitement < 50ms
- Capacité > 1000 TPS
- Perte de messages < 0.01%
- Temps de récupération < 5s

### WebSocket

- Temps de reconnexion < 1s
- Taux de perte de connexion < 0.1%
- Latence moyenne < 50ms

## Exécution des Tests

### Prérequis

```bash
pip install pytest-benchmark pytest-asyncio
```

### Commandes

```bash
# Tests de performance complets
pytest tests/performance/

# Tests spécifiques
pytest tests/performance/test_orderbook_perf.py
pytest tests/performance/test_transaction_perf.py

# Tests avec métriques détaillées
pytest tests/performance/ --benchmark-only
```

### Environnement de Test

- Utiliser un environnement isolé
- Monitorer les ressources système
- Exécuter les tests à différents moments
- Documenter les conditions de test

## Analyse des Résultats

### Génération de Rapports

```bash
# Générer un rapport HTML
pytest tests/performance/ --benchmark-only --benchmark-json output.json
pytest-benchmark compare output.json --csv output.csv
```

### Interprétation

- Comparer avec les seuils définis
- Analyser les tendances
- Identifier les anomalies
- Documenter les résultats

## Maintenance

### Mise à Jour des Tests

- Réviser régulièrement les seuils
- Ajouter de nouveaux scénarios
- Mettre à jour les métriques
- Optimiser les tests

### Intégration Continue

- Exécuter les tests de performance dans CI
- Alerter sur les régressions
- Archiver les résultats
- Générer des rapports de tendance 