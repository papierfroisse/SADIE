"""Test de la connexion à la base de données."""

import asyncio
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from SADIE.core.models.events import Event, MarketEvent

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_database():
    """Test basique des opérations de base de données."""
    try:
        # 1. Connexion à la base de données
        logger.info("Connexion à la base de données...")
        database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/sadie")
        engine = create_async_engine(database_url, echo=True)
        
        async_session = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # 2. Test d'insertion
        logger.info("Test d'insertion...")
        async with async_session() as session:
            # Création d'un événement de test
            event = MarketEvent(
                topic="test_market",
                timestamp=datetime.utcnow(),
                data={"raw_data": "test"},
                symbol="BTC/USD",
                price=50000 * 10**8,  # $50,000
                volume=1 * 10**8,     # 1 BTC
                side="buy",
                exchange="test_exchange"
            )
            
            session.add(event)
            await session.commit()
            logger.info(f"Événement créé avec ID: {event.id}")
            
            # 3. Test de lecture
            logger.info("Test de lecture...")
            result = await session.get(MarketEvent, event.id)
            logger.info(f"Événement lu: {result}")
            
            # 4. Test de mise à jour
            logger.info("Test de mise à jour...")
            result.price = 51000 * 10**8  # $51,000
            await session.commit()
            
            # 5. Test de suppression
            logger.info("Test de suppression...")
            await session.delete(result)
            await session.commit()
            
        logger.info("Test de la base de données terminé avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur pendant le test de la base de données: {e}")
        raise
    finally:
        # Fermeture de la connexion
        await engine.dispose()

if __name__ == "__main__":
    logger.info("Démarrage du test de la base de données...")
    asyncio.run(test_database()) 