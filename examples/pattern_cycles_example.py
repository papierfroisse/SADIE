"""Exemple d'utilisation de l'analyseur de patterns de cycles de marché."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from SADIE.analysis.pattern_cycles import CyclePatternAnalyzer

def create_sample_data(days: int = 365) -> pd.DataFrame:
    """Crée des données simulées avec des patterns."""
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days),
        end=datetime.now(),
        freq='D'
    )
    
    # Création d'une tendance
    t = np.linspace(0, 4*np.pi, len(dates))
    trend = 100 + t * 2
    
    # Ajout de cycles
    cycle1 = 10 * np.sin(t)  # Cycle principal
    cycle2 = 5 * np.sin(2*t)  # Cycle secondaire
    cycle3 = 2 * np.sin(4*t)  # Cycle tertiaire
    
    # Ajout de patterns spécifiques
    patterns = np.zeros_like(t)
    # Head & Shoulders
    patterns[50:150] = -5 * np.sin(np.linspace(0, 2*np.pi, 100)) + \
                      2 * np.sin(np.linspace(0, 4*np.pi, 100))
    # ABC
    patterns[200:300] = 8 * np.sin(np.linspace(0, np.pi, 100))
    
    # Combinaison des composantes
    price = trend + cycle1 + cycle2 + cycle3 + patterns
    
    # Ajout de bruit
    noise = np.random.normal(0, 1, len(dates))
    price += noise
    
    # Création du volume avec divergences
    volume = np.random.lognormal(10, 1, len(dates))
    # Ajout de divergences
    volume[100:150] = volume[100:150] * np.linspace(1.5, 0.5, 50)  # Divergence baissière
    volume[250:300] = volume[250:300] * np.linspace(0.5, 1.5, 50)  # Divergence haussière
    
    return pd.DataFrame({
        'close': price,
        'volume': volume
    }, index=dates)

def plot_patterns(data: pd.DataFrame, analyzer: CyclePatternAnalyzer) -> None:
    """Crée une visualisation interactive des patterns."""
    # Identification des patterns et divergences
    patterns = analyzer.identify_patterns()
    divergences = analyzer.detect_divergences()
    
    # Création du graphique avec 3 sous-graphiques
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            'Prix et Patterns',
            'Volume et Divergences',
            'Corrélations entre Cycles'
        ),
        row_heights=[0.5, 0.25, 0.25]
    )
    
    # 1. Prix et patterns
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['close'],
            name='Prix',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    # Marquage des patterns
    colors = {
        'ABC': 'rgba(255, 165, 0, 0.3)',
        'ABCD': 'rgba(144, 238, 144, 0.3)',
        'Head&Shoulders': 'rgba(255, 99, 71, 0.3)'
    }
    
    for pattern in patterns:
        # Zone du pattern
        fig.add_vrect(
            x0=pattern.start_date,
            x1=pattern.end_date,
            fillcolor=colors.get(pattern.pattern_type, 'rgba(128, 128, 128, 0.3)'),
            opacity=0.5,
            layer='below',
            line_width=0,
            row=1, col=1
        )
        
        # Points clés du pattern
        x_points = [p[0] for p in pattern.points]
        y_points = [p[1] for p in pattern.points]
        
        fig.add_trace(
            go.Scatter(
                x=x_points,
                y=y_points,
                mode='markers+lines',
                name=f'Pattern {pattern.pattern_type}',
                line=dict(dash='dot'),
                marker=dict(size=8)
            ),
            row=1, col=1
        )
    
    # 2. Volume et divergences
    fig.add_trace(
        go.Bar(
            x=data.index,
            y=data['volume'],
            name='Volume',
            marker_color='lightgray'
        ),
        row=2, col=1
    )
    
    # Marquage des divergences
    for div in divergences:
        color = 'red' if div['type'] == 'bearish' else 'green'
        
        fig.add_vrect(
            x0=div['start_date'],
            x1=div['end_date'],
            fillcolor=color,
            opacity=0.2,
            layer='below',
            line_width=0,
            row=2, col=1
        )
    
    # 3. Corrélations entre cycles
    correlations = analyzer.analyze_cycle_correlations()
    if not correlations.empty:
        fig.add_trace(
            go.Scatter(
                x=correlations.index,
                y=correlations['correlation'],
                name='Corrélation',
                line=dict(color='purple')
            ),
            row=3, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=correlations.index,
                y=correlations['distance'],
                name='Distance',
                line=dict(color='orange', dash='dash'),
                yaxis='y2'
            ),
            row=3, col=1
        )
    
    # Mise en forme
    fig.update_layout(
        title='Analyse des Patterns de Cycles de Marché',
        height=1200,
        showlegend=True,
        template='plotly_white'
    )
    
    # Affichage
    fig.show()

async def main():
    """Point d'entrée principal."""
    try:
        # Création des données d'exemple
        data = create_sample_data(days=365)
        
        # Initialisation de l'analyseur
        analyzer = CyclePatternAnalyzer(data)
        
        # Identification des patterns
        patterns = analyzer.identify_patterns()
        
        print("\nPatterns identifiés:")
        for i, pattern in enumerate(patterns, 1):
            print(f"\nPattern {i}:")
            print(f"  Type: {pattern.pattern_type}")
            print(f"  Période: {pattern.start_date.date()} - {pattern.end_date.date()}")
            print(f"  Confiance: {pattern.confidence:.2%}")
            print(f"  Description: {pattern.description}")
        
        # Détection des divergences
        divergences = analyzer.detect_divergences()
        
        print("\nDivergences détectées:")
        for i, div in enumerate(divergences, 1):
            print(f"\nDivergence {i}:")
            print(f"  Type: {div['type']}")
            print(f"  Période: {div['start_date'].date()} - {div['end_date'].date()}")
            print(f"  Confiance: {div['confidence']:.2%}")
        
        # Clustering des cycles
        clusters = analyzer.cluster_cycles()
        
        print("\nClusters de cycles:")
        for cluster, cycles in clusters.items():
            print(f"\n{cluster}:")
            print(f"  Nombre de cycles: {len(cycles)}")
            print(f"  Indices des cycles: {cycles}")
        
        # Analyse des corrélations
        correlations = analyzer.analyze_cycle_correlations()
        
        if not correlations.empty:
            print("\nCorrélations entre cycles consécutifs:")
            print(correlations.describe())
        
        # Visualisation
        plot_patterns(data, analyzer)
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 