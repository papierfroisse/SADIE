"""Script for analyzing collected sentiment data."""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from textblob import TextBlob

from sadie.data.collectors.sentiment import (
    get_sentiment_category,
    get_subjectivity_category,
    calculate_weighted_sentiment,
)
from sadie.storage.database import DatabaseManager


async def fetch_sentiment_data(
    db_manager: DatabaseManager,
    symbol: str,
    days: int = 7,
) -> List[Dict]:
    """Fetch sentiment data for analysis.
    
    Args:
        db_manager: Database manager instance
        symbol: Trading pair symbol
        days: Number of days of data to fetch
    
    Returns:
        List of sentiment records
    """
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    return await db_manager.get_sentiment(
        symbol=symbol,
        start_time=start_time,
        end_time=end_time,
    )


def analyze_sentiment_distribution(data: List[Dict]) -> Dict:
    """Analyze sentiment score distribution.
    
    Args:
        data: List of sentiment records
    
    Returns:
        Dictionary containing distribution metrics
    """
    polarities = [record["polarity"] for record in data]
    subjectivities = [record["subjectivity"] for record in data]
    
    return {
        "polarity": {
            "mean": np.mean(polarities),
            "median": np.median(polarities),
            "std": np.std(polarities),
            "skew": stats.skew(polarities),
            "kurtosis": stats.kurtosis(polarities),
        },
        "subjectivity": {
            "mean": np.mean(subjectivities),
            "median": np.median(subjectivities),
            "std": np.std(subjectivities),
            "skew": stats.skew(subjectivities),
            "kurtosis": stats.kurtosis(subjectivities),
        },
    }


def analyze_temporal_patterns(data: List[Dict]) -> pd.DataFrame:
    """Analyze temporal patterns in sentiment.
    
    Args:
        data: List of sentiment records
    
    Returns:
        DataFrame with temporal analysis
    """
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df["created_at"] = pd.to_datetime(df["created_at"])
    df.set_index("created_at", inplace=True)
    
    # Resample to hourly intervals
    hourly = df.resample("1H").agg({
        "polarity": "mean",
        "subjectivity": "mean",
        "tweet_id": "count",
    }).rename(columns={"tweet_id": "volume"})
    
    # Calculate rolling averages
    hourly["polarity_ma"] = hourly["polarity"].rolling(window=24).mean()
    hourly["volume_ma"] = hourly["volume"].rolling(window=24).mean()
    
    return hourly


def analyze_user_influence(data: List[Dict]) -> pd.DataFrame:
    """Analyze user influence on sentiment.
    
    Args:
        data: List of sentiment records
    
    Returns:
        DataFrame with user influence analysis
    """
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Calculate weighted sentiment
    df["weighted_sentiment"] = df.apply(
        lambda x: calculate_weighted_sentiment(
            x["polarity"],
            x["user_followers"],
            x["retweet_count"],
            x["favorite_count"],
        ),
        axis=1,
    )
    
    # Group by user
    user_stats = df.groupby("user_id").agg({
        "polarity": ["mean", "std", "count"],
        "weighted_sentiment": "mean",
        "user_followers": "first",
        "retweet_count": "mean",
        "favorite_count": "mean",
    })
    
    # Flatten column names
    user_stats.columns = [
        f"{col[0]}_{col[1]}" if col[1] else col[0]
        for col in user_stats.columns
    ]
    
    return user_stats.sort_values("weighted_sentiment_mean", ascending=False)


def plot_sentiment_trends(
    df: pd.DataFrame,
    symbol: str,
    save_path: str = None,
):
    """Plot sentiment trends.
    
    Args:
        df: DataFrame with temporal analysis
        symbol: Trading pair symbol
        save_path: Path to save the plot (optional)
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Plot sentiment
    ax1.plot(df.index, df["polarity"], alpha=0.5, label="Hourly")
    ax1.plot(df.index, df["polarity_ma"], label="24h MA")
    ax1.set_ylabel("Sentiment Polarity")
    ax1.set_title(f"{symbol} Sentiment Analysis")
    ax1.legend()
    ax1.grid(True)
    
    # Plot volume
    ax2.plot(df.index, df["volume"], alpha=0.5, label="Hourly")
    ax2.plot(df.index, df["volume_ma"], label="24h MA")
    ax2.set_ylabel("Tweet Volume")
    ax2.set_xlabel("Time")
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


async def main():
    """Run sentiment analysis."""
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
        # Analyze sentiment for multiple symbols
        symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        
        for symbol in symbols:
            logger.info("Analyzing sentiment for %s...", symbol)
            
            # Fetch data
            data = await fetch_sentiment_data(
                db_manager=db_manager,
                symbol=symbol,
                days=7,
            )
            
            if not data:
                logger.warning("No data found for %s", symbol)
                continue
            
            # Analyze distribution
            dist = analyze_sentiment_distribution(data)
            
            logger.info("\nSentiment Distribution:")
            logger.info("Polarity:")
            for metric, value in dist["polarity"].items():
                logger.info("  %s: %.3f", metric, value)
            
            logger.info("\nSubjectivity:")
            for metric, value in dist["subjectivity"].items():
                logger.info("  %s: %.3f", metric, value)
            
            # Analyze temporal patterns
            temporal_df = analyze_temporal_patterns(data)
            
            logger.info("\nTemporal Analysis:")
            logger.info("Average daily tweet volume: %.1f", temporal_df["volume"].mean())
            logger.info(
                "Peak tweet volume: %d at %s",
                temporal_df["volume"].max(),
                temporal_df["volume"].idxmax().strftime("%Y-%m-%d %H:%M:%S"),
            )
            
            # Analyze user influence
            user_df = analyze_user_influence(data)
            
            logger.info("\nTop Influencers:")
            for user_id, stats in user_df.head().iterrows():
                logger.info(
                    "User %s - Followers: %d, Weighted Sentiment: %.3f, Tweets: %d",
                    user_id,
                    stats["user_followers"],
                    stats["weighted_sentiment_mean"],
                    stats["polarity_count"],
                )
            
            # Plot trends
            plot_sentiment_trends(
                temporal_df,
                symbol,
                save_path=f"sentiment_{symbol.lower()}.png",
            )
            
            logger.info("\nPlot saved as sentiment_%s.png", symbol.lower())
            
            # Calculate sentiment categories
            categories = pd.Series([
                get_sentiment_category(record["polarity"])
                for record in data
            ]).value_counts()
            
            logger.info("\nSentiment Categories:")
            for category, count in categories.items():
                logger.info("  %s: %d (%.1f%%)", category, count, count/len(data)*100)
            
            # Calculate correlation with volume
            correlation = temporal_df["polarity"].corr(temporal_df["volume"])
            logger.info(
                "\nCorrelation between sentiment and volume: %.3f",
                correlation
            )
    
    except Exception as e:
        logger.error("Error during analysis: %s", str(e), exc_info=True)
    
    finally:
        # Clean up
        await db_manager.disconnect()


if __name__ == "__main__":
    asyncio.run(main()) 