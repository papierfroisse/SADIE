"""Tests d'intégration pour les repositories."""

import pytest
from datetime import datetime, timezone

from src.sadie.storage.database.repositories import (
    DataSourceRepository,
    DataCollectionRepository,
    DataPointRepository,
    AnalysisResultRepository,
)


@pytest.mark.asyncio
async def test_data_source_repository(db_manager):
    """Test du repository DataSource."""
    async with db_manager.session() as session:
        repo = DataSourceRepository(session)

        # Création
        source = await repo.create(
            name="binance",
            type="rest",
            config={"base_url": "https://api.binance.com"},
            description="Binance REST API",
        )
        assert source.id is not None
        assert source.name == "binance"

        # Lecture
        retrieved = await repo.get(source.id)
        assert retrieved is not None
        assert retrieved.name == source.name

        # Mise à jour
        updated = await repo.update_config(
            source.id, {"base_url": "https://api.binance.com/v2"}
        )
        assert updated is not None
        assert updated.config["base_url"] == "https://api.binance.com/v2"

        # Suppression
        deleted = await repo.delete(source.id)
        assert deleted is True


@pytest.mark.asyncio
async def test_data_collection_repository(db_manager):
    """Test du repository DataCollection."""
    async with db_manager.session() as session:
        # Création d'une source de données
        source_repo = DataSourceRepository(session)
        source = await source_repo.create(
            name="binance",
            type="rest",
            config={"base_url": "https://api.binance.com"},
        )

        # Test du repository DataCollection
        repo = DataCollectionRepository(session)

        # Création
        collection = await repo.create(
            source_id=source.id,
            symbol="BTC-USD",
            interval="1m",
            status="active",
            config={"limit": 1000},
        )
        assert collection.id is not None
        assert collection.symbol == "BTC-USD"

        # Lecture
        retrieved = await repo.get(collection.id)
        assert retrieved is not None
        assert retrieved.symbol == collection.symbol

        # Mise à jour du statut
        updated = await repo.update_status(collection.id, "paused", error_count=1)
        assert updated is not None
        assert updated.status == "paused"
        assert updated.error_count == 1

        # Mise à jour du timestamp
        now = datetime.now(timezone.utc)
        updated = await repo.update_last_collected(collection.id, now)
        assert updated is not None
        assert updated.last_collected_at == now

        # Suppression
        deleted = await repo.delete(collection.id)
        assert deleted is True


@pytest.mark.asyncio
async def test_data_point_repository(db_manager):
    """Test du repository DataPoint."""
    async with db_manager.session() as session:
        # Création d'une source et d'une collection
        source_repo = DataSourceRepository(session)
        source = await source_repo.create(
            name="binance",
            type="rest",
            config={"base_url": "https://api.binance.com"},
        )

        collection_repo = DataCollectionRepository(session)
        collection = await collection_repo.create(
            source_id=source.id,
            symbol="BTC-USD",
            interval="1m",
            status="active",
            config={"limit": 1000},
        )

        # Test du repository DataPoint
        repo = DataPointRepository(session)

        # Création en masse
        now = datetime.now(timezone.utc)
        points = await repo.bulk_create(
            [
                {
                    "collection_id": collection.id,
                    "timestamp": now,
                    "value": 50000.0,
                    "meta_data": {"volume": 1.5},
                },
                {
                    "collection_id": collection.id,
                    "timestamp": now,
                    "value": 50001.0,
                    "meta_data": {"volume": 2.0},
                },
            ]
        )
        assert len(points) == 2

        # Lecture par collection
        retrieved = await repo.get_by_collection(collection.id)
        assert len(retrieved) == 2

        # Lecture du dernier point
        latest = await repo.get_latest_by_collection(collection.id)
        assert latest is not None
        assert latest.value == 50001.0

        # Suppression par collection
        deleted_count = await repo.delete_by_collection(collection.id)
        assert deleted_count == 2


@pytest.mark.asyncio
async def test_analysis_result_repository(db_manager):
    """Test du repository AnalysisResult."""
    async with db_manager.session() as session:
        # Création d'une source et d'une collection
        source_repo = DataSourceRepository(session)
        source = await source_repo.create(
            name="binance",
            type="rest",
            config={"base_url": "https://api.binance.com"},
        )

        collection_repo = DataCollectionRepository(session)
        collection = await collection_repo.create(
            source_id=source.id,
            symbol="BTC-USD",
            interval="1m",
            status="active",
            config={"limit": 1000},
        )

        # Test du repository AnalysisResult
        repo = AnalysisResultRepository(session)

        # Création en masse
        now = datetime.now(timezone.utc)
        results = await repo.bulk_create(
            [
                {
                    "collection_id": collection.id,
                    "type": "volatility",
                    "timestamp": now,
                    "parameters": {"window": 60},
                    "results": {"value": 0.15},
                    "meta_data": {"confidence": 0.95},
                },
                {
                    "collection_id": collection.id,
                    "type": "trend",
                    "timestamp": now,
                    "parameters": {"window": 60},
                    "results": {"direction": "up"},
                    "meta_data": {"confidence": 0.85},
                },
            ]
        )
        assert len(results) == 2

        # Lecture par collection
        retrieved = await repo.get_by_collection(collection.id)
        assert len(retrieved) == 2

        # Lecture par type
        volatility = await repo.get_by_collection(collection.id, analysis_type="volatility")
        assert len(volatility) == 1
        assert volatility[0].type == "volatility"

        # Lecture du dernier résultat
        latest = await repo.get_latest_by_collection(collection.id, analysis_type="trend")
        assert latest is not None
        assert latest.type == "trend"

        # Suppression par collection
        deleted_count = await repo.delete_by_collection(collection.id)
        assert deleted_count == 2 