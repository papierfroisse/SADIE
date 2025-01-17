"""Exemple d'utilisation de l'analyseur de figures chartistes."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from SADIE.analysis.chart_patterns import ChartPatternAnalyzer, PatternType, ChartPattern

def create_sample_data(days: int = 365) -> pd.DataFrame:
    """Génère des données de test avec des figures chartistes."""
    # Générer des dates
    dates = pd.date_range(start='2024-01-01', periods=days*24, freq='H')
    
    # Générer une tendance et des cycles
    t = np.linspace(0, days, len(dates))
    trend = 0.1 * t + np.sin(t/30) * 5  # Tendance haussière avec cycle long
    cycle1 = np.sin(t/5) * 2  # Cycle court
    cycle2 = np.sin(t/15) * 3  # Cycle moyen
    noise = np.random.normal(0, 0.5, len(dates))  # Bruit réduit
    
    # Combiner les composantes
    close = 60000 + trend*1000 + cycle1*1000 + cycle2*1000 + noise*1000
    
    # Générer OHLC
    high = close + np.abs(np.random.normal(0, 100, len(dates)))
    low = close - np.abs(np.random.normal(0, 100, len(dates)))
    open = low + (high - low) * np.random.random(len(dates))
    
    # Générer le volume (corrélé avec les mouvements de prix)
    base_volume = np.random.normal(1000, 200, len(dates))
    price_changes = np.diff(close, prepend=close[0])
    volume = base_volume * (1 + np.abs(price_changes/1000))
    
    # Créer le DataFrame
    data = pd.DataFrame({
        'open': open,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    return data

def plot_chart_patterns(data: pd.DataFrame, analyzer: ChartPatternAnalyzer) -> None:
    """Visualise les données et les figures détectées."""
    # Créer les sous-graphiques
    fig = make_subplots(rows=4, cols=1, 
                       shared_xaxes=True,
                       vertical_spacing=0.02,
                       row_heights=[0.55, 0.15, 0.15, 0.15])

    # Graphique des prix
    fig.add_trace(go.Candlestick(x=data.index,
                                open=data['open'],
                                high=data['high'],
                                low=data['low'],
                                close=data['close'],
                                name='OHLC'), row=1, col=1)
    
    # Ajouter les bandes de Bollinger
    bb_upper, bb_middle, bb_lower = analyzer._calculate_bollinger_bands()
    fig.add_trace(go.Scatter(x=data.index, y=bb_upper, 
                            line=dict(color='rgba(173, 204, 255, 0.3)'),
                            name='BB Upper'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=bb_middle,
                            line=dict(color='rgba(173, 204, 255, 0.7)'),
                            name='BB Middle'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=bb_lower,
                            line=dict(color='rgba(173, 204, 255, 0.3)'),
                            name='BB Lower', fill='tonexty'), row=1, col=1)

    # Volume
    colors = ['red' if row['close'] < row['open'] else 'green' 
              for idx, row in data.iterrows()]
    fig.add_trace(go.Bar(x=data.index, y=data['volume'],
                        marker_color=colors,
                        name='Volume'), row=2, col=1)

    # RSI
    rsi = analyzer._calculate_rsi()
    fig.add_trace(go.Scatter(x=data.index, y=rsi,
                            line=dict(color='purple'),
                            name='RSI'), row=3, col=1)
    # Ajouter les niveaux de surachat/survente
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)

    # MACD
    macd_line, signal_line, histogram = analyzer._calculate_macd()
    fig.add_trace(go.Scatter(x=data.index, y=macd_line,
                            line=dict(color='blue'),
                            name='MACD'), row=4, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=signal_line,
                            line=dict(color='orange'),
                            name='Signal'), row=4, col=1)
    colors = ['red' if h < 0 else 'green' for h in histogram]
    fig.add_trace(go.Bar(x=data.index, y=histogram,
                        marker_color=colors,
                        name='Histogram'), row=4, col=1)

    # Détecter et annoter les figures
    patterns = analyzer.detect_all_patterns()
    for pattern in patterns:
        # Ajouter une annotation pour la figure
        fig.add_annotation(
            x=pattern.end_date,
            y=data.loc[pattern.end_date, 'high'],
            text=f"{pattern.pattern_type.name}<br>Conf: {pattern.confidence*100:.1f}%",
            showarrow=True,
            arrowhead=1,
            row=1, col=1
        )
        
        # Ajouter les niveaux de breakout et target
        fig.add_hline(y=pattern.breakout_level, 
                     line_dash="dot",
                     line_color="yellow",
                     row=1, col=1)
        fig.add_hline(y=pattern.target_price,
                     line_dash="dot",
                     line_color="green" if pattern.trend == "bullish" else "red",
                     row=1, col=1)

    # Mise à jour du layout
    fig.update_layout(
        title='Analyse Technique avec Détection de Figures',
        template='plotly_dark',
        showlegend=True,
        height=1200,
        xaxis_rangeslider_visible=False
    )

    # Afficher le graphique
    fig.show()

async def main():
    """Fonction principale."""
    try:
        # Générer les données de test
        data = create_sample_data()
        print(f"Structure des données reçues :\n{data.head()}")
        
        # Créer l'analyseur et détecter les figures
        analyzer = ChartPatternAnalyzer(data)
        
        # Visualiser les résultats
        plot_chart_patterns(data, analyzer)
        
    except Exception as e:
        print(f"Erreur lors de l'analyse : {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 