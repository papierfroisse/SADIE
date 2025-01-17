"""Exemple d'utilisation de l'analyseur de cycles de marché."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from SADIE.analysis.market_cycles import CycleAnalyzer

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

def plot_cycles(data: pd.DataFrame, analyzer: CycleAnalyzer) -> None:
    """Crée une visualisation interactive des cycles."""
    # Décomposition tendance-cycle
    decomp = analyzer.decompose_trend()
    
    # Identification des cycles
    cycles = analyzer.identify_cycles()
    
    # Création du graphique
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=('Prix et Cycles', 'Composante Cyclique')
    )
    
    # Prix et tendance
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
                marker=dict(size=10, symbol='triangle-down')
            ),
            row=1, col=1
        )
    
    # Composante cyclique
    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=decomp['cycle'],
            name='Composante Cyclique',
            line=dict(color='green')
        ),
        row=2, col=1
    )
    
    # Mise en forme
    fig.update_layout(
        title='Analyse des Cycles de Marché',
        height=800,
        showlegend=True
    )
    
    # Affichage
    fig.show()

async def main():
    """Point d'entrée principal."""
    try:
        # Création des données d'exemple
        data = create_sample_data(days=365)
        
        # Initialisation de l'analyseur
        analyzer = CycleAnalyzer(data)
        
        # Identification des cycles
        cycles = analyzer.identify_cycles()
        
        # Affichage des résultats
        print("\nCycles identifiés :")
        for i, cycle in enumerate(cycles, 1):
            print(f"\nCycle {i}:")
            print(f"  Début: {cycle.start_date.date()}")
            print(f"  Fin: {cycle.end_date.date()}")
            print(f"  Durée: {cycle.duration} jours")
            print(f"  Amplitude: {cycle.amplitude:.2f}")
            print(f"  Tendance: {cycle.trend}")
            print(f"  Confiance: {cycle.confidence:.2%}")
            
        # Analyse de la phase actuelle
        current_phase = analyzer.analyze_current_phase()
        print("\nPhase actuelle du marché:")
        print(f"  Phase: {current_phase['phase']}")
        print(f"  Confiance: {current_phase['confidence']:.2%}")
        print(f"  Jours depuis dernier pic: {current_phase['days_since_last_peak']}")
        print(f"  Distance du pic: {current_phase['price_from_peak']:.2%}")
        print(f"  Distance du creux: {current_phase['price_from_trough']:.2%}")
        
        # Visualisation
        plot_cycles(data, analyzer)
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 