"""Exemple d'utilisation du collecteur avec Redis."""

import asyncio
import os
import sys
from dotenv import load_dotenv
from sadie.core.collectors import BinanceTradeCollector
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
    """Vérifie si Redis est accessible.
    
    Returns:
        bool: True si Redis est accessible, False sinon
    """
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

async def check_binance_credentials(api_key: Optional[str], api_secret: Optional[str]) -> bool:
    """Vérifie si les credentials Binance sont valides.
    
    Returns:
        bool: True si les credentials sont valides, False sinon
    """
    if not api_key or not api_secret:
        logger.error("Clés API Binance non configurées")
        return False
        
    try:
        collector = BinanceTradeCollector(
            name="credentials_test",
            symbols=["BTCUSDT"],
            api_key=api_key,
            api_secret=api_secret
        )
        await collector._connect()
        await collector.stop()
        return True
    except Exception as e:
        logger.error(f"Erreur de connexion à Binance: {str(e)}")
        return False

async def main():
    """Fonction principale."""
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Paramètres de connexion
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    binance_key = os.getenv("BINANCE_API_KEY")
    binance_secret = os.getenv("BINANCE_API_SECRET")
    
    # Vérification des prérequis
    logger.info("Vérification des connexions...")
    
    if not await check_redis_connection(redis_host, redis_port):
        logger.error("Redis n'est pas accessible. Veuillez vérifier que Redis est démarré.")
        return
        
    if not await check_binance_credentials(binance_key, binance_secret):
        logger.error("Impossible de se connecter à Binance. Veuillez vérifier vos credentials.")
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
    collector = BinanceTradeCollector(
        name="example_collector",
        symbols=["BTCUSDT", "ETHUSDT"],
        storage=storage,
        api_key=binance_key,
        api_secret=binance_secret,
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
        for symbol in ["BTCUSDT", "ETHUSDT"]:
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