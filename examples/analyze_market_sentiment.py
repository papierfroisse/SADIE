"""Advanced market sentiment analysis combining price and sentiment data."""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import adfuller, grangercausalitytests

from sadie.data.collectors.sentiment import (
    get_sentiment_category,
    calculate_weighted_sentiment,
)
from sadie.storage.database import DatabaseManager


class MarketSentimentAnalyzer:
    """Advanced market sentiment analyzer."""
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        symbol: str,
        lookback_days: int = 30,
        min_tweets: int = 1000,
        significance_level: float = 0.05,
    ):
        """Initialize the analyzer.
        
        Args:
            db_manager: Database manager instance
            symbol: Trading pair symbol
            lookback_days: Days of historical data to analyze
            min_tweets: Minimum number of tweets required
            significance_level: Statistical significance level
        """
        self.db_manager = db_manager
        self.symbol = symbol
        self.lookback_days = lookback_days
        self.min_tweets = min_tweets
        self.significance_level = significance_level
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
    
    async def fetch_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Fetch price and sentiment data.
        
        Returns:
            Tuple of (price_df, sentiment_df)
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=self.lookback_days)
        
        # Fetch price data
        price_data = await self.db_manager.get_ohlcv(
            symbol=self.symbol,
            start_time=start_time,
            end_time=end_time,
            interval="1m",
        )
        
        # Fetch sentiment data
        sentiment_data = await self.db_manager.get_sentiment(
            symbol=self.symbol,
            start_time=start_time,
            end_time=end_time,
        )
        
        if not price_data or not sentiment_data:
            raise ValueError("Insufficient data for analysis")
        
        # Convert to DataFrames
        price_df = pd.DataFrame(price_data)
        price_df["timestamp"] = pd.to_datetime(price_df["timestamp"])
        price_df.set_index("timestamp", inplace=True)
        
        sentiment_df = pd.DataFrame(sentiment_data)
        sentiment_df["created_at"] = pd.to_datetime(sentiment_df["created_at"])
        sentiment_df.set_index("created_at", inplace=True)
        
        return price_df, sentiment_df
    
    def detect_market_regimes(
        self,
        price_df: pd.DataFrame,
        n_regimes: int = 3,
    ) -> pd.Series:
        """Detect market regimes using price action.
        
        Args:
            price_df: Price DataFrame
            n_regimes: Number of regimes to detect
        
        Returns:
            Series of regime labels
        """
        # Calculate features for regime detection
        features = pd.DataFrame()
        
        # Returns and volatility
        features["returns"] = price_df["close"].pct_change()
        features["volatility"] = features["returns"].rolling(window=30).std()
        
        # Volume and price trends
        features["volume_ratio"] = price_df["volume"] / price_df["volume"].rolling(window=30).mean()
        features["price_trend"] = price_df["close"].pct_change(periods=60)  # 1-hour trend
        
        # Standardize features
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features.fillna(0))
        
        # Detect regimes using KMeans
        kmeans = KMeans(n_clusters=n_regimes, random_state=42)
        regimes = kmeans.fit_predict(scaled_features)
        
        return pd.Series(regimes, index=price_df.index)
    
    def analyze_sentiment_impact(
        self,
        price_df: pd.DataFrame,
        sentiment_df: pd.DataFrame,
        regimes: pd.Series,
    ) -> Dict:
        """Analyze sentiment impact across market regimes.
        
        Args:
            price_df: Price DataFrame
            sentiment_df: Sentiment DataFrame
            regimes: Market regime labels
        
        Returns:
            Dictionary containing impact analysis results
        """
        results = {}
        
        # Resample sentiment to match price data
        resampled_sentiment = sentiment_df.resample("1min").agg({
            "polarity": "mean",
            "subjectivity": "mean",
            "tweet_id": "count",
        }).fillna(method="ffill")
        
        # Merge data
        df = pd.merge(
            price_df,
            resampled_sentiment,
            left_index=True,
            right_index=True,
            how="inner",
        )
        df["regime"] = regimes
        
        # Analyze each regime
        for regime in df["regime"].unique():
            regime_data = df[df["regime"] == regime]
            
            # Calculate correlations
            correlations = {}
            for lag in range(0, 61, 5):  # Up to 1 hour lag
                sentiment_lagged = regime_data["polarity"].shift(lag)
                correlations[lag] = regime_data["returns"].corr(sentiment_lagged)
            
            # Find optimal lag
            optimal_lag = max(correlations.items(), key=lambda x: abs(x[1]))
            
            # Test Granger causality
            sentiment_lagged = regime_data["polarity"].shift(optimal_lag[0])
            granger_test = grangercausalitytests(
                pd.concat([regime_data["returns"], sentiment_lagged], axis=1).dropna(),
                maxlag=1,
                verbose=False,
            )
            
            # Calculate impact metrics
            impact = {
                "correlation": correlations[optimal_lag[0]],
                "optimal_lag": optimal_lag[0],
                "granger_pvalue": granger_test[1][0]["ssr_chi2test"][1],
                "avg_sentiment": regime_data["polarity"].mean(),
                "avg_returns": regime_data["returns"].mean(),
                "volatility": regime_data["returns"].std(),
                "tweet_volume": regime_data["tweet_id"].mean(),
            }
            
            results[f"regime_{regime}"] = impact
        
        return results
    
    def test_predictive_power(
        self,
        price_df: pd.DataFrame,
        sentiment_df: pd.DataFrame,
        forward_windows: List[int] = [5, 15, 30, 60],
    ) -> pd.DataFrame:
        """Test predictive power of sentiment on future returns.
        
        Args:
            price_df: Price DataFrame
            sentiment_df: Sentiment DataFrame
            forward_windows: List of forward-looking windows in minutes
        
        Returns:
            DataFrame containing prediction test results
        """
        results = []
        
        # Resample sentiment to match price data
        resampled_sentiment = sentiment_df.resample("1min").agg({
            "polarity": "mean",
            "subjectivity": "mean",
            "tweet_id": "count",
        }).fillna(method="ffill")
        
        # Merge data
        df = pd.merge(
            price_df,
            resampled_sentiment,
            left_index=True,
            right_index=True,
            how="inner",
        )
        
        for window in forward_windows:
            # Calculate forward returns
            df[f"fwd_returns_{window}"] = df["close"].pct_change(periods=window).shift(-window)
            
            # Split data by sentiment quantiles
            sentiment_quantiles = pd.qcut(df["polarity"], q=5)
            
            # Calculate returns by sentiment quantile
            returns_by_sentiment = df.groupby(sentiment_quantiles)[f"fwd_returns_{window}"].agg([
                "mean",
                "std",
                "count",
            ])
            
            # Calculate information ratio
            ir = returns_by_sentiment["mean"] / returns_by_sentiment["std"]
            
            # Perform statistical tests
            high_sentiment = df[df["polarity"] > df["polarity"].quantile(0.8)][f"fwd_returns_{window}"]
            low_sentiment = df[df["polarity"] < df["polarity"].quantile(0.2)][f"fwd_returns_{window}"]
            
            tstat, pvalue = stats.ttest_ind(
                high_sentiment.dropna(),
                low_sentiment.dropna(),
            )
            
            results.append({
                "window": window,
                "returns_by_sentiment": returns_by_sentiment,
                "information_ratio": ir,
                "tstat": tstat,
                "pvalue": pvalue,
            })
        
        return pd.DataFrame(results)
    
    def analyze_tweet_influence(
        self,
        sentiment_df: pd.DataFrame,
        min_tweets: int = 10,
    ) -> pd.DataFrame:
        """Analyze influence of individual tweets and users.
        
        Args:
            sentiment_df: Sentiment DataFrame
            min_tweets: Minimum number of tweets per user
        
        Returns:
            DataFrame containing user influence analysis
        """
        # Group by user
        user_stats = sentiment_df.groupby("user_id").agg({
            "polarity": ["mean", "std", "count"],
            "user_followers": "first",
            "retweet_count": "mean",
            "favorite_count": "mean",
        })
        
        # Flatten column names
        user_stats.columns = [
            f"{col[0]}_{col[1]}" if col[1] else col[0]
            for col in user_stats.columns
        ]
        
        # Filter users with minimum number of tweets
        user_stats = user_stats[user_stats["polarity_count"] >= min_tweets]
        
        # Calculate influence score
        user_stats["influence_score"] = (
            user_stats["polarity_mean"].abs() *
            np.log1p(user_stats["user_followers"]) *
            np.log1p(user_stats["retweet_count"]) *
            np.log1p(user_stats["favorite_count"])
        )
        
        return user_stats.sort_values("influence_score", ascending=False)
    
    async def run_analysis(self) -> Dict:
        """Run complete market sentiment analysis.
        
        Returns:
            Dictionary containing all analysis results
        """
        try:
            # Fetch data
            price_df, sentiment_df = await self.fetch_data()
            
            if len(sentiment_df) < self.min_tweets:
                raise ValueError(f"Insufficient tweets: {len(sentiment_df)} < {self.min_tweets}")
            
            # Detect market regimes
            regimes = self.detect_market_regimes(price_df)
            
            # Analyze sentiment impact
            impact_analysis = self.analyze_sentiment_impact(
                price_df,
                sentiment_df,
                regimes,
            )
            
            # Test predictive power
            prediction_tests = self.test_predictive_power(
                price_df,
                sentiment_df,
            )
            
            # Analyze tweet influence
            influence_analysis = self.analyze_tweet_influence(sentiment_df)
            
            return {
                "impact_analysis": impact_analysis,
                "prediction_tests": prediction_tests,
                "influence_analysis": influence_analysis.to_dict(),
                "data_summary": {
                    "price_points": len(price_df),
                    "sentiment_points": len(sentiment_df),
                    "unique_users": sentiment_df["user_id"].nunique(),
                    "time_range": {
                        "start": price_df.index.min(),
                        "end": price_df.index.max(),
                    },
                },
            }
        
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise


async def main():
    """Run market sentiment analysis example."""
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
        # Create analyzer
        analyzer = MarketSentimentAnalyzer(
            db_manager=db_manager,
            symbol="BTCUSDT",
            lookback_days=30,
            min_tweets=1000,
        )
        
        # Run analysis
        results = await analyzer.run_analysis()
        
        # Log results
        logger.info("\nMarket Sentiment Analysis Results:")
        
        logger.info("\nData Summary:")
        for key, value in results["data_summary"].items():
            logger.info(f"  {key}: {value}")
        
        logger.info("\nSentiment Impact Analysis:")
        for regime, impact in results["impact_analysis"].items():
            logger.info(f"\n{regime}:")
            for metric, value in impact.items():
                logger.info(f"  {metric}: {value:.3f}")
        
        logger.info("\nPredictive Power Tests:")
        for _, row in results["prediction_tests"].iterrows():
            logger.info(
                f"\n{row['window']}min forward window:"
                f"\n  Information Ratio: {row['information_ratio'].mean():.3f}"
                f"\n  t-statistic: {row['tstat']:.2f}"
                f"\n  p-value: {row['pvalue']:.3f}"
            )
        
        logger.info("\nTop Influential Users:")
        influence_df = pd.DataFrame.from_dict(results["influence_analysis"])
        for user_id in influence_df.sort_values("influence_score", ascending=False).head().index:
            user = influence_df.loc[user_id]
            logger.info(
                f"\nUser {user_id}:"
                f"\n  Followers: {user['user_followers']:,}"
                f"\n  Avg Retweets: {user['retweet_count']:.1f}"
                f"\n  Influence Score: {user['influence_score']:.3f}"
            )
    
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
    
    finally:
        # Clean up
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 