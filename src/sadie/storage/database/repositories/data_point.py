"""Data point repository module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import DataPoint
from ..repository import BaseRepository


class DataPointRepository(BaseRepository[DataPoint]):
    """Repository for data point operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.
        
        Args:
            session: Database session.
        """
        super().__init__(session, DataPoint)

    async def get_by_collection(
        self,
        collection_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> list[DataPoint]:
        """Get all data points for a collection within a time range.
        
        Args:
            collection_id: Collection ID.
            start_time: Optional start time filter.
            end_time: Optional end time filter.
        
        Returns:
            List of data points.
        """
        stmt = select(self._model).where(self._model.collection_id == collection_id)

        if start_time is not None:
            stmt = stmt.where(self._model.timestamp >= start_time)
        if end_time is not None:
            stmt = stmt.where(self._model.timestamp <= end_time)

        stmt = stmt.order_by(self._model.timestamp)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_collection(
        self, collection_id: UUID
    ) -> Optional[DataPoint]:
        """Get the latest data point for a collection.
        
        Args:
            collection_id: Collection ID.
        
        Returns:
            The latest data point if found, None otherwise.
        """
        stmt = (
            select(self._model)
            .where(self._model.collection_id == collection_id)
            .order_by(self._model.timestamp.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def bulk_create(self, data_points: list[dict]) -> list[DataPoint]:
        """Create multiple data points.
        
        Args:
            data_points: List of data point attributes.
        
        Returns:
            List of created data points.
        """
        records = [self._model(**data) for data in data_points]
        self._session.add_all(records)
        await self._session.flush()
        return records

    async def delete_by_collection(
        self,
        collection_id: UUID,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        """Delete data points for a collection within a time range.
        
        Args:
            collection_id: Collection ID.
            start_time: Optional start time filter.
            end_time: Optional end time filter.
        
        Returns:
            Number of deleted records.
        """
        stmt = select(self._model).where(self._model.collection_id == collection_id)

        if start_time is not None:
            stmt = stmt.where(self._model.timestamp >= start_time)
        if end_time is not None:
            stmt = stmt.where(self._model.timestamp <= end_time)

        result = await self._session.execute(stmt)
        records = result.scalars().all()
        
        for record in records:
            await self._session.delete(record)
        
        await self._session.flush()
        return len(records) 