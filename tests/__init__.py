"""
Tests pour le package sadie.

Structure :
- unit/ : Tests unitaires
- integration/ : Tests d'intégration
- performance/ : Tests de performance
"""

import pytest

# Configuration des fixtures globales
@pytest.fixture(autouse=True)
def setup_test_env():
    """Configure l'environnement de test."""
    # Configuration avant chaque test
    yield
    # Nettoyage après chaque test
