"""Module de collecteurs de données."""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from ...core.monitoring import get_logger
from ...utils.decorators import log_execution, retry
from ..exceptions import CollectorError

logger = get_logger(__name__)

class DataCollector(ABC):
    """Classe de base pour les collecteurs de données."""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"collector.{name}")
        self._running = False
        self._tasks: List[asyncio.Task] = []
        
    async def __aenter__(self):
        """Support du context manager."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Arrête le collecteur à la sortie du context."""
        await self.stop()
        
    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """Collecte les données.
        
        Returns:
            Données collectées
        """
        pass
        
    @log_execution()
    async def start(self) -> None:
        """Démarre le collecteur."""
        if not self._running:
            self._running = True
            self.logger.info(f"Collecteur {self.name} démarré")
            
    @log_execution()
    async def stop(self) -> None:
        """Arrête le collecteur."""
        if self._running:
            self._running = False
            for task in self._tasks:
                task.cancel()
            await asyncio.gather(*self._tasks, return_exceptions=True)
            self._tasks.clear()
            self.logger.info(f"Collecteur {self.name} arrêté")
            
    @retry(max_attempts=3)
    async def collect_with_retry(self) -> Dict[str, Any]:
        """Collecte les données avec retry."""
        try:
            return await self.collect()
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte: {e}")
            raise CollectorError(f"Erreur de collecte: {e}")
            
    async def collect_periodic(
        self,
        interval: float,
        callback: Optional[callable] = None
    ) -> None:
        """Collecte périodique des données.
        
        Args:
            interval: Intervalle en secondes
            callback: Fonction de callback pour les données collectées
        """
        while self._running:
            try:
                start_time = datetime.utcnow()
                data = await self.collect_with_retry()
                
                if callback:
                    try:
                        await callback(data)
                    except Exception as e:
                        self.logger.error(f"Erreur dans le callback: {e}")
                        
                # Calcul du temps d'attente
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                wait_time = max(0, interval - elapsed)
                await asyncio.sleep(wait_time)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erreur dans la collecte périodique: {e}")
                await asyncio.sleep(interval)
                
    def start_periodic(
        self,
        interval: float,
        callback: Optional[callable] = None
    ) -> None:
        """Démarre la collecte périodique.
        
        Args:
            interval: Intervalle en secondes
            callback: Fonction de callback pour les données collectées
        """
        task = asyncio.create_task(
            self.collect_periodic(interval, callback)
        )
        self._tasks.append(task)
        self.logger.info(
            f"Collecte périodique démarrée "
            f"(intervalle={interval}s)"
        ) 