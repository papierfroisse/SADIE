"""Data collection repository module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DataCollection
from ..repository import BaseRepository


class DataCollectionRepository(BaseRepository[DataCollection]):
    """Repository for data collection operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.
        
        Args:
            session: Database session.
        """
        super().__init__(session, DataCollection)

    async def get_by_source(self, source_id: UUID) -> list[DataCollection]:
        """Get all collections for a data source.
        
        Args:
            source_id: Data source ID.
        
        Returns:
            List of data collections.
        """
        stmt = select(self._model).where(self._model.source_id == source_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_symbol(self, symbol: str) -> list[DataCollection]:
        """Get all collections for a symbol.
        
        Args:
            symbol: Symbol to search for.
        
        Returns:
            List of data collections.
        """
        stmt = select(self._model).where(self._model.symbol == symbol)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[DataCollection]:
        """Get all collections with a specific status.
        
        Args:
            status: Status to search for.
        
        Returns:
            List of data collections.
        """
        stmt = select(self._model).where(self._model.status == status)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_source_and_symbol(
        self, source_id: UUID, symbol: str
    ) -> Optional[DataCollection]:
        """Get a collection by source and symbol.
        
        Args:
            source_id: Data source ID.
            symbol: Symbol to search for.
        
        Returns:
            The data collection if found, None otherwise.
        """
        stmt = select(self._model).where(
            self._model.source_id == source_id,
            self._model.symbol == symbol
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self, id: UUID, status: str, error_count: Optional[int] = None
    ) -> Optional[DataCollection]:
        """Update a collection's status.
        
        Args:
            id: Collection ID.
            status: New status.
            error_count: Optional error count to update.
        
        Returns:
            The updated collection if found, None otherwise.
        """
        updates = {"status": status}
        if error_count is not None:
            updates["error_count"] = error_count
        return await self.update(id, **updates)

    async def update_last_collected(
        self, id: UUID, timestamp: datetime
    ) -> Optional[DataCollection]:
        """Update a collection's last collected timestamp.
        
        Args:
            id: Collection ID.
            timestamp: New last collected timestamp.
        
        Returns:
            The updated collection if found, None otherwise.
        """
        return await self.update(id, last_collected_at=timestamp) 