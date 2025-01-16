"""Module de gestion de la base de données."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import AsyncAdaptedQueuePool

from ..core.monitoring import get_logger
from ..utils.config import config
from ..utils.decorators import log_execution, retry
from .base import StorageBackend

logger = get_logger(__name__)

class DatabaseStorage(StorageBackend):
    """Backend de stockage base de données."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: int = 30
    ):
        """Initialise le stockage base de données.
        
        Args:
            url: URL de connexion à la base de données
            pool_size: Taille du pool de connexions
            max_overflow: Nombre maximum de connexions supplémentaires
            pool_timeout: Timeout du pool en secondes
        """
        self.url = url or config.get("database.url")
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self._engine: Optional[AsyncEngine] = None
        self._session_maker = None
        self.logger = get_logger(__name__)
        
    @log_execution()
    async def connect(self) -> None:
        """Établit la connexion à la base de données."""
        try:
            self._engine = create_async_engine(
                self.url,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_pre_ping=True,
                poolclass=AsyncAdaptedQueuePool,
                echo=config.get("database.echo", False)
            )
            
            self._session_maker = sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            # Test de connexion
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                
            self.logger.info(
                f"Connexion établie à {self.url} "
                f"(pool_size={self.pool_size})"
            )
            
        except Exception as e:
            self.logger.error(f"Erreur de connexion à la base de données: {e}")
            raise
            
    @log_execution()
    async def disconnect(self) -> None:
        """Ferme la connexion à la base de données."""
        if self._engine is not None:
            try:
                await self._engine.dispose()
                self._engine = None
                self._session_maker = None
                self.logger.info("Connexion à la base de données fermée")
            except Exception as e:
                self.logger.error(
                    f"Erreur lors de la fermeture de la connexion: {e}"
                )
                raise
                
    async def get_session(self) -> AsyncSession:
        """Retourne une session de base de données."""
        if self._session_maker is None:
            await self.connect()
        return self._session_maker()
        
    @retry(max_attempts=3)
    async def execute(
        self,
        query: Union[str, text],
        params: Optional[Dict] = None
    ) -> Any:
        """Exécute une requête SQL.
        
        Args:
            query: Requête SQL
            params: Paramètres de la requête
        """
        async with self.get_session() as session:
            try:
                result = await session.execute(
                    text(query) if isinstance(query, str) else query,
                    params or {}
                )
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Erreur lors de l'exécution de la requête: {e}")
                raise
                
    async def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur de la base de données."""
        query = text("""
            SELECT value
            FROM key_value_store
            WHERE key = :key
        """)
        
        try:
            result = await self.execute(query, {"key": key})
            row = result.first()
            return row[0] if row else None
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture: {e}")
            raise
            
    async def set(self, key: str, value: Any) -> None:
        """Stocke une valeur dans la base de données."""
        query = text("""
            INSERT INTO key_value_store (key, value)
            VALUES (:key, :value)
            ON CONFLICT (key) DO UPDATE
            SET value = :value
        """)
        
        try:
            await self.execute(query, {"key": key, "value": value})
        except Exception as e:
            self.logger.error(f"Erreur lors de l'écriture: {e}")
            raise
            
    async def delete(self, key: str) -> None:
        """Supprime une valeur de la base de données."""
        query = text("""
            DELETE FROM key_value_store
            WHERE key = :key
        """)
        
        try:
            await self.execute(query, {"key": key})
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression: {e}")
            raise
            
    async def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans la base de données."""
        query = text("""
            SELECT EXISTS(
                SELECT 1
                FROM key_value_store
                WHERE key = :key
            )
        """)
        
        try:
            result = await self.execute(query, {"key": key})
            return result.scalar()
        except Exception as e:
            self.logger.error(f"Erreur lors de la vérification: {e}")
            raise
            
    async def clear(self) -> None:
        """Vide la table de stockage."""
        query = text("TRUNCATE TABLE key_value_store")
        
        try:
            await self.execute(query)
        except Exception as e:
            self.logger.error(f"Erreur lors du vidage: {e}")
            raise 