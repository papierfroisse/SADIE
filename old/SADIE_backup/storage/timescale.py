"""Module de stockage TimescaleDB."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import asyncpg
from asyncpg.pool import Pool

from sadie.core.models.events import Trade
from .base import BaseStorage

class TimescaleStorage(BaseStorage):
    """Stockage des données dans TimescaleDB."""
    
    def __init__(
        self,
        name: str,
        dsn: str,
        min_connections: int = 1,
        max_connections: int = 10,
        logger: Optional[logging.Logger] = None
    ):
        """Initialise le stockage TimescaleDB.
        
        Args:
            name: Nom du stockage
            dsn: DSN de connexion à la base
            min_connections: Nombre minimum de connexions dans le pool
            max_connections: Nombre maximum de connexions dans le pool
            logger: Logger optionnel
        """
        super().__init__(name, logger)
        
        self.dsn = dsn
        self.min_connections = min_connections
        self.max_connections = max_connections
        
        self._pool: Optional[Pool] = None
    
    async def connect(self) -> None:
        """Établit la connexion à TimescaleDB."""
        if self._pool:
            return
            
        # Création du pool de connexions
        self._pool = await asyncpg.create_pool(
            dsn=self.dsn,
            min_size=self.min_connections,
            max_size=self.max_connections
        )
        
        # Création des tables si nécessaire
        async with self._pool.acquire() as conn:
            # Extension TimescaleDB
            await conn.execute('CREATE EXTENSION IF NOT EXISTS timescaledb;')
            
            # Table des trades
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    exchange TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    price DOUBLE PRECISION NOT NULL,
                    amount DOUBLE PRECISION NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    side TEXT NOT NULL,
                    trade_id TEXT NOT NULL,
                    PRIMARY KEY (exchange, symbol, trade_id)
                );
            ''')
            
            # Conversion en hypertable
            await conn.execute('''
                SELECT create_hypertable('trades', 'timestamp', 
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                );
            ''')
            
            # Table des statistiques
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    symbol TEXT NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    data JSONB NOT NULL,
                    PRIMARY KEY (symbol, timestamp)
                );
            ''')
            
            # Conversion en hypertable
            await conn.execute('''
                SELECT create_hypertable('statistics', 'timestamp',
                    if_not_exists => TRUE,
                    migrate_data => TRUE
                );
            ''')
            
            # Index pour les requêtes fréquentes
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS trades_symbol_timestamp_idx 
                ON trades (symbol, timestamp DESC);
                
                CREATE INDEX IF NOT EXISTS statistics_symbol_timestamp_idx 
                ON statistics (symbol, timestamp DESC);
            ''')
        
        self.logger.info(f"Connecté à TimescaleDB: {self.dsn}")
    
    async def disconnect(self) -> None:
        """Ferme la connexion à TimescaleDB."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self.logger.info("Déconnecté de TimescaleDB")
    
    async def store_trades(self, symbol: str, trades: List[Trade]) -> None:
        """Stocke une liste de trades.
        
        Args:
            symbol: Symbole des trades
            trades: Liste des trades à stocker
        """
        if not self._pool:
            raise RuntimeError("Non connecté à TimescaleDB")
            
        # Préparation des données
        values = [
            (
                t.exchange,
                t.symbol,
                t.price,
                t.amount,
                t.timestamp,
                t.side,
                t.trade_id
            )
            for t in trades
        ]
        
        # Insertion des trades
        async with self._pool.acquire() as conn:
            await conn.executemany('''
                INSERT INTO trades (
                    exchange, symbol, price, amount, timestamp, side, trade_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (exchange, symbol, trade_id) DO NOTHING;
            ''', values)
    
    async def get_trades(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[Trade]:
        """Récupère les trades stockés.
        
        Args:
            symbol: Symbole des trades
            start_time: Timestamp de début (optionnel)
            end_time: Timestamp de fin (optionnel)
            limit: Nombre maximum de trades à retourner (optionnel)
            
        Returns:
            Liste des trades correspondants aux critères
        """
        if not self._pool:
            raise RuntimeError("Non connecté à TimescaleDB")
            
        # Construction de la requête
        query = '''
            SELECT exchange, symbol, price, amount, timestamp, side, trade_id
            FROM trades
            WHERE symbol = $1
        '''
        params = [symbol]
        
        if start_time:
            query += ' AND timestamp >= $' + str(len(params) + 1)
            params.append(datetime.fromtimestamp(start_time))
            
        if end_time:
            query += ' AND timestamp <= $' + str(len(params) + 1)
            params.append(datetime.fromtimestamp(end_time))
            
        query += ' ORDER BY timestamp DESC'
        
        if limit:
            query += ' LIMIT $' + str(len(params) + 1)
            params.append(limit)
        
        # Exécution de la requête
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        
        # Conversion en objets Trade
        return [
            Trade(
                exchange=row['exchange'],
                symbol=row['symbol'],
                price=row['price'],
                amount=row['amount'],
                timestamp=row['timestamp'].timestamp(),
                side=row['side'],
                trade_id=row['trade_id']
            )
            for row in rows
        ]
    
    async def store_statistics(self, symbol: str, statistics: Dict[str, Any]) -> None:
        """Stocke les statistiques d'un symbole.
        
        Args:
            symbol: Symbole concerné
            statistics: Statistiques à stocker
        """
        if not self._pool:
            raise RuntimeError("Non connecté à TimescaleDB")
            
        # Insertion des statistiques
        async with self._pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO statistics (symbol, timestamp, data)
                VALUES ($1, NOW(), $2);
            ''', symbol, statistics)
    
    async def get_statistics(
        self,
        symbol: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Récupère les statistiques stockées.
        
        Args:
            symbol: Symbole concerné
            start_time: Timestamp de début (optionnel)
            end_time: Timestamp de fin (optionnel)
            
        Returns:
            Statistiques correspondant aux critères
        """
        if not self._pool:
            raise RuntimeError("Non connecté à TimescaleDB")
            
        # Construction de la requête
        query = '''
            SELECT data
            FROM statistics
            WHERE symbol = $1
        '''
        params = [symbol]
        
        if start_time:
            query += ' AND timestamp >= $' + str(len(params) + 1)
            params.append(datetime.fromtimestamp(start_time))
            
        if end_time:
            query += ' AND timestamp <= $' + str(len(params) + 1)
            params.append(datetime.fromtimestamp(end_time))
            
        query += ' ORDER BY timestamp DESC LIMIT 1'
        
        # Exécution de la requête
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, *params)
            
        return row['data'] if row else {} 