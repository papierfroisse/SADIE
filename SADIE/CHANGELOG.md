# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - En développement
### Ajouté
- Collecteur de données tick par tick
  - Support WebSocket pour les données en temps réel
  - Traitement par lots avec statistiques
  - Cache optimisé pour les données haute fréquence
  - Tests unitaires complets

- Carnets d'ordres avancés
  - Support complet des carnets d'ordres L2/L3
  - Métriques en temps réel (spread, profondeur, déséquilibre)
  - Gestion efficace des mises à jour avec SortedDict
  - Callbacks pour les métriques en temps réel
  - Tests unitaires et d'intégration complets

### En cours
- Flux de transactions en temps réel
- Tests de charge et de résilience

## [0.1.2] - 2024-01-08
### Ajouté
- Classe de base BaseCollector pour standardiser les collecteurs de données
- Collecteur OrderBook pour les données L2/L3 de Binance
- Tests unitaires complets pour le collecteur OrderBook
- Tests de performance pour les collecteurs de données
- Tests d'intégration pour les collecteurs
- Documentation complète des collecteurs dans `docs/collectors.md`

### Amélioré
- Optimisation des performances des collecteurs
- Meilleure gestion des erreurs et des reconnexions
- Documentation plus détaillée et exemples d'utilisation

## [0.1.1] - 2024-01-08
### Ajouté
- Intégration de l'API Binance
- Intégration de l'API Alpha Vantage
- Configuration PostgreSQL/TimescaleDB
- Système de cache avec gestion de la persistance
- Documentation des APIs et de la base de données

### Modifié
- Amélioration de la structure du projet
- Optimisation de la gestion des connexions API

### Corrigé
- Gestion des erreurs dans les appels API
- Problèmes de connexion à la base de données

## [0.1.0] - 2024-01-08
### Ajouté
- Structure initiale du projet
- Configuration Git et GitHub Actions
- Documentation de base (README, CONTRIBUTING)
- Tests unitaires de base
- Configuration de l'environnement de développement
- Fichiers de configuration initiaux
- Structure des dossiers du projet

### Sécurité
- Mise en place des bonnes pratiques de sécurité
- Configuration des variables d'environnement
- Gestion sécurisée des clés API 