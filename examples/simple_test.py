"""Test simple des fonctionnalités de base."""

import asyncio
import logging
from datetime import datetime

from SADIE.core.streaming import StreamEvent, StreamManager
from SADIE.core.streaming.handlers import LoggingHandler

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_simple_stream():
    """Test basique du streaming."""
    try:
        # 1. Création du gestionnaire de flux
        logger.info("Initialisation du stream manager...")
        stream_manager = StreamManager()
        
        # 2. Ajout d'un simple handler de logging
        logger.info("Configuration du handler...")
        stream_manager.subscribe(
            "test_topic",
            LoggingHandler(level=logging.INFO)
        )
        
        # 3. Démarrage du stream manager
        logger.info("Démarrage du stream manager...")
        async with stream_manager:
            # 4. Envoi de quelques événements de test
            logger.info("Envoi des événements de test...")
            for i in range(5):
                event = StreamEvent(
                    topic="test_topic",
                    data={
                        "message": f"Test message {i}",
                        "value": i * 100
                    }
                )
                await stream_manager.publish(event)
                await asyncio.sleep(1)  # Pause entre chaque événement
                
            logger.info("Test terminé avec succès!")
            
    except Exception as e:
        logger.error(f"Erreur pendant le test: {e}")
        raise

if __name__ == "__main__":
    logger.info("Démarrage du test...")
    asyncio.run(test_simple_stream()) 