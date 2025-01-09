"""Base repository module."""

from typing import Any, Generic, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Base repository class for database operations."""

    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        """Initialize the repository.
        
        Args:
            session: Database session.
            model: SQLAlchemy model class.
        """
        self._session = session
        self._model = model

    async def get(self, id: UUID) -> Optional[T]:
        """Get a record by ID.
        
        Args:
            id: Record ID.
        
        Returns:
            The record if found, None otherwise.
        """
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self) -> list[T]:
        """Get all records.
        
        Returns:
            List of all records.
        """
        stmt = select(self._model)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> T:
        """Create a new record.
        
        Args:
            **kwargs: Record attributes.
        
        Returns:
            The created record.
        """
        record = self._model(**kwargs)
        self._session.add(record)
        await self._session.flush()
        return record

    async def update(self, id: UUID, **kwargs: Any) -> Optional[T]:
        """Update a record.
        
        Args:
            id: Record ID.
            **kwargs: Record attributes to update.
        
        Returns:
            The updated record if found, None otherwise.
        """
        record = await self.get(id)
        if record is None:
            return None

        for key, value in kwargs.items():
            setattr(record, key, value)

        await self._session.flush()
        return record

    async def delete(self, id: UUID) -> bool:
        """Delete a record.
        
        Args:
            id: Record ID.
        
        Returns:
            True if the record was deleted, False if not found.
        """
        record = await self.get(id)
        if record is None:
            return False

        await self._session.delete(record)
        await self._session.flush()
        return True

    async def exists(self, id: UUID) -> bool:
        """Check if a record exists.
        
        Args:
            id: Record ID.
        
        Returns:
            True if the record exists, False otherwise.
        """
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.first() is not None 