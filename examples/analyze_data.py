"""
Exemple d'analyse de données.
"""

import asyncio
import logging
from datetime import datetime, timedelta

import pandas as pd

from sadie.analysis import TimeSeriesAnalyzer, StatisticalAnalyzer
from sadie.storage import MemoryStorage
from sadie.utils.logging import setup_logging

# Configuration du logging
setup_logging(level="INFO")
logger = logging.getLogger(__name__)

async def main():
    """Fonction principale."""
    # Initialisation des composants
    storage = MemoryStorage()
    time_series = TimeSeriesAnalyzer(window_size=20)
    statistical = StatisticalAnalyzer(confidence_level=0.95)
    
    try:
        # Connexion au stockage
        await storage.connect()
        
        # Récupération des données des dernières 24h
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)
        
        data = await storage.retrieve(
            start_time=start_time,
            end_time=end_time,
            symbol="BTCUSDT"
        )
        
        if not data:
            logger.warning("Aucune donnée trouvée")
            return
        
        # Préparation des données pour l'analyse
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        
        # Analyse des séries temporelles
        logger.info("Analyse des séries temporelles...")
        ts_results = await time_series.analyze(df)
        
        logger.info("Résultats de l'analyse des séries temporelles:")
        logger.info(f"Tendance du prix: {ts_results['trend'].get('price', 'N/A')}")
        logger.info(f"Moyenne mobile du prix: {ts_results['rolling_mean'].get('price', 'N/A'):.2f}")
        logger.info(f"Volatilité (std): {ts_results['rolling_std'].get('price', 'N/A'):.2f}")
        
        # Analyse statistique
        logger.info("\nAnalyse statistique...")
        stat_results = await statistical.analyze(df)
        
        logger.info("Résultats de l'analyse statistique:")
        if "price_normal_test" in stat_results:
            normal_test = stat_results["price_normal_test"]
            logger.info(f"Test de normalité du prix:")
            logger.info(f"  - p-value: {normal_test['p_value']:.4f}")
            logger.info(f"  - distribution normale: {normal_test['is_normal']}")
        
        if "correlations" in stat_results:
            logger.info("\nMatrice de corrélation:")
            for col1, corrs in stat_results["correlations"].items():
                for col2, corr in corrs.items():
                    if col1 < col2:  # Évite les doublons
                        logger.info(f"{col1} vs {col2}: {corr:.2f}")
    
    except Exception as e:
        logger.error(f"Erreur: {e}")
    finally:
        # Nettoyage
        await storage.disconnect()
        logger.info("Analyse terminée")

if __name__ == "__main__":
    asyncio.run(main()) 