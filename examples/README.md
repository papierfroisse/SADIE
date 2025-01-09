# Exemples d'utilisation de SADIE

Ce dossier contient des exemples d'utilisation du package SADIE pour la collecte et l'analyse de données financières.

## Exemples disponibles

### 1. Collecte de données d'orderbook (`collect_orderbook.py`)

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

### 2. Analyse de données (`analyze_data.py`)

Cet exemple illustre :
- La récupération de données historiques
- L'analyse de séries temporelles
- L'analyse statistique des données
- La visualisation des résultats

Pour exécuter :
```bash
python examples/analyze_data.py
```

## Prérequis

1. Installation des dépendances :
```bash
pip install -r requirements/base.txt
```

2. Configuration :
- Copier `.env.example` vers `.env`
- Remplir les variables d'environnement nécessaires

## Notes

- Les exemples utilisent le stockage en mémoire par défaut
- Les données sont conservées uniquement pendant l'exécution
- Pour un stockage persistant, configurez une base de données

## Personnalisation

Vous pouvez modifier les paramètres dans les exemples :
- Symboles à collecter
- Intervalles de temps
- Paramètres d'analyse
- Configuration du logging

## Contribution

N'hésitez pas à proposer de nouveaux exemples ou à améliorer les existants via des pull requests. 