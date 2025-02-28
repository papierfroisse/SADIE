"""
Moteur de backtesting pour SADIE.

Ce module fournit le moteur d'exécution pour tester des stratégies
de trading sur des données historiques et évaluer leurs performances.
"""

from typing import Dict, List, Optional, Any, Tuple, Union, Type
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from dataclasses import dataclass
from sadie.core.backtest.strategy import Strategy, StrategyResult


@dataclass
class BacktestConfig:
    """Configuration pour le moteur de backtesting."""
    
    initial_capital: float = 10000.0
    commission_rate: float = 0.001  # 0.1%
    slippage: float = 0.0005  # 0.05%
    use_stop_loss: bool = False
    use_take_profit: bool = False
    max_open_positions: int = 1
    enable_short_positions: bool = False
    enable_pyramiding: bool = False


@dataclass
class PerformanceMetrics:
    """Métriques de performance pour évaluer une stratégie."""
    
    total_return: float = 0.0
    annualized_return: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    avg_profit: float = 0.0
    avg_loss: float = 0.0
    avg_holding_period: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0
    expectancy: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit les métriques en dictionnaire."""
        return {
            "total_return": f"{self.total_return:.2%}",
            "annualized_return": f"{self.annualized_return:.2%}",
            "sharpe_ratio": f"{self.sharpe_ratio:.2f}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "win_rate": f"{self.win_rate:.2%}",
            "profit_factor": f"{self.profit_factor:.2f}",
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "avg_profit": f"{self.avg_profit:.2%}",
            "avg_loss": f"{self.avg_loss:.2%}",
            "avg_holding_period": f"{self.avg_holding_period:.1f}",
            "max_consecutive_wins": self.max_consecutive_wins,
            "max_consecutive_losses": self.max_consecutive_losses,
            "expectancy": f"{self.expectancy:.4f}"
        }


class BacktestResult:
    """Résultat d'un backtest."""
    
    def __init__(
        self,
        strategy_result: StrategyResult,
        config: BacktestConfig,
        data: pd.DataFrame
    ):
        """
        Initialise un nouveau résultat de backtest.
        
        Args:
            strategy_result: Résultat de la stratégie exécutée
            config: Configuration du backtest
            data: Données utilisées pour le backtest
        """
        self.strategy_result = strategy_result
        self.config = config
        self.data = data
        self.metrics = self._calculate_metrics()
        
    def _calculate_metrics(self) -> PerformanceMetrics:
        """
        Calcule les métriques de performance pour la stratégie.
        
        Returns:
            PerformanceMetrics: Métriques de performance calculées
        """
        # Initialiser les métriques
        metrics = PerformanceMetrics()
        
        # Récupérer les positions fermées
        closed_positions = self.strategy_result.closed_positions
        
        if not closed_positions:
            return metrics
        
        # Calculer les métriques de base
        metrics.total_trades = len(closed_positions)
        metrics.winning_trades = len(self.strategy_result.winning_positions)
        metrics.losing_trades = len(self.strategy_result.losing_positions)
        
        # Win rate
        metrics.win_rate = metrics.winning_trades / metrics.total_trades if metrics.total_trades > 0 else 0.0
        
        # Calculer les profits et pertes
        profits = [p.pnl for p in self.strategy_result.winning_positions if p.pnl]
        losses = [p.pnl for p in self.strategy_result.losing_positions if p.pnl]
        
        # Profit total
        total_profit = sum(profits) if profits else 0.0
        total_loss = sum(losses) if losses else 0.0
        
        # Profit factor
        metrics.profit_factor = abs(total_profit / total_loss) if total_loss != 0 else 0.0
        
        # Moyenne des profits et pertes
        metrics.avg_profit = total_profit / len(profits) if profits else 0.0
        metrics.avg_loss = total_loss / len(losses) if losses else 0.0
        
        # Expectancy
        metrics.expectancy = (metrics.win_rate * metrics.avg_profit) - ((1 - metrics.win_rate) * abs(metrics.avg_loss))
        
        # Durée moyenne des positions
        if all(p.duration is not None for p in closed_positions):
            holding_periods = [p.duration for p in closed_positions if p.duration is not None]
            metrics.avg_holding_period = sum(holding_periods) / len(holding_periods) if holding_periods else 0.0
        
        # Calculer les séquences de gains/pertes
        current_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for p in closed_positions:
            if p.pnl and p.pnl > 0:
                if current_streak > 0:
                    current_streak += 1
                else:
                    current_streak = 1
                max_win_streak = max(max_win_streak, current_streak)
            else:
                if current_streak < 0:
                    current_streak -= 1
                else:
                    current_streak = -1
                max_loss_streak = max(max_loss_streak, abs(current_streak))
        
        metrics.max_consecutive_wins = max_win_streak
        metrics.max_consecutive_losses = max_loss_streak
        
        # Obtenir la courbe d'équité
        equity_curve = np.array(self.strategy_result.equity_curve)
        
        # Calculer le rendement total
        metrics.total_return = (equity_curve[-1] - equity_curve[0]) / self.config.initial_capital
        
        # Calculer le drawdown
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        metrics.max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0.0
        
        # Calculer le rendement annualisé et le ratio de Sharpe
        if len(self.strategy_result.timestamps) >= 2:
            try:
                # Convertir les timestamps en datetime si ce sont des entiers
                timestamps = [
                    t if isinstance(t, datetime) else datetime.fromtimestamp(t / 1000) 
                    if t > 1e10 else datetime.fromtimestamp(t)
                    for t in self.strategy_result.timestamps
                ]
                
                # Calculer la durée en années
                first_date = timestamps[0]
                last_date = timestamps[-1]
                years = (last_date - first_date).total_seconds() / (365.25 * 24 * 60 * 60)
                
                if years > 0:
                    metrics.annualized_return = (1 + metrics.total_return) ** (1 / years) - 1
                    
                    # Calculer les rendements quotidiens pour le ratio de Sharpe
                    daily_returns = np.diff(equity_curve) / equity_curve[:-1]
                    excess_returns = daily_returns - 0.0  # Rendement sans risque (supposé 0)
                    
                    if len(excess_returns) > 1:
                        sharpe = np.mean(excess_returns) / np.std(excess_returns)
                        metrics.sharpe_ratio = sharpe * np.sqrt(252)  # Annualiser
            except Exception as e:
                print(f"Erreur lors du calcul des métriques temporelles: {e}")
        
        return metrics
    
    def plot_equity_curve(self) -> Figure:
        """
        Génère un graphique de la courbe d'équité.
        
        Returns:
            Figure: Figure matplotlib contenant le graphique
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        equity_curve = self.strategy_result.equity_curve
        
        if self.strategy_result.timestamps:
            # Convertir les timestamps en datetime si nécessaire
            timestamps = self.strategy_result.timestamps
            if isinstance(timestamps[0], (int, float)):
                if timestamps[0] > 1e10:  # Millisecondes
                    timestamps = [datetime.fromtimestamp(t / 1000) for t in timestamps]
                else:  # Secondes
                    timestamps = [datetime.fromtimestamp(t) for t in timestamps]
            
            ax.plot(timestamps, equity_curve, label="Équité", color="blue")
        else:
            ax.plot(equity_curve, label="Équité", color="blue")
        
        # Ajouter les points d'entrée/sortie
        for position in self.strategy_result.positions:
            if position.position_type.value == "long":
                # Entrer en position longue
                entry_idx = self._find_timestamp_index(position.entry_time)
                if entry_idx is not None:
                    ax.plot(
                        self.strategy_result.timestamps[entry_idx], 
                        equity_curve[entry_idx], 
                        '^', 
                        color="green", 
                        markersize=10
                    )
                
                # Sortir de position longue
                if position.exit_time:
                    exit_idx = self._find_timestamp_index(position.exit_time)
                    if exit_idx is not None:
                        ax.plot(
                            self.strategy_result.timestamps[exit_idx], 
                            equity_curve[exit_idx], 
                            'v', 
                            color="red", 
                            markersize=10
                        )
            else:
                # Entrer en position courte
                entry_idx = self._find_timestamp_index(position.entry_time)
                if entry_idx is not None:
                    ax.plot(
                        self.strategy_result.timestamps[entry_idx], 
                        equity_curve[entry_idx], 
                        'v', 
                        color="red", 
                        markersize=10
                    )
                
                # Sortir de position courte
                if position.exit_time:
                    exit_idx = self._find_timestamp_index(position.exit_time)
                    if exit_idx is not None:
                        ax.plot(
                            self.strategy_result.timestamps[exit_idx], 
                            equity_curve[exit_idx], 
                            '^', 
                            color="green", 
                            markersize=10
                        )
        
        # Calculer et tracer le drawdown
        equity_array = np.array(equity_curve)
        peak = np.maximum.accumulate(equity_array)
        drawdown = (peak - equity_array) / peak
        
        ax2 = ax.twinx()
        ax2.fill_between(
            range(len(drawdown)) if not self.strategy_result.timestamps else self.strategy_result.timestamps,
            0,
            drawdown * 100,
            color="red",
            alpha=0.3,
            label="Drawdown"
        )
        ax2.set_ylabel("Drawdown (%)")
        ax2.set_ylim(0, max(drawdown) * 100 * 1.1)
        
        # Formater le graphique
        ax.set_title("Courbe d'équité et Drawdown")
        ax.set_ylabel("Équité")
        ax.set_xlabel("Date" if self.strategy_result.timestamps else "Périodes")
        ax.grid(True)
        
        # Ajouter les métriques principales
        info_text = (
            f"Rendement total: {self.metrics.total_return:.2%}\n"
            f"Ratio de Sharpe: {self.metrics.sharpe_ratio:.2f}\n"
            f"Drawdown max: {self.metrics.max_drawdown:.2%}\n"
            f"Win Rate: {self.metrics.win_rate:.2%}\n"
            f"Profit Factor: {self.metrics.profit_factor:.2f}"
        )
        plt.figtext(0.01, 0.01, info_text, fontsize=10, ha="left")
        
        # Ajouter la légende
        handles, labels = ax.get_legend_handles_labels()
        handles2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(handles + handles2, labels + labels2, loc="upper left")
        
        plt.tight_layout()
        return fig
    
    def plot_monthly_returns(self) -> Figure:
        """
        Génère un graphique des rendements mensuels.
        
        Returns:
            Figure: Figure matplotlib contenant le graphique
        """
        if not self.strategy_result.timestamps or len(self.strategy_result.timestamps) < 2:
            return None
        
        # Convertir les timestamps en datetime si nécessaire
        timestamps = self.strategy_result.timestamps
        if isinstance(timestamps[0], (int, float)):
            if timestamps[0] > 1e10:  # Millisecondes
                timestamps = [datetime.fromtimestamp(t / 1000) for t in timestamps]
            else:  # Secondes
                timestamps = [datetime.fromtimestamp(t) for t in timestamps]
        
        # Créer un DataFrame avec les données
        equity_df = pd.DataFrame({
            'date': timestamps,
            'equity': self.strategy_result.equity_curve
        })
        
        # Convertir l'index en datetime si ce n'est pas déjà le cas
        equity_df['date'] = pd.to_datetime(equity_df['date'])
        equity_df.set_index('date', inplace=True)
        
        # Calculer les rendements mensuels
        equity_df = equity_df.resample('M').last()
        equity_df['monthly_return'] = equity_df['equity'].pct_change() * 100
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Tracer les rendements mensuels
        bars = ax.bar(
            equity_df.index, 
            equity_df['monthly_return'], 
            color=np.where(equity_df['monthly_return'] >= 0, 'green', 'red')
        )
        
        # Formater le graphique
        ax.set_title("Rendements mensuels (%)")
        ax.set_ylabel("Rendement (%)")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.3)
        
        # Formater les dates sur l'axe x
        plt.xticks(rotation=45)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            height = bar.get_height()
            text_height = height + 0.5 if height >= 0 else height - 1.5
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                text_height,
                f'{height:.1f}%',
                ha='center',
                va='bottom' if height >= 0 else 'top',
                fontsize=8
            )
        
        plt.tight_layout()
        return fig
    
    def _find_timestamp_index(self, timestamp: Union[datetime, int]) -> Optional[int]:
        """
        Trouve l'index d'un timestamp dans la liste des timestamps.
        
        Args:
            timestamp: Timestamp à rechercher
            
        Returns:
            Optional[int]: Index du timestamp ou None s'il n'est pas trouvé
        """
        if not self.strategy_result.timestamps:
            return None
        
        # Si les types sont différents, convertir
        target_timestamp = timestamp
        if isinstance(timestamp, datetime) and isinstance(self.strategy_result.timestamps[0], (int, float)):
            target_timestamp = timestamp.timestamp()
            if self.strategy_result.timestamps[0] > 1e10:
                target_timestamp *= 1000  # Millisecondes
        elif isinstance(timestamp, (int, float)) and isinstance(self.strategy_result.timestamps[0], datetime):
            if timestamp > 1e10:  # Millisecondes
                target_timestamp = datetime.fromtimestamp(timestamp / 1000)
            else:
                target_timestamp = datetime.fromtimestamp(timestamp)
        
        # Chercher l'index exact ou le plus proche
        try:
            if target_timestamp in self.strategy_result.timestamps:
                return self.strategy_result.timestamps.index(target_timestamp)
            else:
                # Trouver l'index le plus proche
                timestamps_array = np.array(self.strategy_result.timestamps)
                if isinstance(target_timestamp, datetime):
                    timestamps_array = np.array([t.timestamp() for t in timestamps_array])
                    target_timestamp = target_timestamp.timestamp()
                
                idx = np.abs(timestamps_array - target_timestamp).argmin()
                return idx
        except:
            return None


class BacktestEngine:
    """Moteur d'exécution pour le backtesting."""
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        """
        Initialise un nouveau moteur de backtesting.
        
        Args:
            config: Configuration du moteur (optionnel)
        """
        self.config = config or BacktestConfig()
    
    def run(self, strategy: Strategy, data: pd.DataFrame) -> BacktestResult:
        """
        Exécute un backtest avec une stratégie et des données.
        
        Args:
            strategy: Stratégie à tester
            data: Données historiques pour le backtest
            
        Returns:
            BacktestResult: Résultat du backtest
        """
        # Vérifier les données
        if data.empty:
            raise ValueError("Les données sont vides")
        
        # Vérifier les colonnes nécessaires
        required_columns = ['timestamp', 'open', 'high', 'low', 'close']
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"Les données doivent contenir les colonnes: {', '.join(required_columns)}")
        
        # Exécuter la stratégie
        strategy_result = strategy.execute(data)
        
        # Créer et retourner le résultat du backtest
        return BacktestResult(strategy_result, self.config, data)
    
    def compare_strategies(
        self,
        strategies: List[Strategy],
        data: pd.DataFrame
    ) -> Dict[str, BacktestResult]:
        """
        Compare plusieurs stratégies sur les mêmes données.
        
        Args:
            strategies: Liste des stratégies à comparer
            data: Données historiques pour le backtest
            
        Returns:
            Dict[str, BacktestResult]: Dictionnaire des résultats par stratégie
        """
        results = {}
        
        for strategy in strategies:
            result = self.run(strategy, data)
            results[strategy.name] = result
        
        return results
    
    def plot_comparison(self, results: Dict[str, BacktestResult]) -> Figure:
        """
        Génère un graphique comparatif des courbes d'équité.
        
        Args:
            results: Dictionnaire des résultats par stratégie
            
        Returns:
            Figure: Figure matplotlib contenant le graphique
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for name, result in results.items():
            equity_curve = result.strategy_result.equity_curve
            
            if result.strategy_result.timestamps:
                # Convertir les timestamps en datetime si nécessaire
                timestamps = result.strategy_result.timestamps
                if isinstance(timestamps[0], (int, float)):
                    if timestamps[0] > 1e10:  # Millisecondes
                        timestamps = [datetime.fromtimestamp(t / 1000) for t in timestamps]
                    else:  # Secondes
                        timestamps = [datetime.fromtimestamp(t) for t in timestamps]
                
                ax.plot(timestamps, equity_curve, label=name)
            else:
                ax.plot(equity_curve, label=name)
        
        # Formater le graphique
        ax.set_title("Comparaison des courbes d'équité")
        ax.set_ylabel("Équité")
        ax.set_xlabel("Date" if any(result.strategy_result.timestamps for result in results.values()) else "Périodes")
        ax.grid(True)
        ax.legend()
        
        plt.tight_layout()
        return fig 