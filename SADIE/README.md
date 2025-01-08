# SADIE (Système Avancé D'Intelligence et d'Exécution)

## Description
SADIE est une plateforme sophistiquée d'analyse de marché et d'optimisation de portefeuille, actuellement en version 0.2.0. Le projet combine des collecteurs de données haute performance, des systèmes de stockage optimisés, et des capacités d'analyse en temps réel.

## État Actuel (v0.2.0)

### Fonctionnalités Implémentées

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

## Infrastructure Technique

### Stack Technologique
- Python 3.9+ pour le backend
- TimescaleDB pour le stockage temporel
- Redis pour le cache distribué
- Kafka pour le streaming de données
- Docker pour la conteneurisation
- Kubernetes pour l'orchestration

### Configuration Requise
- CPU : 8+ cœurs recommandés
- RAM : Minimum 16GB, 32GB recommandé
- Stockage : SSD avec minimum 500GB
- Réseau : Connexion faible latence (<50ms)
- OS : Linux (Ubuntu 20.04+ recommandé)

## Installation

### Prérequis
```bash
# Dépendances système
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-dev python3-pip

# Dépendances de base de données
sudo apt-get install -y postgresql postgresql-contrib

# Outils de développement
sudo apt-get install -y build-essential git
```

### Installation avec Docker
```bash
# Cloner le repository
git clone https://github.com/votre-repo/SADIE.git
cd SADIE

# Construire l'image
docker-compose build

# Démarrer les services
docker-compose up -d
```

### Installation Manuelle
```bash
# Créer un environnement virtuel
python3.9 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env
# Éditer .env avec vos paramètres
```

## Utilisation

### Collecte de Données
```python
from sadie.data.collectors import OrderBookCollector
from sadie.data.collectors.tick import TickCollector

# Initialiser les collecteurs
orderbook = OrderBookCollector(
    symbols=["BTC/USD", "ETH/USD"],
    depth_level="L2"
)

tick = TickCollector(
    symbols=["BTC/USD"],
    batch_size=1000
)

# Démarrer la collecte avec métriques
orderbook.start(enable_metrics=True)
tick.start(enable_metrics=True)

# Récupérer les données
order_book_data = orderbook.get_current_book("BTC/USD")
tick_data = tick.get_latest_ticks("BTC/USD", limit=100)
```

### Analyse en Temps Réel
```python
from sadie.analysis.orderbook_metrics import OrderBookAnalyzer
from sadie.analysis.indicators import TechnicalIndicators

# Analyse du carnet d'ordres
analyzer = OrderBookAnalyzer(orderbook)
metrics = analyzer.compute_metrics()

# Indicateurs techniques
indicators = TechnicalIndicators()
rsi = indicators.calculate_rsi(tick_data, period=14)
vwap = indicators.calculate_vwap(tick_data)
```

## Tests et Validation

### Tests Unitaires
```bash
# Exécuter tous les tests
pytest

# Tests spécifiques
pytest tests/unit/test_collectors.py
pytest tests/performance/test_orderbook_perf.py
```

### Tests de Performance
```bash
# Tests de charge
python -m sadie.tests.load_testing

# Tests de latence
python -m sadie.tests.latency_testing
```

## Monitoring

### Métriques Disponibles
- Latence des collecteurs (p95, p99)
- Utilisation des ressources système
- Performance du cache
- Santé des connexions WebSocket

### Dashboard
- Accès Grafana : http://localhost:3000
- Métriques Prometheus : http://localhost:9090

## Documentation
- [Guide Développeur](docs/DEVBOOK.md)
- [Guide Performance](docs/performance.md)
- [Roadmap](docs/ROADMAP.md)
- [Changelog](CHANGELOG.md)

## Sécurité
- [Guide de Sécurité](docs/SECURITY.md)
- [Politique de Confidentialité](docs/PRIVACY.md)

## Support et Contact
- Documentation : /docs/
- Issues : GitHub Issues
- Discussion : GitHub Discussions
- Wiki : GitHub Wiki

## Licence
Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---
Dernière mise à jour : 2024-01-08
Version actuelle : 0.2.0 