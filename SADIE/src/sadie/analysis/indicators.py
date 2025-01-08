"""Technical indicators module for SADIE."""
from typing import List, Dict, Union, Optional
import numpy as np
import pandas as pd
import talib
from dataclasses import dataclass

@dataclass
class IndicatorConfig:
    """Configuration for technical indicators."""
    
    # Moving Averages
    ma_periods: List[int] = (20, 50, 200)
    ema_periods: List[int] = (12, 26)
    
    # Oscillators
    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # Volatility
    bb_period: int = 20
    bb_std: float = 2.0
    atr_period: int = 14
    
    # Volume
    obv_smooth: int = 10
    vwap_period: int = 14

class TechnicalAnalysis:
    """Technical analysis class with advanced indicators."""
    
    def __init__(self, config: Optional[IndicatorConfig] = None):
        """Initialize technical analysis with configuration."""
        self.config = config or IndicatorConfig()
        
    def calculate_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators."""
        result = df.copy()
        
        # Moving Averages
        for period in self.config.ma_periods:
            result[f'sma_{period}'] = talib.SMA(df['close'], timeperiod=period)
            
        for period in self.config.ema_periods:
            result[f'ema_{period}'] = talib.EMA(df['close'], timeperiod=period)
            
        # MACD
        macd, signal, hist = talib.MACD(
            df['close'],
            fastperiod=self.config.macd_fast,
            slowperiod=self.config.macd_slow,
            signalperiod=self.config.macd_signal
        )
        result['macd'] = macd
        result['macd_signal'] = signal
        result['macd_hist'] = hist
        
        # RSI
        result['rsi'] = talib.RSI(df['close'], timeperiod=self.config.rsi_period)
        
        # Bollinger Bands
        upper, middle, lower = talib.BBANDS(
            df['close'],
            timeperiod=self.config.bb_period,
            nbdevup=self.config.bb_std,
            nbdevdn=self.config.bb_std
        )
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower
        
        # ATR
        result['atr'] = talib.ATR(
            df['high'],
            df['low'],
            df['close'],
            timeperiod=self.config.atr_period
        )
        
        # Volume Indicators
        result['obv'] = talib.OBV(df['close'], df['volume'])
        result['obv_ema'] = talib.EMA(result['obv'], timeperiod=self.config.obv_smooth)
        
        # VWAP
        result['vwap'] = self._calculate_vwap(df)
        
        # Additional Advanced Indicators
        self._add_advanced_indicators(df, result)
        
        return result
        
    def _calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """Calculate Volume Weighted Average Price."""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        return (typical_price * df['volume']).rolling(
            window=self.config.vwap_period
        ).sum() / df['volume'].rolling(window=self.config.vwap_period).sum()
        
    def _add_advanced_indicators(self, source: pd.DataFrame, target: pd.DataFrame) -> None:
        """Add advanced technical indicators."""
        # Momentum
        target['momentum'] = talib.MOM(source['close'], timeperiod=10)
        target['roc'] = talib.ROC(source['close'], timeperiod=10)
        
        # Stochastic
        slowk, slowd = talib.STOCH(
            source['high'],
            source['low'],
            source['close'],
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0
        )
        target['stoch_k'] = slowk
        target['stoch_d'] = slowd
        
        # ADX
        target['adx'] = talib.ADX(
            source['high'],
            source['low'],
            source['close'],
            timeperiod=14
        )
        
        # Ichimoku Cloud
        self._add_ichimoku(source, target)
        
    def _add_ichimoku(self, source: pd.DataFrame, target: pd.DataFrame) -> None:
        """Add Ichimoku Cloud indicators."""
        high_values = source['high']
        low_values = source['low']
        
        # Tenkan-sen (Conversion Line)
        period9_high = high_values.rolling(window=9).max()
        period9_low = low_values.rolling(window=9).min()
        target['ichimoku_tenkan'] = (period9_high + period9_low) / 2
        
        # Kijun-sen (Base Line)
        period26_high = high_values.rolling(window=26).max()
        period26_low = low_values.rolling(window=26).min()
        target['ichimoku_kijun'] = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A)
        target['ichimoku_senkou_a'] = ((target['ichimoku_tenkan'] + target['ichimoku_kijun']) / 2).shift(26)
        
        # Senkou Span B (Leading Span B)
        period52_high = high_values.rolling(window=52).max()
        period52_low = low_values.rolling(window=52).min()
        target['ichimoku_senkou_b'] = ((period52_high + period52_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span)
        target['ichimoku_chikou'] = source['close'].shift(-26)
        
    def get_signals(self, df: pd.DataFrame) -> Dict[str, float]:
        """Generate trading signals based on technical indicators."""
        signals = {}
        
        # Moving Average Crossovers
        for slow_ma in [50, 200]:
            fast_ma = 20
            signals[f'ma_cross_{fast_ma}_{slow_ma}'] = (
                (df[f'sma_{fast_ma}'] > df[f'sma_{slow_ma}']).astype(float).iloc[-1]
            )
        
        # RSI Signals
        rsi = df['rsi'].iloc[-1]
        signals['rsi_oversold'] = 1.0 if rsi < 30 else 0.0
        signals['rsi_overbought'] = 1.0 if rsi > 70 else 0.0
        
        # MACD Signals
        signals['macd_cross'] = (
            (df['macd'] > df['macd_signal']).astype(float).iloc[-1]
        )
        
        # Bollinger Bands
        close = df['close'].iloc[-1]
        signals['bb_lower_break'] = 1.0 if close < df['bb_lower'].iloc[-1] else 0.0
        signals['bb_upper_break'] = 1.0 if close > df['bb_upper'].iloc[-1] else 0.0
        
        # Volume Signals
        signals['volume_surge'] = (
            (df['volume'] > df['volume'].rolling(20).mean() * 2).astype(float).iloc[-1]
        )
        
        # Trend Strength
        signals['adx_strong_trend'] = 1.0 if df['adx'].iloc[-1] > 25 else 0.0
        
        return signals 