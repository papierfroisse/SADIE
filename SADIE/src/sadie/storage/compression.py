"""
Module de compression intelligente des données.
"""

import logging
import zlib
import lz4.frame
import snappy
import numpy as np
from typing import Any, Dict, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)

class CompressionAlgorithm(Enum):
    """Algorithmes de compression supportés."""
    ZLIB = "zlib"
    LZ4 = "lz4"
    SNAPPY = "snappy"
    NONE = "none"

class DataType(Enum):
    """Types de données supportés."""
    ORDERBOOK = "orderbook"
    TRADES = "trades"
    TICKS = "ticks"
    SENTIMENT = "sentiment"
    NEWS = "news"
    METRICS = "metrics"

class CompressionProfile:
    """Profile de compression avec paramètres optimisés."""
    
    def __init__(
        self,
        algorithm: CompressionAlgorithm,
        level: int = 6,
        chunk_size: int = 1024 * 1024  # 1MB par défaut
    ):
        """
        Initialise un profil de compression.
        
        Args:
            algorithm: Algorithme de compression
            level: Niveau de compression (1-9 pour zlib)
            chunk_size: Taille des chunks pour la compression par bloc
        """
        self.algorithm = algorithm
        self.level = level
        self.chunk_size = chunk_size

class CompressionManager:
    """Gestionnaire de compression intelligente."""
    
    # Profiles de compression optimisés par type de données
    DEFAULT_PROFILES = {
        DataType.ORDERBOOK: CompressionProfile(
            algorithm=CompressionAlgorithm.LZ4,
            level=1,  # Compression rapide pour les données temps réel
            chunk_size=512 * 1024  # 512KB chunks
        ),
        DataType.TRADES: CompressionProfile(
            algorithm=CompressionAlgorithm.SNAPPY,
            chunk_size=256 * 1024  # 256KB chunks
        ),
        DataType.TICKS: CompressionProfile(
            algorithm=CompressionAlgorithm.LZ4,
            level=1,
            chunk_size=128 * 1024  # 128KB chunks
        ),
        DataType.SENTIMENT: CompressionProfile(
            algorithm=CompressionAlgorithm.ZLIB,
            level=6,  # Compression moyenne
            chunk_size=1024 * 1024  # 1MB chunks
        ),
        DataType.NEWS: CompressionProfile(
            algorithm=CompressionAlgorithm.ZLIB,
            level=9,  # Compression maximale
            chunk_size=2 * 1024 * 1024  # 2MB chunks
        ),
        DataType.METRICS: CompressionProfile(
            algorithm=CompressionAlgorithm.SNAPPY,
            chunk_size=64 * 1024  # 64KB chunks
        )
    }
    
    def __init__(self, profiles: Optional[Dict[DataType, CompressionProfile]] = None):
        """
        Initialise le gestionnaire de compression.
        
        Args:
            profiles: Profiles de compression personnalisés
        """
        self.profiles = profiles or self.DEFAULT_PROFILES
        
    def compress(
        self,
        data: Union[bytes, str, Dict],
        data_type: DataType
    ) -> bytes:
        """
        Compresse les données selon leur type.
        
        Args:
            data: Données à compresser
            data_type: Type de données
            
        Returns:
            Données compressées
        """
        # Convertir en bytes si nécessaire
        if isinstance(data, str):
            data = data.encode('utf-8')
        elif isinstance(data, dict):
            data = str(data).encode('utf-8')
            
        profile = self.profiles[data_type]
        
        try:
            if profile.algorithm == CompressionAlgorithm.ZLIB:
                return zlib.compress(data, level=profile.level)
            elif profile.algorithm == CompressionAlgorithm.LZ4:
                return lz4.frame.compress(
                    data,
                    compression_level=profile.level,
                    block_size=profile.chunk_size
                )
            elif profile.algorithm == CompressionAlgorithm.SNAPPY:
                return snappy.compress(data)
            else:
                return data
                
        except Exception as e:
            logger.error(f"Erreur lors de la compression: {str(e)}")
            return data
            
    def decompress(
        self,
        data: bytes,
        data_type: DataType
    ) -> Union[bytes, str, Dict]:
        """
        Décompresse les données selon leur type.
        
        Args:
            data: Données compressées
            data_type: Type de données
            
        Returns:
            Données décompressées
        """
        profile = self.profiles[data_type]
        
        try:
            if profile.algorithm == CompressionAlgorithm.ZLIB:
                return zlib.decompress(data)
            elif profile.algorithm == CompressionAlgorithm.LZ4:
                return lz4.frame.decompress(data)
            elif profile.algorithm == CompressionAlgorithm.SNAPPY:
                return snappy.decompress(data)
            else:
                return data
                
        except Exception as e:
            logger.error(f"Erreur lors de la décompression: {str(e)}")
            return data
            
    def get_compression_stats(
        self,
        original_data: Union[bytes, str, Dict],
        data_type: DataType
    ) -> Dict[str, float]:
        """
        Calcule les statistiques de compression.
        
        Args:
            original_data: Données originales
            data_type: Type de données
            
        Returns:
            Statistiques de compression
        """
        if isinstance(original_data, str):
            original_size = len(original_data.encode('utf-8'))
        elif isinstance(original_data, dict):
            original_size = len(str(original_data).encode('utf-8'))
        else:
            original_size = len(original_data)
            
        compressed_data = self.compress(original_data, data_type)
        compressed_size = len(compressed_data)
        
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': original_size / compressed_size if compressed_size > 0 else 1.0,
            'space_saving': (1 - compressed_size / original_size) * 100 if original_size > 0 else 0.0
        }
        
    def optimize_profile(
        self,
        sample_data: List[Union[bytes, str, Dict]],
        data_type: DataType
    ) -> CompressionProfile:
        """
        Optimise le profil de compression pour un type de données.
        
        Args:
            sample_data: Échantillon de données
            data_type: Type de données
            
        Returns:
            Profil de compression optimisé
        """
        best_profile = None
        best_ratio = 0.0
        
        # Tester différentes configurations
        algorithms = [
            CompressionAlgorithm.ZLIB,
            CompressionAlgorithm.LZ4,
            CompressionAlgorithm.SNAPPY
        ]
        
        levels = [1, 3, 6, 9] if data_type not in [DataType.ORDERBOOK, DataType.TICKS] else [1]
        chunk_sizes = [64*1024, 256*1024, 1024*1024]
        
        for algo in algorithms:
            for level in levels:
                for chunk_size in chunk_sizes:
                    profile = CompressionProfile(algo, level, chunk_size)
                    total_ratio = 0.0
                    
                    # Tester sur l'échantillon
                    for data in sample_data:
                        stats = self.get_compression_stats(data, data_type)
                        total_ratio += stats['compression_ratio']
                        
                    avg_ratio = total_ratio / len(sample_data)
                    
                    if avg_ratio > best_ratio:
                        best_ratio = avg_ratio
                        best_profile = profile
                        
        return best_profile 