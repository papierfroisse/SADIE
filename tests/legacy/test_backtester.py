"""Tests unitaires pour le module de backtesting."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
from sadie.analysis.backtesting import Strategy, Backtester, Position, Trade

class SimpleStrategy(Strategy):
    """Stratégie simple pour les tests."""
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Génère des signaux simples pour les tests."""
        signals = pd.Series(0, index=data.index)
        signals.iloc[1] = 1  # Signal d'achat au deuxième point
        signals.iloc[3] = -1  # Signal de vente au quatrième point
        return signals

@pytest.fixture
def sample_data():
    """Crée des données de test."""
    dates = pd.date_range(
        start=datetime(2023, 1, 1, tzinfo=timezone.utc),
        end=datetime(2023, 1, 2, tzinfo=timezone.utc),
        freq='h'
    )
    data = pd.DataFrame({
        'timestamp': dates,
        'open': [100.0, 101.0, 102.0, 101.0, 100.0] * 5,
        'high': [102.0, 103.0, 104.0, 103.0, 102.0] * 5,
        'low': [99.0, 100.0, 101.0, 100.0, 99.0] * 5,
        'close': [101.0, 102.0, 103.0, 102.0, 101.0] * 5,
        'volume': [1000.0, 1100.0, 1200.0, 1100.0, 1000.0] * 5
    })
    return data

@pytest.fixture
def backtester(sample_data):
    """Crée une instance du backtester avec les données de test."""
    return Backtester(
        data=sample_data,
        initial_capital=100000.0,
        commission=0.001,
        slippage=0.0005
    )

def test_backtester_initialization(backtester, sample_data):
    """Teste l'initialisation du backtester."""
    assert backtester._initial_capital == 100000.0
    assert backtester._commission == 0.001
    assert backtester._slippage == 0.0005
    assert len(backtester._data) == len(sample_data)
    assert backtester._current_capital == 100000.0
    assert len(backtester._positions) == 0
    assert len(backtester._trades) == 0

def test_validate_data():
    """Teste la validation des données d'entrée."""
    # Données valides
    valid_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', end='2023-01-02', freq='h'),
        'open': [100.0] * 25,
        'high': [101.0] * 25,
        'low': [99.0] * 25,
        'close': [100.0] * 25,
        'volume': [1000.0] * 25
    })
    backtester = Backtester(valid_data)
    
    # Données invalides (colonne manquante)
    invalid_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', end='2023-01-02', freq='h'),
        'open': [100.0] * 25,
        'high': [101.0] * 25,
        'low': [99.0] * 25,
        'close': [100.0] * 25
    })
    with pytest.raises(ValueError):
        Backtester(invalid_data)

def test_position_management(backtester):
    """Teste la gestion des positions."""
    # Créer une position
    position = Position(
        symbol='TEST',
        direction='long',
        size=1000.0,
        entry_price=100.0,
        entry_time=datetime.now(timezone.utc),
        stop_loss=95.0,
        take_profit=105.0
    )
    
    # Tester le calcul de la valeur
    assert backtester._calculate_position_value(position, 102.0) == 2000.0
    
    # Tester le stop loss
    assert not backtester._check_stop_loss(position, 96.0)
    assert backtester._check_stop_loss(position, 94.0)
    
    # Tester le take profit
    assert not backtester._check_take_profit(position, 104.0)
    assert backtester._check_take_profit(position, 106.0)

def test_trade_execution(backtester):
    """Teste l'exécution des trades."""
    # Créer une position
    position = Position(
        symbol='TEST',
        direction='long',
        size=1000.0,
        entry_price=100.0,
        entry_time=datetime.now(timezone.utc)
    )
    
    # Fermer la position
    exit_time = datetime.now(timezone.utc)
    backtester._close_position(position, 105.0, exit_time)
    
    # Vérifier le trade
    assert len(backtester._trades) == 1
    trade = backtester._trades[0]
    assert trade.direction == 'long'
    assert trade.entry_price == 100.0
    assert trade.exit_price == 105.0
    assert trade.pnl == 5000.0
    assert trade.pnl_pct == 0.05
    
    # Vérifier la mise à jour du capital
    expected_fees = 1000.0 * 105.0 * 0.001
    expected_capital = 100000.0 + 5000.0 - expected_fees
    assert backtester._current_capital == pytest.approx(expected_capital)

def test_strategy_execution(backtester):
    """Teste l'exécution d'une stratégie complète."""
    strategy = SimpleStrategy()
    results = backtester.run(strategy)
    
    # Vérifier les résultats
    assert 'initial_capital' in results
    assert 'final_capital' in results
    assert 'total_return' in results
    assert 'sharpe_ratio' in results
    assert 'max_drawdown' in results
    assert 'trade_count' in results
    assert 'win_rate' in results
    assert 'profit_factor' in results
    assert 'equity_curve' in results
    assert 'trades' in results
    
    # Vérifier qu'il y a eu des trades
    assert len(results['trades']) > 0
    
    # Vérifier que l'equity curve est cohérente
    assert len(results['equity_curve']) > 0
    assert results['equity_curve'].iloc[0] == 100000.0

def test_metrics_calculation(backtester):
    """Teste le calcul des métriques de performance."""
    # Simuler quelques trades
    backtester._equity = [100000.0, 101000.0, 99000.0, 102000.0]
    backtester._trades = [
        Trade(
            symbol='TEST',
            direction='long',
            size=1000.0,
            entry_price=100.0,
            exit_price=101.0,
            entry_time=datetime.now(timezone.utc),
            exit_time=datetime.now(timezone.utc),
            pnl=1000.0,
            pnl_pct=0.01,
            fees=10.0
        ),
        Trade(
            symbol='TEST',
            direction='long',
            size=1000.0,
            entry_price=101.0,
            exit_price=99.0,
            entry_time=datetime.now(timezone.utc),
            exit_time=datetime.now(timezone.utc),
            pnl=-2000.0,
            pnl_pct=-0.02,
            fees=10.0
        )
    ]
    
    # Tester le calcul du drawdown maximum
    assert backtester._calculate_max_drawdown() == pytest.approx(-0.019801980198019802)
    
    # Tester le calcul du taux de réussite
    assert backtester._calculate_win_rate() == 0.5
    
    # Tester le calcul du facteur de profit
    assert backtester._calculate_profit_factor() == pytest.approx(0.5) 