"""Exemple d'utilisation du backtester avec une stratégie de croisement de moyennes mobiles."""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from SADIE.analysis.backtesting import Strategy, Backtester

class MovingAverageCrossStrategy(Strategy):
    """Stratégie basée sur le croisement de moyennes mobiles."""
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        """Initialise la stratégie.
        
        Args:
            short_window: Fenêtre de la moyenne mobile courte
            long_window: Fenêtre de la moyenne mobile longue
        """
        self.short_window = short_window
        self.long_window = long_window
        
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Génère les signaux de trading.
        
        Args:
            data: DataFrame avec les données de marché
            
        Returns:
            Série avec les signaux (1: achat, -1: vente, 0: neutre)
        """
        # Calculer les moyennes mobiles
        short_ma = data['close'].rolling(window=self.short_window).mean()
        long_ma = data['close'].rolling(window=self.long_window).mean()
        
        # Initialiser les signaux
        signals = pd.Series(0, index=data.index)
        
        # Générer les signaux de croisement
        signals[short_ma > long_ma] = 1  # Signal d'achat
        signals[short_ma < long_ma] = -1  # Signal de vente
        
        return signals

async def main():
    """Fonction principale."""
    try:
        # Charger les données historiques (exemple avec des données simulées)
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='1H')
        data = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.normal(100, 2, len(dates)),
            'high': np.random.normal(101, 2, len(dates)),
            'low': np.random.normal(99, 2, len(dates)),
            'close': np.random.normal(100, 2, len(dates)),
            'volume': np.random.normal(1000, 200, len(dates))
        })
        
        # Créer la stratégie
        strategy = MovingAverageCrossStrategy(short_window=20, long_window=50)
        
        # Initialiser le backtester
        backtester = Backtester(
            data=data,
            initial_capital=100000.0,
            commission=0.001,  # 0.1% de commission
            slippage=0.0005    # 0.05% de slippage
        )
        
        # Exécuter le backtest
        results = backtester.run(strategy)
        
        # Afficher les résultats
        print("\nRésultats du backtest:")
        print(f"Capital initial: {results['initial_capital']:.2f}")
        print(f"Capital final: {results['final_capital']:.2f}")
        print(f"Rendement total: {results['total_return']:.2%}")
        print(f"Ratio de Sharpe: {results['sharpe_ratio']:.2f}")
        print(f"Drawdown maximum: {results['max_drawdown']:.2%}")
        print(f"Nombre de trades: {results['trade_count']}")
        print(f"Taux de réussite: {results['win_rate']:.2%}")
        print(f"Facteur de profit: {results['profit_factor']:.2f}")
        
        # Afficher les 5 derniers trades
        print("\nDerniers trades:")
        for trade in results['trades'][-5:]:
            print(f"Direction: {trade.direction}")
            print(f"Entrée: {trade.entry_price:.2f} @ {trade.entry_time}")
            print(f"Sortie: {trade.exit_price:.2f} @ {trade.exit_time}")
            print(f"P&L: {trade.pnl:.2f} ({trade.pnl_pct:.2%})")
            print("---")
            
    except Exception as e:
        print(f"Erreur lors du backtest: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 