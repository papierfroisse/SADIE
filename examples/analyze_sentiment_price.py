"""Script for analyzing sentiment data alongside price data."""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import mutual_info_score
from sklearn.preprocessing import StandardScaler

from sadie.data.collectors.sentiment import (
    get_sentiment_category,
    calculate_weighted_sentiment,
)
from sadie.storage.database import DatabaseManager


async def fetch_data(
    db_manager: DatabaseManager,
    symbol: str,
    days: int = 30,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch sentiment and price data for analysis.
    
    Args:
        db_manager: Database manager instance
        symbol: Trading pair symbol
        days: Number of days of data to fetch
    
    Returns:
        Tuple of (sentiment_df, price_df)
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Fetch sentiment data
    sentiment_data = await db_manager.get_sentiment(
        symbol=symbol,
        start_time=start_time,
        end_time=end_time,
    )
    
    # Fetch price data
    price_data = await db_manager.get_ohlcv(
        symbol=symbol,
        start_time=start_time,
        end_time=end_time,
        interval="1m",
    )
    
    # Convert to DataFrames
    sentiment_df = pd.DataFrame(sentiment_data)
    sentiment_df["created_at"] = pd.to_datetime(sentiment_df["created_at"])
    sentiment_df.set_index("created_at", inplace=True)
    
    price_df = pd.DataFrame(price_data)
    price_df["timestamp"] = pd.to_datetime(price_df["timestamp"])
    price_df.set_index("timestamp", inplace=True)
    
    return sentiment_df, price_df


def calculate_price_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate price-based metrics.
    
    Args:
        df: Price DataFrame
    
    Returns:
        DataFrame with additional metrics
    """
    # Calculate returns
    df["returns"] = df["close"].pct_change()
    df["log_returns"] = np.log(df["close"]) - np.log(df["close"].shift(1))
    
    # Calculate volatility
    df["volatility"] = df["returns"].rolling(window=30).std()
    
    # Calculate price momentum
    df["momentum_1h"] = df["close"].pct_change(periods=60)
    df["momentum_4h"] = df["close"].pct_change(periods=240)
    df["momentum_24h"] = df["close"].pct_change(periods=1440)
    
    # Calculate trading volume metrics
    df["volume_ma"] = df["volume"].rolling(window=30).mean()
    df["volume_ratio"] = df["volume"] / df["volume_ma"]
    
    # Calculate price levels
    df["price_ma_1h"] = df["close"].rolling(window=60).mean()
    df["price_ma_4h"] = df["close"].rolling(window=240).mean()
    df["price_ma_24h"] = df["close"].rolling(window=1440).mean()
    
    return df


def calculate_sentiment_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate sentiment-based metrics.
    
    Args:
        df: Sentiment DataFrame
    
    Returns:
        DataFrame with additional metrics
    """
    # Resample to minute intervals
    resampled = df.resample("1min").agg({
        "polarity": "mean",
        "subjectivity": "mean",
        "tweet_id": "count",
        "user_followers": "mean",
        "retweet_count": "sum",
        "favorite_count": "sum",
    }).rename(columns={"tweet_id": "volume"})
    
    # Calculate moving averages
    resampled["polarity_ma_1h"] = resampled["polarity"].rolling(window=60).mean()
    resampled["volume_ma_1h"] = resampled["volume"].rolling(window=60).mean()
    
    # Calculate sentiment momentum
    resampled["sentiment_momentum_1h"] = resampled["polarity"].diff(periods=60)
    resampled["sentiment_momentum_4h"] = resampled["polarity"].diff(periods=240)
    
    # Calculate weighted metrics
    resampled["weighted_sentiment"] = resampled.apply(
        lambda x: calculate_weighted_sentiment(
            x["polarity"],
            x["user_followers"],
            x["retweet_count"],
            x["favorite_count"],
        ) if pd.notnull(x["polarity"]) else np.nan,
        axis=1,
    )
    
    return resampled


def analyze_correlation(
    sentiment_df: pd.DataFrame,
    price_df: pd.DataFrame,
    windows: List[int] = [1, 5, 15, 30, 60, 240],
) -> Dict[str, pd.DataFrame]:
    """Analyze correlation between sentiment and price metrics.
    
    Args:
        sentiment_df: Sentiment DataFrame
        price_df: Price DataFrame
        windows: List of window sizes in minutes
    
    Returns:
        Dictionary containing correlation analysis results
    """
    results = {}
    
    # Merge DataFrames
    df = pd.merge(
        sentiment_df,
        price_df,
        left_index=True,
        right_index=True,
        how="inner",
    )
    
    # Calculate correlations for different time windows
    for window in windows:
        # Rolling correlation
        rolling_corr = df["polarity"].rolling(window=window).corr(df["returns"])
        
        # Lagged correlations
        lags = range(-window, window + 1)
        lag_corrs = [
            df["polarity"].corr(df["returns"].shift(lag))
            for lag in lags
        ]
        
        # Mutual information
        mi = mutual_info_score(
            df["polarity"].fillna(0),
            pd.qcut(df["returns"].fillna(0), q=10, labels=False),
        )
        
        results[f"{window}min"] = pd.DataFrame({
            "rolling_correlation": rolling_corr,
            "lag_correlations": pd.Series(lag_corrs, index=lags),
            "mutual_information": mi,
        })
    
    return results


def analyze_predictive_power(
    sentiment_df: pd.DataFrame,
    price_df: pd.DataFrame,
    forward_windows: List[int] = [5, 15, 30, 60],
) -> pd.DataFrame:
    """Analyze predictive power of sentiment on future returns.
    
    Args:
        sentiment_df: Sentiment DataFrame
        price_df: Price DataFrame
        forward_windows: List of forward-looking windows in minutes
    
    Returns:
        DataFrame containing prediction analysis results
    """
    results = []
    
    # Merge DataFrames
    df = pd.merge(
        sentiment_df,
        price_df,
        left_index=True,
        right_index=True,
        how="inner",
    )
    
    # Calculate forward returns
    for window in forward_windows:
        forward_returns = df["close"].pct_change(periods=window).shift(-window)
        
        # Split data into quantiles based on sentiment
        sentiment_quantiles = pd.qcut(df["weighted_sentiment"], q=5)
        
        # Calculate average forward returns for each sentiment quantile
        returns_by_sentiment = forward_returns.groupby(sentiment_quantiles).agg([
            "mean",
            "std",
            "count",
        ])
        
        # Calculate information coefficient
        ic = df["weighted_sentiment"].corr(forward_returns)
        
        # Perform statistical tests
        high_sentiment = forward_returns[df["weighted_sentiment"] > df["weighted_sentiment"].quantile(0.8)]
        low_sentiment = forward_returns[df["weighted_sentiment"] < df["weighted_sentiment"].quantile(0.2)]
        
        tstat, pvalue = stats.ttest_ind(
            high_sentiment.dropna(),
            low_sentiment.dropna(),
        )
        
        results.append({
            "window": window,
            "returns_by_sentiment": returns_by_sentiment,
            "information_coefficient": ic,
            "tstat": tstat,
            "pvalue": pvalue,
        })
    
    return pd.DataFrame(results)


def analyze_regime_dependence(
    sentiment_df: pd.DataFrame,
    price_df: pd.DataFrame,
) -> Dict[str, pd.DataFrame]:
    """Analyze regime-dependent relationships between sentiment and price.
    
    Args:
        sentiment_df: Sentiment DataFrame
        price_df: Price DataFrame
    
    Returns:
        Dictionary containing regime analysis results
    """
    # Merge DataFrames
    df = pd.merge(
        sentiment_df,
        price_df,
        left_index=True,
        right_index=True,
        how="inner",
    )
    
    results = {}
    
    # Volatility regimes
    vol = df["returns"].rolling(window=30).std()
    vol_regimes = pd.qcut(vol, q=3, labels=["low", "medium", "high"])
    
    results["volatility"] = df.groupby(vol_regimes).agg({
        "polarity": ["mean", "std", "corr"],
        "returns": ["mean", "std"],
        "volume": "mean",
    })
    
    # Trend regimes
    momentum = df["close"].pct_change(periods=1440)  # 24h momentum
    trend_regimes = pd.qcut(momentum, q=3, labels=["down", "flat", "up"])
    
    results["trend"] = df.groupby(trend_regimes).agg({
        "polarity": ["mean", "std", "corr"],
        "returns": ["mean", "std"],
        "volume": "mean",
    })
    
    # Volume regimes
    volume_ratio = df["volume"] / df["volume"].rolling(window=1440).mean()
    volume_regimes = pd.qcut(volume_ratio, q=3, labels=["low", "medium", "high"])
    
    results["volume"] = df.groupby(volume_regimes).agg({
        "polarity": ["mean", "std", "corr"],
        "returns": ["mean", "std"],
        "volume": "mean",
    })
    
    return results


async def main():
    """Run sentiment and price analysis."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)
    
    # Initialize database manager
    db_manager = DatabaseManager(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "sadie"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
    )
    await db_manager.connect()
    
    try:
        # Analyze multiple symbols
        symbols = ["BTCUSDT", "ETHUSDT"]
        
        for symbol in symbols:
            logger.info("Analyzing %s...", symbol)
            
            # Fetch data
            sentiment_df, price_df = await fetch_data(
                db_manager=db_manager,
                symbol=symbol,
                days=30,
            )
            
            if len(sentiment_df) == 0 or len(price_df) == 0:
                logger.warning("No data found for %s", symbol)
                continue
            
            # Calculate metrics
            price_df = calculate_price_metrics(price_df)
            sentiment_df = calculate_sentiment_metrics(sentiment_df)
            
            # Analyze correlations
            correlations = analyze_correlation(sentiment_df, price_df)
            
            logger.info("\nCorrelation Analysis:")
            for window, corr in correlations.items():
                logger.info(
                    "%s window - Avg correlation: %.3f, Max lag correlation: %.3f",
                    window,
                    corr["rolling_correlation"].mean(),
                    corr["lag_correlations"].max(),
                )
            
            # Analyze predictive power
            predictions = analyze_predictive_power(sentiment_df, price_df)
            
            logger.info("\nPredictive Power Analysis:")
            for _, row in predictions.iterrows():
                logger.info(
                    "%dmin forward window - IC: %.3f, t-stat: %.2f, p-value: %.3f",
                    row["window"],
                    row["information_coefficient"],
                    row["tstat"],
                    row["pvalue"],
                )
            
            # Analyze regime dependence
            regimes = analyze_regime_dependence(sentiment_df, price_df)
            
            logger.info("\nRegime Analysis:")
            for regime_type, analysis in regimes.items():
                logger.info("\n%s regimes:", regime_type.capitalize())
                logger.info(analysis)
    
    except Exception as e:
        logger.error("Error during analysis: %s", str(e), exc_info=True)
    
    finally:
        # Clean up
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 