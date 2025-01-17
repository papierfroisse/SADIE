"""Exemple d'utilisation de l'analyseur avancé des cycles de marché."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from SADIE.analysis.advanced_cycles import AdvancedCycleAnalyzer

def create_sample_data(days: int = 365) -> pd.DataFrame:
    """Crée des données simulées avec des cycles."""
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
    
    # Combinaison des composantes
    price = trend + cycle1 + cycle2 + cycle3
    
    # Ajout de bruit
    noise = np.random.normal(0, 1, len(dates))
    price += noise
    
    return pd.DataFrame({
        'close': price,
        'volume': np.random.lognormal(10, 1, len(dates))
    }, index=dates)

def plot_advanced_cycles(data: pd.DataFrame, analyzer: AdvancedCycleAnalyzer) -> None:
    """Crée une visualisation interactive avancée des cycles."""
    # Décomposition et analyse
    decomp = analyzer.decompose_trend()
    cycles = analyzer.identify_cycles()
    regime_changes = analyzer.detect_regime_change()
    
    # Création du graphique avec 4 sous-graphiques
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(
            'Prix, Tendance et Cycles',
            'Composante Cyclique',
            'Changements de Régime',
            'Métriques Glissantes'
        ),
        row_heights=[0.4, 0.2, 0.2, 0.2]
    )
    
    # 1. Prix et tendance
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data['close'],
            name='Prix',
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=decomp['trend'],
            name='Tendance',
            line=dict(color='red', dash='dash')
        ),
        row=1, col=1
    )
    
    # Marquage des cycles
    for cycle in cycles:
        # Zone du cycle
        fig.add_vrect(
            x0=cycle.start_date,
            x1=cycle.end_date,
            fillcolor='gray',
            opacity=0.1,
            layer='below',
            line_width=0,
            row=1, col=1
        )
        
        # Points de retournement
        fig.add_trace(
            go.Scatter(
                x=[cycle.start_date, cycle.end_date],
                y=[data.loc[cycle.start_date, 'close'],
                   data.loc[cycle.end_date, 'close']],
                mode='markers',
                name=f'Cycle {cycle.trend}',
                marker=dict(
                    size=10,
                    symbol='triangle-down',
                    color='green' if cycle.trend == 'bullish' else 'red'
                )
            ),
            row=1, col=1
        )
    
    # 2. Composante cyclique
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=decomp['cycle'],
            name='Composante Cyclique',
            line=dict(color='green')
        ),
        row=2, col=1
    )
    
    # Ligne horizontale à zéro
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        row=2, col=1
    )
    
    # 3. Probabilités de changement de régime
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=regime_changes,
            name='Probabilité de Changement de Régime',
            line=dict(color='purple')
        ),
        row=3, col=1
    )
    
    # 4. Métriques glissantes
    window = 20
    returns = data['close'].pct_change()
    volatility = returns.rolling(window=window).std()
    
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=volatility,
            name='Volatilité',
            line=dict(color='orange')
        ),
        row=4, col=1
    )
    
    # Mise en forme
    fig.update_layout(
        title='Analyse Avancée des Cycles de Marché',
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
        
        # Initialisation de l'analyseur avancé
        analyzer = AdvancedCycleAnalyzer(data)
        
        # Analyse des caractéristiques des cycles
        characteristics = analyzer.analyze_cycle_characteristics()
        
        print("\nCaractéristiques des cycles:")
        print(f"Durée moyenne: {characteristics.duration_mean:.1f} jours")
        print(f"Amplitude moyenne: {characteristics.amplitude_mean:.2f}")
        print(f"Score de symétrie: {characteristics.symmetry_score:.2%}")
        print(f"Période dominante: {characteristics.dominant_period:.1f} jours")
        print(f"Force de la saisonnalité: {characteristics.seasonality_score:.2%}")
        print(f"Force de la tendance: {characteristics.trend_strength:.2%}")
        
        # Prévision du prochain cycle
        forecast = analyzer.forecast_next_cycle()
        
        print("\nPrévision du prochain cycle:")
        print(f"Durée attendue: {forecast['expected_duration']:.1f} jours")
        print(f"Amplitude attendue: {forecast['expected_amplitude']:.2f}")
        print(f"Probabilité haussière: {forecast['bullish_probability']:.2%}")
        print(f"Confiance: {forecast['confidence']:.2%}")
        
        # Métriques supplémentaires
        metrics = analyzer.get_cycle_metrics()
        
        print("\nMétriques des cycles:")
        print(f"Régularité des cycles: {metrics['cycle_regularity']:.2%}")
        print(f"Stabilité des amplitudes: {metrics['amplitude_stability']:.2%}")
        print(f"Biais de tendance: {metrics['trend_bias']:.2f}")
        print(f"Qualité des cycles: {metrics['cycle_quality']:.2%}")
        
        # Visualisation
        plot_advanced_cycles(data, analyzer)
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 