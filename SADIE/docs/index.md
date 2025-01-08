# SADIE - Documentation

Bienvenue dans la documentation de SADIE (Système Avancé D'Intelligence et d'Exécution).

## Vue d'ensemble

SADIE est une plateforme sophistiquée d'analyse de marché et d'optimisation de portefeuille qui combine :
- Des collecteurs de données haute performance
- Des systèmes de stockage optimisés
- Des capacités d'analyse en temps réel
- Des stratégies d'exécution avancées

## Version Actuelle : 0.2.0

### Fonctionnalités Principales

#### 1. Collecte de Données
- Order Books L2/L3 complets avec WebSocket optimisé
- Données tick-by-tick en temps réel
- Transactions en temps réel avec analyse de flux
- Tests de performance et métriques de latence

#### 2. Stockage Optimisé
- Compression multi-algorithmes (LZ4, ZLIB, SNAPPY)
- Partitionnement adaptatif des données
- Gestion hot/warm/cold data
- Cache prédictif en développement

#### 3. Analyse en Temps Réel
- Métriques de marché avancées
- Indicateurs techniques personnalisés
- Analyse de liquidité et profondeur
- Intégration avec OrderBookAnalyzer

## Démarrage rapide

### Prérequis
```bash
# Dépendances système
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-dev python3-pip postgresql postgresql-contrib build-essential git
```

### Installation avec Docker
```bash
# Cloner le repository
git clone https://github.com/votre-repo/SADIE.git
cd SADIE

# Construire et démarrer
docker-compose up -d
```

### Installation Manuelle
```bash
# Environnement virtuel
python3.9 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos paramètres
```

## Structure du Projet

```
SADIE/
├── src/
│   └── sadie/
│       ├── data/
│       │   └── collectors/     # Collecteurs de données
│       ├── analysis/          # Analyse et métriques
│       ├── storage/           # Gestion du stockage
│       └── execution/         # Stratégies d'exécution
├── tests/
│   ├── unit/                 # Tests unitaires
│   ├── integration/          # Tests d'intégration
│   └── performance/          # Tests de performance
├── docs/                     # Documentation
└── config/                   # Configuration
```

## Documentation Détaillée

- [Guide Développeur](DEVBOOK.md) - Guide technique détaillé
- [Guide Performance](performance.md) - Optimisations et métriques
- [Roadmap](ROADMAP.md) - Planning et objectifs
- [Contexte du Projet](PROJECT_CONTEXT.md) - Vue d'ensemble complète

## Monitoring et Métriques

### Dashboard
- Grafana : http://localhost:3000
- Prometheus : http://localhost:9090

### Métriques Clés
- Latence des collecteurs (p95, p99)
- Utilisation des ressources système
- Performance du cache
- Santé des connexions WebSocket

## Support et Contact

- Documentation : /docs/
- Issues : GitHub Issues
- Discussion : GitHub Discussions
- Wiki : GitHub Wiki

---
Dernière mise à jour : 2024-01-08
Version actuelle : 0.2.0