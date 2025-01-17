# Changelog

## [0.2.1] - 2024-03-XX

### Ajouté
- Nouveau système de collecteurs de données avec classes de base :
  - `BaseCollector` : Classe abstraite de base pour tous les collecteurs
  - `RESTCollector` : Collecteur pour les API REST
  - `WebSocketCollector` : Collecteur pour les WebSockets
- Collecteurs spécifiques pour les exchanges :
  - `BinanceTradeCollector` : Collecte des trades sur Binance
  - `KrakenTradeCollector` : Collecte des trades sur Kraken
  - `CoinbaseTradeCollector` : Collecte des trades sur Coinbase
- Exemples d'utilisation :
  - `trades_example.py` : Exemple simple de collecte de trades
  - `market_aggregator.py` : Agrégation de données multi-exchanges
  - `arbitrage_detector.py` : Détection d'opportunités d'arbitrage

### Modifié
- Refactoring complet du système de collecte de données
- Amélioration de la gestion des erreurs et de la résilience
- Mise à jour de la documentation

### Corrigé
- Correction des imports pour utiliser le nom du package en minuscules
- Amélioration de la gestion des connexions WebSocket
- Correction des formats de symboles entre les exchanges 