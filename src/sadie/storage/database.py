"""Database manager module."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import asyncpg
from asyncpg import Connection, Pool

from ..utils.logging import setup_logging

# Configuration du logging
setup_logging()
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager class for handling database operations."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 5432,
        database: str = "sadie",
        user: str = "postgres",
        password: str = "postgres",
        min_connections: int = 10,
        max_connections: int = 50,
    ) -> None:
        """Initialize the database manager.
        
        Args:
            host: Database host.
            port: Database port.
            database: Database name.
            user: Database user.
            password: Database password.
            min_connections: Minimum number of connections in the pool.
            max_connections: Maximum number of connections in the pool.
        """
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password
        self._min_connections = min_connections
        self._max_connections = max_connections
        self._pool: Optional[Pool] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        """Connect to the database."""
        if self._pool is not None:
            logger.warning("Database connection already established")
            return

        try:
            self._pool = await asyncpg.create_pool(
                host=self._host,
                port=self._port,
                database=self._database,
                user=self._user,
                password=self._password,
                min_size=self._min_connections,
                max_size=self._max_connections,
            )
            logger.info("Connected to database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from the database."""
        if self._pool is None:
            logger.warning("No database connection to close")
            return

        try:
            await self._pool.close()
            self._pool = None
            logger.info("Disconnected from database")
        except Exception as e:
            logger.error(f"Failed to disconnect from database: {e}")
            raise

    async def execute_query(
        self,
        query: str,
        *args: Any,
        fetch: bool = True,
    ) -> Optional[List[Dict[str, Any]]]:
        """Execute a database query.
        
        Args:
            query: SQL query to execute.
            *args: Query parameters.
            fetch: Whether to fetch and return results.
            
        Returns:
            Query results if fetch is True, None otherwise.
        """
        if self._pool is None:
            raise RuntimeError("Database not connected")

        try:
            async with self._pool.acquire() as conn:
                if fetch:
                    result = await conn.fetch(query, *args)
                    return [dict(row) for row in result]
                else:
                    await conn.execute(query, *args)
                    return None
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    async def insert_order_book(
        self,
        symbol: str,
        timestamp: datetime,
        bids: List[List[Union[str, float]]],
        asks: List[List[Union[str, float]]],
        exchange: str,
        depth_level: str,
    ) -> None:
        """Insert order book data into the database.
        
        Args:
            symbol: Trading pair symbol.
            timestamp: Timestamp of the order book snapshot.
            bids: List of [price, quantity] pairs for bids.
            asks: List of [price, quantity] pairs for asks.
            exchange: Name of the exchange.
            depth_level: Depth level of the order book.
        """
        query = """
            INSERT INTO order_books (
                symbol, timestamp, exchange, depth_level, bids, asks
            ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        try:
            await self.execute_query(
                query,
                symbol,
                timestamp,
                exchange,
                depth_level,
                json.dumps(bids),
                json.dumps(asks),
                fetch=False,
            )
        except Exception as e:
            logger.error(f"Failed to insert order book data: {e}")
            raise

    async def get_order_book(
        self,
        symbol: str,
        timestamp: Optional[datetime] = None,
        exchange: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Get order book data from the database.
        
        Args:
            symbol: Trading pair symbol.
            timestamp: Optional timestamp to get data for.
            exchange: Optional exchange name to filter by.
            
        Returns:
            Order book data if found, None otherwise.
        """
        conditions = ["symbol = $1"]
        params = [symbol]
        param_count = 1

        if timestamp:
            param_count += 1
            conditions.append(f"timestamp = ${param_count}")
            params.append(timestamp)

        if exchange:
            param_count += 1
            conditions.append(f"exchange = ${param_count}")
            params.append(exchange)

        query = f"""
            SELECT * FROM order_books
            WHERE {' AND '.join(conditions)}
            ORDER BY timestamp DESC
            LIMIT 1
        """

        try:
            results = await self.execute_query(query, *params)
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Failed to get order book data: {e}")
            raise

    async def get_order_book_history(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        exchange: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get historical order book data.
        
        Args:
            symbol: Trading pair symbol.
            start_time: Start time of the period.
            end_time: End time of the period.
            exchange: Optional exchange name to filter by.
            limit: Maximum number of records to return.
            
        Returns:
            List of order book snapshots.
        """
        conditions = [
            "symbol = $1",
            "timestamp >= $2",
            "timestamp <= $3"
        ]
        params = [symbol, start_time, end_time]
        param_count = 3

        if exchange:
            param_count += 1
            conditions.append(f"exchange = ${param_count}")
            params.append(exchange)

        query = f"""
            SELECT * FROM order_books
            WHERE {' AND '.join(conditions)}
            ORDER BY timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)

        try:
            return await self.execute_query(query, *params) or []
        except Exception as e:
            logger.error(f"Failed to get order book history: {e}")
            raise

    async def insert_trades(
        self,
        trades: List[Dict[str, Any]],
        exchange: str,
    ) -> None:
        """Insert trade data into the database.
        
        Args:
            trades: List of trade records.
            exchange: Name of the exchange.
        """
        query = """
            INSERT INTO trades (
                trade_id, symbol, exchange, price, quantity,
                timestamp, buyer_order_id, seller_order_id,
                buyer_is_maker, is_best_match
            )
            SELECT * FROM unnest($1::bigint[], $2::varchar[], $3::varchar[],
                               $4::decimal[], $5::decimal[], $6::timestamptz[],
                               $7::bigint[], $8::bigint[], $9::boolean[],
                               $10::boolean[])
            ON CONFLICT (exchange, trade_id) DO NOTHING
        """
        
        try:
            # Prepare data for bulk insert
            trade_ids = []
            symbols = []
            exchanges = []
            prices = []
            quantities = []
            timestamps = []
            buyer_order_ids = []
            seller_order_ids = []
            buyer_is_makers = []
            is_best_matches = []
            
            for trade in trades:
                trade_ids.append(trade["trade_id"])
                symbols.append(trade["symbol"])
                exchanges.append(exchange)
                prices.append(float(trade["price"]))
                quantities.append(float(trade["quantity"]))
                timestamps.append(datetime.fromtimestamp(trade["timestamp"] / 1000))
                buyer_order_ids.append(trade["buyer_order_id"])
                seller_order_ids.append(trade["seller_order_id"])
                buyer_is_makers.append(trade["buyer_is_maker"])
                is_best_matches.append(trade["is_best_match"])
            
            await self.execute_query(
                query,
                trade_ids,
                symbols,
                exchanges,
                prices,
                quantities,
                timestamps,
                buyer_order_ids,
                seller_order_ids,
                buyer_is_makers,
                is_best_matches,
                fetch=False,
            )
        except Exception as e:
            logger.error(f"Failed to insert trade data: {e}")
            raise

    async def get_trades(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        exchange: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get trade data from the database.
        
        Args:
            symbol: Trading pair symbol.
            start_time: Start time of the period.
            end_time: End time of the period.
            exchange: Optional exchange name to filter by.
            limit: Maximum number of records to return.
            
        Returns:
            List of trade records.
        """
        conditions = [
            "symbol = $1",
            "timestamp >= $2",
            "timestamp <= $3"
        ]
        params = [symbol, start_time, end_time]
        param_count = 3

        if exchange:
            param_count += 1
            conditions.append(f"exchange = ${param_count}")
            params.append(exchange)

        query = f"""
            SELECT * FROM trades
            WHERE {' AND '.join(conditions)}
            ORDER BY timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)

        try:
            return await self.execute_query(query, *params) or []
        except Exception as e:
            logger.error(f"Failed to get trade data: {e}")
            raise

    async def get_ohlcv(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        exchange: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get OHLCV data from the trades_1m materialized view.
        
        Args:
            symbol: Trading pair symbol.
            start_time: Start time of the period.
            end_time: End time of the period.
            exchange: Optional exchange name to filter by.
            
        Returns:
            List of OHLCV records.
        """
        conditions = [
            "symbol = $1",
            "bucket >= $2",
            "bucket <= $3"
        ]
        params = [symbol, start_time, end_time]
        param_count = 3

        if exchange:
            param_count += 1
            conditions.append(f"exchange = ${param_count}")
            params.append(exchange)

        query = f"""
            SELECT
                bucket as timestamp,
                symbol,
                exchange,
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                trade_count
            FROM trades_1m
            WHERE {' AND '.join(conditions)}
            ORDER BY bucket DESC
        """

        try:
            return await self.execute_query(query, *params) or []
        except Exception as e:
            logger.error(f"Failed to get OHLCV data: {e}")
            raise

    async def insert_sentiment(
        self,
        sentiment_data: List[Dict[str, Any]],
    ) -> None:
        """Insert sentiment data into the database.
        
        Args:
            sentiment_data: List of sentiment records.
        """
        query = """
            INSERT INTO sentiment (
                symbol, tweet_id, text, created_at, user_id,
                user_followers, retweet_count, favorite_count,
                polarity, subjectivity, query, source
            )
            SELECT * FROM unnest(
                $1::varchar[], $2::varchar[], $3::text[], $4::timestamptz[],
                $5::varchar[], $6::integer[], $7::integer[], $8::integer[],
                $9::decimal[], $10::decimal[], $11::varchar[], $12::varchar[]
            )
            ON CONFLICT (source, tweet_id) DO NOTHING
        """
        
        try:
            # Prepare data for bulk insert
            symbols = []
            tweet_ids = []
            texts = []
            created_ats = []
            user_ids = []
            user_followers = []
            retweet_counts = []
            favorite_counts = []
            polarities = []
            subjectivities = []
            queries = []
            sources = []
            
            for record in sentiment_data:
                symbols.append(record["symbol"])
                tweet_ids.append(record["tweet_id"])
                texts.append(record["text"])
                created_ats.append(record["created_at"])
                user_ids.append(record["user_id"])
                user_followers.append(record["user_followers"])
                retweet_counts.append(record["retweet_count"])
                favorite_counts.append(record["favorite_count"])
                polarities.append(float(record["polarity"]))
                subjectivities.append(float(record["subjectivity"]))
                queries.append(record["query"])
                sources.append("twitter")
            
            await self.execute_query(
                query,
                symbols,
                tweet_ids,
                texts,
                created_ats,
                user_ids,
                user_followers,
                retweet_counts,
                favorite_counts,
                polarities,
                subjectivities,
                queries,
                sources,
                fetch=False,
            )
        except Exception as e:
            logger.error(f"Failed to insert sentiment data: {e}")
            raise

    async def get_sentiment(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        source: Optional[str] = None,
        limit: int = 1000,
    ) -> List[Dict[str, Any]]:
        """Get sentiment data from the database.
        
        Args:
            symbol: Trading pair symbol.
            start_time: Start time of the period.
            end_time: End time of the period.
            source: Optional source to filter by.
            limit: Maximum number of records to return.
            
        Returns:
            List of sentiment records.
        """
        conditions = [
            "symbol = $1",
            "created_at >= $2",
            "created_at <= $3"
        ]
        params = [symbol, start_time, end_time]
        param_count = 3

        if source:
            param_count += 1
            conditions.append(f"source = ${param_count}")
            params.append(source)

        query = f"""
            SELECT * FROM sentiment
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)

        try:
            return await self.execute_query(query, *params) or []
        except Exception as e:
            logger.error(f"Failed to get sentiment data: {e}")
            raise

    async def get_sentiment_aggregates(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        source: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get aggregated sentiment data from the sentiment_1h view.
        
        Args:
            symbol: Trading pair symbol.
            start_time: Start time of the period.
            end_time: End time of the period.
            source: Optional source to filter by.
            
        Returns:
            List of aggregated sentiment records.
        """
        conditions = [
            "symbol = $1",
            "bucket >= $2",
            "bucket <= $3"
        ]
        params = [symbol, start_time, end_time]
        param_count = 3

        if source:
            param_count += 1
            conditions.append(f"source = ${param_count}")
            params.append(source)

        query = f"""
            SELECT
                bucket as timestamp,
                symbol,
                source,
                message_count,
                avg_polarity,
                avg_subjectivity,
                total_reach,
                total_retweets,
                total_favorites
            FROM sentiment_1h
            WHERE {' AND '.join(conditions)}
            ORDER BY bucket DESC
        """

        try:
            return await self.execute_query(query, *params) or []
        except Exception as e:
            logger.error(f"Failed to get sentiment aggregates: {e}")
            raise 