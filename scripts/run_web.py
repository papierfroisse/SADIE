"""Script de lancement de l'application web."""

import uvicorn
import asyncio
import logging
from sadie.web import app, StreamManager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('web.log')
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Point d'entrée principal."""
    try:
        # Création et démarrage du gestionnaire de flux
        stream_manager = StreamManager()
        await stream_manager.start()
        
        # Configuration de l'application
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            log_level="info",
            reload=True
        )
        
        # Démarrage du serveur
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du serveur: {e}")
        raise
    finally:
        # Arrêt propre
        await stream_manager.stop()

if __name__ == "__main__":
    asyncio.run(main()) 