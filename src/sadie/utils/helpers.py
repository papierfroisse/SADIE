"""
Fonctions utilitaires diverses.
"""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .logging import get_logger

logger = get_logger(__name__)

def ensure_dir(path: Union[str, Path]) -> Path:
    """
    S'assure qu'un répertoire existe.

    Args:
        path: Chemin du répertoire

    Returns:
        Chemin du répertoire créé
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def load_json(path: Union[str, Path]) -> Dict[str, Any]:
    """
    Charge un fichier JSON.

    Args:
        path: Chemin du fichier

    Returns:
        Données JSON
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement du fichier JSON {path}: {e}")
        return {}

def save_json(data: Dict[str, Any], path: Union[str, Path], indent: int = 2) -> None:
    """
    Sauvegarde des données en JSON.

    Args:
        data: Données à sauvegarder
        path: Chemin du fichier
        indent: Indentation
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier JSON {path}: {e}")

def hash_data(data: Any) -> str:
    """
    Calcule le hash d'une donnée.

    Args:
        data: Donnée à hasher

    Returns:
        Hash de la donnée
    """
    try:
        if isinstance(data, (dict, list)):
            data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(str(data).encode()).hexdigest()
    except Exception as e:
        logger.error(f"Erreur lors du calcul du hash: {e}")
        return ""

def format_timestamp(
    timestamp: Optional[Union[int, float, str, datetime]] = None,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Formate un timestamp.

    Args:
        timestamp: Timestamp à formater
        format_str: Format de sortie

    Returns:
        Timestamp formaté
    """
    try:
        if timestamp is None:
            dt = datetime.now(timezone.utc)
        elif isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp, timezone.utc)
        elif isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        else:
            dt = timestamp
        
        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"Erreur lors du formatage du timestamp: {e}")
        return ""

def parse_timestamp(
    timestamp: str,
    format_str: Optional[str] = None
) -> Optional[datetime]:
    """
    Parse un timestamp.

    Args:
        timestamp: Timestamp à parser
        format_str: Format d'entrée

    Returns:
        Datetime parsé
    """
    try:
        if format_str:
            return datetime.strptime(timestamp, format_str)
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except Exception as e:
        logger.error(f"Erreur lors du parsing du timestamp: {e}")
        return None

def chunk_list(lst: List[Any], size: int) -> List[List[Any]]:
    """
    Découpe une liste en morceaux.

    Args:
        lst: Liste à découper
        size: Taille des morceaux

    Returns:
        Liste de morceaux
    """
    return [lst[i:i + size] for i in range(0, len(lst), size)]

def deep_get(obj: Dict[str, Any], path: str, default: Any = None) -> Any:
    """
    Récupère une valeur dans un dictionnaire imbriqué.

    Args:
        obj: Dictionnaire
        path: Chemin de la valeur (e.g. "a.b.c")
        default: Valeur par défaut

    Returns:
        Valeur trouvée ou valeur par défaut
    """
    try:
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if not isinstance(current, dict):
                return default
            if part not in current:
                return default
            current = current[part]
        
        return current
    except Exception:
        return default

def deep_set(obj: Dict[str, Any], path: str, value: Any) -> None:
    """
    Définit une valeur dans un dictionnaire imbriqué.

    Args:
        obj: Dictionnaire
        path: Chemin de la valeur (e.g. "a.b.c")
        value: Valeur à définir
    """
    parts = path.split(".")
    current = obj
    
    for part in parts[:-1]:
        if part not in current or not isinstance(current[part], dict):
            current[part] = {}
        current = current[part]
    
    current[parts[-1]] = value

def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
    """
    Met à jour un dictionnaire de manière récursive.

    Args:
        d: Dictionnaire à mettre à jour
        u: Dictionnaire avec les nouvelles valeurs

    Returns:
        Dictionnaire mis à jour
    """
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            d[k] = deep_update(d[k], v)
        else:
            d[k] = v
    return d

def get_file_size(path: Union[str, Path]) -> int:
    """
    Récupère la taille d'un fichier.

    Args:
        path: Chemin du fichier

    Returns:
        Taille en octets
    """
    try:
        return os.path.getsize(path)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la taille du fichier {path}: {e}")
        return 0

def format_size(size: int) -> str:
    """
    Formate une taille en octets.

    Args:
        size: Taille en octets

    Returns:
        Taille formatée
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB" 