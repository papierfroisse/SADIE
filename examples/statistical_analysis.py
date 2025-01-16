"""Exemple d'utilisation de l'analyseur statistique."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from SADIE.analysis.statistics import StatisticalAnalyzer

async def main():
    """Fonction principale."""
    try:
        # Création de données simulées
        dates = pd.date_range(
            start=datetime(2023, 1, 1, tzinfo=timezone.utc),
            end=datetime(2023, 12, 31, tzinfo=timezone.utc),
            freq='D'
        )
        
        # Simulation de prix avec une tendance et de la volatilité
        n = len(dates)
        trend = np.linspace(0, 0.2, n)  # Tendance haussière plus modérée
        volatility = np.random.normal(0, 0.01, n)  # Volatilité réduite
        returns = trend + volatility
        prices = 100 * np.exp(np.cumsum(returns))  # Prix simulés
        volumes = np.random.lognormal(8, 0.5, n)  # Volumes plus modérés
        
        # Création du DataFrame
        data = pd.DataFrame({
            'timestamp': dates,
            'close': prices,
            'volume': volumes
        })
        
        # Initialisation de l'analyseur
        analyzer = StatisticalAnalyzer(data)
        
        # Analyse de la distribution des prix
        print("\nAnalyse de la distribution des prix:")
        stats = analyzer.analyze_distribution('close')
        print(f"Moyenne: {stats.mean:.2f}")
        print(f"Médiane: {stats.median:.2f}")
        print(f"Écart-type: {stats.std:.2f}")
        print(f"Skewness: {stats.skewness:.2f}")
        print(f"Kurtosis: {stats.kurtosis:.2f}")
        print(f"Distribution normale: {stats.is_normal}")
        
        # Calcul des rendements et de la volatilité
        returns = analyzer.calculate_returns('close')
        volatility = analyzer.calculate_volatility('close', window=20)
        print("\nAnalyse des rendements:")
        print(f"Rendement moyen: {returns.mean():.4f}")
        print(f"Volatilité moyenne: {volatility.mean():.4f}")
        
        # Détection des outliers
        outliers = analyzer.detect_outliers('close', method='zscore')
        n_outliers = outliers.sum()
        print(f"\nNombre d'outliers détectés: {n_outliers}")
        
        # Calcul de la corrélation prix-volume
        correlation, p_value = analyzer.calculate_correlation('close', 'volume')
        print("\nAnalyse de la corrélation prix-volume:")
        print(f"Coefficient de corrélation: {correlation:.4f}")
        print(f"P-value: {p_value:.4f}")
        
        # Calcul des métriques de risque
        print("\nMétriques de risque:")
        var = analyzer.calculate_var(returns, confidence_level=0.95)
        cvar = analyzer.calculate_cvar(returns, confidence_level=0.95)
        print(f"VaR (95%): {var:.4f}")
        print(f"CVaR (95%): {cvar:.4f}")
        
        # Calcul des ratios de performance
        print("\nRatios de performance:")
        sharpe = analyzer.calculate_sharpe_ratio(returns, risk_free_rate=0.02)
        sortino = analyzer.calculate_sortino_ratio(returns, risk_free_rate=0.02)
        print(f"Ratio de Sharpe: {sharpe:.4f}")
        print(f"Ratio de Sortino: {sortino:.4f}")
        
    except Exception as e:
        print(f"Erreur lors de l'analyse: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 