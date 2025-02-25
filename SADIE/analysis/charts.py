import pandas as pd
import numpy as np
from typing import Dict, Any, List

def create_candlestick_chart(trades: pd.DataFrame) -> Dict[str, Any]:
    """Crée un graphique en chandeliers avec Plotly.
    
    Args:
        trades: DataFrame avec les trades
        
    Returns:
        Dictionnaire avec les données et le layout du graphique
    """
    # Conversion en bougies
    ohlcv = trades.resample('1min').agg({
        'price': ['first', 'max', 'min', 'last'],
        'quantity': 'sum'
    })
    ohlcv.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Création des données pour le graphique en chandeliers
    candlestick = {
        'x': ohlcv.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'open': ohlcv['open'].tolist(),
        'high': ohlcv['high'].tolist(),
        'low': ohlcv['low'].tolist(),
        'close': ohlcv['close'].tolist(),
        'type': 'candlestick',
        'name': 'OHLC',
        'showlegend': False
    }
    
    # Création du graphique de volume
    colors = ['red' if close < open else 'green' 
              for close, open in zip(ohlcv['close'], ohlcv['open'])]
    
    volume = {
        'x': ohlcv.index.strftime('%Y-%m-%d %H:%M:%S').tolist(),
        'y': ohlcv['volume'].tolist(),
        'type': 'bar',
        'name': 'Volume',
        'marker': {
            'color': colors,
            'opacity': 0.5
        },
        'yaxis': 'y2',
        'showlegend': False
    }
    
    # Configuration du layout
    layout = {
        'title': {
            'text': 'Analyse Technique',
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'title': 'Date/Heure',
            'rangeslider': {'visible': False},
            'type': 'date'
        },
        'yaxis': {
            'title': 'Prix',
            'domain': [0.3, 1.0]
        },
        'yaxis2': {
            'title': 'Volume',
            'domain': [0, 0.2],
            'showticklabels': True
        },
        'plot_bgcolor': '#1a1a1a',
        'paper_bgcolor': '#2d2d2d',
        'font': {
            'color': '#ffffff'
        },
        'margin': {
            'l': 50,
            'r': 50,
            'b': 50,
            't': 50,
            'pad': 4
        },
        'showlegend': False,
        'dragmode': 'zoom',
        'hovermode': 'x unified'
    }
    
    return {
        'data': [candlestick, volume],
        'layout': layout
    }

def add_indicators_to_chart(chart: Dict[str, Any], indicators: Dict[str, Any]) -> Dict[str, Any]:
    """Ajoute les indicateurs techniques au graphique.
    
    Args:
        chart: Graphique de base
        indicators: Dictionnaire des indicateurs
        
    Returns:
        Graphique mis à jour
    """
    data = chart['data']
    
    # Ajout du RSI
    data.append({
        'x': chart['data'][0]['x'],
        'y': [indicators['rsi']] * len(chart['data'][0]['x']),
        'type': 'scatter',
        'name': 'RSI',
        'line': {'color': '#9C27B0'},
        'yaxis': 'y3'
    })
    
    # Ajout du MACD
    data.append({
        'x': chart['data'][0]['x'],
        'y': [indicators['macd']['macd']] * len(chart['data'][0]['x']),
        'type': 'scatter',
        'name': 'MACD',
        'line': {'color': '#2196F3'},
        'yaxis': 'y4'
    })
    
    # Ajout des bandes de Bollinger
    bb = indicators['bollinger_bands']
    for name, values, color in [
        ('BB Upper', [bb['upper']] * len(chart['data'][0]['x']), '#4CAF50'),
        ('BB Middle', [bb['middle']] * len(chart['data'][0]['x']), '#FFC107'),
        ('BB Lower', [bb['lower']] * len(chart['data'][0]['x']), '#F44336')
    ]:
        data.append({
            'x': chart['data'][0]['x'],
            'y': values,
            'type': 'scatter',
            'name': name,
            'line': {
                'color': color,
                'dash': 'dash'
            }
        })
    
    # Mise à jour du layout
    chart['layout'].update({
        'yaxis3': {
            'title': 'RSI',
            'domain': [0.7, 0.85],
            'showticklabels': True
        },
        'yaxis4': {
            'title': 'MACD',
            'domain': [0.5, 0.65],
            'showticklabels': True
        }
    })
    
    return chart

def add_patterns_to_chart(chart: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ajoute les motifs harmoniques au graphique.
    
    Args:
        chart: Graphique de base
        patterns: Liste des motifs détectés
        
    Returns:
        Graphique mis à jour
    """
    data = chart['data']
    
    for pattern in patterns:
        # Extraction des points du motif
        x = [chart['data'][0]['x'][p[0]] for p in pattern['points']]
        y = [p[1] for p in pattern['points']]
        
        # Ajout des lignes du motif
        data.append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': pattern['type'],
            'line': {
                'color': '#E91E63' if pattern['trend'] == 'Bearish' else '#4CAF50',
                'width': 2
            },
            'marker': {
                'size': 8,
                'symbol': 'diamond'
            }
        })
        
        # Ajout de la zone de retournement
        data.append({
            'x': [x[-1], x[-1]],
            'y': [y[-1], pattern['reversal_zone']],
            'type': 'scatter',
            'mode': 'lines',
            'name': f"{pattern['type']} Target",
            'line': {
                'color': '#E91E63' if pattern['trend'] == 'Bearish' else '#4CAF50',
                'dash': 'dot',
                'width': 1
            },
            'showlegend': False
        })
    
    return chart 