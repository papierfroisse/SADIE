"""Tests unitaires pour le module de partitionnement."""

import pytest
from datetime import datetime, timedelta
from typing import Dict

from sadie.storage.partitioning import (
    PartitionManager,
    PartitionStrategy,
    PartitionConfig,
    Partition,
    AccessPattern,
    DataType
)

@pytest.fixture
def sample_data() -> Dict:
    """Crée des données de test."""
    return {
        'key1': b'test data 1',
        'key2': b'test data 2',
        'key3': b'test data 3'
    }

@pytest.fixture
def partition_manager():
    """Crée une instance du gestionnaire de partitionnement."""
    return PartitionManager(base_path="./test_data")

def test_partition_config_initialization():
    """Teste l'initialisation des configurations de partition."""
    config = PartitionConfig(
        strategy=PartitionStrategy.TIME,
        time_interval=timedelta(hours=1),
        max_size=1024*1024,
        access_threshold=50,
        compression_level=6
    )
    
    assert config.strategy == PartitionStrategy.TIME
    assert config.time_interval == timedelta(hours=1)
    assert config.max_size == 1024*1024
    assert config.access_threshold == 50
    assert config.compression_level == 6

def test_default_configs(partition_manager):
    """Teste les configurations par défaut."""
    assert DataType.ORDERBOOK in partition_manager.configs
    assert DataType.TRADES in partition_manager.configs
    assert DataType.NEWS in partition_manager.configs
    
    orderbook_config = partition_manager.configs[DataType.ORDERBOOK]
    assert orderbook_config.strategy == PartitionStrategy.HYBRID
    assert orderbook_config.time_interval == timedelta(hours=1)
    assert orderbook_config.compression_level == 1
    
    news_config = partition_manager.configs[DataType.NEWS]
    assert news_config.strategy == PartitionStrategy.TIME
    assert news_config.time_interval == timedelta(days=1)
    assert news_config.compression_level == 9

def test_partition_initialization():
    """Teste l'initialisation d'une partition."""
    now = datetime.utcnow()
    partition = Partition(
        id="test_partition",
        strategy=PartitionStrategy.TIME,
        data_type=DataType.TRADES,
        start_time=now,
        end_time=now + timedelta(hours=1),
        symbol="BTC/USDT"
    )
    
    assert partition.id == "test_partition"
    assert partition.strategy == PartitionStrategy.TIME
    assert partition.data_type == DataType.TRADES
    assert partition.start_time == now
    assert partition.end_time == now + timedelta(hours=1)
    assert partition.symbol == "BTC/USDT"
    assert partition.size == 0
    assert partition.access_count == 0
    assert partition.last_access is None

def test_add_get_data(partition_manager, sample_data):
    """Teste l'ajout et la récupération de données."""
    now = datetime.utcnow()
    partition = partition_manager.get_partition(
        data_type=DataType.TRADES,
        timestamp=now,
        symbol="BTC/USDT"
    )
    
    # Ajouter des données
    for key, value in sample_data.items():
        success = partition.add_data(key, value)
        assert success
        
    # Vérifier la taille
    expected_size = sum(len(value) for value in sample_data.values())
    assert partition.size == expected_size
    
    # Récupérer les données
    for key, value in sample_data.items():
        data = partition.get_data(key)
        assert data == value
        
    # Vérifier le compteur d'accès
    assert partition.access_count == len(sample_data)
    assert partition.last_access is not None

def test_partition_size_limit(partition_manager):
    """Teste la limite de taille des partitions."""
    now = datetime.utcnow()
    partition = partition_manager.get_partition(
        data_type=DataType.TRADES,
        timestamp=now,
        symbol="BTC/USDT"
    )
    
    # Créer des données qui dépassent la taille maximale
    large_data = b'x' * (partition_manager.configs[DataType.TRADES].max_size + 1)
    
    # L'ajout devrait échouer
    success = partition.add_data('large_key', large_data)
    assert not success
    assert partition.size == 0

def test_time_based_partitioning(partition_manager):
    """Teste le partitionnement basé sur le temps."""
    now = datetime.utcnow()
    
    # Créer des partitions à différents moments
    partition1 = partition_manager.get_partition(
        data_type=DataType.TRADES,
        timestamp=now
    )
    
    partition2 = partition_manager.get_partition(
        data_type=DataType.TRADES,
        timestamp=now + timedelta(hours=5)
    )
    
    # Les partitions devraient être différentes
    assert partition1.id != partition2.id
    assert partition1.start_time != partition2.start_time

def test_symbol_based_partitioning(partition_manager):
    """Teste le partitionnement basé sur les symboles."""
    now = datetime.utcnow()
    
    # Créer des partitions pour différents symboles
    partition1 = partition_manager.get_partition(
        data_type=DataType.SENTIMENT,
        timestamp=now,
        symbol="BTC/USDT"
    )
    
    partition2 = partition_manager.get_partition(
        data_type=DataType.SENTIMENT,
        timestamp=now,
        symbol="ETH/USDT"
    )
    
    # Les partitions devraient être différentes
    assert partition1.id != partition2.id
    assert partition1.symbol != partition2.symbol

def test_access_patterns(partition_manager, sample_data):
    """Teste les patterns d'accès aux données."""
    now = datetime.utcnow()
    partition = partition_manager.get_partition(
        data_type=DataType.TRADES,
        timestamp=now,
        symbol="BTC/USDT"
    )
    
    # Au début, le pattern devrait être COLD
    assert partition.get_access_pattern(
        partition_manager.configs[DataType.TRADES]
    ) == AccessPattern.COLD
    
    # Ajouter et accéder aux données
    for key, value in sample_data.items():
        partition.add_data(key, value)
        
    # Simuler plusieurs accès
    for _ in range(200):
        partition.get_data('key1')
        
    # Le pattern devrait maintenant être HOT
    assert partition.get_access_pattern(
        partition_manager.configs[DataType.TRADES]
    ) == AccessPattern.HOT

def test_partition_optimization(partition_manager, sample_data):
    """Teste l'optimisation des partitions."""
    now = datetime.utcnow()
    
    # Créer et remplir plusieurs partitions
    for i in range(3):
        partition = partition_manager.get_partition(
            data_type=DataType.TRADES,
            timestamp=now + timedelta(hours=i),
            symbol=f"BTC/USDT_{i}"
        )
        
        for key, value in sample_data.items():
            partition.add_data(key, value)
            
        # Simuler différents patterns d'accès
        if i == 0:  # Partition chaude
            for _ in range(200):
                partition.get_data('key1')
        elif i == 1:  # Partition tiède
            for _ in range(50):
                partition.get_data('key1')
                
    # Optimiser les partitions
    partition_manager.optimize_partitions()
    
    # Vérifier les statistiques
    stats = partition_manager.get_partition_stats()
    assert len(stats) == 3
    
    patterns = [stat['pattern'] for stat in stats.values()]
    assert AccessPattern.HOT.value in patterns
    assert AccessPattern.WARM.value in patterns
    assert AccessPattern.COLD.value in patterns

def test_custom_configs():
    """Teste l'utilisation de configurations personnalisées."""
    custom_configs = {
        DataType.TRADES: PartitionConfig(
            strategy=PartitionStrategy.HYBRID,
            time_interval=timedelta(minutes=15),
            max_size=100*1024*1024,
            compression_level=3
        )
    }
    
    manager = PartitionManager(configs=custom_configs)
    assert manager.configs[DataType.TRADES].strategy == PartitionStrategy.HYBRID
    assert manager.configs[DataType.TRADES].time_interval == timedelta(minutes=15)
    assert manager.configs[DataType.TRADES].max_size == 100*1024*1024
    assert manager.configs[DataType.TRADES].compression_level == 3 