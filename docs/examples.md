# Exemples d'Utilisation

## Analyse Technique

### Calcul d'Indicateurs
```python
import pandas as pd
from sadie.analysis.indicators import TechnicalIndicators

# Chargement des données
data = pd.read_csv("data.csv")
data.set_index("timestamp", inplace=True)

# Initialisation
indicators = TechnicalIndicators(data)

# Calcul des indicateurs
bb_mid, bb_up, bb_low, bb_b = indicators.bollinger_bands()
macd, signal, hist = indicators.macd()
k, d = indicators.stochastic()
rsi = indicators.rsi()

# Détection des divergences
divergences = indicators.detect_divergences(rsi)
for div in divergences:
    print(f"Divergence {div['type']} trouvée le {div['date']}")
    print(f"Force: {div['strength']:.2f}")
```

### Détection de Patterns Harmoniques
```python
from sadie.analysis.harmonic_patterns import HarmonicAnalyzer

# Initialisation
analyzer = HarmonicAnalyzer(data)

# Détection avec paramètres personnalisés
patterns = analyzer.identify_patterns(
    min_swing=0.02,      # 2% minimum pour les swings
    min_confidence=0.80  # 80% de confiance minimum
)

# Analyse des résultats
for pattern in patterns:
    print(f"\nPattern {pattern.pattern_type.value} détecté:")
    print(f"- Tendance: {pattern.trend.value}")
    print(f"- Confiance: {pattern.confidence:.1%}")
    print(f"- Points:")
    for date, price in pattern.points:
        print(f"  {date}: {price:.2f}")
    print(f"- Zone de retournement: {pattern.potential_reversal_zone[0]:.2f} - {pattern.potential_reversal_zone[1]:.2f}")
```

### Visualisation Interactive
```python
from sadie.analysis.visualization import ChartVisualizer

# Création du graphique
visualizer = ChartVisualizer(
    data=data,
    indicators=indicators,  # Réutilisation des indicateurs calculés
    analyzer=analyzer      # Réutilisation de l'analyseur
)

# Personnalisation des couleurs
visualizer.colors.update({
    'up': '#00ff00',      # Vert pour les hausses
    'down': '#ff0000',    # Rouge pour les baisses
    'volume': '#2196f3',  # Bleu pour le volume
    'bb_middle': '#9b59b6',  # Violet pour les BB
    'macd_fast': '#2196f3',  # Bleu pour le MACD
    'macd_slow': '#f44336'   # Rouge pour le signal
})

# Création du graphique complet
fig = visualizer.create_chart(
    show_volume=True,
    show_bb=True,
    show_macd=True,
    show_stoch=True,
    show_patterns=True
)

# Sauvegarde au format HTML interactif
fig.write_html("analysis.html")
```

## Collecte et Analyse en Temps Réel

### Configuration
```python
import asyncio
from datetime import datetime, timedelta
from sadie.data.collectors.binance import BinanceTradeCollector
from sadie.storage.redis import RedisStorage
from sadie.analysis.indicators import TechnicalIndicators
from sadie.analysis.visualization import ChartVisualizer

async def analyze_market():
    # Configuration
    symbol = "BTCUSDT"
    interval = "1h"
    lookback = 100
    
    # Initialisation du collecteur
    collector = BinanceTradeCollector(
        name="binance",
        symbols=[symbol],
        update_interval=60
    )
    
    # Connexion au stockage
    storage = RedisStorage(
        host="localhost",
        port=6379,
        db=0
    )
    await storage.connect()
    
    try:
        # Démarrage de la collecte
        await collector.start()
        print(f"Collecte des trades pour {symbol}...")
        await asyncio.sleep(10)
        
        # Récupération et traitement des données
        trades = await storage.get_trades(
            symbol=symbol,
            start_time=datetime.now() - timedelta(hours=lookback),
            end_time=datetime.now()
        )
        
        # Conversion en OHLCV
        df = pd.DataFrame(trades)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        ohlcv = df.resample(interval).agg({
            'price': ['first', 'max', 'min', 'last'],
            'amount': 'sum'
        })
        ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Analyse technique
        indicators = TechnicalIndicators(ohlcv)
        bb_mid, bb_up, bb_low, bb_b = indicators.bollinger_bands()
        macd, signal, hist = indicators.macd()
        k, d = indicators.stochastic()
        
        # Visualisation
        visualizer = ChartVisualizer(ohlcv, indicators)
        fig = visualizer.create_chart()
        fig.write_html("realtime_analysis.html")
        
    finally:
        await collector.stop()
        await storage.disconnect()

if __name__ == "__main__":
    asyncio.run(analyze_market())
```

## Backtesting Simple

### Test d'une Stratégie Basée sur le MACD
```python
import pandas as pd
import numpy as np
from sadie.analysis.indicators import TechnicalIndicators

def backtest_macd_strategy(data: pd.DataFrame) -> pd.DataFrame:
    # Calcul des indicateurs
    indicators = TechnicalIndicators(data)
    macd, signal, hist = indicators.macd()
    
    # Génération des signaux
    signals = pd.DataFrame(index=data.index)
    signals['signal'] = 0
    
    # Signal d'achat : MACD croise le signal à la hausse
    signals.loc[(macd > signal) & (macd.shift(1) <= signal.shift(1)), 'signal'] = 1
    
    # Signal de vente : MACD croise le signal à la baisse
    signals.loc[(macd < signal) & (macd.shift(1) >= signal.shift(1)), 'signal'] = -1
    
    # Calcul des positions
    positions = signals['signal'].cumsum()
    
    # Calcul des rendements
    data['returns'] = np.log(data['close'] / data['close'].shift(1))
    signals['strategy_returns'] = data['returns'] * positions.shift(1)
    
    # Calcul des performances cumulées
    signals['cumulative_returns'] = signals['strategy_returns'].cumsum()
    
    return signals

# Utilisation
data = pd.read_csv("historical_data.csv")
results = backtest_macd_strategy(data)

print(f"Rendement total: {results['cumulative_returns'].iloc[-1]:.2%}")
print(f"Rendement annualisé: {(1 + results['cumulative_returns'].iloc[-1]) ** (252/len(results)) - 1:.2%}")
``` 