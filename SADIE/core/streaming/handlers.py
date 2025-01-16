"""Handlers pour le système de streaming."""

import json
import logging
from typing import Any, Dict, Optional

from . import StreamEvent, StreamHandler
from ..monitoring import get_logger

class LoggingHandler(StreamHandler):
    """Handler qui enregistre les événements dans les logs."""
    
    def __init__(self, level: int = logging.INFO):
        self.logger = get_logger(__name__)
        self.level = level
    
    async def handle(self, event: StreamEvent) -> None:
        """Enregistre l'événement dans les logs."""
        self.logger.log(
            self.level,
            f"Event reçu - Topic: {event.topic}, Data: {event.data}"
        )

class DatabaseHandler(StreamHandler):
    """Handler qui sauvegarde les événements dans la base de données."""
    
    def __init__(self, session_maker):
        self.session_maker = session_maker
        self.logger = get_logger(__name__)
    
    async def handle(self, event: StreamEvent) -> None:
        """Sauvegarde l'événement dans la base de données."""
        from ..models.events import Event
        
        async with self.session_maker() as session:
            try:
                db_event = Event(
                    topic=event.topic,
                    timestamp=event.timestamp,
                    data=event.data
                )
                session.add(db_event)
                await session.commit()
                self.logger.debug(f"Event sauvegardé en DB: {event}")
            except Exception as e:
                self.logger.error(f"Erreur lors de la sauvegarde en DB: {e}")
                await session.rollback()
                raise

class CacheHandler(StreamHandler):
    """Handler qui met en cache les événements."""
    
    def __init__(self, cache, ttl: Optional[int] = None):
        self.cache = cache
        self.ttl = ttl
        self.logger = get_logger(__name__)
    
    async def handle(self, event: StreamEvent) -> None:
        """Met l'événement en cache."""
        try:
            key = f"event:{event.topic}:{event.timestamp.isoformat()}"
            await self.cache.set(
                key,
                {
                    "topic": event.topic,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data
                },
                ttl=self.ttl
            )
            self.logger.debug(f"Event mis en cache: {key}")
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise en cache: {e}")
            raise

class WebSocketHandler(StreamHandler):
    """Handler qui envoie les événements via WebSocket."""
    
    def __init__(self, websocket):
        self.websocket = websocket
        self.logger = get_logger(__name__)
    
    async def handle(self, event: StreamEvent) -> None:
        """Envoie l'événement via WebSocket."""
        try:
            message = {
                "topic": event.topic,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data
            }
            await self.websocket.send_json(message)
            self.logger.debug(f"Event envoyé via WebSocket: {event}")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi WebSocket: {e}")
            raise 