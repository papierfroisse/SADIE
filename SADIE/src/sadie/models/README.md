# Module des Modèles Prédictifs

## Vue d'ensemble

Ce module contient les modèles d'apprentissage profond et d'optimisation pour SADIE.

## Architecture

### 🧠 Modèles LSTM (`lstm/`)
- `trend.py` : LSTM spécialisé pour les tendances
  ```python
  class TrendLSTM:
      - input_size: historical_data + indicators
      - lstm_layers: [128, 64, 32]
      - attention_mechanism: self_attention
      - output: trend_prediction
  ```
- `volatility.py` : LSTM pour la volatilité
  ```python
  class VolatilityLSTM:
      - input_size: price_changes + volumes
      - lstm_layers: [64, 32, 16]
      - attention_mechanism: temporal_attention
      - output: volatility_forecast
  ```
- `volume.py` : LSTM pour les volumes
  ```python
  class VolumeLSTM:
      - input_size: volume_profile + order_book
      - lstm_layers: [96, 48, 24]
      - attention_mechanism: cross_attention
      - output: volume_prediction
  ```

### 🎯 Attention (`attention/`)
- `self_attention.py` : Mécanisme d'auto-attention
- `cross_attention.py` : Attention croisée
- `temporal_attention.py` : Attention temporelle

### 🎮 GAN (`gan/`)
- `generator.py` : Générateur de scénarios
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
- `discriminator.py` : Validation des scénarios
- `trainer.py` : Entraînement adversarial

### 💼 Portfolio (`portfolio/`)
- `optimizer.py` : Optimisation de portefeuille
- `risk.py` : Gestion des risques
- `rebalancer.py` : Rebalancement dynamique

## Utilisation

### LSTM
```python
from sadie.models import TrendLSTM, VolatilityLSTM

# Configuration des modèles
trend_model = TrendLSTM(
    input_size=64,
    hidden_size=128,
    num_layers=3
)

# Entraînement
await trend_model.train(
    train_data=train_dataset,
    epochs=100,
    batch_size=32
)

# Prédiction
predictions = await trend_model.predict(market_data)
```

### GAN
```python
from sadie.models import MarketGAN

# Configuration du GAN
gan = MarketGAN(
    latent_dim=100,
    condition_dim=20
)

# Entraînement
await gan.train(
    real_data=historical_data,
    epochs=500,
    batch_size=64
)

# Génération de scénarios
scenarios = await gan.generate(
    num_scenarios=100,
    market_conditions=current_conditions
)
```

## Hyperparamètres

### LSTM
- Learning rate: 0.001
- Dropout: 0.2
- Batch normalization: True
- Early stopping patience: 10

### GAN
- Generator learning rate: 0.0002
- Discriminator learning rate: 0.0001
- Gradient penalty weight: 10
- Training ratio: 5

## Métriques d'évaluation

### Prédiction
- MSE (Mean Squared Error)
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score

### Portfolio
- Ratio Sharpe
- Ratio Sortino
- Maximum Drawdown
- Value at Risk (VaR)

## Tests

```bash
# Tests des modèles LSTM
pytest tests/models/test_lstm.py

# Tests des GANs
pytest tests/models/test_gan.py

# Tests d'optimisation
pytest tests/models/test_portfolio.py
```

## Performance

- Support GPU (CUDA)
- Batch processing
- Inférence optimisée
- Quantization pour production 