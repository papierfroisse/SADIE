"""Exemple d'utilisation de plusieurs collecteurs simultanément."""

import asyncio
import os
import sys
from dotenv import load_dotenv
import logging
from typing import Dict, List

# Importation standardisée des collecteurs
from sadie.core.collectors import KrakenTradeCollector, BinanceTradeCollector
from sadie.storage import RedisStorage

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultiExchangeCollector:
    """Collecteur multi-exchange qui gère plusieurs collecteurs simultanément."""
    
    def __init__(self, 
                 symbols_map: Dict[str, List[str]],
                 redis_host: str = "localhost", 
                 redis_port: int = 6379,
                 redis_ttl: int = 3600):
        """Initialise le collecteur multi-exchange.
        
        Args:
            symbols_map: Dictionnaire avec les exchanges comme clés et les listes de symboles comme valeurs
            redis_host: Hôte Redis
            redis_port: Port Redis
            redis_ttl: Durée de vie des données en secondes
        """
        self.symbols_map = symbols_map
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_ttl = redis_ttl
        self.collectors = {}
        self.storage = None
    
    async def setup(self):
        """Configure le stockage et les collecteurs."""
        # Configuration du stockage Redis
        self.storage = RedisStorage(
            name="multi_exchange_storage",
            host=self.redis_host,
            port=self.redis_port,
            default_ttl=self.redis_ttl,
            retry_on_timeout=True,
            max_retries=3
        )
        
        # Connexion au stockage
        logger.info("Connexion à Redis...")
        await self.storage.connect()
        
        # Création des collecteurs pour chaque exchange
        if "kraken" in self.symbols_map:
            logger.info("Configuration du collecteur Kraken...")
            self.collectors["kraken"] = KrakenTradeCollector(
                name="kraken_collector",
                symbols=self.symbols_map["kraken"],
                storage=self.storage,
                api_key=os.getenv("KRAKEN_API_KEY"),
                api_secret=os.getenv("KRAKEN_API_SECRET"),
                max_retries=3,
                retry_delay=5
            )
            
        if "binance" in self.symbols_map:
            logger.info("Configuration du collecteur Binance...")
            self.collectors["binance"] = BinanceTradeCollector(
                name="binance_collector",
                symbols=self.symbols_map["binance"],
                storage=self.storage,
                api_key=os.getenv("BINANCE_API_KEY"),
                api_secret=os.getenv("BINANCE_API_SECRET"),
                max_retries=3,
                retry_delay=5
            )
    
    async def start(self):
        """Démarre tous les collecteurs."""
        for exchange, collector in self.collectors.items():
            logger.info(f"Démarrage du collecteur {exchange}...")
            await collector.start()
    
    async def stop(self):
        """Arrête tous les collecteurs et déconnecte le stockage."""
        for exchange, collector in self.collectors.items():
            logger.info(f"Arrêt du collecteur {exchange}...")
            await collector.stop()
            
        logger.info("Déconnexion de Redis...")
        if self.storage:
            await self.storage.disconnect()
    
    async def display_stats(self, duration: int = 10, interval: int = 2):
        """Affiche des statistiques sur les trades collectés.
        
        Args:
            duration: Durée totale en secondes
            interval: Intervalle entre les affichages en secondes
        """
        end_time = asyncio.get_event_loop().time() + duration
        
        while asyncio.get_event_loop().time() < end_time:
            logger.info("=" * 50)
            logger.info("STATISTIQUES DES TRADES EN TEMPS RÉEL")
            logger.info("=" * 50)
            
            for exchange, collector in self.collectors.items():
                logger.info(f"Exchange: {exchange.upper()}")
                data = await collector.collect()
                
                for symbol, symbol_data in data.items():
                    trades = symbol_data.get("trades", [])
                    stats = symbol_data.get("statistics", {})
                    
                    logger.info(f"  Symbole: {symbol}")
                    logger.info(f"  Nombre de trades: {stats.get('count', 0)}")
                    logger.info(f"  Volume total: {stats.get('volume', 0)}")
                    logger.info(f"  Prix moyen: {stats.get('price', {}).get('average', 0)}")
                    logger.info(f"  Dernier prix: {stats.get('price', {}).get('last', 0)}")
                    logger.info(f"  Variation: {stats.get('price', {}).get('change_percent', 0):.2f}%")
                    logger.info("")
            
            await asyncio.sleep(interval)

async def main():
    """Fonction principale."""
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Configuration des paires à suivre pour chaque exchange
    symbols_map = {
        "kraken": ["XBT/USD", "ETH/USD"],  # Bitcoin et Ethereum en USD sur Kraken
        "binance": ["BTCUSDT", "ETHUSDT"]  # Bitcoin et Ethereum en USDT sur Binance
    }
    
    # Création du collecteur multi-exchange
    multi_collector = MultiExchangeCollector(
        symbols_map=symbols_map,
        redis_host=os.getenv("REDIS_HOST", "localhost"),
        redis_port=int(os.getenv("REDIS_PORT", 6379))
    )
    
    try:
        # Configuration
        await multi_collector.setup()
        
        # Démarrage des collecteurs
        await multi_collector.start()
        
        # Affichage des statistiques pendant 60 secondes
        logger.info("Affichage des statistiques pendant 60 secondes...")
        await multi_collector.display_stats(duration=60, interval=5)
                
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur...")
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")
        
    finally:
        # Arrêt propre
        await multi_collector.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Programme arrêté par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur fatale: {str(e)}")
        sys.exit(1) 