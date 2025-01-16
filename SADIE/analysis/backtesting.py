"""Module de backtesting pour SADIE."""

from typing import Dict, List, Optional, Union, Callable
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Position:
    """Représente une position ouverte."""
    symbol: str
    direction: str  # 'long' ou 'short'
    size: float
    entry_price: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None

@dataclass
class Trade:
    """Représente une transaction complétée."""
    symbol: str
    direction: str
    size: float
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_pct: float
    fees: float

class Strategy(ABC):
    """Classe de base pour les stratégies de trading."""
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Génère les signaux de trading.
        
        Args:
            data: DataFrame avec les données de marché
            
        Returns:
            Série avec les signaux (1: achat, -1: vente, 0: neutre)
        """
        pass

class Backtester:
    """Classe pour le backtesting des stratégies."""
    
    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        slippage: float = 0.0
    ):
        """Initialise le backtester.
        
        Args:
            data: DataFrame avec les données de marché
            initial_capital: Capital initial
            commission: Commission par trade (en %)
            slippage: Slippage par trade (en %)
        """
        self._data = data.copy()
        self._initial_capital = initial_capital
        self._commission = commission
        self._slippage = slippage
        
        self._validate_data()
        self._reset()
        
    def _validate_data(self):
        """Valide le format des données d'entrée."""
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in self._data.columns for col in required_columns):
            raise ValueError(f"Les données doivent contenir les colonnes: {required_columns}")
            
    def _reset(self):
        """Réinitialise l'état du backtester."""
        self._equity = [self._initial_capital]
        self._positions: List[Position] = []
        self._trades: List[Trade] = []
        self._current_capital = self._initial_capital
        
    def _calculate_position_value(self, position: Position, current_price: float) -> float:
        """Calcule la valeur actuelle d'une position.
        
        Args:
            position: Position à évaluer
            current_price: Prix actuel
            
        Returns:
            Valeur actuelle de la position
        """
        if position.direction == 'long':
            return position.size * (current_price - position.entry_price)
        else:
            return position.size * (position.entry_price - current_price)
            
    def _check_stop_loss(self, position: Position, current_price: float) -> bool:
        """Vérifie si le stop loss est atteint.
        
        Args:
            position: Position à vérifier
            current_price: Prix actuel
            
        Returns:
            True si le stop loss est atteint
        """
        if position.stop_loss is None:
            return False
            
        if position.direction == 'long':
            return current_price <= position.stop_loss
        else:
            return current_price >= position.stop_loss
            
    def _check_take_profit(self, position: Position, current_price: float) -> bool:
        """Vérifie si le take profit est atteint.
        
        Args:
            position: Position à vérifier
            current_price: Prix actuel
            
        Returns:
            True si le take profit est atteint
        """
        if position.take_profit is None:
            return False
            
        if position.direction == 'long':
            return current_price >= position.take_profit
        else:
            return current_price <= position.take_profit
            
    def _close_position(self, position: Position, exit_price: float, exit_time: datetime):
        """Ferme une position.
        
        Args:
            position: Position à fermer
            exit_price: Prix de sortie
            exit_time: Heure de sortie
        """
        # Calculer le P&L
        if position.direction == 'long':
            pnl = position.size * (exit_price - position.entry_price)
            pnl_pct = (exit_price - position.entry_price) / position.entry_price
        else:
            pnl = position.size * (position.entry_price - exit_price)
            pnl_pct = (position.entry_price - exit_price) / position.entry_price
            
        # Calculer les frais
        fees = position.size * exit_price * self._commission
        
        # Créer le trade
        trade = Trade(
            symbol=position.symbol,
            direction=position.direction,
            size=position.size,
            entry_price=position.entry_price,
            exit_price=exit_price,
            entry_time=position.entry_time,
            exit_time=exit_time,
            pnl=pnl,
            pnl_pct=pnl_pct,
            fees=fees
        )
        
        # Mettre à jour le capital
        self._current_capital += pnl - fees
        self._equity.append(self._current_capital)
        
        # Enregistrer le trade
        self._trades.append(trade)
        
    def run(self, strategy: Strategy) -> Dict[str, Union[float, pd.Series]]:
        """Exécute le backtest.
        
        Args:
            strategy: Stratégie à tester
            
        Returns:
            Résultats du backtest
        """
        # Réinitialiser l'état
        self._reset()
        
        # Générer les signaux
        signals = strategy.generate_signals(self._data)
        
        # Parcourir les données
        for i in range(1, len(self._data)):
            current_bar = self._data.iloc[i]
            previous_bar = self._data.iloc[i-1]
            
            # Vérifier les positions existantes
            for position in self._positions[:]:
                # Vérifier stop loss et take profit
                if self._check_stop_loss(position, current_bar['low']):
                    self._close_position(position, position.stop_loss, current_bar['timestamp'])
                    self._positions.remove(position)
                elif self._check_take_profit(position, current_bar['high']):
                    self._close_position(position, position.take_profit, current_bar['timestamp'])
                    self._positions.remove(position)
                    
            # Traiter les nouveaux signaux
            if signals.iloc[i] != 0:
                # Fermer les positions existantes
                for position in self._positions[:]:
                    self._close_position(position, current_bar['open'], current_bar['timestamp'])
                    self._positions.remove(position)
                    
                # Ouvrir une nouvelle position
                if signals.iloc[i] == 1:  # Signal d'achat
                    position = Position(
                        symbol=self._data.index.name or 'UNKNOWN',
                        direction='long',
                        size=self._current_capital * 0.95,  # Utiliser 95% du capital
                        entry_price=current_bar['open'],
                        entry_time=current_bar['timestamp']
                    )
                    self._positions.append(position)
                elif signals.iloc[i] == -1:  # Signal de vente
                    position = Position(
                        symbol=self._data.index.name or 'UNKNOWN',
                        direction='short',
                        size=self._current_capital * 0.95,
                        entry_price=current_bar['open'],
                        entry_time=current_bar['timestamp']
                    )
                    self._positions.append(position)
                    
        # Fermer les positions restantes
        last_bar = self._data.iloc[-1]
        for position in self._positions[:]:
            self._close_position(position, last_bar['close'], last_bar['timestamp'])
            
        # Calculer les métriques
        returns = pd.Series(self._equity).pct_change().dropna()
        
        return {
            'initial_capital': self._initial_capital,
            'final_capital': self._current_capital,
            'total_return': (self._current_capital - self._initial_capital) / self._initial_capital,
            'sharpe_ratio': returns.mean() / returns.std() * np.sqrt(252) if len(returns) > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown(),
            'trade_count': len(self._trades),
            'win_rate': self._calculate_win_rate(),
            'profit_factor': self._calculate_profit_factor(),
            'equity_curve': pd.Series(self._equity),
            'trades': self._trades
        }
        
    def _calculate_max_drawdown(self) -> float:
        """Calcule le drawdown maximum.
        
        Returns:
            Drawdown maximum en pourcentage
        """
        equity_series = pd.Series(self._equity)
        rolling_max = equity_series.expanding().max()
        drawdowns = (equity_series - rolling_max) / rolling_max
        return float(drawdowns.min())
        
    def _calculate_win_rate(self) -> float:
        """Calcule le taux de trades gagnants.
        
        Returns:
            Taux de trades gagnants
        """
        if not self._trades:
            return 0.0
            
        winning_trades = sum(1 for trade in self._trades if trade.pnl > 0)
        return winning_trades / len(self._trades)
        
    def _calculate_profit_factor(self) -> float:
        """Calcule le facteur de profit.
        
        Returns:
            Facteur de profit
        """
        gross_profit = sum(trade.pnl for trade in self._trades if trade.pnl > 0)
        gross_loss = abs(sum(trade.pnl for trade in self._trades if trade.pnl < 0))
        
        return gross_profit / gross_loss if gross_loss != 0 else float('inf') 