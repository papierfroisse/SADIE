"""Tests unitaires pour le collecteur de base."""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from sadie.data.collectors.base import BaseCollector

# Classe concrète pour tester BaseCollector (qui est abstraite)
class TestCollector(BaseCollector):
    """Implémentation concrète de BaseCollector pour les tests."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_called = False
        self.run_count = 0
    
    async def _run(self):
        """Implémentation de la méthode abstraite _run."""
        self.run_called = True
        self.run_count += 1

@pytest.fixture
def collector():
    """Fixture pour le collecteur de test."""
    return TestCollector(
        name="test_collector",
        symbols=["BTC/USD", "ETH/USD"],
        update_interval=0.1,
        logger=logging.getLogger("test")
    )

@pytest.mark.asyncio
async def test_initialization(collector):
    """Test de l'initialisation correcte du collecteur."""
    assert collector.name == "test_collector"
    assert collector.symbols == ["BTC/USD", "ETH/USD"]
    assert collector.update_interval == 0.1
    assert collector._running is False
    assert collector._task is None
    
    # Vérification de l'initialisation des données
    assert "BTC/USD" in collector._data
    assert "ETH/USD" in collector._data
    for symbol in collector.symbols:
        assert "price" in collector._data[symbol]
        assert "volume" in collector._data[symbol]
        assert "high" in collector._data[symbol]
        assert "low" in collector._data[symbol]

@pytest.mark.asyncio
async def test_start_stop(collector):
    """Test du démarrage et de l'arrêt du collecteur."""
    # Démarrage
    await collector.start()
    assert collector._running is True
    assert collector._task is not None
    
    # Vérification que _run est appelé
    await asyncio.sleep(0.2)  # Attente pour que _run soit appelé
    assert collector.run_called is True
    assert collector.run_count > 0
    
    # Arrêt
    await collector.stop()
    assert collector._running is False
    assert collector._task is None

@pytest.mark.asyncio
async def test_double_start(collector):
    """Test que le démarrage multiple ne cause pas de problèmes."""
    await collector.start()
    run_count = collector.run_count
    
    # Démarrage supplémentaire
    await collector.start()
    
    # Vérification que rien n'a changé (le collecteur était déjà démarré)
    assert collector._running is True
    assert collector.run_count == run_count  # Le compteur ne devrait pas augmenter immédiatement
    
    # Nettoyage
    await collector.stop()

@pytest.mark.asyncio
async def test_stop_when_not_running(collector):
    """Test que l'arrêt quand le collecteur n'est pas démarré ne cause pas d'erreur."""
    assert collector._running is False
    await collector.stop()  # Ne devrait pas lever d'exception
    assert collector._running is False

@pytest.mark.asyncio
async def test_get_data(collector):
    """Test de la récupération des données."""
    # Modification manuelle des données pour tester
    collector._data["BTC/USD"]["price"] = 50000.0
    collector._data["ETH/USD"]["volume"] = 10.5
    
    # Récupération de toutes les données
    all_data = await collector.get_data()
    assert "BTC/USD" in all_data
    assert "ETH/USD" in all_data
    assert all_data["BTC/USD"]["price"] == 50000.0
    assert all_data["ETH/USD"]["volume"] == 10.5
    
    # Récupération des données pour un symbole spécifique
    btc_data = await collector.get_data("BTC/USD")
    assert btc_data["price"] == 50000.0
    
    # Récupération des données pour un symbole inexistant
    unknown_data = await collector.get_data("UNKNOWN")
    assert unknown_data == {}

@pytest.mark.asyncio
async def test_run_loop_error_handling():
    """Test de la gestion des erreurs dans la boucle principale."""
    # Configuration du collecteur avec un _run qui lève une exception
    collector = TestCollector(
        name="error_test",
        symbols=["BTC/USD"],
        update_interval=0.1
    )
    
    # Patch de la méthode _run pour qu'elle lève une exception
    error_run = AsyncMock(side_effect=Exception("Test error"))
    with patch.object(collector, '_run', error_run):
        # Démarrage du collecteur
        await collector.start()
        
        # Attente pour que _run soit appelé plusieurs fois (avec des erreurs)
        await asyncio.sleep(0.3)
        
        # Vérification que le collecteur est toujours en cours d'exécution malgré les erreurs
        assert collector._running is True
        assert error_run.call_count > 1  # La méthode a été appelée plusieurs fois
        
        # Arrêt du collecteur
        await collector.stop()
        assert collector._running is False 