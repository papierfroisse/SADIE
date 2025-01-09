"""Test de connexion à la base de données."""

import os
import pytest
from dotenv import load_dotenv

from src.sadie.storage.database import DatabaseManager

# Chargement des variables d'environnement
load_dotenv()


@pytest.fixture
async def db_manager():
    """Fixture pour le gestionnaire de base de données."""
    url = (
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    manager = DatabaseManager(url=url)
    await manager.initialize()
    yield manager
    await manager.close()


@pytest.mark.asyncio
async def test_database_connection(db_manager):
    """Test de la connexion à la base de données."""
    async with db_manager.session() as session:
        # Exécution d'une requête simple
        result = await session.execute("SELECT 1")
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_create_tables(db_manager):
    """Test de la création des tables."""
    await db_manager.create_all()
    async with db_manager.session() as session:
        # Vérification de l'existence des tables
        result = await session.execute(
            """
            SELECT tablename 
            FROM pg_tables 
            WHERE schemaname = 'public'
            """
        )
        tables = {row[0] for row in result}
        assert "data_sources" in tables
        assert "data_collections" in tables
        assert "data_points" in tables
        assert "analysis_results" in tables 