# sadie - Système d'Analyse et de Détection d'Indicateurs pour l'Échange

## Vue d'ensemble

sadie est une plateforme d'analyse technique des marchés financiers qui permet de :
- Suivre les données de marché en temps réel
- Créer et gérer des alertes sur les prix et indicateurs
- Visualiser les données historiques et les indicateurs techniques
- Recevoir des notifications en temps réel
- Monitorer les performances des collecteurs via un tableau de bord dédié
- Effectuer du backtesting sur des stratégies d'analyse technique (en développement)
- Suivre et analyser la performance de son portefeuille (planifié)

## Architecture

Le projet est structuré en plusieurs composants :

```
sadie/
├── core/           # Logique métier principale
│   ├── collectors/  # Collecteurs des données (version standardisée)
│   ├── models/      # Modèles de données
│   ├── monitoring/  # Système de métriques et surveillance
│   └── utils/       # Utilitaires partagés
├── data/           # Gestion des données (ancienne structure)
│   ├── collectors/  # Collecteurs obsolètes (utiliser core.collectors à la place)
│   └── storage/     # Stockage des données
├── web/            # Interface web et API
│   ├── static/      # Application front-end React
│   ├── routes/      # Routes API organisées par fonctionnalité
│   └── app.py       # API FastAPI
├── analysis/       # Analyse technique et indicateurs
├── scripts/        # Scripts utilitaires (vérifications de sécurité, hooks Git)
└── tests/          # Tests unitaires et d'intégration
    ├── unit/       # Tests unitaires
    ├── integration/ # Tests d'intégration
    ├── performance/ # Tests de performance
    └── stress/      # Tests de performance et de charge
```

## Technologies

- **Backend**
  - Python 3.8+
  - FastAPI
  - Redis
  - TimescaleDB
  - WebSocket
  - Pandas
  - JWT (authentification)
  - Prometheus (monitoring)

- **Frontend**
  - React 17+
  - TypeScript 4.5+
  - Material-UI 5
  - WebSocket
  - Chart.js
  - React Router

## Installation

1. Cloner le dépôt
```bash
git clone https://github.com/yourusername/sadie.git
cd sadie
```

2. Installer les dépendances Python
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Pour le développement
```

3. Installer les dépendances Node.js
```bash
cd web/static
npm install
```

4. Configurer l'environnement
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. Installer les hooks de sécurité Git (recommandé)
```bash
python scripts/install_security_hooks.py
```

## Configuration

Le fichier `.env` doit contenir :

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# TimescaleDB
TIMESCALE_HOST=localhost
TIMESCALE_PORT=5432
TIMESCALE_USER=postgres
TIMESCALE_PASSWORD=
TIMESCALE_DB=sadie

# API
API_HOST=0.0.0.0
API_PORT=8000

# API Keys (optionnel)
BINANCE_API_KEY=
BINANCE_API_SECRET=
KRAKEN_API_KEY=
KRAKEN_API_SECRET=

# Logging
LOG_LEVEL=INFO

# Prometheus (optionnel)
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

## Démarrage

1. Démarrer les services de base de données
```bash
redis-server
# Et TimescaleDB selon votre configuration
```

2. Démarrer l'API
```bash
cd sadie
uvicorn web.app:app --reload
```

3. Démarrer le frontend
```bash
cd web/static
npm start
```

## Documentation

La documentation complète est disponible dans le répertoire `docs/` :

- [Installation](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Métriques](docs/metrics.md)
- [Métriques avancées](docs/metrics_advanced.md)
- [API](docs/api.md)
- [API des métriques](docs/api/metrics.md)
- [Alertes](docs/alerts.md)
- [Sécurité](docs/security.md)
- [Plan de consolidation](docs/consolidation_plan.md)
- [Backtesting](docs/backtesting.md) (en préparation)
- [Analyse Technique](docs/technical_analysis.md) (en préparation)

## Sécurité

Le projet intègre plusieurs mesures de sécurité :

- **Vérifications automatisées** : Script `scripts/security_check.py` pour détecter les problèmes courants
- **Hooks Git de pre-commit** : Installation via `scripts/install_security_hooks.py`
- **Gestion sécurisée des API keys** : Stockage dans des variables d'environnement uniquement
- **Authentification et autorisation** : Système basé sur JWT avec gestion des rôles
- **Communications sécurisées** : Support HTTPS/WSS
- **Audit de sécurité régulier** : Guide complet dans `docs/security.md`

## Tests

### Backend
```bash
# Tous les tests
pytest tests/

# Tests unitaires uniquement
pytest tests/unit/

# Tests d'intégration uniquement
pytest tests/integration/

# Tests des métriques avancées
pytest tests/integration/test_metrics_monitoring.py

# Tests avec couverture
pytest --cov=sadie tests/
```

### Frontend
```bash
cd web/static
npm test
```

## Exemples de code

Des exemples d'utilisation sont disponibles dans le répertoire `examples/` :

- [Utilisation de base](examples/basic_usage.py)
- [Création d'alertes](examples/alerts_example.py)
- [Métriques avancées](examples/metrics_advanced_example.py)

## Fonctionnalités

### Données de marché
- Suivi en temps réel des prix
- Historique des données
- Indicateurs techniques
  - RSI
  - MACD
  - EMA (20, 50, 200)
  - Bandes de Bollinger
  - Stochastique
  - Ichimoku Cloud
  - Support/Résistance (en développement)

### Collecteurs de données
- Architecture standardisée avec la classe `BaseCollector`
- Support des exchanges principaux:
  - Binance
  - Kraken
  - Coinbase
- Gestion des erreurs robuste
- Mécanismes de reconnexion automatique
- Logging avancé
- Métriques de performance en temps réel

### Métriques et surveillance
- **Tableau de bord de métriques** : Interface dédiée pour visualiser les performances des collecteurs de données en temps réel (`/metrics`)
- **Alertes automatiques** : Création d'alertes basées sur des seuils de performance personnalisables
- **Tableaux de bord personnalisables** : Création de tableaux de bord avec des widgets configurables pour visualiser les métriques importantes
- **Exportation des données** : Export des métriques aux formats JSON et CSV pour analyse externe
- **Intégration Prometheus/Grafana** : Exposition des métriques au format Prometheus pour une intégration avec des outils de surveillance tiers

### Alertes
- Alertes sur les prix
- Alertes sur les indicateurs
- Notifications en temps réel
- Historique des alertes
- Configuration des canaux de notification (email, webhooks)

### Interface utilisateur
- Dashboard en temps réel
- Graphiques interactifs
- Gestion des alertes
- Configuration des indicateurs
- Surveillance des performances
- Interface de backtesting (en développement)
- Analyse technique avancée (en développement)

### Nouvelles fonctionnalités (en développement)
- **Système de backtesting** : Testez vos stratégies sur des données historiques
- **Détection de patterns** : Identification automatique des figures chartistes
- **Portfolio et tracking** : Suivi de portefeuille multi-exchange avec calcul de performance
- **Visualisations avancées** : Superposition d'indicateurs multiples et personnalisation des vues

### Sécurité
- Authentification basée sur JWT
- Gestion des rôles et permissions
- Protection des routes API
- Connexion sécurisée WebSocket
- Vérifications automatisées de sécurité
- Hooks Git pour les contrôles de sécurité pré-commit

## Roadmap

Consultez [roadmap.md](roadmap.md) pour plus de détails sur les fonctionnalités planifiées.

## Mises à jour récentes (Juin 2024)

Nous avons récemment mis à jour le projet avec de nouvelles fonctionnalités et améliorations :

- Standardisation complète des noms (SADIE → sadie)
- Nouvelles fonctionnalités de sécurité et hooks Git
- Documentation détaillée des futures fonctionnalités d'analyse technique et de backtesting
- Support pour TimescaleDB et Prometheus
- Interface améliorée pour les métriques et le monitoring

Pour plus de détails, consultez notre [récapitulatif des mises à jour de juin 2024](docs/mise_a_jour_juin_2024.md) et notre [guide de démarrage rapide](docs/guide_demarrage_rapide.md).

## Contribuer

Les contributions sont les bienvenues ! Veuillez consulter notre [guide de contribution](CONTRIBUTING.md) et notre [code de conduite](CODE_OF_CONDUCT.md).

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Support

Pour toute question ou problème :
1. Consulter la [documentation](docs/)
2. Ouvrir une issue sur GitHub
3. Contacter l'équipe de support 