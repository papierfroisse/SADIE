"""Module de base pour les collecteurs de données."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from sadie.core.monitoring.metrics import CollectorPerformanceMonitor, CollectorMetricsManager

# Gestionnaire global des métriques
global_metrics_manager = CollectorMetricsManager()

class BaseCollector(ABC):
    """Classe de base pour tous les collecteurs de données.
    
    Définit l'interface commune que tous les collecteurs doivent implémenter.
    """
    
    def __init__(
        self,
        name: str,
        symbols: List[str],
        update_interval: float = 1.0,
        logger: Optional[logging.Logger] = None,
        exchange: str = "unknown",
        enable_metrics: bool = True,
    ):
        """Initialise le collecteur de base.
        
        Args:
            name: Nom unique du collecteur
            symbols: Liste des symboles à collecter
            update_interval: Intervalle de mise à jour en secondes
            logger: Logger optionnel
            exchange: Nom de l'exchange (binance, kraken, etc.)
            enable_metrics: Active ou désactive le monitoring des performances
        """
        self.name = name
        self.symbols = symbols
        self.update_interval = update_interval
        self.logger = logger or logging.getLogger(f"sadie.collectors.{name}")
        self.exchange = exchange
        
        self._running = False
        self._task = None
        self._data = {symbol: {"price": 0.0, "volume": 0.0, "high": 0.0, "low": float("inf")} for symbol in symbols}
        
        # Initialisation du moniteur de performances si activé
        self._performance_monitor = None
        if enable_metrics:
            self._performance_monitor = CollectorPerformanceMonitor(
                collector_name=name,
                exchange=exchange,
                symbols=symbols,
                metrics_manager=global_metrics_manager
            )
    
    async def start(self) -> None:
        """Démarre le collecteur."""
        if self._running:
            self.logger.warning(f"Collecteur {self.name} déjà en cours d'exécution")
            return
            
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        self.logger.info(f"Collecteur {self.name} démarré")
    
    async def stop(self) -> None:
        """Arrête le collecteur."""
        if not self._running:
            return
            
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            
        # Enregistrement final des métriques
        if self._performance_monitor:
            await self._performance_monitor.record_metrics(force=True)
            
        self.logger.info(f"Collecteur {self.name} arrêté")
    
    async def _run_loop(self) -> None:
        """Boucle principale du collecteur."""
        while self._running:
            try:
                # Mesure du temps de traitement pour les métriques
                start_time = time.time()
                
                await self._run()
                
                # Enregistrement des métriques de performance
                if self._performance_monitor:
                    processing_time = (time.time() - start_time) * 1000  # en ms
                    self._performance_monitor.record_processing_time(processing_time)
                    self._performance_monitor.messages_received += 1
                    await self._performance_monitor.record_metrics()
                    
                await asyncio.sleep(self.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur dans le collecteur {self.name}: {e}")
                
                # Enregistrement de l'erreur dans les métriques
                if self._performance_monitor:
                    self._performance_monitor.record_error()
                    
                await asyncio.sleep(self.update_interval)
    
    @abstractmethod
    async def _run(self) -> None:
        """Méthode principale d'exécution du collecteur.
        
        Cette méthode doit être implémentée par toutes les sous-classes.
        """
        pass
    
    async def get_data(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """Récupère les données collectées.
        
        Args:
            symbol: Symbole spécifique ou None pour tous les symboles
            
        Returns:
            Les données collectées pour le(s) symbole(s) demandé(s)
        """
        if symbol:
            return self._data.get(symbol, {})
        return self._data.copy()
        
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques de performance du collecteur.
        
        Returns:
            Rapport de performance ou dictionnaire vide si les métriques sont désactivées
        """
        if self._performance_monitor:
            return await self._performance_monitor.get_performance_report()
        return {
            "collector": {
                "name": self.name,
                "exchange": self.exchange,
                "symbols": self.symbols,
                "metrics_enabled": False
            }
        }

# Fonction pour démarrer le gestionnaire global des métriques
async def start_metrics_manager():
    """Démarre le gestionnaire global des métriques."""
    await global_metrics_manager.start()

# Fonction pour arrêter le gestionnaire global des métriques
async def stop_metrics_manager():
    """Arrête le gestionnaire global des métriques."""
    await global_metrics_manager.stop() 