"""
Module de gestion du cache pour les données.
"""

import datetime
import json
import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

class DataCache:
    """Gestionnaire de cache pour les données."""
    
    def __init__(self, cache_dir: Union[str, Path]):
        """
        Initialise le gestionnaire de cache.
        
        Args:
            cache_dir: Chemin du répertoire de cache
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(
        self,
        source: str,
        symbol: str,
        data_type: str,
        interval: Optional[str] = None
    ) -> Path:
        """
        Génère le chemin du fichier de cache.
        
        Args:
            source: Source des données
            symbol: Symbole
            data_type: Type de données
            interval: Intervalle de temps (optionnel)
            
        Returns:
            Chemin du fichier de cache
        """
        filename = f"{symbol.replace('/', '_')}_{data_type}"
        if interval:
            filename += f"_{interval}"
        filename += ".pkl"
        return self.cache_dir / source / filename
    
    def save(
        self,
        data: Any,
        source: str,
        symbol: str,
        data_type: str,
        interval: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Sauvegarde des données dans le cache.
        
        Args:
            data: Données à sauvegarder
            source: Source des données
            symbol: Symbole
            data_type: Type de données
            interval: Intervalle de temps (optionnel)
            metadata: Métadonnées (optionnel)
        """
        cache_path = self._get_cache_path(source, symbol, data_type, interval)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        
        cache_data = {
            "data": data,
            "metadata": metadata or {},
            "timestamp": datetime.datetime.now().timestamp()
        }
        
        with open(cache_path, "wb") as f:
            pickle.dump(cache_data, f)
    
    def load(
        self,
        source: str,
        symbol: str,
        data_type: str,
        interval: Optional[str] = None,
        max_age: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Charge des données depuis le cache.
        
        Args:
            source: Source des données
            symbol: Symbole
            data_type: Type de données
            interval: Intervalle de temps (optionnel)
            max_age: Âge maximum des données en secondes (optionnel)
            
        Returns:
            Données et métadonnées ou None si non trouvées ou expirées
        """
        cache_path = self._get_cache_path(source, symbol, data_type, interval)
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, "rb") as f:
                cache_data = pickle.load(f)
            
            # Vérification de l'âge des données
            if max_age is not None:
                age = datetime.datetime.now().timestamp() - cache_data["timestamp"]
                if age > max_age:
                    return None
            
            return cache_data
        except (pickle.UnpicklingError, KeyError, EOFError):
            return None
    
    def clear(
        self,
        source: Optional[str] = None,
        symbol: Optional[str] = None,
        data_type: Optional[str] = None,
        interval: Optional[str] = None
    ) -> None:
        """
        Supprime des données du cache.
        
        Args:
            source: Source des données (optionnel)
            symbol: Symbole (optionnel)
            data_type: Type de données (optionnel)
            interval: Intervalle de temps (optionnel)
        """
        if source:
            source_dir = self.cache_dir / source
            if not source_dir.exists():
                return
            
            if symbol:
                pattern = f"{symbol.replace('/', '_')}"
                if data_type:
                    pattern += f"_{data_type}"
                    if interval:
                        pattern += f"_{interval}"
                pattern += ".pkl"
                
                for file in source_dir.glob(pattern):
                    file.unlink()
            else:
                for file in source_dir.glob("*.pkl"):
                    file.unlink()
                if not any(source_dir.iterdir()):
                    source_dir.rmdir()
        else:
            for source_dir in self.cache_dir.glob("*"):
                if source_dir.is_dir():
                    for file in source_dir.glob("*.pkl"):
                        file.unlink()
                    if not any(source_dir.iterdir()):
                        source_dir.rmdir()
    
    def get_info(self) -> Dict[str, Any]:
        """
        Récupère des informations sur le cache.
        
        Returns:
            Dictionnaire contenant les informations sur le cache
        """
        info = {
            "size": 0,
            "files": 0,
            "sources": {}
        }
        
        for source_dir in self.cache_dir.glob("*"):
            if source_dir.is_dir():
                source_info = {
                    "size": 0,
                    "files": 0,
                    "symbols": set()
                }
                
                for file in source_dir.glob("*.pkl"):
                    source_info["size"] += file.stat().st_size
                    source_info["files"] += 1
                    
                    # Extraction du symbole
                    symbol = file.stem.split("_")[0].replace("_", "/")
                    source_info["symbols"].add(symbol)
                
                if source_info["files"] > 0:
                    info["size"] += source_info["size"]
                    info["files"] += source_info["files"]
                    source_info["symbols"] = sorted(source_info["symbols"])
                    info["sources"][source_dir.name] = source_info
        
        return info 