"""Exemple d'utilisation de l'analyseur de patterns harmoniques."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import platform
from plotly.subplots import make_subplots

from SADIE.analysis.harmonic_patterns import HarmonicAnalyzer, PatternType
from SADIE.core.collectors.trade_collector import TradeCollector
from SADIE.core.models.events import Exchange, Symbol, Timeframe

async def get_market_data(exchange: str = "binance", symbol: str = "BTC/USDT", timeframe: str = "1h", limit: int = 1000) -> pd.DataFrame:
    """Récupère les données historiques du marché."""
    collector = TradeCollector()
    await collector.connect()
    
    data = await collector.get_historical_data(
        exchange=Exchange(exchange),
        symbol=Symbol(symbol),
        timeframe=Timeframe(timeframe),
        limit=limit
    )
    
    await collector.disconnect()
    
    # Vérification et préparation des données
    print("\nStructure des données reçues:")
    print(f"Type: {type(data)}")
    print(f"Colonnes: {data.columns.tolist()}")
    print(f"Index: {type(data.index)}")
    print(f"Nombre de lignes: {len(data)}")
    print("\nPremières lignes:")
    print(data.head())
    
    # S'assurer que l'index est en datetime
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
    
    # Conversion des colonnes en float
    numeric_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in numeric_columns:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')
    
    # Suppression des lignes avec des valeurs manquantes
    data = data.dropna()
    
    # Tri par ordre chronologique
    data = data.sort_index()
    
    return data

def plot_harmonic_patterns(data: pd.DataFrame, analyzer: HarmonicAnalyzer) -> None:
    """Crée une visualisation interactive des patterns harmoniques."""
    # Identification des patterns avec un seuil plus bas
    patterns = analyzer.identify_patterns(min_swing=0.005)
    
    # Création des sous-graphiques
    fig = make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.1, 0.1, 0.15, 0.15],
        subplot_titles=(
            'Prix et Patterns Harmoniques',
            'Volume et Moyenne Mobile (20)',
            'Bandes de Bollinger %B',
            'MACD (12,26,9)',
            'Stochastique (14,3,3)'
        )
    )
    
    # Bougies japonaises avec tooltips personnalisés
    candlestick = go.Candlestick(
        x=data.index,
        open=data['open'],
        high=data['high'],
        low=data['low'],
        close=data['close'],
        name='BTCUSDT',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350',
        increasing_fillcolor='#26a69a',
        decreasing_fillcolor='#ef5350',
        hovertemplate="<br>".join([
            "<b>Date</b>: %{x}",
            "<b>Open</b>: %{open:,.2f}",
            "<b>High</b>: %{high:,.2f}",
            "<b>Low</b>: %{low:,.2f}",
            "<b>Close</b>: %{close:,.2f}",
            "<extra></extra>"
        ])
    )
    fig.add_trace(candlestick, row=1, col=1)
    
    # Bandes de Bollinger avec tooltips améliorés
    window = 20
    std_dev = 2
    rolling_mean = data['close'].rolling(window=window).mean()
    rolling_std = data['close'].rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * std_dev)
    lower_band = rolling_mean - (rolling_std * std_dev)
    
    for band, name, color in [
        (upper_band, 'BB Upper', 'rgba(255, 255, 255, 0.5)'),
        (rolling_mean, 'BB Middle', 'rgba(255, 255, 255, 0.7)'),
        (lower_band, 'BB Lower', 'rgba(255, 255, 255, 0.5)')
    ]:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=band,
                name=name,
                line=dict(
                    color=color,
                    dash='dash' if name != 'BB Middle' else 'solid',
                    width=1
                ),
                hovertemplate=f"<b>{name}</b>: %{{y:,.2f}}<extra></extra>",
                showlegend=True
            ),
            row=1, col=1
        )
    
    # Volume avec moyenne mobile et tooltips améliorés
    volume_ma = data['volume'].rolling(window=20).mean()
    colors = ['#ef5350' if close < open else '#26a69a'
              for close, open in zip(data['close'], data['open'])]
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.8,
            hovertemplate="<b>Volume</b>: %{y:,.2f}<extra></extra>"
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=volume_ma,
            name='Volume MA(20)',
            line=dict(color='rgba(255, 255, 255, 0.7)', width=1.5),
            hovertemplate="<b>Volume MA(20)</b>: %{y:,.2f}<extra></extra>",
            showlegend=True
        ),
        row=2, col=1
    )
    
    # Bandes de Bollinger %B avec tooltips améliorés
    bb_b = (data['close'] - lower_band) / (upper_band - lower_band)
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=bb_b,
            name='BB %B',
            line=dict(color='#FFD700', width=1.5),
            hovertemplate="<b>BB %B</b>: %{y:.2%}<extra></extra>"
        ),
        row=3, col=1
    )
    
    # Lignes de référence BB %B avec labels et zones colorées
    for level, color, text in [
        (1, 'rgba(255,0,0,0.1)', 'Surachat'),
        (0.5, 'rgba(255,255,255,0.1)', 'Neutre'),
        (0, 'rgba(0,255,0,0.1)', 'Survente')
    ]:
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color=color.replace('0.1', '0.5'),
            opacity=0.5,
            row=3,
            col=1,
            annotation_text=f"{text} ({level})",
            annotation_position="left"
        )
        # Ajout des zones colorées
        if level in [0, 1]:
            fig.add_hrect(
                y0=level,
                y1=0.5,
                fillcolor=color,
                line_width=0,
                row=3,
                col=1
            )
    
    # MACD avec tooltips améliorés
    exp1 = data['close'].ewm(span=12, adjust=False).mean()
    exp2 = data['close'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=macd,
            name='MACD',
            line=dict(color='#00FF00', width=1.5),
            hovertemplate="<b>MACD</b>: %{y:.2f}<extra></extra>"
        ),
        row=4, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=signal,
            name='Signal',
            line=dict(color='#FF0000', width=1.5),
            hovertemplate="<b>Signal</b>: %{y:.2f}<extra></extra>"
        ),
        row=4, col=1
    )
    
    # Histogramme MACD avec divergences
    colors = []
    for i in range(len(histogram)):
        if i > 0:
            # Divergence haussière
            if histogram[i] > histogram[i-1] and data['close'].iloc[i] < data['close'].iloc[i-1]:
                colors.append('#00FF00')  # Vert vif
            # Divergence baissière
            elif histogram[i] < histogram[i-1] and data['close'].iloc[i] > data['close'].iloc[i-1]:
                colors.append('#FF0000')  # Rouge vif
            else:
                colors.append('#26a69a' if histogram[i] >= 0 else '#ef5350')
        else:
            colors.append('#26a69a' if histogram[i] >= 0 else '#ef5350')
    
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=histogram,
            name='MACD Histogram',
            marker_color=colors,
            opacity=0.8,
            hovertemplate="<b>Histogram</b>: %{y:.2f}<extra></extra>"
        ),
        row=4, col=1
    )
    
    # Stochastique avec tooltips améliorés
    period = 14
    k_period = 3
    d_period = 3
    
    low_min = data['low'].rolling(window=period).min()
    high_max = data['high'].rolling(window=period).max()
    
    k = 100 * ((data['close'] - low_min) / (high_max - low_min))
    k = k.rolling(window=k_period).mean()
    d = k.rolling(window=d_period).mean()
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=k,
            name='%K',
            line=dict(color='#00FF00', width=1.5),
            hovertemplate="<b>%K</b>: %{y:.2f}%<extra></extra>"
        ),
        row=5, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=d,
            name='%D',
            line=dict(color='#FF0000', width=1.5),
            hovertemplate="<b>%D</b>: %{y:.2f}%<extra></extra>"
        ),
        row=5, col=1
    )
    
    # Zones de surachat/survente pour le Stochastique
    for level, color, text in [
        (80, 'rgba(255,0,0,0.1)', 'Surachat'),
        (20, 'rgba(0,255,0,0.1)', 'Survente')
    ]:
        fig.add_hline(
            y=level,
            line_dash="dash",
            line_color=color.replace('0.1', '0.5'),
            opacity=0.5,
            row=5,
            col=1,
            annotation_text=text,
            annotation_position="left"
        )
        # Ajout des zones colorées
        if level == 80:
            fig.add_hrect(
                y0=level,
                y1=100,
                fillcolor=color,
                line_width=0,
                row=5,
                col=1
            )
        else:
            fig.add_hrect(
                y0=0,
                y1=level,
                fillcolor=color,
                line_width=0,
                row=5,
                col=1
            )
    
    # Couleurs pour les différents types de patterns
    colors = {
        PatternType.GARTLEY: 'rgba(255, 165, 0, 0.8)',  # Orange
        PatternType.BUTTERFLY: 'rgba(144, 238, 144, 0.8)',  # Vert clair
        PatternType.BAT: 'rgba(255, 99, 71, 0.8)',  # Rouge-orange
        PatternType.CRAB: 'rgba(135, 206, 235, 0.8)',  # Bleu ciel
        PatternType.SHARK: 'rgba(218, 112, 214, 0.8)',  # Orchidée
        PatternType.CYPHER: 'rgba(240, 230, 140, 0.8)'  # Kaki clair
    }
    
    # Ajout des patterns avec tooltips améliorés
    for pattern in patterns:
        x_points = [p[0] for p in pattern.points]
        y_points = [p[1] for p in pattern.points]
        
        # Création du tooltip personnalisé
        hover_text = [
            f"<b>Point {point}</b><br>" +
            f"Date: {x.strftime('%Y-%m-%d %H:%M')}<br>" +
            f"Prix: {y:.2f}"
            for point, x, y in zip(['X', 'A', 'B', 'C', 'D'], x_points, y_points)
        ]
        
        fig.add_trace(
            go.Scatter(
                x=x_points,
                y=y_points,
                mode='lines+markers+text',
                name=f'{pattern.pattern_type.value} ({pattern.trend})',
                text=['X', 'A', 'B', 'C', 'D'],
                textposition='top center',
                line=dict(
                    color=colors[pattern.pattern_type],
                    width=2
                ),
                marker=dict(
                    size=8,
                    symbol='circle'
                ),
                hovertext=hover_text,
                hoverinfo='text'
            ),
            row=1, col=1
        )
        
        # Zone de renversement potentielle (PRZ) avec tooltip amélioré
        prz_hover = (
            f"<b>Zone de Renversement Potentielle</b><br>" +
            f"Pattern: {pattern.pattern_type.value}<br>" +
            f"Confiance: {pattern.confidence:.1%}<br>" +
            f"Min: {pattern.potential_reversal_zone[0]:.2f}<br>" +
            f"Max: {pattern.potential_reversal_zone[1]:.2f}"
        )
        
        fig.add_trace(
            go.Scatter(
                x=[pattern.end_date, pattern.end_date],
                y=[pattern.potential_reversal_zone[0],
                   pattern.potential_reversal_zone[1]],
                mode='lines+text',
                name=f'PRZ ({pattern.confidence:.1%})',
                text=['PRZ Min', 'PRZ Max'],
                textposition=['bottom center', 'top center'],
                line=dict(
                    color=colors[pattern.pattern_type],
                    width=2,
                    dash='dash'
                ),
                hovertext=prz_hover,
                hoverinfo='text',
                showlegend=False
            ),
            row=1, col=1
        )
        
        # Annotation des ratios avec style amélioré
        ratio_points = ['X', 'A', 'B', 'C', 'D']
        for ratio_name, ratio_value in pattern.ratios.items():
            if '/' in ratio_name:
                points = ratio_name.split('/')
                start_idx = ratio_points.index(points[0][0])
                end_idx = ratio_points.index(points[1][0])
                
                x_pos = x_points[end_idx]
                y_pos = y_points[end_idx]
                
                fig.add_annotation(
                    x=x_pos,
                    y=y_pos,
                    text=f'{ratio_name}: {ratio_value:.3f}',
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    ax=0,
                    ay=30 if end_idx % 2 == 0 else -30,
                    font=dict(size=10, color='white', family='Arial Black'),
                    bgcolor=colors[pattern.pattern_type],
                    bordercolor='white',
                    borderwidth=2,
                    borderpad=4,
                    row=1, col=1
                )
    
    # Mise en forme globale
    fig.update_layout(
        title=dict(
            text=f'Patterns Harmoniques Détectés - {data.index[0].date()} à {data.index[-1].date()}',
            font=dict(size=24, family='Arial Black'),
            y=0.95
        ),
        height=1200,
        plot_bgcolor='rgb(19, 23, 34)',
        paper_bgcolor='rgb(19, 23, 34)',
        font=dict(
            color='white',
            size=12,
            family='Arial'
        ),
        showlegend=True,
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            font=dict(color='white'),
            bordercolor='rgba(255, 255, 255, 0.3)',
            borderwidth=1,
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        ),
        margin=dict(t=100, l=50, r=50, b=30),
        hovermode='x unified'
    )
    
    # Mise à jour des axes
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 255, 255, 0.1)',
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor='rgba(255, 255, 255, 0.3)',
        title_font=dict(size=12)
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(255, 255, 255, 0.1)',
        zeroline=False,
        showline=True,
        linewidth=1,
        linecolor='rgba(255, 255, 255, 0.3)',
        title_font=dict(size=12)
    )
    
    # Affichage
    fig.show()

async def main():
    """Point d'entrée principal."""
    try:
        # Récupération des données réelles
        print("Récupération des données du marché...")
        data = await get_market_data(
            exchange="binance",
            symbol="BTC/USDT",
            timeframe="1h",
            limit=1000
        )
        
        print(f"\nAnalyse des données du {data.index[0].date()} au {data.index[-1].date()}")
        
        # Initialisation de l'analyseur
        analyzer = HarmonicAnalyzer(data, tolerance=0.15)
        
        # Identification des patterns
        patterns = analyzer.identify_patterns(min_swing=0.005)
        
        # Tri des patterns par confiance
        patterns.sort(key=lambda x: x.confidence, reverse=True)
        
        print("\n" + "="*50)
        print(f"🔍 {len(patterns)} patterns harmoniques identifiés")
        print("="*50)
        
        for i, pattern in enumerate(patterns, 1):
            print(f"\n📊 Pattern {i} - {pattern.pattern_type.value}")
            print("  " + "-"*40)
            print(f"  📈 Tendance: {pattern.trend}")
            print(f"  📅 Période: {pattern.start_date.date()} - {pattern.end_date.date()}")
            print(f"  ✨ Confiance: {pattern.confidence:.2%}")
            print("  📐 Ratios:")
            for name, value in pattern.ratios.items():
                if '/' in name:
                    print(f"    • {name}: {value:.3f}")
            print("  🎯 Zone de renversement potentielle:")
            print(f"    • Min: {pattern.potential_reversal_zone[0]:.2f}")
            print(f"    • Max: {pattern.potential_reversal_zone[1]:.2f}")
            print("  " + "-"*40)
        
        # Visualisation
        plot_harmonic_patterns(data, analyzer)
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if platform.system() == "Windows":
        # Configuration spécifique pour Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main()) 