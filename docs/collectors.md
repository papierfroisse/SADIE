# Guide d'Utilisation des Collecteurs de Données

## TradeCollector

Le `TradeCollector` est un composant optimisé pour la collecte et le traitement des données de trading en temps réel.

### Caractéristiques
- Traitement haute performance (4800+ trades/seconde)
- Gestion optimisée de la mémoire
- Cache Redis intégré (optionnel)
- Mécanisme de retry robuste
- Gestion des erreurs avancée

### Installation

```bash
pip install -r requirements.txt

# Si vous souhaitez utiliser le cache Redis (optionnel)
pip install redis
```

### Utilisation de Base

```python
from SADIE.core.collectors.trade_collector import TradeCollector
from SADIE.core.models.events import Symbol

# Création du collecteur
collector = TradeCollector(
    name="my_collector",
    symbols=[Symbol.BTC_USDT.value],
    max_trades_per_symbol=10000
)

# Connexion à l'exchange
await collector.connect("binance")

# Traitement d'un trade
trade = {
    "trade_id": "123",
    "symbol": "BTC/USDT",
    "price": "50000.0",
    "amount": "1.0",
    "side": "buy",
    "timestamp": "2024-01-17T12:00:00"
}
await collector.process_trade("BTC/USDT", trade)

# Récupération des trades
trades = collector.get_trades("BTC/USDT", limit=100)
```

### Configuration Avancée

```python
collector = TradeCollector(
    name="advanced_collector",
    symbols=["BTC/USDT", "ETH/USDT"],
    max_trades_per_symbol=10000,
    connection_pool_size=5,  # Nombre de connexions parallèles
    cache_enabled=True,      # Activation du cache Redis
    cache_host="localhost",
    cache_port=6379,
    cache_db=0,
    max_retries=3,          # Nombre de tentatives en cas d'erreur
    retry_delay=1.0         # Délai initial entre les tentatives
)
```

### Gestion des Erreurs

Le collecteur gère automatiquement :
- Les erreurs réseau
- Les timeouts
- Les données invalides
- Les déconnexions

Exemple de gestion d'erreur personnalisée :

```python
try:
    await collector.process_trade(symbol, trade)
except KeyError as e:
    logger.error(f"Données invalides : {e}")
except Exception as e:
    logger.error(f"Erreur inattendue : {e}")
```

### Performance et Monitoring

- Utilisez `max_trades_per_symbol` pour contrôler l'utilisation mémoire
- Activez le cache Redis pour les données fréquemment accédées
- Ajustez `connection_pool_size` selon vos besoins
- Utilisez le logging pour monitorer les performances :
  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  ``` 