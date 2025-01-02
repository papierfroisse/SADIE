# DEVBOOK - Crypto Tracker

## État Actuel
- Structure de base du projet React/TypeScript
- Configuration initiale de PostgreSQL
- Services de base pour les exchanges (Binance/Kraken)

## Priorités

### 1. Système de Collecte et Stockage des Données (En cours)
- [ ] Définir le schéma de base de données pour les données de marché
  - Tables pour les bougies (OHLCV)
  - Tables pour les paires de trading
  - Tables pour les exchanges
- [ ] Créer un service de collecte de données
  - Collecte historique avec gestion de rate limiting
  - WebSocket pour les mises à jour en temps réel
  - Système de fallback en cas de déconnexion
- [ ] Implémenter un système de mise en cache
  - Cache en mémoire pour les données récentes
  - Stratégie de mise à jour optimisée
- [ ] Système de synchronisation avec la base de données
  - Batch inserts pour les performances
  - Gestion des conflits et des mises à jour

### 2. Module de Rendu de Graphique (À venir)
- [ ] Créer un canvas renderer personnalisé
  - Système de coordonnées et de mise à l'échelle
  - Gestion des événements souris/tactile
  - Support du zoom et du défilement
- [ ] Implémenter le rendu des bougies japonaises
  - Optimisation du rendu pour grandes quantités de données
  - Gestion des différentes échelles de temps
- [ ] Ajouter le support des overlays
  - Système de calques pour les indicateurs
  - Gestion des styles et des couleurs
- [ ] Créer un système d'annotations
  - Support des lignes de tendance
  - Marqueurs et étiquettes

### 3. Calcul d'Indicateurs Techniques (À venir)
- [ ] Implémenter les indicateurs de base
  - Moyennes mobiles (SMA, EMA, WMA)
  - Oscillateurs (RSI, Stochastique)
  - Bandes de Bollinger
  - MACD
- [ ] Créer un système extensible pour les indicateurs
  - Architecture plugin pour nouveaux indicateurs
  - Cache des calculs pour les performances
- [ ] Optimisation des calculs
  - Calculs incrémentaux quand possible
  - Parallélisation des calculs lourds

### 4. Système de Backtesting (À venir)
- [ ] Créer le moteur de backtesting
  - Replay précis des données historiques
  - Gestion des ordres et des positions
  - Calcul des performances
- [ ] Implémenter les métriques de performance
  - Ratio de Sharpe
  - Drawdown maximum
  - Rendement ajusté au risque
- [ ] Ajouter des outils d'analyse
  - Visualisation des trades
  - Rapports de performance
  - Export des résultats

## Prochaines Étapes Immédiates
1. Créer le schéma de base de données
2. Implémenter le service de collecte de données
3. Mettre en place le système de synchronisation
4. Commencer le développement du renderer de graphique

## Notes Techniques
- Utiliser des transactions pour la cohérence des données
- Implémenter des tests unitaires pour chaque composant
- Documenter l'API et les structures de données
- Maintenir une couverture de code élevée

## Conventions de Commit
- feat: Nouvelle fonctionnalité
- fix: Correction de bug
- refactor: Refactoring du code
- docs: Mise à jour de la documentation
- test: Ajout ou modification de tests
- chore: Maintenance générale

## Structure des Branches
- main: Code de production
- develop: Développement principal
- feature/*: Nouvelles fonctionnalités
- fix/*: Corrections de bugs
- release/*: Préparation des releases 