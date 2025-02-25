# Exemples d'utilisation de SADIE

Ce dossier contient des exemples d'utilisation du package SADIE pour la collecte et l'analyse de données financières.

## Exemples disponibles

### 1. Collecteurs de données

#### Collecteur standard (`collector_example.py`)

Cet exemple montre comment :
- Initialiser un collecteur de trades Binance standardisé
- Se connecter à Redis pour le stockage des données
- Collecter et stocker les données en temps réel
- Gérer les erreurs et les reconnexions

Pour exécuter :
```bash
python examples/collector_example.py
```

#### Collecteur Kraken (`kraken_example.py`)

Cet exemple démontre :
- L'utilisation du collecteur Kraken standardisé
- La connexion à l'API WebSocket de Kraken
- La collecte de trades pour plusieurs symboles
- Le stockage des données dans Redis

Pour exécuter :
```bash
python examples/kraken_example.py
```

#### Multi-Exchange (`multi_exchange_example.py`) - NOUVEAU

Cet exemple avancé illustre :
- L'utilisation simultanée de plusieurs collecteurs (Binance et Kraken)
- La gestion unifiée des données multi-exchange
- L'affichage de statistiques en temps réel
- La gestion des erreurs et des déconnexions pour plusieurs sources

Pour exécuter :
```bash
python examples/multi_exchange_example.py
```

### 2. Collecte de données d'orderbook (`collect_orderbook.py`)

Cet exemple montre comment :
- Initialiser un collecteur d'orderbook
- Se connecter à l'API WebSocket de Binance
- Souscrire à plusieurs symboles
- Collecter et stocker les données en temps réel
- Calculer des métriques sur les données collectées

Pour exécuter :
```bash
python examples/collect_orderbook.py
```

### 3. Analyse de données (`analyze_data.py`)

Cet exemple illustre :
- La récupération de données historiques
- L'analyse de séries temporelles
- L'analyse statistique des données
- La visualisation des résultats

Pour exécuter :
```bash
python examples/analyze_data.py
```

## Architecture des collecteurs standardisés

Depuis Mai 2024, SADIE utilise une architecture standardisée pour les collecteurs:

```python
from sadie.core.collectors import BaseCollector, KrakenTradeCollector, BinanceTradeCollector

# Tous les collecteurs héritent de BaseCollector et partagent une interface commune
```

Avantages de cette standardisation:
- Interface unifiée pour tous les collecteurs
- Gestion des erreurs robuste
- Mécanismes de reconnexion automatique
- Facilité d'intégration de nouveaux exchanges
- Support du multi-exchange

## Prérequis

1. Installation des dépendances :
```bash
pip install -r requirements.txt
```

2. Configuration :
- Copier `.env.example` vers `.env`
- Remplir les variables d'environnement nécessaires:
  ```
  # Redis
  REDIS_HOST=localhost
  REDIS_PORT=6379
  
  # API Keys (optionnel)
  BINANCE_API_KEY=votre_clé_api
  BINANCE_API_SECRET=votre_secret_api
  KRAKEN_API_KEY=votre_clé_api
  KRAKEN_API_SECRET=votre_secret_api
  ```

## Notes

- Les exemples sont configurés pour Redis par défaut
- Pour un stockage persistant à long terme, configurez TimescaleDB
- Les collecteurs gèrent automatiquement les erreurs et les reconnexions

## Personnalisation

Vous pouvez modifier les paramètres dans les exemples :
- Symboles à collecter
- Intervalles de temps
- Paramètres d'analyse
- Configuration du logging

## Contribution

N'hésitez pas à proposer de nouveaux exemples ou à améliorer les existants via des pull requests. 