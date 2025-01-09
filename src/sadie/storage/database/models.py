"""Database models."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class BaseModel(Base):
    """Base model with common fields."""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class DataSource(BaseModel):
    """Data source configuration."""

    __tablename__ = "data_sources"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Relations
    collections: Mapped[list["DataCollection"]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan"
    )

class DataCollection(BaseModel):
    """Data collection metadata."""

    __tablename__ = "data_collections"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_sources.id"),
        nullable=False
    )
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    interval: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    last_collected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_count: Mapped[int] = mapped_column(default=0, nullable=False)
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relations
    source: Mapped[DataSource] = relationship(back_populates="collections")
    data_points: Mapped[list["DataPoint"]] = relationship(
        back_populates="collection",
        cascade="all, delete-orphan"
    )

class DataPoint(BaseModel):
    """Time series data point."""

    __tablename__ = "data_points"

    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_collections.id"),
        nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    meta_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relations
    collection: Mapped[DataCollection] = relationship(back_populates="data_points")

    class Config:
        """Model configuration."""

        indexes = [
            ("collection_id", "timestamp")  # Composite index for time series queries
        ]

class AnalysisResult(BaseModel):
    """Analysis result."""

    __tablename__ = "analysis_results"

    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_collections.id"),
        nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    results: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    meta_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)

    # Relations
    collection: Mapped[DataCollection] = relationship(back_populates="analysis_results")

    class Config:
        """Model configuration."""

        indexes = [
            ("collection_id", "timestamp", "type")  # Composite index for analysis queries
        ]

# Add back-reference to DataCollection
DataCollection.analysis_results = relationship(
    AnalysisResult,
    back_populates="collection",
    cascade="all, delete-orphan"
) 