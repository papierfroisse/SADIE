# Guide de Configuration

Ce guide explique comment configurer SADIE pour votre utilisation.

## Configuration de base

### Variables d'environnement

Le fichier `.env` contient toutes les variables d'environnement nécessaires :

```bash
# API Keys
ALPHA_VANTAGE_KEY=votre_clé_alpha_vantage
TWITTER_API_KEY=votre_clé_twitter
TWITTER_API_SECRET=votre_secret_twitter

# Base de données
DB_USER=sadie_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sadie_db

# Configuration API
API_SECRET_KEY=votre_clé_secrète
API_DEBUG=false
```

### Configuration des modèles

Le fichier `config/config.yaml` permet de configurer les modèles :

```yaml
models:
  lstm:
    layers: [64, 32, 16]
    dropout: 0.2
    learning_rate: 0.001
    batch_size: 32
    epochs: 100
    
  transformer:
    n_heads: 8
    n_layers: 6
    d_model: 512
    dropout: 0.1
```

## Configuration avancée

### Optimisation du portefeuille

```yaml
portfolio:
  rebalancing:
    frequency: "1d"  # Fréquence de rééquilibrage
    threshold: 0.05  # Seuil de déclenchement
  
  risk_management:
    max_position_size: 0.2  # Taille maximale d'une position
    stop_loss: 0.1         # Stop loss automatique
    take_profit: 0.2       # Take profit automatique
```

### Sources de données

```yaml
data:
  sources:
    - name: "yahoo_finance"
      enabled: true
      update_frequency: "1h"
      assets: ["BTC-USD", "ETH-USD", "SPY", "QQQ"]
    
    - name: "alpha_vantage"
      enabled: true
      update_frequency: "1d"
```

## Personnalisation

### Ajout de nouvelles sources de données

Pour ajouter une nouvelle source de données :

1. Créez un nouveau fichier dans `src/data/sources/`
2. Implémentez l'interface `DataSource`
3. Ajoutez la configuration dans `config.yaml`

### Modification des modèles

Pour modifier les paramètres des modèles :

1. Éditez `config.yaml`
2. Ajustez les hyperparamètres selon vos besoins
3. Relancez l'entraînement

## Sécurité

### Bonnes pratiques

- Ne commitez jamais le fichier `.env`
- Utilisez des secrets sécurisés pour l'API
- Limitez l'accès à la base de données

### Monitoring

Configuration de la surveillance :

```yaml
monitoring:
  enabled: true
  metrics:
    - "model_accuracy"
    - "portfolio_performance"
  alert_threshold:
    accuracy_drop: 0.1
    performance_drop: 0.05
```

## Prochaines étapes

- [Guide d'utilisation](usage.md)
- [Architecture](../dev-guide/architecture.md) 