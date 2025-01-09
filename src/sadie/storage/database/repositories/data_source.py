"""Data source repository module."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DataSource
from ..repository import BaseRepository


class DataSourceRepository(BaseRepository[DataSource]):
    """Repository for data source operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.
        
        Args:
            session: Database session.
        """
        super().__init__(session, DataSource)

    async def get_by_name(self, name: str) -> Optional[DataSource]:
        """Get a data source by name.
        
        Args:
            name: Data source name.
        
        Returns:
            The data source if found, None otherwise.
        """
        stmt = select(self._model).where(self._model.name == name)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_type(self, type: str) -> list[DataSource]:
        """Get all data sources of a specific type.
        
        Args:
            type: Data source type.
        
        Returns:
            List of data sources.
        """
        stmt = select(self._model).where(self._model.type == type)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update_config(self, id: UUID, config: dict) -> Optional[DataSource]:
        """Update a data source's configuration.
        
        Args:
            id: Data source ID.
            config: New configuration.
        
        Returns:
            The updated data source if found, None otherwise.
        """
        return await self.update(id, config=config) 