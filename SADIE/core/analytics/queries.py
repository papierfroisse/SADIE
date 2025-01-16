"""Module de requêtes d'agrégation TimescaleDB."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ..models.events import MarketEvent, SentimentEvent

class TimeScaleQueries:
    """Classe utilitaire pour les requêtes TimescaleDB."""
    
    def __init__(self, session: AsyncSession):
        """Initialise avec une session SQLAlchemy.
        
        Args:
            session: Session SQLAlchemy asynchrone
        """
        self.session = session
    
    async def get_market_vwap(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = '1 hour'
    ) -> List[Dict]:
        """Calcule le VWAP (Volume Weighted Average Price) par intervalle.
        
        Args:
            symbol: Symbole du marché
            start_time: Début de la période
            end_time: Fin de la période
            interval: Intervalle de temps pour l'agrégation
        """
        query = text("""
            SELECT
                time_bucket(:interval, timestamp) AS bucket,
                symbol,
                SUM(price * volume) / SUM(volume) / 100000000.0 as vwap,
                SUM(volume) / 100000000.0 as total_volume
            FROM market_events
            WHERE
                symbol = :symbol
                AND timestamp BETWEEN :start_time AND :end_time
            GROUP BY bucket, symbol
            ORDER BY bucket ASC
        """)
        
        result = await self.session.execute(
            query,
            {
                "interval": interval,
                "symbol": symbol,
                "start_time": start_time,
                "end_time": end_time
            }
        )
        return [dict(row) for row in result]
    
    async def get_market_stats(
        self,
        symbol: str,
        window: str = '1 hour'
    ) -> Dict:
        """Calcule les statistiques en temps réel sur une fenêtre glissante.
        
        Args:
            symbol: Symbole du marché
            window: Taille de la fenêtre glissante
        """
        query = text("""
            SELECT
                symbol,
                MAX(price) / 100000000.0 as high_price,
                MIN(price) / 100000000.0 as low_price,
                FIRST(price, timestamp) / 100000000.0 as open_price,
                LAST(price, timestamp) / 100000000.0 as close_price,
                SUM(CASE WHEN side = 'buy' THEN volume ELSE 0 END) / 100000000.0 as buy_volume,
                SUM(CASE WHEN side = 'sell' THEN volume ELSE 0 END) / 100000000.0 as sell_volume
            FROM market_events
            WHERE
                symbol = :symbol
                AND timestamp > NOW() - :window::interval
            GROUP BY symbol
        """)
        
        result = await self.session.execute(
            query,
            {
                "symbol": symbol,
                "window": window
            }
        )
        return dict(result.first() or {})
    
    async def get_sentiment_trends(
        self,
        entity: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = '1 hour'
    ) -> List[Dict]:
        """Analyse les tendances de sentiment.
        
        Args:
            entity: Entité à analyser
            start_time: Début de la période
            end_time: Fin de la période
            interval: Intervalle de temps pour l'agrégation
        """
        query = text("""
            SELECT
                time_bucket(:interval, timestamp) AS bucket,
                entity,
                AVG(score) / 100.0 as avg_sentiment,
                COUNT(*) as mention_count,
                percentile_cont(0.5) WITHIN GROUP (ORDER BY score) / 100.0 as median_sentiment
            FROM sentiment_events
            WHERE
                entity = :entity
                AND timestamp BETWEEN :start_time AND :end_time
            GROUP BY bucket, entity
            ORDER BY bucket ASC
        """)
        
        result = await self.session.execute(
            query,
            {
                "interval": interval,
                "entity": entity,
                "start_time": start_time,
                "end_time": end_time
            }
        )
        return [dict(row) for row in result]
    
    async def get_correlated_events(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        min_correlation: float = 0.5
    ) -> List[Dict]:
        """Trouve les corrélations entre prix et sentiment.
        
        Args:
            symbol: Symbole du marché
            start_time: Début de la période
            end_time: Fin de la période
            min_correlation: Corrélation minimum à considérer
        """
        query = text("""
            WITH market_changes AS (
                SELECT
                    time_bucket('5 minutes', timestamp) AS bucket,
                    AVG(price) / 100000000.0 as avg_price
                FROM market_events
                WHERE
                    symbol = :symbol
                    AND timestamp BETWEEN :start_time AND :end_time
                GROUP BY bucket
            ),
            sentiment_scores AS (
                SELECT
                    time_bucket('5 minutes', timestamp) AS bucket,
                    AVG(score) / 100.0 as avg_sentiment
                FROM sentiment_events
                WHERE
                    entity = :symbol
                    AND timestamp BETWEEN :start_time AND :end_time
                GROUP BY bucket
            )
            SELECT
                corr(m.avg_price, s.avg_sentiment) as correlation,
                COUNT(*) as sample_size
            FROM market_changes m
            JOIN sentiment_scores s ON s.bucket = m.bucket
            HAVING corr(m.avg_price, s.avg_sentiment) >= :min_correlation
        """)
        
        result = await self.session.execute(
            query,
            {
                "symbol": symbol,
                "start_time": start_time,
                "end_time": end_time,
                "min_correlation": min_correlation
            }
        )
        return [dict(row) for row in result]
    
    async def get_system_metrics(self) -> Dict:
        """Récupère les métriques système de TimescaleDB."""
        query = text("""
            SELECT
                hypertable_name,
                total_bytes,
                total_bytes - compressed_total_bytes as uncompressed_bytes,
                compressed_total_bytes,
                compression_ratio
            FROM timescaledb_information.hypertable_compression_stats
        """)
        
        result = await self.session.execute(query)
        return [dict(row) for row in result] 