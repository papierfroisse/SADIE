"""SQLAlchemy base configuration."""

from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically."""
        return cls.__name__.lower()

    def dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        } 