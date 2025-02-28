"""
Module de backtesting pour SADIE.

Ce module permet de tester des stratégies de trading sur des données historiques,
d'évaluer leurs performances et d'optimiser leurs paramètres.
"""

from sadie.core.backtest.strategy import (
    Strategy, StrategyResult, Position, PositionType
)
from sadie.core.backtest.engine import (
    BacktestEngine, BacktestConfig, BacktestResult, 
    PerformanceMetrics
)
from sadie.core.backtest.optimizer import (
    StrategyOptimizer, OptimizationResult, OptimizationConfig,
    optimize_strategy
)

__all__ = [
    'Strategy', 'StrategyResult', 'Position', 'PositionType',
    'BacktestEngine', 'BacktestConfig', 'BacktestResult', 'PerformanceMetrics',
    'StrategyOptimizer', 'OptimizationResult', 'OptimizationConfig',
    'optimize_strategy'
] 