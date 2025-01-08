"""Unit tests for order book metrics."""
import pytest
import numpy as np
from sadie.analysis.orderbook_metrics import OrderBookAnalyzer, OrderBookMetrics

@pytest.fixture
def analyzer():
    """Create an analyzer instance for testing."""
    return OrderBookAnalyzer(window_size=10, depth_levels=5)

@pytest.fixture
def sample_orderbook():
    """Create sample order book data."""
    bids = [
        (100.0, 1.0),  # price, quantity
        (99.5, 2.0),
        (99.0, 3.0),
        (98.5, 4.0),
        (98.0, 5.0),
    ]
    asks = [
        (101.0, 1.0),
        (101.5, 2.0),
        (102.0, 3.0),
        (102.5, 4.0),
        (103.0, 5.0),
    ]
    return bids, asks

def test_initialization(analyzer):
    """Test analyzer initialization."""
    assert analyzer.window_size == 10
    assert analyzer.depth_levels == 5
    assert len(analyzer.price_history) == 0

def test_compute_spread(analyzer, sample_orderbook):
    """Test spread calculation."""
    bids, asks = sample_orderbook
    spread = analyzer._compute_spread(bids[0][0], asks[0][0])
    assert spread == 1.0  # 101.0 - 100.0

def test_compute_weighted_mid_price(analyzer, sample_orderbook):
    """Test weighted mid price calculation."""
    bids, asks = sample_orderbook
    weighted_mid = analyzer._compute_weighted_mid_price(bids, asks)
    
    # Manual calculation for verification
    bid_volume = sum(qty for _, qty in bids[:5])
    ask_volume = sum(qty for _, qty in asks[:5])
    
    weighted_bid = sum(price * qty for price, qty in bids[:5]) / bid_volume
    weighted_ask = sum(price * qty for price, qty in asks[:5]) / ask_volume
    
    expected = (weighted_bid + weighted_ask) / 2
    assert abs(weighted_mid - expected) < 1e-6

def test_compute_depth(analyzer, sample_orderbook):
    """Test depth calculation."""
    bids, asks = sample_orderbook
    bid_depth = analyzer._compute_depth(bids)
    ask_depth = analyzer._compute_depth(asks)
    
    assert bid_depth == 15.0  # 1 + 2 + 3 + 4 + 5
    assert ask_depth == 15.0  # 1 + 2 + 3 + 4 + 5

def test_compute_imbalance(analyzer):
    """Test imbalance calculation."""
    imbalance = analyzer._compute_imbalance(bid_depth=20.0, ask_depth=10.0)
    assert imbalance == 0.3333333333333333  # (20 - 10) / (20 + 10)

def test_compute_pressure(analyzer, sample_orderbook):
    """Test pressure calculation."""
    bids, asks = sample_orderbook
    pressure = analyzer._compute_pressure(bids, asks)
    
    # Pressure should be close to 0 for symmetric book
    assert abs(pressure) < 1e-6

def test_compute_volatility(analyzer):
    """Test volatility calculation."""
    # Add some price history
    prices = [100.0, 101.0, 99.0, 100.5, 101.5]
    for price in prices:
        analyzer.price_history.append(price)
        
    volatility = analyzer._compute_volatility()
    assert volatility > 0  # Should be positive for varying prices

def test_compute_liquidity_score(analyzer):
    """Test liquidity score calculation."""
    score = analyzer._compute_liquidity_score(
        spread=1.0,
        bid_depth=100.0,
        ask_depth=100.0
    )
    assert 0 <= score <= 1  # Score should be normalized

def test_compute_metrics_empty_book(analyzer):
    """Test metrics computation with empty order book."""
    with pytest.raises(ValueError):
        analyzer.compute_metrics([], [])

def test_compute_metrics_full(analyzer, sample_orderbook):
    """Test full metrics computation."""
    bids, asks = sample_orderbook
    metrics = analyzer.compute_metrics(bids, asks)
    
    assert isinstance(metrics, OrderBookMetrics)
    assert metrics.spread == 1.0
    assert metrics.mid_price == 100.5
    assert metrics.bid_depth == 15.0
    assert metrics.ask_depth == 15.0
    assert abs(metrics.imbalance) < 1e-6  # Symmetric book
    assert 0 <= metrics.liquidity_score <= 1

def test_metrics_consistency(analyzer):
    """Test metrics consistency over multiple updates."""
    bids = [(100.0, 1.0), (99.0, 2.0)]
    asks = [(101.0, 1.0), (102.0, 2.0)]
    
    # Compute metrics multiple times
    metrics1 = analyzer.compute_metrics(bids, asks)
    metrics2 = analyzer.compute_metrics(bids, asks)
    
    # Basic metrics should be identical
    assert metrics1.spread == metrics2.spread
    assert metrics1.mid_price == metrics2.mid_price
    assert metrics1.bid_depth == metrics2.bid_depth
    assert metrics1.ask_depth == metrics2.ask_depth
    
    # Volatility might change as we add more history
    assert metrics2.volatility >= 0

def test_metrics_with_extreme_values(analyzer):
    """Test metrics computation with extreme values."""
    bids = [(1e6, 1e6), (0.99e6, 1e6)]
    asks = [(1.01e6, 1e6), (1.02e6, 1e6)]
    
    metrics = analyzer.compute_metrics(bids, asks)
    
    assert np.isfinite(metrics.spread)
    assert np.isfinite(metrics.mid_price)
    assert np.isfinite(metrics.weighted_mid_price)
    assert np.isfinite(metrics.bid_depth)
    assert np.isfinite(metrics.ask_depth)
    assert np.isfinite(metrics.imbalance)
    assert np.isfinite(metrics.pressure)
    assert np.isfinite(metrics.volatility)
    assert np.isfinite(metrics.liquidity_score) 