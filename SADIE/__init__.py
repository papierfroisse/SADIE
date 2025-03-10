"""Module principal de SADIE."""

from . import core
from . import storage
from . import analysis
from . import web

__version__ = "0.2.1"

__all__ = [
    'core',
    'storage',
    'analysis',
    'web'
]