"""Module d'utilitaires."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ..core.monitoring import get_logger

logger = get_logger(__name__)

def ensure_dir(path: Union[str, Path]) -> Path:
    """Assure qu'un répertoire existe.
    
    Args:
        path: Chemin du répertoire
        
    Returns:
        Chemin du répertoire créé
    """
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def format_timestamp(timestamp: datetime) -> str:
    """Formate un timestamp en chaîne ISO."""
    return timestamp.isoformat()

def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse une chaîne ISO en timestamp."""
    return datetime.fromisoformat(timestamp_str)

def format_size(size_bytes: int) -> str:
    """Formate une taille en bytes en format lisible."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"

def get_file_size(path: Union[str, Path]) -> int:
    """Retourne la taille d'un fichier en bytes."""
    return os.path.getsize(path)

def hash_data(data: Any) -> str:
    """Calcule le hash SHA-256 de données."""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True)
    return hashlib.sha256(str(data).encode()).hexdigest()

def load_json(path: Union[str, Path]) -> Dict:
    """Charge un fichier JSON."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data: Dict, path: Union[str, Path]) -> None:
    """Sauvegarde des données en JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Divise une liste en chunks de taille donnée."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def deep_get(obj: Dict, path: str, default: Any = None) -> Any:
    """Récupère une valeur dans un dictionnaire imbriqué."""
    try:
        for key in path.split('.'):
            obj = obj[key]
        return obj
    except (KeyError, TypeError):
        return default

def deep_set(obj: Dict, path: str, value: Any) -> None:
    """Définit une valeur dans un dictionnaire imbriqué."""
    keys = path.split('.')
    for key in keys[:-1]:
        obj = obj.setdefault(key, {})
    obj[keys[-1]] = value

def deep_update(target: Dict, source: Dict) -> Dict:
    """Met à jour un dictionnaire de manière récursive."""
    for key, value in source.items():
        if isinstance(value, dict):
            target[key] = deep_update(target.get(key, {}), value)
        else:
            target[key] = value
    return target

def validate_symbol(symbol: str) -> bool:
    """Valide un symbole de trading."""
    if not isinstance(symbol, str):
        return False
    parts = symbol.split('/')
    return (
        len(parts) == 2 and
        all(part.isalnum() for part in parts) and
        all(3 <= len(part) <= 5 for part in parts)
    )

def validate_data(data: Dict, required_fields: List[str]) -> bool:
    """Valide la présence de champs requis dans un dictionnaire."""
    return all(field in data for field in required_fields) 