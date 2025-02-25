"""Exemple d'utilisation des modules d'analyse technique."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from sadie.analysis.indicators import TechnicalIndicators
from sadie.analysis.harmonic_patterns import HarmonicAnalyzer
from sadie.analysis.visualization import ChartVisualizer

async def main():
    """Exemple principal."""
    # Création de données de test
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    data = pd.DataFrame({
        'open': np.random.normal(100, 2, 100),
        'high': np.random.normal(102, 2, 100),
        'low': np.random.normal(98, 2, 100),
        'close': np.random.normal(100, 2, 100),
        'volume': np.random.normal(1000, 100, 100)
    }, index=dates)
    
    # Correction des high/low pour assurer high >= low
    data['high'] = data[['open', 'close', 'high']].max(axis=1)
    data['low'] = data[['open', 'close', 'low']].min(axis=1)
    
    # Création des indicateurs
    indicators = TechnicalIndicators(data)
    analyzer = HarmonicAnalyzer(data)
    
    # Calcul des indicateurs
    bb_mid, bb_up, bb_low, bb_b = indicators.bollinger_bands()
    macd, signal, hist = indicators.macd()
    k, d = indicators.stochastic()
    patterns = analyzer.identify_patterns()
    
    # Affichage des résultats
    print("\nAnalyse technique")
    print("-" * 50)
    
    print("\nBandes de Bollinger:")
    print(f"Moyenne mobile: {bb_mid.iloc[-1]:.2f}")
    print(f"Bande supérieure: {bb_up.iloc[-1]:.2f}")
    print(f"Bande inférieure: {bb_low.iloc[-1]:.2f}")
    print(f"%B: {bb_b.iloc[-1]:.2%}")
    
    print("\nMACD:")
    print(f"MACD: {macd.iloc[-1]:.2f}")
    print(f"Signal: {signal.iloc[-1]:.2f}")
    print(f"Histogramme: {hist.iloc[-1]:.2f}")
    
    print("\nStochastique:")
    print(f"%K: {k.iloc[-1]:.2f}")
    print(f"%D: {d.iloc[-1]:.2f}")
    
    if patterns:
        print("\nMotifs harmoniques détectés:")
        for pattern in patterns:
            print(f"- {pattern.pattern_type.value} ({pattern.trend.value})")
            print(f"  Confiance: {pattern.confidence:.1%}")
            print(f"  Zone de retournement: {pattern.potential_reversal_zone[0]:.2f} - {pattern.potential_reversal_zone[1]:.2f}")
    
    # Création du graphique
    visualizer = ChartVisualizer(data, indicators, analyzer)
    fig = visualizer.create_chart(
        show_volume=True,
        show_bb=True,
        show_macd=True,
        show_stoch=True,
        show_patterns=True
    )
    
    # Sauvegarde du graphique
    fig.write_html("analysis.html")
    print("\nGraphique sauvegardé dans analysis.html")

if __name__ == "__main__":
    asyncio.run(main()) 