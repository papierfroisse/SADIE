"""Module de streaming pour SADIE."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set

from ..monitoring import get_logger

logger = get_logger(__name__)

class StreamEvent:
    """Représente un événement dans le système de streaming."""
    
    def __init__(
        self,
        topic: str,
        data: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        self.topic = topic
        self.data = data
        self.timestamp = timestamp or datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"StreamEvent(topic='{self.topic}', timestamp='{self.timestamp}')"

class StreamHandler:
    """Classe de base pour tous les handlers d'événements."""
    
    async def handle(self, event: StreamEvent) -> None:
        """Traite un événement."""
        raise NotImplementedError("Les sous-classes doivent implémenter handle()")

class StreamManager:
    """Gestionnaire de flux de données."""
    
    def __init__(self):
        self._handlers: Dict[str, Set[StreamHandler]] = {}
        self._running = False
        self._queue: asyncio.Queue[StreamEvent] = asyncio.Queue()
        
    async def __aenter__(self):
        """Démarre le gestionnaire de flux."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Arrête le gestionnaire de flux."""
        await self.stop()
    
    def subscribe(self, topic: str, handler: StreamHandler) -> None:
        """Ajoute un handler pour un topic."""
        if topic not in self._handlers:
            self._handlers[topic] = set()
        self._handlers[topic].add(handler)
        logger.info(f"Handler ajouté pour le topic '{topic}'")
    
    def unsubscribe(self, topic: str, handler: StreamHandler) -> None:
        """Retire un handler d'un topic."""
        if topic in self._handlers:
            self._handlers[topic].discard(handler)
            if not self._handlers[topic]:
                del self._handlers[topic]
            logger.info(f"Handler retiré du topic '{topic}'")
    
    async def publish(self, event: StreamEvent) -> None:
        """Publie un événement dans le flux."""
        await self._queue.put(event)
        logger.debug(f"Événement publié: {event}")
    
    async def _process_events(self) -> None:
        """Traite les événements dans la queue."""
        while self._running:
            try:
                event = await self._queue.get()
                handlers = self._handlers.get(event.topic, set())
                
                for handler in handlers:
                    try:
                        await handler.handle(event)
                    except Exception as e:
                        logger.error(f"Erreur dans le handler: {e}")
                        
                self._queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erreur dans le traitement des événements: {e}")
    
    async def start(self) -> None:
        """Démarre le gestionnaire de flux."""
        if not self._running:
            self._running = True
            asyncio.create_task(self._process_events())
            logger.info("StreamManager démarré")
    
    async def stop(self) -> None:
        """Arrête le gestionnaire de flux."""
        if self._running:
            self._running = False
            await self._queue.join()
            logger.info("StreamManager arrêté") 