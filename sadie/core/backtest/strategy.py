"""
Module des stratégies de trading pour le backtesting SADIE.

Ce module fournit les classes de base pour implémenter des stratégies
de trading qui peuvent être testées avec le moteur de backtesting.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Union
import pandas as pd
import numpy as np
from datetime import datetime


class PositionType(Enum):
    """Types de positions possibles."""
    
    LONG = "long"
    SHORT = "short"


class Position:
    """Représente une position de trading ouverte ou fermée."""
    
    def __init__(
        self,
        position_type: PositionType,
        entry_price: float,
        entry_time: Union[datetime, int],
        size: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        meta: Optional[Dict[str, Any]] = None
    ):
        """
        Initialise une nouvelle position.
        
        Args:
            position_type: Type de position (LONG ou SHORT)
            entry_price: Prix d'entrée
            entry_time: Timestamp d'entrée
            size: Taille de la position
            stop_loss: Prix de stop-loss (optionnel)
            take_profit: Prix de take-profit (optionnel)
            meta: Métadonnées supplémentaires (optionnel)
        """
        self.position_type = position_type
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.size = size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.meta = meta or {}
        
        # Attributs d'une position fermée
        self.exit_price: Optional[float] = None
        self.exit_time: Optional[Union[datetime, int]] = None
        self.pnl: Optional[float] = None
        self.exit_reason: Optional[str] = None
        
    def close(
        self,
        exit_price: float,
        exit_time: Union[datetime, int],
        exit_reason: str = "manual"
    ) -> float:
        """
        Ferme la position et calcule le P&L.
        
        Args:
            exit_price: Prix de sortie
            exit_time: Timestamp de sortie
            exit_reason: Raison de la sortie (manuel, stop-loss, take-profit, etc.)
            
        Returns:
            float: Le P&L généré par la position
        """
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = exit_reason
        
        # Calcul du P&L
        if self.position_type == PositionType.LONG:
            self.pnl = (exit_price - self.entry_price) * self.size
        else:
            self.pnl = (self.entry_price - exit_price) * self.size
            
        return self.pnl
    
    @property
    def is_open(self) -> bool:
        """Vérifie si la position est toujours ouverte."""
        return self.exit_price is None
    
    @property
    def duration(self) -> Optional[float]:
        """Retourne la durée de la position en secondes ou ticks."""
        if not self.is_open and isinstance(self.entry_time, (int, float)) and isinstance(self.exit_time, (int, float)):
            return self.exit_time - self.entry_time
        elif not self.is_open and isinstance(self.entry_time, datetime) and isinstance(self.exit_time, datetime):
            return (self.exit_time - self.entry_time).total_seconds()
        return None
    
    def current_pnl(self, current_price: float) -> float:
        """
        Calcule le P&L non-réalisé de la position.
        
        Args:
            current_price: Prix actuel de l'actif
            
        Returns:
            float: Le P&L non-réalisé
        """
        if not self.is_open:
            return self.pnl or 0.0
        
        if self.position_type == PositionType.LONG:
            return (current_price - self.entry_price) * self.size
        else:
            return (self.entry_price - current_price) * self.size
    
    def should_close(self, current_price: float) -> Tuple[bool, Optional[str]]:
        """
        Vérifie si la position doit être fermée en fonction du prix actuel.
        
        Args:
            current_price: Prix actuel de l'actif
            
        Returns:
            Tuple[bool, Optional[str]]: Tuple indiquant si la position doit être fermée et pourquoi
        """
        if not self.is_open:
            return False, None
        
        # Vérifier le stop-loss
        if self.stop_loss is not None:
            if self.position_type == PositionType.LONG and current_price <= self.stop_loss:
                return True, "stop_loss"
            elif self.position_type == PositionType.SHORT and current_price >= self.stop_loss:
                return True, "stop_loss"
        
        # Vérifier le take-profit
        if self.take_profit is not None:
            if self.position_type == PositionType.LONG and current_price >= self.take_profit:
                return True, "take_profit"
            elif self.position_type == PositionType.SHORT and current_price <= self.take_profit:
                return True, "take_profit"
        
        return False, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la position en dictionnaire."""
        return {
            "position_type": self.position_type.value,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat() if isinstance(self.entry_time, datetime) else self.entry_time,
            "size": self.size,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "exit_price": self.exit_price,
            "exit_time": self.exit_time.isoformat() if isinstance(self.exit_time, datetime) else self.exit_time,
            "pnl": self.pnl,
            "exit_reason": self.exit_reason,
            "meta": self.meta
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        """Crée une position à partir d'un dictionnaire."""
        position = cls(
            position_type=PositionType(data["position_type"]),
            entry_price=data["entry_price"],
            entry_time=data["entry_time"],
            size=data["size"],
            stop_loss=data.get("stop_loss"),
            take_profit=data.get("take_profit"),
            meta=data.get("meta", {})
        )
        
        # Restaurer les attributs d'une position fermée
        if data.get("exit_price") is not None:
            position.exit_price = data["exit_price"]
            position.exit_time = data["exit_time"]
            position.pnl = data["pnl"]
            position.exit_reason = data["exit_reason"]
        
        return position


class StrategyResult:
    """Résultat d'exécution d'une stratégie."""
    
    def __init__(self):
        """Initialise un nouveau résultat de stratégie."""
        self.positions: List[Position] = []
        self.equity_curve: List[float] = []
        self.timestamps: List[Union[datetime, int]] = []
        self.indicators: Dict[str, List[float]] = {}
    
    @property
    def total_pnl(self) -> float:
        """Calcule le P&L total de toutes les positions."""
        return sum(position.pnl or 0 for position in self.positions if not position.is_open)
    
    @property
    def open_positions(self) -> List[Position]:
        """Retourne les positions actuellement ouvertes."""
        return [position for position in self.positions if position.is_open]
    
    @property
    def closed_positions(self) -> List[Position]:
        """Retourne les positions fermées."""
        return [position for position in self.positions if not position.is_open]
    
    @property
    def winning_positions(self) -> List[Position]:
        """Retourne les positions gagnantes."""
        return [position for position in self.closed_positions if position.pnl and position.pnl > 0]
    
    @property
    def losing_positions(self) -> List[Position]:
        """Retourne les positions perdantes."""
        return [position for position in self.closed_positions if position.pnl and position.pnl <= 0]
    
    @property
    def win_rate(self) -> float:
        """Calcule le taux de réussite."""
        total_positions = len(self.closed_positions)
        return len(self.winning_positions) / total_positions if total_positions > 0 else 0.0
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convertit les résultats en DataFrame pandas."""
        data = {
            "timestamp": self.timestamps,
            "equity": self.equity_curve
        }
        
        # Ajouter les indicateurs
        for name, values in self.indicators.items():
            data[name] = values
        
        return pd.DataFrame(data)


class Strategy(ABC):
    """
    Classe de base abstraite pour les stratégies de trading.
    
    Toutes les stratégies de backtesting doivent hériter de cette classe
    et implémenter la méthode execute().
    """
    
    def __init__(self, name: str = "Strategy", parameters: Optional[Dict[str, Any]] = None):
        """
        Initialise une nouvelle stratégie.
        
        Args:
            name: Nom de la stratégie
            parameters: Paramètres de la stratégie
        """
        self.name = name
        self.parameters = parameters or {}
        self.result = StrategyResult()
    
    @abstractmethod
    def execute(self, data: pd.DataFrame) -> StrategyResult:
        """
        Exécute la stratégie sur les données fournies.
        
        Args:
            data: DataFrame pandas contenant les données OHLCV
            
        Returns:
            StrategyResult: Les résultats de la stratégie
        """
        pass
    
    def reset(self) -> None:
        """Réinitialise les résultats de la stratégie."""
        self.result = StrategyResult()


class SimpleMovingAverageCrossover(Strategy):
    """
    Stratégie simple basée sur le croisement de deux moyennes mobiles.
    
    Cette stratégie génère un signal d'achat lorsque la moyenne mobile rapide
    passe au-dessus de la moyenne mobile lente, et un signal de vente lorsque
    la moyenne mobile rapide passe en dessous de la moyenne mobile lente.
    """
    
    def __init__(
        self,
        fast_period: int = 10,
        slow_period: int = 30,
        position_size: float = 1.0,
        use_stop_loss: bool = False,
        stop_loss_pct: float = 0.02,
        use_take_profit: bool = False,
        take_profit_pct: float = 0.05,
        name: str = "SMA Crossover"
    ):
        """
        Initialise la stratégie SMA Crossover.
        
        Args:
            fast_period: Période de la moyenne mobile rapide
            slow_period: Période de la moyenne mobile lente
            position_size: Taille de la position (nombre d'unités par trade)
            use_stop_loss: Utiliser un stop-loss ?
            stop_loss_pct: Pourcentage pour le stop-loss (relatif au prix d'entrée)
            use_take_profit: Utiliser un take-profit ?
            take_profit_pct: Pourcentage pour le take-profit (relatif au prix d'entrée)
            name: Nom de la stratégie
        """
        parameters = {
            "fast_period": fast_period,
            "slow_period": slow_period,
            "position_size": position_size,
            "use_stop_loss": use_stop_loss,
            "stop_loss_pct": stop_loss_pct,
            "use_take_profit": use_take_profit,
            "take_profit_pct": take_profit_pct
        }
        super().__init__(name=name, parameters=parameters)
        
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.position_size = position_size
        self.use_stop_loss = use_stop_loss
        self.stop_loss_pct = stop_loss_pct
        self.use_take_profit = use_take_profit
        self.take_profit_pct = take_profit_pct
    
    def execute(self, data: pd.DataFrame) -> StrategyResult:
        """
        Exécute la stratégie SMA Crossover sur les données fournies.
        
        Args:
            data: DataFrame pandas contenant les données OHLCV
            
        Returns:
            StrategyResult: Les résultats de la stratégie
        """
        # Réinitialiser les résultats
        self.reset()
        
        # Vérifier les colonnes requises
        if not all(col in data.columns for col in ['timestamp', 'close']):
            raise ValueError("Les données doivent contenir au moins les colonnes 'timestamp' et 'close'")
        
        # Copier les données pour éviter des modifications indésirables
        df = data.copy()
        
        # Calculer les moyennes mobiles
        df['fast_sma'] = df['close'].rolling(window=self.fast_period).mean()
        df['slow_sma'] = df['close'].rolling(window=self.slow_period).mean()
        
        # Calculer le signal de croisement
        df['signal'] = 0
        df['signal'] = np.where(df['fast_sma'] > df['slow_sma'], 1, 0)
        df['position_change'] = df['signal'].diff()
        
        # Initialiser le capital
        equity = [0.0]
        current_position = None
        
        # Parcourir les données pour simuler les trades
        for i in range(1, len(df)):
            row = df.iloc[i]
            prev_row = df.iloc[i-1]
            
            # Vérifier si nous avons une position ouverte
            if current_position is not None and current_position.is_open:
                # Vérifier si nous devons fermer la position basée sur le stop-loss ou take-profit
                should_close, reason = current_position.should_close(row['close'])
                if should_close:
                    current_position.close(row['close'], row['timestamp'], reason)
                    self.result.positions.append(current_position)
                    current_position = None
            
            # Vérifier les signaux d'entrée/sortie
            if row['position_change'] == 1:  # Signal d'achat
                if current_position is not None and current_position.is_open:
                    # Fermer la position existante si elle est SHORT
                    if current_position.position_type == PositionType.SHORT:
                        current_position.close(row['close'], row['timestamp'], "signal_reversed")
                        self.result.positions.append(current_position)
                
                # Ouvrir une nouvelle position LONG
                stop_loss = row['close'] * (1 - self.stop_loss_pct) if self.use_stop_loss else None
                take_profit = row['close'] * (1 + self.take_profit_pct) if self.use_take_profit else None
                
                current_position = Position(
                    position_type=PositionType.LONG,
                    entry_price=row['close'],
                    entry_time=row['timestamp'],
                    size=self.position_size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    meta={"fast_sma": row['fast_sma'], "slow_sma": row['slow_sma']}
                )
                
            elif row['position_change'] == -1:  # Signal de vente
                if current_position is not None and current_position.is_open:
                    # Fermer la position existante si elle est LONG
                    if current_position.position_type == PositionType.LONG:
                        current_position.close(row['close'], row['timestamp'], "signal_reversed")
                        self.result.positions.append(current_position)
                
                # Ouvrir une nouvelle position SHORT si activé
                stop_loss = row['close'] * (1 + self.stop_loss_pct) if self.use_stop_loss else None
                take_profit = row['close'] * (1 - self.take_profit_pct) if self.use_take_profit else None
                
                current_position = Position(
                    position_type=PositionType.SHORT,
                    entry_price=row['close'],
                    entry_time=row['timestamp'],
                    size=self.position_size,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    meta={"fast_sma": row['fast_sma'], "slow_sma": row['slow_sma']}
                )
            
            # Mettre à jour l'équité
            pnl_for_bar = 0
            if current_position is not None and current_position.is_open:
                pnl_for_bar = current_position.current_pnl(row['close'])
            
            new_equity = equity[-1] + pnl_for_bar
            equity.append(new_equity)
            
            # Stocker les timestamps et les indicateurs
            self.result.timestamps.append(row['timestamp'])
            self.result.equity_curve.append(new_equity)
        
        # Fermer toute position ouverte à la fin de la période
        if current_position is not None and current_position.is_open:
            last_row = df.iloc[-1]
            current_position.close(last_row['close'], last_row['timestamp'], "end_of_period")
            self.result.positions.append(current_position)
        
        # Stocker les indicateurs pour l'analyse
        self.result.indicators['fast_sma'] = df['fast_sma'].values
        self.result.indicators['slow_sma'] = df['slow_sma'].values
        
        return self.result 