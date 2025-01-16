"""Test de la connexion Redis."""

import asyncio
import logging
from datetime import timedelta

from SADIE.core.cache import Cache, RedisCache

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_redis():
    """Test basique des opérations Redis."""
    try:
        # 1. Initialisation du cache
        logger.info("Connexion à Redis...")
        cache = Cache(RedisCache(
            url="redis://localhost",
            prefix="test:"
        ))
        
        # 2. Test d'écriture
        logger.info("Test d'écriture...")
        await cache.set(
            "test_key",
            {"message": "Hello Redis!"},
            ttl=timedelta(minutes=5)
        )
        
        # 3. Test de lecture
        logger.info("Test de lecture...")
        value = await cache.get("test_key")
        logger.info(f"Valeur lue: {value}")
        
        # 4. Test d'existence
        logger.info("Test d'existence...")
        exists = await cache.exists("test_key")
        logger.info(f"La clé existe: {exists}")
        
        # 5. Test de suppression
        logger.info("Test de suppression...")
        await cache.delete("test_key")
        exists = await cache.exists("test_key")
        logger.info(f"La clé existe après suppression: {exists}")
        
        logger.info("Test Redis terminé avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur pendant le test Redis: {e}")
        raise

if __name__ == "__main__":
    logger.info("Démarrage du test Redis...")
    asyncio.run(test_redis()) 