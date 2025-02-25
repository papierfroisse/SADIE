"""Exemple d'utilisation du collecteur Kraken avec Redis."""

import asyncio
import os
import sys
from dotenv import load_dotenv
from sadie.core.collectors import KrakenTradeCollector
from sadie.storage import RedisStorage
import logging
import redis.exceptions
from typing import Optional

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def check_redis_connection(host: str, port: int) -> bool:
    """Vérifie si Redis est accessible."""
    try:
        storage = RedisStorage(
            name="connection_test",
            host=host,
            port=port,
            socket_timeout=2
        )
        await storage.connect()
        await storage.disconnect()
        return True
    except redis.exceptions.ConnectionError:
        logger.error(f"Impossible de se connecter à Redis ({host}:{port})")
        return False
    except Exception as e:
        logger.error(f"Erreur lors du test de connexion Redis: {str(e)}")
        return False

async def check_kraken_credentials(api_key: Optional[str], api_secret: Optional[str]) -> bool:
    """Vérifie si les credentials Kraken sont valides."""
    if not api_key or not api_secret:
        logger.error("Clés API Kraken non configurées")
        return False
        
    try:
        collector = KrakenTradeCollector(
            name="credentials_test",
            symbols=["XBT/USD"],  # Bitcoin/USD
            api_key=api_key,
            api_secret=api_secret
        )
        await collector._connect()
        await collector.stop()
        return True
    except Exception as e:
        logger.error(f"Erreur de connexion à Kraken: {str(e)}")
        return False

async def main():
    """Fonction principale."""
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Paramètres de connexion
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    kraken_key = os.getenv("KRAKEN_API_KEY")
    kraken_secret = os.getenv("KRAKEN_API_SECRET")
    
    # Vérification des prérequis
    logger.info("Vérification des connexions...")
    
    if not await check_redis_connection(redis_host, redis_port):
        logger.error("Redis n'est pas accessible. Veuillez vérifier que Redis est démarré.")
        return
        
    if not await check_kraken_credentials(kraken_key, kraken_secret):
        logger.error("Impossible de se connecter à Kraken. Veuillez vérifier vos credentials.")
        return
    
    # Configuration du stockage Redis
    storage = RedisStorage(
        name="example_storage",
        host=redis_host,
        port=redis_port,
        default_ttl=3600,  # 1 heure
        retry_on_timeout=True,
        max_retries=3
    )
    
    # Configuration du collecteur
    collector = KrakenTradeCollector(
        name="example_collector",
        symbols=["XBT/USD", "ETH/USD"],  # Bitcoin et Ethereum en USD
        storage=storage,
        api_key=kraken_key,
        api_secret=kraken_secret,
        max_retries=3,
        retry_delay=5
    )
    
    try:
        # Connexion au stockage
        logger.info("Connexion à Redis...")
        await storage.connect()
        
        # Démarrage du collecteur
        logger.info("Démarrage du collecteur...")
        await collector.start()
        
        # Attente de quelques trades
        logger.info("Collecte des trades pendant 60 secondes...")
        await asyncio.sleep(60)
        
        # Récupération des trades stockés
        for symbol in ["XBTUSD", "ETHUSD"]:  # Format Kraken
            trades = await storage.get_trades(symbol, limit=5)
            logger.info(f"Derniers trades pour {symbol}:")
            for trade in trades:
                logger.info(f"  Prix: {trade['price']}, Volume: {trade['amount']}")
                
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur...")
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        
    finally:
        # Arrêt propre
        logger.info("Arrêt du collecteur...")
        await collector.stop()
        
        logger.info("Déconnexion de Redis...")
        await storage.disconnect()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Programme arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}")
        sys.exit(1) 