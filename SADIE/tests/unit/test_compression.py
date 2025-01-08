"""Tests unitaires pour le module de compression."""

import pytest
import json
from typing import Dict, List
import numpy as np

from sadie.storage.compression import (
    CompressionManager,
    CompressionAlgorithm,
    CompressionProfile,
    DataType
)

@pytest.fixture
def sample_orderbook() -> Dict:
    """Crée un order book de test."""
    return {
        'bids': [
            [50000.0, 1.5],
            [49999.5, 2.0],
            [49999.0, 1.0]
        ],
        'asks': [
            [50000.5, 1.0],
            [50001.0, 2.0],
            [50001.5, 1.5]
        ],
        'timestamp': 1642665600000
    }

@pytest.fixture
def sample_trades() -> List[Dict]:
    """Crée une liste de trades de test."""
    return [
        {
            'id': 1,
            'price': 50000.0,
            'amount': 1.5,
            'side': 'buy',
            'timestamp': 1642665600000
        },
        {
            'id': 2,
            'price': 50001.0,
            'amount': 2.0,
            'side': 'sell',
            'timestamp': 1642665601000
        }
    ]

@pytest.fixture
def sample_news() -> str:
    """Crée un article de test."""
    return """
    Bitcoin Reaches New All-Time High as Institutional Adoption Grows
    
    The world's largest cryptocurrency by market capitalization has reached a new
    all-time high today, driven by increasing institutional adoption and growing
    retail interest. Major financial institutions have announced new crypto
    investment products, while several publicly traded companies have added
    Bitcoin to their balance sheets.
    
    Market analysts suggest this could be the beginning of a new bull run,
    citing strong on-chain metrics and declining exchange reserves. However,
    some experts urge caution, noting the historical volatility of the asset
    class.
    """

@pytest.fixture
def compression_manager():
    """Crée une instance du gestionnaire de compression."""
    return CompressionManager()

def test_compression_profile_initialization():
    """Teste l'initialisation des profils de compression."""
    profile = CompressionProfile(
        algorithm=CompressionAlgorithm.ZLIB,
        level=6,
        chunk_size=1024*1024
    )
    
    assert profile.algorithm == CompressionAlgorithm.ZLIB
    assert profile.level == 6
    assert profile.chunk_size == 1024*1024

def test_default_profiles(compression_manager):
    """Teste les profils de compression par défaut."""
    assert DataType.ORDERBOOK in compression_manager.profiles
    assert DataType.TRADES in compression_manager.profiles
    assert DataType.NEWS in compression_manager.profiles
    
    orderbook_profile = compression_manager.profiles[DataType.ORDERBOOK]
    assert orderbook_profile.algorithm == CompressionAlgorithm.LZ4
    assert orderbook_profile.level == 1  # Compression rapide
    
    news_profile = compression_manager.profiles[DataType.NEWS]
    assert news_profile.algorithm == CompressionAlgorithm.ZLIB
    assert news_profile.level == 9  # Compression maximale

def test_compress_decompress_orderbook(compression_manager, sample_orderbook):
    """Teste la compression/décompression d'un order book."""
    # Compression
    compressed = compression_manager.compress(sample_orderbook, DataType.ORDERBOOK)
    assert isinstance(compressed, bytes)
    assert len(compressed) < len(str(sample_orderbook).encode('utf-8'))
    
    # Décompression
    decompressed = compression_manager.decompress(compressed, DataType.ORDERBOOK)
    assert isinstance(decompressed, bytes)
    
    # Vérifier que les données sont préservées
    original_json = json.dumps(sample_orderbook, sort_keys=True)
    decompressed_str = decompressed.decode('utf-8')
    assert json.loads(decompressed_str) == json.loads(original_json)

def test_compress_decompress_trades(compression_manager, sample_trades):
    """Teste la compression/décompression des trades."""
    # Compression
    compressed = compression_manager.compress(sample_trades, DataType.TRADES)
    assert isinstance(compressed, bytes)
    assert len(compressed) < len(str(sample_trades).encode('utf-8'))
    
    # Décompression
    decompressed = compression_manager.decompress(compressed, DataType.TRADES)
    assert isinstance(decompressed, bytes)
    
    # Vérifier que les données sont préservées
    original_json = json.dumps(sample_trades, sort_keys=True)
    decompressed_str = decompressed.decode('utf-8')
    assert json.loads(decompressed_str) == json.loads(original_json)

def test_compress_decompress_news(compression_manager, sample_news):
    """Teste la compression/décompression des actualités."""
    # Compression
    compressed = compression_manager.compress(sample_news, DataType.NEWS)
    assert isinstance(compressed, bytes)
    assert len(compressed) < len(sample_news.encode('utf-8'))
    
    # Décompression
    decompressed = compression_manager.decompress(compressed, DataType.NEWS)
    assert isinstance(decompressed, bytes)
    
    # Vérifier que les données sont préservées
    assert decompressed.decode('utf-8') == sample_news

def test_compression_stats(compression_manager, sample_orderbook):
    """Teste le calcul des statistiques de compression."""
    stats = compression_manager.get_compression_stats(
        sample_orderbook,
        DataType.ORDERBOOK
    )
    
    assert 'original_size' in stats
    assert 'compressed_size' in stats
    assert 'compression_ratio' in stats
    assert 'space_saving' in stats
    assert stats['original_size'] > stats['compressed_size']
    assert stats['compression_ratio'] > 1.0
    assert 0 <= stats['space_saving'] <= 100

def test_optimize_profile(compression_manager, sample_trades):
    """Teste l'optimisation des profils de compression."""
    sample_data = [sample_trades] * 10  # Créer un échantillon
    
    optimized_profile = compression_manager.optimize_profile(
        sample_data,
        DataType.TRADES
    )
    
    assert isinstance(optimized_profile, CompressionProfile)
    assert optimized_profile.algorithm in [
        CompressionAlgorithm.ZLIB,
        CompressionAlgorithm.LZ4,
        CompressionAlgorithm.SNAPPY
    ]

def test_error_handling(compression_manager):
    """Teste la gestion des erreurs."""
    # Test avec des données invalides
    invalid_data = b'\x00\xFF\x00\xFF'  # Données binaires invalides
    
    # La compression ne devrait pas échouer
    compressed = compression_manager.compress(invalid_data, DataType.METRICS)
    assert isinstance(compressed, bytes)
    
    # La décompression ne devrait pas échouer
    decompressed = compression_manager.decompress(compressed, DataType.METRICS)
    assert isinstance(decompressed, bytes)

def test_custom_profiles():
    """Teste l'utilisation de profils personnalisés."""
    custom_profiles = {
        DataType.ORDERBOOK: CompressionProfile(
            algorithm=CompressionAlgorithm.SNAPPY,
            chunk_size=128*1024
        )
    }
    
    manager = CompressionManager(profiles=custom_profiles)
    assert manager.profiles[DataType.ORDERBOOK].algorithm == CompressionAlgorithm.SNAPPY
    assert manager.profiles[DataType.ORDERBOOK].chunk_size == 128*1024 