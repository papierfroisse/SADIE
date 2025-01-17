# Roadmap sadie

## ✅ Réalisé

### Architecture de base
- ✅ Refactoring du code pour utiliser "sadie" en minuscules
- ✅ Mise en place de la structure du projet
- ✅ Implémentation des collecteurs de base
- ✅ Support multi-exchange (Binance, Kraken, Coinbase)

### Stockage des données
- ✅ Architecture de stockage hybride (Redis + TimescaleDB)
- ✅ Implémentation du stockage Redis pour les données temps réel
- ✅ Implémentation du stockage TimescaleDB pour l'historique
- ✅ Tests unitaires et d'intégration pour le stockage
- ✅ Tests de résilience du stockage
- ✅ Exemples d'utilisation du stockage

## 🚧 En cours

### API et Interface Web
- Développement de l'API REST
- Implémentation des endpoints WebSocket
- Interface web de visualisation des données
- Documentation de l'API

### Analyse des données
- Calcul de métriques avancées
- Détection d'opportunités d'arbitrage
- Backtesting des stratégies
- Optimisation des performances

## 📅 Planifié

### Phase 1 : API et Visualisation (2-3 semaines)
1. Finaliser l'API REST avec FastAPI
2. Implémenter les WebSockets pour les données temps réel
3. Créer une interface web moderne avec React/Vue.js
4. Ajouter des graphiques interactifs (TradingView)
5. Documenter l'API avec OpenAPI/Swagger

### Phase 2 : Analyse et Trading (3-4 semaines)
1. Développer des indicateurs techniques
2. Implémenter la détection d'arbitrage
3. Créer un moteur de backtesting
4. Ajouter le support des ordres en papier
5. Optimiser les performances du système

### Phase 3 : Production et Monitoring (2-3 semaines)
1. Ajouter des métriques Prometheus
2. Configurer des alertes Grafana
3. Optimiser la gestion de la mémoire
4. Améliorer la résilience du système
5. Préparer le déploiement en production

## 🎯 Objectifs futurs

### Fonctionnalités avancées
- Support d'exchanges supplémentaires
- Analyse de sentiment (Twitter, Reddit, News)
- Machine Learning pour la prédiction
- Stratégies de trading automatisées
- Support des NFTs et DeFi

### Infrastructure
- Déploiement sur Kubernetes
- Scaling automatique
- Backup et disaster recovery
- Support multi-région
- Optimisation des coûts 