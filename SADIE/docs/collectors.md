# Documentation des Collecteurs de Données

## Vue d'ensemble

Les collecteurs de données sont des composants essentiels de SADIE qui permettent de récupérer et de traiter les données de marché à partir de différentes sources. Chaque collecteur est spécialisé dans un type de données spécifique et suit une interface commune pour assurer la cohérence et la maintenabilité.

## Types de Collecteurs

### 1. BaseCollector

La classe de base pour tous les collecteurs de données. Elle définit l'interface commune et implémente les fonctionnalités partagées.

```python
from sadie.data.collectors import BaseCollector

class MyCollector(BaseCollector):
    def __init__(self, api_key, api_secret=None):
        super().__init__(api_key, api_secret)
```

### 2. OrderBookCollector

Spécialisé dans la collecte des données de carnet d'ordres (L2/L3) de Binance.

#### Fonctionnalités
- Récupération des carnets d'ordres L2 (prix/quantité)
- Récupération des carnets d'ordres L3 (prix/quantité/ordre)
- Flux de mises à jour en temps réel
- Gestion automatique des reconnexions

#### Exemple d'utilisation
```python
from sadie.data.collectors.orderbook import OrderBookCollector

collector = OrderBookCollector(api_key="your_key", api_secret="your_secret")

# Récupérer le carnet d'ordres L2
book_l2 = collector.get_order_book("BTC/USDT", level="L2")

# Récupérer le carnet d'ordres L3
book_l3 = collector.get_order_book("BTC/USDT", level="L3")

# S'abonner aux mises à jour en temps réel
def on_update(update):
    print(f"Nouvelle mise à jour: {update}")

collector.start_order_book_stream("BTC/USDT", on_update)
```

### 3. BinanceDataCollector

Collecteur général pour les données Binance.

#### Fonctionnalités
- Données historiques OHLCV
- Prix en temps réel
- Statistiques de marché
- Données de trading

#### Exemple d'utilisation
```python
from sadie.data.collectors.binance import BinanceDataCollector

collector = BinanceDataCollector(api_key="your_key", api_secret="your_secret")

# Récupérer des données historiques
data = collector.get_historical_data(
    symbol="BTC/USDT",
    interval="1h",
    start_time="2024-01-01"
)

# Récupérer le prix actuel
price = collector.get_current_price("BTC/USDT")
```

## Factory de Collecteurs

La `DataCollectorFactory` permet de créer des instances de collecteurs de manière standardisée.

```python
from sadie.data.collectors.factory import DataCollectorFactory

# Créer un collecteur Binance
binance_collector = DataCollectorFactory.create(
    source="binance",
    api_key="your_key",
    api_secret="your_secret"
)

# Créer un collecteur OrderBook
orderbook_collector = DataCollectorFactory.create(
    source="orderbook",
    api_key="your_key",
    api_secret="your_secret"
)
```

## Configuration

Les collecteurs utilisent les variables d'environnement suivantes :
- `BINANCE_API_KEY` : Clé API Binance
- `BINANCE_API_SECRET` : Secret API Binance
- `ALPHA_VANTAGE_API_KEY` : Clé API Alpha Vantage

## Bonnes Pratiques

1. **Gestion des Ressources**
   - Utilisez les context managers pour les connexions
   - Fermez proprement les flux de données
   - Gérez les limites de taux d'API

2. **Traitement des Erreurs**
   - Implémentez une gestion robuste des erreurs
   - Utilisez les retry patterns pour les appels réseau
   - Loggez les erreurs de manière appropriée

3. **Performance**
   - Utilisez le cache quand approprié
   - Optimisez les requêtes batch
   - Surveillez l'utilisation de la mémoire

## Tests

Les collecteurs sont testés à trois niveaux :

1. **Tests Unitaires**
   ```bash
   pytest tests/unit/test_data_collectors.py
   ```

2. **Tests d'Intégration**
   ```bash
   pytest tests/integration/test_collectors_integration.py
   ```

3. **Tests de Performance**
   ```bash
   pytest tests/performance/test_collectors_perf.py
   ```

## Contribution

Pour ajouter un nouveau collecteur :

1. Créez une nouvelle classe héritant de `BaseCollector`
2. Implémentez les méthodes requises
3. Ajoutez les tests appropriés
4. Enregistrez le collecteur dans la factory
5. Mettez à jour la documentation

## Roadmap

- [ ] Support pour plus d'exchanges
- [ ] Collecteur de données on-chain
- [ ] Amélioration des performances
- [ ] Support WebSocket pour tous les collecteurs 