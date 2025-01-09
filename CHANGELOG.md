# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2024-01-22

### Ajouté
- Implémentation des collecteurs de données :
  - Classe de base `BaseCollector`
  - Collecteur REST avec `AsyncRESTCollector`
  - Collecteur WebSocket avec `AsyncWebSocketCollector`
  - Tests unitaires complets pour les collecteurs
  - Documentation des APIs et des classes

### Modifié
- Mise à jour de la structure des tests
- Amélioration de la gestion des erreurs
- Optimisation des reconnexions WebSocket

## [0.1.0] - 2024-01-15

### Ajouté
- Structure initiale du projet
- Configuration de base avec `pyproject.toml` et `setup.py`
- Système de logging configurable
- Collecteurs de données REST et WebSocket
- Stockage en mémoire des données
- Analyseurs de séries temporelles et statistiques
- Tests unitaires, d'intégration et de performance
- Documentation de base
- Exemples d'utilisation
- Configuration CI/CD avec GitHub Actions
- Mise en place des fichiers de configuration:
  - `.env.example` pour la configuration d'environnement
  - `requirements/` pour les dépendances
  - `.gitignore` pour les exclusions Git
  - `CODE_OF_CONDUCT.md` pour les règles de conduite
  - `CONTRIBUTING.md` pour les guides de contribution
  - `LICENSE` pour la licence MIT
  - `README.md` pour la documentation principale

### Modifié
- Mise à jour de la structure du projet pour suivre les meilleures pratiques
- Amélioration de la documentation
- Standardisation des fichiers de configuration
- Mise à jour des dépendances dans requirements
- Optimisation de la configuration de développement

### Corrigé
- Correction des chemins d'importation
- Correction des problèmes de typage
- Harmonisation des versions de dépendances
- Standardisation des formats de fichiers
- Correction des configurations de tests

## [0.0.1] - 2024-01-01

### Ajouté
- Initialisation du projet
- Création du repository
- Ajout des fichiers de base (README, LICENSE, etc.) 