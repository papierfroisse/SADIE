# Work In Progress

## Tâches en cours 🔄

### Enrichissement des Données
- [ ] Intégration des sources de marché
  - [ ] Order books L2/L3
  - [ ] Données tick par tick
  - [ ] Carnets d'ordres complets
- [ ] Sources alternatives
  - [ ] API Twitter (sentiment)
  - [ ] API Reddit (analyse communautaire)
  - [ ] Flux d'actualités temps réel
  - [ ] Données institutionnelles
- [ ] Données blockchain
  - [ ] Connexion nodes ETH/BTC
  - [ ] Métriques DeFi
  - [ ] Analyse on-chain

### Prétraitement Ultra-Avancé
- [ ] Système de correction des biais
  - [ ] Détecteur d'événements exceptionnels
  - [ ] Analyseur de contexte
  - [ ] Correcteur d'outliers intelligent
- [ ] Pipeline GAN
  - [ ] Architecture génératrice
  - [ ] Discriminateur spécialisé
  - [ ] Générateur de scénarios
- [ ] Système d'annotation
  - [ ] Classifieur de régimes
  - [ ] Détecteur de patterns
  - [ ] Marqueur d'événements

### Infrastructure Data
- [x] TimescaleDB setup
- [x] Migration asyncpg
- [ ] Optimisation stockage
  - [ ] Compression intelligente
  - [ ] Partitionnement adaptatif
  - [ ] Cache prédictif

## Prochaines tâches prioritaires 📋

### Pour la version 0.2.0
1. Pipeline de données ultra-enrichi
   - [ ] Intégration multi-source
   - [ ] Synchronisation temporelle
   - [ ] Validation croisée des sources
   - [ ] Tests de cohérence

2. Prétraitement nouvelle génération
   - [ ] Setup GAN
     - [ ] Architecture de base
     - [ ] Tests initiaux
     - [ ] Validation des données générées
   - [ ] Système d'annotation
     - [ ] Règles de base
     - [ ] Apprentissage supervisé
     - [ ] Validation humaine

3. Infrastructure scalable
   - [ ] Optimisation stockage
   - [ ] Distribution des calculs
   - [ ] Monitoring avancé

### Pour la version 0.3.0
1. Architecture LSTM avancée
   - [ ] LSTM spécialisés
     - [ ] Module tendances
     - [ ] Module volatilité
     - [ ] Module volumes
   - [ ] Optimisation bayésienne
     - [ ] Framework de base
     - [ ] Tests initiaux
     - [ ] Validation des résultats

2. Modèles hybrides
   - [ ] LSTM + Attention
     - [ ] Self-attention
     - [ ] Cross-attention
     - [ ] Attention temporelle
   - [ ] LSTM + GAN
     - [ ] Architecture de base
     - [ ] Tests de génération
     - [ ] Validation adversariale

## Notes techniques 📝

### Architecture LSTM Avancée
- Modules spécialisés:
  ```python
  class TrendLSTM:
    - input_size: historical_data + indicators
    - lstm_layers: [128, 64, 32]
    - attention_mechanism: self_attention
    - output: trend_prediction

  class VolatilityLSTM:
    - input_size: price_changes + volumes
    - lstm_layers: [64, 32, 16]
    - attention_mechanism: temporal_attention
    - output: volatility_forecast

  class VolumeLSTM:
    - input_size: volume_profile + order_book
    - lstm_layers: [96, 48, 24]
    - attention_mechanism: cross_attention
    - output: volume_prediction
  ```

### Prétraitement GAN
- Architecture:
  ```python
  class MarketGAN:
    - generator:
      - input: noise + market_conditions
      - layers: [256, 512, 256, 128]
      - output: synthetic_data
    
    - discriminator:
      - input: real_or_synthetic_data
      - layers: [128, 256, 128, 1]
      - output: authenticity_score
  ```

### Infrastructure
- TimescaleDB:
  - Compression: après 7 jours
  - Rétention: 5 ans
  - Chunks: adaptatifs selon volatilité
- Cache:
  - L1: mémoire (1h)
  - L2: Redis (24h)
  - L3: disque (7j) 