"""
Module de cache pour SADIE.

Implémente un système de cache efficace pour les données de marché
avec gestion de la mémoire et expiration des données.
"""

import time
from typing import Dict, List, Any, Optional
from collections import deque
import threading

class Cache:
    """Cache avec gestion de la mémoire et expiration."""
    
    def __init__(
        self,
        max_size: int = 1000000,
        expiry_seconds: Optional[int] = None
    ):
        """Initialise le cache.
        
        Args:
            max_size: Taille maximale par clé
            expiry_seconds: Durée de vie des données en secondes
        """
        self._max_size = max_size
        self._expiry = expiry_seconds
        self._data: Dict[str, deque] = {}
        self._timestamps: Dict[str, deque] = {}
        self._lock = threading.Lock()
        
    def add(self, key: str, value: Any) -> None:
        """Ajoute une valeur au cache.
        
        Args:
            key: Clé d'identification
            value: Valeur à stocker
        """
        with self._lock:
            # Initialiser les queues si nécessaire
            if key not in self._data:
                self._data[key] = deque(maxlen=self._max_size)
                self._timestamps[key] = deque(maxlen=self._max_size)
            
            # Ajouter la valeur et son timestamp
            self._data[key].append(value)
            self._timestamps[key].append(time.time())
            
            # Nettoyer les données expirées
            if self._expiry:
                self._cleanup_expired(key)
                
    def get(self, key: str) -> deque:
        """Récupère toutes les valeurs pour une clé.
        
        Args:
            key: Clé d'identification
            
        Returns:
            Queue des valeurs
        """
        with self._lock:
            if key not in self._data:
                return deque()
                
            if self._expiry:
                self._cleanup_expired(key)
                
            return self._data[key]
            
    def get_latest(self, key: str, limit: int = 1) -> List[Any]:
        """Récupère les dernières valeurs pour une clé.
        
        Args:
            key: Clé d'identification
            limit: Nombre de valeurs à récupérer
            
        Returns:
            Liste des dernières valeurs
        """
        with self._lock:
            if key not in self._data:
                return []
                
            if self._expiry:
                self._cleanup_expired(key)
                
            return list(self._data[key])[-limit:]
            
    def clear(self, key: Optional[str] = None) -> None:
        """Vide le cache.
        
        Args:
            key: Clé spécifique à vider (tout le cache si None)
        """
        with self._lock:
            if key:
                if key in self._data:
                    self._data[key].clear()
                    self._timestamps[key].clear()
            else:
                self._data.clear()
                self._timestamps.clear()
                
    def _cleanup_expired(self, key: str) -> None:
        """Nettoie les données expirées pour une clé.
        
        Args:
            key: Clé à nettoyer
        """
        if not self._expiry:
            return
            
        current_time = time.time()
        while (
            self._timestamps[key] and
            current_time - self._timestamps[key][0] > self._expiry
        ):
            self._timestamps[key].popleft()
            self._data[key].popleft()
            
    def get_size(self, key: Optional[str] = None) -> int:
        """Retourne la taille du cache.
        
        Args:
            key: Clé spécifique (taille totale si None)
            
        Returns:
            Nombre d'éléments dans le cache
        """
        with self._lock:
            if key:
                return len(self._data.get(key, deque()))
            return sum(len(q) for q in self._data.values())
            
    def get_keys(self) -> List[str]:
        """Retourne la liste des clés dans le cache.
        
        Returns:
            Liste des clés
        """
        with self._lock:
            return list(self._data.keys())
            
    def get_stats(self) -> Dict[str, Any]:
        """Retourne des statistiques sur le cache.
        
        Returns:
            Dictionnaire des statistiques
        """
        with self._lock:
            return {
                "total_keys": len(self._data),
                "total_items": self.get_size(),
                "keys": {
                    key: len(self._data[key])
                    for key in self._data
                },
                "memory_usage": sum(
                    len(str(item).encode())
                    for queue in self._data.values()
                    for item in queue
                )
            } 