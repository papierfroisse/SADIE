"""Database manager module."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ...utils.logging import setup_logging
from .base import Base

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database connection manager."""

    def __init__(
        self,
        url: str,
        pool_size: int = 5,
        max_overflow: int = 10,
        echo: bool = False,
    ) -> None:
        """Initialize the database manager.
        
        Args:
            url: Database connection URL.
            pool_size: Connection pool size.
            max_overflow: Maximum number of connections that can be created beyond pool_size.
            echo: Whether to log SQL queries.
        """
        self._url = url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker[AsyncSession]] = None
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._echo = echo

    async def initialize(self) -> None:
        """Initialize database connection and session factory."""
        if self._engine is not None:
            return

        try:
            self._engine = create_async_engine(
                self._url,
                pool_size=self._pool_size,
                max_overflow=self._max_overflow,
                echo=self._echo,
            )
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            raise

    async def close(self) -> None:
        """Close database connection."""
        if self._engine is None:
            return

        try:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Failed to close database connection: {e}")
            raise

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session.
        
        Yields:
            An async database session.
        
        Raises:
            RuntimeError: If the database is not initialized.
        """
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")

        async with self._session_factory() as session:
            try:
                yield session
            except Exception as e:
                logger.error(f"Database session error: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()

    async def create_all(self) -> None:
        """Create all database tables."""
        if self._engine is None:
            raise RuntimeError("Database not initialized")

        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

    async def drop_all(self) -> None:
        """Drop all database tables."""
        if self._engine is None:
            raise RuntimeError("Database not initialized")

        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
            logger.info("Database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise 