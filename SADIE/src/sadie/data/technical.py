"""
Module de gestion des données techniques.
"""

import logging
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
import ta

from sadie.data.collectors.exceptions import ValidationError
from sadie.data.config import DataConfig

logger = logging.getLogger(__name__)

class TechnicalManager:
    """Gestionnaire de données techniques."""
    
    def __init__(self):
        """Initialise le gestionnaire de données techniques."""
        pass
    
    def add_momentum_indicators(
        self,
        df: pd.DataFrame,
        window: int = 14,
        fillna: bool = True
    ) -> pd.DataFrame:
        """
        Ajoute les indicateurs de momentum.
        
        Args:
            df: DataFrame avec les données OHLCV
            window: Fenêtre de calcul
            fillna: Remplir les valeurs manquantes
            
        Returns:
            DataFrame avec les indicateurs ajoutés
        """
        # RSI
        df["rsi"] = ta.momentum.RSIIndicator(
            close=df["close"],
            window=window,
            fillna=fillna
        ).rsi()
        
        # Stochastic RSI
        stoch_rsi = ta.momentum.StochRSIIndicator(
            close=df["close"],
            window=window,
            smooth1=3,
            smooth2=3,
            fillna=fillna
        )
        df["stoch_rsi_k"] = stoch_rsi.stochrsi_k()
        df["stoch_rsi_d"] = stoch_rsi.stochrsi_d()
        
        # MACD
        macd = ta.trend.MACD(
            close=df["close"],
            window_slow=26,
            window_fast=12,
            window_sign=9,
            fillna=fillna
        )
        df["macd"] = macd.macd()
        df["macd_signal"] = macd.macd_signal()
        df["macd_diff"] = macd.macd_diff()
        
        # TSI (True Strength Index)
        df["tsi"] = ta.momentum.TSIIndicator(
            close=df["close"],
            window_slow=25,
            window_fast=13,
            fillna=fillna
        ).tsi()
        
        return df
    
    def add_trend_indicators(
        self,
        df: pd.DataFrame,
        window: int = 14,
        fillna: bool = True
    ) -> pd.DataFrame:
        """
        Ajoute les indicateurs de tendance.
        
        Args:
            df: DataFrame avec les données OHLCV
            window: Fenêtre de calcul
            fillna: Remplir les valeurs manquantes
            
        Returns:
            DataFrame avec les indicateurs ajoutés
        """
        # ADX (Average Directional Index)
        adx = ta.trend.ADXIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=window,
            fillna=fillna
        )
        df["adx"] = adx.adx()
        df["adx_pos"] = adx.adx_pos()
        df["adx_neg"] = adx.adx_neg()
        
        # Aroon
        aroon = ta.trend.AroonIndicator(
            close=df["close"],
            window=window,
            fillna=fillna
        )
        df["aroon_up"] = aroon.aroon_up()
        df["aroon_down"] = aroon.aroon_down()
        df["aroon_indicator"] = aroon.aroon_indicator()
        
        # CCI (Commodity Channel Index)
        df["cci"] = ta.trend.CCIIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=window,
            constant=0.015,
            fillna=fillna
        ).cci()
        
        # DPO (Detrended Price Oscillator)
        df["dpo"] = ta.trend.DPOIndicator(
            close=df["close"],
            window=window,
            fillna=fillna
        ).dpo()
        
        return df
    
    def add_volatility_indicators(
        self,
        df: pd.DataFrame,
        window: int = 14,
        fillna: bool = True
    ) -> pd.DataFrame:
        """
        Ajoute les indicateurs de volatilité.
        
        Args:
            df: DataFrame avec les données OHLCV
            window: Fenêtre de calcul
            fillna: Remplir les valeurs manquantes
            
        Returns:
            DataFrame avec les indicateurs ajoutés
        """
        # Bollinger Bands
        bollinger = ta.volatility.BollingerBands(
            close=df["close"],
            window=window,
            window_dev=2,
            fillna=fillna
        )
        df["bb_high"] = bollinger.bollinger_hband()
        df["bb_mid"] = bollinger.bollinger_mavg()
        df["bb_low"] = bollinger.bollinger_lband()
        df["bb_width"] = bollinger.bollinger_wband()
        
        # ATR (Average True Range)
        df["atr"] = ta.volatility.AverageTrueRange(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=window,
            fillna=fillna
        ).average_true_range()
        
        # Donchian Channel
        donchian = ta.volatility.DonchianChannel(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=window,
            fillna=fillna
        )
        df["dc_high"] = donchian.donchian_channel_hband()
        df["dc_mid"] = donchian.donchian_channel_mband()
        df["dc_low"] = donchian.donchian_channel_lband()
        
        # Keltner Channel
        keltner = ta.volatility.KeltnerChannel(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            window=window,
            window_atr=10,
            fillna=fillna,
            multiplier=2
        )
        df["kc_high"] = keltner.keltner_channel_hband()
        df["kc_mid"] = keltner.keltner_channel_mband()
        df["kc_low"] = keltner.keltner_channel_lband()
        
        return df
    
    def add_volume_indicators(
        self,
        df: pd.DataFrame,
        window: int = 14,
        fillna: bool = True
    ) -> pd.DataFrame:
        """
        Ajoute les indicateurs de volume.
        
        Args:
            df: DataFrame avec les données OHLCV
            window: Fenêtre de calcul
            fillna: Remplir les valeurs manquantes
            
        Returns:
            DataFrame avec les indicateurs ajoutés
        """
        # Accumulation/Distribution
        df["ad"] = ta.volume.AccDistIndexIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            volume=df["volume"],
            fillna=fillna
        ).acc_dist_index()
        
        # Chaikin Money Flow
        df["cmf"] = ta.volume.ChaikinMoneyFlowIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            volume=df["volume"],
            window=window,
            fillna=fillna
        ).chaikin_money_flow()
        
        # Force Index
        df["fi"] = ta.volume.ForceIndexIndicator(
            close=df["close"],
            volume=df["volume"],
            window=window,
            fillna=fillna
        ).force_index()
        
        # Money Flow Index
        df["mfi"] = ta.volume.MFIIndicator(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            volume=df["volume"],
            window=window,
            fillna=fillna
        ).money_flow_index()
        
        # Volume Price Trend
        df["vpt"] = ta.volume.VolumePriceTrendIndicator(
            close=df["close"],
            volume=df["volume"],
            fillna=fillna
        ).volume_price_trend()
        
        # Volume Weighted Average Price
        df["vwap"] = ta.volume.VolumeWeightedAveragePrice(
            high=df["high"],
            low=df["low"],
            close=df["close"],
            volume=df["volume"],
            window=window,
            fillna=fillna
        ).volume_weighted_average_price()
        
        return df
    
    def add_all_indicators(
        self,
        df: pd.DataFrame,
        window: int = 14,
        fillna: bool = True
    ) -> pd.DataFrame:
        """
        Ajoute tous les indicateurs techniques.
        
        Args:
            df: DataFrame avec les données OHLCV
            window: Fenêtre de calcul
            fillna: Remplir les valeurs manquantes
            
        Returns:
            DataFrame avec les indicateurs ajoutés
        """
        df = self.add_momentum_indicators(df, window, fillna)
        df = self.add_trend_indicators(df, window, fillna)
        df = self.add_volatility_indicators(df, window, fillna)
        df = self.add_volume_indicators(df, window, fillna)
        return df 