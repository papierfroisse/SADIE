"""Processeurs de flux de données."""

import json
from typing import Any, Callable, Dict, Optional
from datetime import datetime

from . import StreamEvent, StreamProcessor

class FilterProcessor(StreamProcessor):
    """Filtre les événements selon un prédicat."""
    
    def __init__(self, predicate: Callable[[StreamEvent], bool]):
        """Initialise le filtre.
        
        Args:
            predicate: Fonction de filtrage retournant True pour garder l'événement
        """
        self.predicate = predicate
        
    async def process(self, event: StreamEvent) -> StreamEvent:
        """Filtre l'événement selon le prédicat."""
        if self.predicate(event):
            return event
        raise ValueError("Event filtered out")

class TransformProcessor(StreamProcessor):
    """Transforme les données d'un événement."""
    
    def __init__(self, transform_func: Callable[[Any], Any]):
        """Initialise le transformateur.
        
        Args:
            transform_func: Fonction de transformation des données
        """
        self.transform_func = transform_func
        
    async def process(self, event: StreamEvent) -> StreamEvent:
        """Transforme les données de l'événement."""
        transformed_data = self.transform_func(event.data)
        return StreamEvent(
            topic=event.topic,
            data=transformed_data,
            timestamp=event.timestamp,
            metadata=event.metadata
        )

class EnrichProcessor(StreamProcessor):
    """Enrichit les événements avec des métadonnées."""
    
    def __init__(self, enrich_func: Callable[[StreamEvent], Dict]):
        """Initialise l'enrichisseur.
        
        Args:
            enrich_func: Fonction retournant les métadonnées à ajouter
        """
        self.enrich_func = enrich_func
        
    async def process(self, event: StreamEvent) -> StreamEvent:
        """Enrichit l'événement avec des métadonnées."""
        additional_metadata = self.enrich_func(event)
        new_metadata = {**event.metadata, **additional_metadata}
        return StreamEvent(
            topic=event.topic,
            data=event.data,
            timestamp=event.timestamp,
            metadata=new_metadata
        )

class ValidationProcessor(StreamProcessor):
    """Valide les événements selon un schéma."""
    
    def __init__(self, schema: Dict):
        """Initialise le validateur.
        
        Args:
            schema: Schéma de validation (format simplifié)
        """
        self.schema = schema
        
    def _validate(self, data: Any, schema: Dict) -> bool:
        """Valide les données selon le schéma."""
        if "type" in schema:
            if schema["type"] == "object":
                if not isinstance(data, dict):
                    return False
                for key, subschema in schema.get("properties", {}).items():
                    if key not in data:
                        if schema.get("required", False):
                            return False
                        continue
                    if not self._validate(data[key], subschema):
                        return False
            elif schema["type"] == "array":
                if not isinstance(data, list):
                    return False
                item_schema = schema.get("items", {})
                return all(self._validate(item, item_schema) for item in data)
            elif schema["type"] == "string":
                return isinstance(data, str)
            elif schema["type"] == "number":
                return isinstance(data, (int, float))
            elif schema["type"] == "boolean":
                return isinstance(data, bool)
        return True
        
    async def process(self, event: StreamEvent) -> StreamEvent:
        """Valide l'événement selon le schéma."""
        if not self._validate(event.data, self.schema):
            raise ValueError("Event validation failed")
        return event

class ThrottleProcessor(StreamProcessor):
    """Limite le débit des événements."""
    
    def __init__(self, max_events: int, window_seconds: float):
        """Initialise le limiteur de débit.
        
        Args:
            max_events: Nombre maximum d'événements
            window_seconds: Fenêtre de temps en secondes
        """
        self.max_events = max_events
        self.window_seconds = window_seconds
        self.events: list[datetime] = []
        
    async def process(self, event: StreamEvent) -> StreamEvent:
        """Limite le débit des événements."""
        now = datetime.utcnow()
        # Supprime les événements hors de la fenêtre
        self.events = [
            ts for ts in self.events 
            if (now - ts).total_seconds() <= self.window_seconds
        ]
        
        if len(self.events) >= self.max_events:
            raise ValueError("Rate limit exceeded")
            
        self.events.append(now)
        return event 