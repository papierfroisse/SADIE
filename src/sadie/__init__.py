"""
SADIE - Système d'Analyse de Données et d'Intelligence Économique.

Un framework modulaire pour la collecte, le stockage et l'analyse de données financières.
"""

from . import analysis, data, storage, utils
from .utils import setup_logging

__version__ = "0.1.0"
__author__ = "Radio France"
__license__ = "MIT"

# Configuration du logging par défaut
setup_logging()

__all__ = [
    "analysis",
    "data",
    "storage",
    "utils",
]
