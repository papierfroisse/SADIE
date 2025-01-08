"""
Module de partitionnement adaptatif des données.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

from sadie.storage.compression import DataType

logger = logging.getLogger(__name__)

class PartitionStrategy(Enum):
    """Stratégies de partitionnement supportées."""
    TIME = "time"  # Partitionnement par intervalle de temps
    SYMBOL = "symbol"  # Partitionnement par symbole
    HYBRID = "hybrid"  # Partitionnement hybride (temps + symbole)
    ADAPTIVE = "adaptive"  # Partitionnement adaptatif basé sur l'accès

class AccessPattern(Enum):
    """Patterns d'accès aux données."""
    HOT = "hot"  # Données fréquemment accédées
    WARM = "warm"  # Données occasionnellement accédées
    COLD = "cold"  # Données rarement accédées

class PartitionConfig:
    """Configuration d'une partition."""
    
    def __init__(
        self,
        strategy: PartitionStrategy,
        time_interval: Optional[timedelta] = None,
        max_size: int = 1024 * 1024 * 1024,  # 1GB par défaut
        access_threshold: int = 100,  # Seuil pour considérer les données comme "hot"
        compression_level: int = 6
    ):
        """
        Initialise la configuration de partition.
        
        Args:
            strategy: Stratégie de partitionnement
            time_interval: Intervalle de temps pour le partitionnement temporel
            max_size: Taille maximale d'une partition
            access_threshold: Seuil d'accès pour les données chaudes
            compression_level: Niveau de compression
        """
        self.strategy = strategy
        self.time_interval = time_interval or timedelta(days=1)
        self.max_size = max_size
        self.access_threshold = access_threshold
        self.compression_level = compression_level

class Partition:
    """Représente une partition de données."""
    
    def __init__(
        self,
        id: str,
        strategy: PartitionStrategy,
        data_type: DataType,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        symbol: Optional[str] = None
    ):
        """
        Initialise une partition.
        
        Args:
            id: Identifiant unique de la partition
            strategy: Stratégie de partitionnement
            data_type: Type de données
            start_time: Début de l'intervalle temporel
            end_time: Fin de l'intervalle temporel
            symbol: Symbole pour le partitionnement par symbole
        """
        self.id = id
        self.strategy = strategy
        self.data_type = data_type
        self.start_time = start_time
        self.end_time = end_time
        self.symbol = symbol
        self.size = 0
        self.access_count = 0
        self.last_access = None
        self.data = {}
        
    def add_data(self, key: str, value: bytes) -> bool:
        """
        Ajoute des données à la partition.
        
        Args:
            key: Clé des données
            value: Données à stocker
            
        Returns:
            True si les données ont été ajoutées avec succès
        """
        new_size = self.size + len(value)
        if new_size > self.max_size:
            return False
            
        self.data[key] = value
        self.size = new_size
        return True
        
    def get_data(self, key: str) -> Optional[bytes]:
        """
        Récupère des données de la partition.
        
        Args:
            key: Clé des données
            
        Returns:
            Données stockées
        """
        self.access_count += 1
        self.last_access = datetime.utcnow()
        return self.data.get(key)
        
    def get_access_pattern(self, config: PartitionConfig) -> AccessPattern:
        """
        Détermine le pattern d'accès de la partition.
        
        Args:
            config: Configuration de partition
            
        Returns:
            Pattern d'accès
        """
        if not self.last_access:
            return AccessPattern.COLD
            
        age = (datetime.utcnow() - self.last_access).total_seconds()
        
        if self.access_count >= config.access_threshold:
            return AccessPattern.HOT
        elif age <= 86400:  # 24 heures
            return AccessPattern.WARM
        else:
            return AccessPattern.COLD

class PartitionManager:
    """Gestionnaire de partitionnement adaptatif."""
    
    # Configurations par défaut selon le type de données
    DEFAULT_CONFIGS = {
        DataType.ORDERBOOK: PartitionConfig(
            strategy=PartitionStrategy.HYBRID,
            time_interval=timedelta(hours=1),
            max_size=512 * 1024 * 1024,  # 512MB
            compression_level=1
        ),
        DataType.TRADES: PartitionConfig(
            strategy=PartitionStrategy.TIME,
            time_interval=timedelta(hours=4),
            max_size=1024 * 1024 * 1024,  # 1GB
            compression_level=6
        ),
        DataType.TICKS: PartitionConfig(
            strategy=PartitionStrategy.HYBRID,
            time_interval=timedelta(minutes=30),
            max_size=256 * 1024 * 1024,  # 256MB
            compression_level=1
        ),
        DataType.SENTIMENT: PartitionConfig(
            strategy=PartitionStrategy.SYMBOL,
            time_interval=timedelta(days=1),
            max_size=100 * 1024 * 1024,  # 100MB
            compression_level=9
        ),
        DataType.NEWS: PartitionConfig(
            strategy=PartitionStrategy.TIME,
            time_interval=timedelta(days=1),
            max_size=2 * 1024 * 1024 * 1024,  # 2GB
            compression_level=9
        ),
        DataType.METRICS: PartitionConfig(
            strategy=PartitionStrategy.ADAPTIVE,
            time_interval=timedelta(hours=1),
            max_size=50 * 1024 * 1024,  # 50MB
            compression_level=6
        )
    }
    
    def __init__(
        self,
        configs: Optional[Dict[DataType, PartitionConfig]] = None,
        base_path: str = "./data"
    ):
        """
        Initialise le gestionnaire de partitionnement.
        
        Args:
            configs: Configurations personnalisées
            base_path: Chemin de base pour le stockage
        """
        self.configs = configs or self.DEFAULT_CONFIGS
        self.base_path = base_path
        self.partitions = {}
        
    def get_partition(
        self,
        data_type: DataType,
        timestamp: datetime,
        symbol: Optional[str] = None
    ) -> Partition:
        """
        Récupère la partition appropriée pour les données.
        
        Args:
            data_type: Type de données
            timestamp: Horodatage des données
            symbol: Symbole (optionnel)
            
        Returns:
            Partition appropriée
        """
        config = self.configs[data_type]
        
        if config.strategy == PartitionStrategy.TIME:
            interval_start = timestamp.replace(
                minute=0 if config.time_interval >= timedelta(hours=1) else timestamp.minute,
                second=0,
                microsecond=0
            )
            key = f"{data_type.value}_{interval_start.isoformat()}"
            
        elif config.strategy == PartitionStrategy.SYMBOL:
            key = f"{data_type.value}_{symbol}"
            
        elif config.strategy == PartitionStrategy.HYBRID:
            interval_start = timestamp.replace(
                minute=0 if config.time_interval >= timedelta(hours=1) else timestamp.minute,
                second=0,
                microsecond=0
            )
            key = f"{data_type.value}_{symbol}_{interval_start.isoformat()}"
            
        else:  # ADAPTIVE
            # Trouver la partition la plus appropriée selon le pattern d'accès
            candidates = [
                p for p in self.partitions.values()
                if p.data_type == data_type and
                (not symbol or p.symbol == symbol) and
                (not p.end_time or timestamp <= p.end_time)
            ]
            
            if candidates:
                best_partition = max(
                    candidates,
                    key=lambda p: (
                        p.get_access_pattern(config).value,
                        p.access_count
                    )
                )
                return best_partition
                
            # Créer une nouvelle partition si nécessaire
            key = f"{data_type.value}_{symbol}_{timestamp.isoformat()}"
            
        if key not in self.partitions:
            self.partitions[key] = Partition(
                id=key,
                strategy=config.strategy,
                data_type=data_type,
                start_time=timestamp,
                end_time=timestamp + config.time_interval if config.strategy != PartitionStrategy.SYMBOL else None,
                symbol=symbol
            )
            
        return self.partitions[key]
        
    def optimize_partitions(self) -> None:
        """Optimise les partitions selon les patterns d'accès."""
        for data_type, config in self.configs.items():
            partitions = [
                p for p in self.partitions.values()
                if p.data_type == data_type
            ]
            
            for partition in partitions:
                pattern = partition.get_access_pattern(config)
                
                if pattern == AccessPattern.COLD:
                    # Archiver les données froides
                    self._archive_partition(partition)
                elif pattern == AccessPattern.HOT:
                    # Optimiser les données chaudes pour l'accès rapide
                    self._optimize_hot_partition(partition)
                    
    def _archive_partition(self, partition: Partition) -> None:
        """
        Archive une partition froide.
        
        Args:
            partition: Partition à archiver
        """
        # TODO: Implémenter l'archivage des données
        logger.info(f"Archivage de la partition {partition.id}")
        
    def _optimize_hot_partition(self, partition: Partition) -> None:
        """
        Optimise une partition chaude.
        
        Args:
            partition: Partition à optimiser
        """
        # TODO: Implémenter l'optimisation des données chaudes
        logger.info(f"Optimisation de la partition {partition.id}")
        
    def get_partition_stats(self) -> Dict[str, Dict]:
        """
        Calcule les statistiques des partitions.
        
        Returns:
            Statistiques par partition
        """
        stats = {}
        
        for partition_id, partition in self.partitions.items():
            stats[partition_id] = {
                'size': partition.size,
                'access_count': partition.access_count,
                'last_access': partition.last_access.isoformat() if partition.last_access else None,
                'data_type': partition.data_type.value,
                'strategy': partition.strategy.value,
                'pattern': partition.get_access_pattern(
                    self.configs[partition.data_type]
                ).value
            }
            
        return stats 