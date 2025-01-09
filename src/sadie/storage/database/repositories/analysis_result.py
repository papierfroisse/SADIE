"""Analysis result repository module."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import AnalysisResult
from ..repository import BaseRepository


class AnalysisResultRepository(BaseRepository[AnalysisResult]):
    """Repository for analysis result operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository.
        
        Args:
            session: Database session.
        """
        super().__init__(session, AnalysisResult)

    async def get_by_collection(
        self,
        collection_id: UUID,
        analysis_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> list[AnalysisResult]:
        """Get all analysis results for a collection within a time range.
        
        Args:
            collection_id: Collection ID.
            analysis_type: Optional analysis type filter.
            start_time: Optional start time filter.
            end_time: Optional end time filter.
        
        Returns:
            List of analysis results.
        """
        stmt = select(self._model).where(self._model.collection_id == collection_id)

        if analysis_type is not None:
            stmt = stmt.where(self._model.type == analysis_type)
        if start_time is not None:
            stmt = stmt.where(self._model.timestamp >= start_time)
        if end_time is not None:
            stmt = stmt.where(self._model.timestamp <= end_time)

        stmt = stmt.order_by(self._model.timestamp)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_collection(
        self,
        collection_id: UUID,
        analysis_type: Optional[str] = None,
    ) -> Optional[AnalysisResult]:
        """Get the latest analysis result for a collection.
        
        Args:
            collection_id: Collection ID.
            analysis_type: Optional analysis type filter.
        
        Returns:
            The latest analysis result if found, None otherwise.
        """
        stmt = (
            select(self._model)
            .where(self._model.collection_id == collection_id)
        )

        if analysis_type is not None:
            stmt = stmt.where(self._model.type == analysis_type)

        stmt = stmt.order_by(self._model.timestamp.desc()).limit(1)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def bulk_create(self, results: list[dict]) -> list[AnalysisResult]:
        """Create multiple analysis results.
        
        Args:
            results: List of analysis result attributes.
        
        Returns:
            List of created analysis results.
        """
        records = [self._model(**result) for result in results]
        self._session.add_all(records)
        await self._session.flush()
        return records

    async def delete_by_collection(
        self,
        collection_id: UUID,
        analysis_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> int:
        """Delete analysis results for a collection within a time range.
        
        Args:
            collection_id: Collection ID.
            analysis_type: Optional analysis type filter.
            start_time: Optional start time filter.
            end_time: Optional end time filter.
        
        Returns:
            Number of deleted records.
        """
        stmt = select(self._model).where(self._model.collection_id == collection_id)

        if analysis_type is not None:
            stmt = stmt.where(self._model.type == analysis_type)
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