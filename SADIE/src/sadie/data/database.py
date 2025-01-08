"""Database management module for SADIE."""
from typing import Optional, List, Dict, Any
import asyncpg
from datetime import datetime
from ..config import DB_CONFIG

class Database:
    """Database management class with TimescaleDB support."""
    
    def __init__(self):
        """Initialize database connection."""
        self.pool: Optional[asyncpg.Pool] = None
        self.config = DB_CONFIG
        
    async def connect(self) -> None:
        """Create database connection pool."""
        self.pool = await asyncpg.create_pool(
            host=self.config["host"],
            port=self.config["port"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["name"]
        )
        
        if self.config["timescaledb"]:
            await self._setup_timescaledb()
            
    async def _setup_timescaledb(self) -> None:
        """Setup TimescaleDB extensions and hypertables."""
        async with self.pool.acquire() as conn:
            # Enable TimescaleDB extension
            await conn.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;')
            
            # Create market data hypertable
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS market_data (
                    time TIMESTAMPTZ NOT NULL,
                    symbol TEXT NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    volume DOUBLE PRECISION NOT NULL,
                    source TEXT NOT NULL
                );
            ''')
            
            # Convert to hypertable
            try:
                await conn.execute(
                    "SELECT create_hypertable('market_data', 'time', if_not_exists => TRUE);"
                )
            except Exception as e:
                print(f"Warning: Could not create hypertable: {e}")
                
    async def insert_market_data(
        self,
        symbol: str,
        price: float,
        volume: float,
        source: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """Insert market data into the database."""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO market_data (time, symbol, price, volume, source)
                VALUES ($1, $2, $3, $4, $5)
            ''', timestamp, symbol, price, volume, source)
            
    async def get_market_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve market data from the database."""
        if end_time is None:
            end_time = datetime.utcnow()
            
        query = '''
            SELECT time, symbol, price, volume, source
            FROM market_data
            WHERE symbol = $1
            AND time BETWEEN $2 AND $3
        '''
        params = [symbol, start_time, end_time]
        
        if source:
            query += ' AND source = $4'
            params.append(source)
            
        query += ' ORDER BY time ASC'
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
            
    async def cleanup_old_data(
        self,
        older_than: datetime,
        symbol: Optional[str] = None,
        source: Optional[str] = None
    ) -> int:
        """Remove old data from the database."""
        query = '''
            DELETE FROM market_data
            WHERE time < $1
        '''
        params = [older_than]
        
        if symbol:
            query += ' AND symbol = $2'
            params.append(symbol)
            
        if source:
            query += f' AND source = ${len(params) + 1}'
            params.append(source)
            
        async with self.pool.acquire() as conn:
            result = await conn.execute(query, *params)
            return int(result.split()[1])  # Extract number of deleted rows
            
    async def close(self) -> None:
        """Close database connection pool."""
        if self.pool:
            await self.pool.close() 