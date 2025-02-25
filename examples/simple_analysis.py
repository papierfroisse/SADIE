"""Exemple simple d'analyse technique."""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Création de données de test
dates = pd.date_range(start='2024-01-01', periods=100, freq='h')
data = pd.DataFrame({
    'open': np.random.normal(100, 2, 100),
    'high': np.random.normal(102, 2, 100),
    'low': np.random.normal(98, 2, 100),
    'close': np.random.normal(100, 2, 100),
    'volume': np.random.normal(1000, 100, 100)
}, index=dates)

# Correction des high/low
data['high'] = data[['open', 'close', 'high']].max(axis=1)
data['low'] = data[['open', 'close', 'low']].min(axis=1)

# Calcul des moyennes mobiles
sma_20 = data['close'].rolling(window=20).mean()
sma_50 = data['close'].rolling(window=50).mean()

# Calcul du RSI
delta = data['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))

# Affichage des résultats
print("\nAnalyse technique")
print("-" * 50)

print("\nDerniers prix:")
print(f"Open: {data['open'].iloc[-1]:.2f}")
print(f"High: {data['high'].iloc[-1]:.2f}")
print(f"Low: {data['low'].iloc[-1]:.2f}")
print(f"Close: {data['close'].iloc[-1]:.2f}")

print("\nMoyennes mobiles:")
print(f"SMA 20: {sma_20.iloc[-1]:.2f}")
print(f"SMA 50: {sma_50.iloc[-1]:.2f}")

print("\nRSI:")
print(f"RSI: {rsi.iloc[-1]:.2f}")

# Création du graphique
fig = make_subplots(
    rows=2,
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.7, 0.3]
)

# Graphique des prix
fig.add_trace(
    go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='OHLC'
    ),
    row=1, col=1
)

# Moyennes mobiles
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=sma_20,
        name='SMA 20',
        line=dict(color='orange')
    ),
    row=1, col=1
)

fig.add_trace(
    go.Scatter(
        x=data.index,
        y=sma_50,
        name='SMA 50',
        line=dict(color='blue')
    ),
    row=1, col=1
)

# RSI
fig.add_trace(
    go.Scatter(
        x=data.index,
        y=rsi,
        name='RSI',
        line=dict(color='purple')
    ),
    row=2, col=1
)

# Lignes de survente/surachat du RSI
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

# Mise en forme
fig.update_layout(
    title="Analyse Technique",
    xaxis_title="Date",
    yaxis_title="Prix",
    template="plotly_dark",
    height=800
)

# Sauvegarde du graphique
fig.write_html('analysis.html')
print("\nGraphique sauvegardé dans analysis.html")

# Sauvegarde des données
data.to_csv('data.csv') 