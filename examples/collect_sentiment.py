"""Example script for collecting sentiment data."""

import asyncio
import logging
import os
from datetime import datetime, timedelta

from sadie.data.collectors.sentiment import SentimentCollector
from sadie.storage.database import DatabaseManager


async def main():
    """Run the sentiment collector example."""
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
        # Create sentiment collector
        collector = SentimentCollector(
            db_manager=db_manager,
            symbols=[
                "BTCUSDT",
                "ETHUSDT",
                "BNBUSDT",
            ],
            twitter_api_key=os.getenv("TWITTER_API_KEY"),
            twitter_api_secret=os.getenv("TWITTER_API_SECRET"),
            twitter_access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            twitter_access_secret=os.getenv("TWITTER_ACCESS_SECRET"),
            batch_size=100,
            batch_interval=1.0,
            lookback_hours=24,
        )
        
        # Start collecting data
        logger.info("Starting sentiment collection...")
        await collector.start()
        
        # Let it run for 5 minutes
        await asyncio.sleep(300)
        
        # Stop collecting
        logger.info("Stopping sentiment collection...")
        await collector.stop()
        
        # Get sentiment summary for the last hour
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        for symbol in collector._symbols:
            sentiment_data = await db_manager.get_sentiment(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
            )
            
            if sentiment_data:
                # Calculate average sentiment
                avg_polarity = sum(
                    record["polarity"] for record in sentiment_data
                ) / len(sentiment_data)
                
                avg_subjectivity = sum(
                    record["subjectivity"] for record in sentiment_data
                ) / len(sentiment_data)
                
                logger.info(
                    "%s sentiment summary (last hour):",
                    symbol
                )
                logger.info(
                    "  Tweets collected: %d",
                    len(sentiment_data)
                )
                logger.info(
                    "  Average polarity: %.2f",
                    avg_polarity
                )
                logger.info(
                    "  Average subjectivity: %.2f",
                    avg_subjectivity
                )
            else:
                logger.info(
                    "No sentiment data collected for %s in the last hour",
                    symbol
                )
        
        # Get aggregated sentiment data
        agg_data = await db_manager.get_sentiment_aggregates(
            symbol="BTCUSDT",
            start_time=start_time,
            end_time=end_time,
            interval="5 minutes",
        )
        
        if agg_data:
            logger.info("\nBTCUSDT sentiment aggregates (5-minute intervals):")
            for record in agg_data:
                logger.info(
                    "  %s - Polarity: %.2f, Subjectivity: %.2f, Tweets: %d",
                    record["time_bucket"].strftime("%H:%M:%S"),
                    record["avg_polarity"],
                    record["avg_subjectivity"],
                    record["tweet_count"],
                )
    
    except Exception as e:
        logger.error("Error during sentiment collection: %s", str(e), exc_info=True)
    
    finally:
        # Clean up
        await db_manager.disconnect()


if __name__ == "__main__":
    # Check for required environment variables
    required_vars = [
        "TWITTER_API_KEY",
        "TWITTER_API_SECRET",
        "TWITTER_ACCESS_TOKEN",
        "TWITTER_ACCESS_SECRET",
    ]
    
    missing_vars = [
        var for var in required_vars
        if not os.getenv(var)
    ]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables before running the script.")
        exit(1)
    
    # Run the example
    asyncio.run(main()) 