# Module d'Analyse Technique et Fondamentale

## Vue d'ensemble

Ce module fournit des outils avancés pour l'analyse des marchés financiers.

## Composants

### 📊 Indicateurs Techniques (`technical/`)
- `momentum.py` : Indicateurs de momentum
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Stochastique
  - ADX (Average Directional Index)

- `volatility.py` : Indicateurs de volatilité
  - Bollinger Bands
  - ATR (Average True Range)
  - Keltner Channels
  - Volatilité historique

- `volume.py` : Indicateurs de volume
  - OBV (On-Balance Volume)
  - Volume Profile
  - Money Flow Index
  - Accumulation/Distribution

### 🔍 Analyse Fondamentale (`fundamental/`)
- `metrics.py` : Métriques fondamentales
  - Market Cap
  - Volume 24h
  - Dominance
  - TVL (Total Value Locked)

- `on_chain.py` : Métriques blockchain
  - Transactions
  - Addresses actives
  - Hash rate
  - Gas fees

### 🎯 Sentiment (`sentiment/`)
- `social.py` : Analyse des réseaux sociaux
  - Twitter sentiment
  - Reddit activity
  - Social volume
  - Influencer tracking

- `news.py` : Analyse des actualités
  - News sentiment
  - Event detection
  - Impact analysis

## Utilisation

### Indicateurs Techniques
```python
from sadie.analysis.technical import MomentumIndicators, VolatilityIndicators

# Configuration
momentum = MomentumIndicators(
    rsi_period=14,
    macd_fast=12,
    macd_slow=26
)

# Calcul des indicateurs
indicators = await momentum.calculate(
    price_data=market_data,
    volume_data=volume_data
)

# Signaux de trading
signals = momentum.generate_signals(
    indicators=indicators,
    thresholds={
        'rsi_oversold': 30,
        'rsi_overbought': 70
    }
)
```

### Analyse de Sentiment
```python
from sadie.analysis.sentiment import SocialAnalyzer

# Configuration
analyzer = SocialAnalyzer(
    twitter_api_key=config.TWITTER_API_KEY,
    reddit_api_key=config.REDDIT_API_KEY
)

# Analyse
sentiment = await analyzer.analyze(
    symbol="BTC",
    timeframe="1h",
    sources=['twitter', 'reddit']
)
```

## Configuration

### Paramètres des indicateurs
```python
INDICATOR_PARAMS = {
    'rsi': {
        'period': 14,
        'overbought': 70,
        'oversold': 30
    },
    'macd': {
        'fast': 12,
        'slow': 26,
        'signal': 9
    },
    'bollinger': {
        'period': 20,
        'std_dev': 2
    }
}
```

### Paramètres de sentiment
```python
SENTIMENT_PARAMS = {
    'twitter': {
        'min_followers': 1000,
        'lang': ['en', 'fr'],
        'max_age': '1h'
    },
    'reddit': {
        'subreddits': ['cryptocurrency', 'bitcoin'],
        'min_score': 10
    }
}
```

## Signaux de Trading

### Génération de signaux
```python
class SignalGenerator:
    def __init__(self):
        self.indicators = IndicatorSet()
        self.sentiment = SentimentAnalyzer()
    
    async def generate_signals(self, market_data):
        technical_signals = await self.indicators.analyze(market_data)
        sentiment_signals = await self.sentiment.analyze(market_data)
        
        return self.combine_signals(technical_signals, sentiment_signals)
```

### Types de signaux
- STRONG_BUY
- BUY
- NEUTRAL
- SELL
- STRONG_SELL

## Tests

```bash
# Tests des indicateurs techniques
pytest tests/analysis/test_technical.py

# Tests de l'analyse fondamentale
pytest tests/analysis/test_fundamental.py

# Tests de l'analyse de sentiment
pytest tests/analysis/test_sentiment.py
```

## Performance

### Optimisation
- Calculs vectorisés avec NumPy
- Cache des résultats intermédiaires
- Parallélisation des calculs lourds

### Métriques
- Temps de calcul < 100ms par indicateur
- Précision sentiment > 80%
- Latence API < 200ms
``` 