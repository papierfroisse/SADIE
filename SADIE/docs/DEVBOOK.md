# Guide du Développeur SADIE

## Architecture du Projet

### Vue d'Ensemble
SADIE est construit autour d'une architecture modulaire orientée performance. Les composants principaux sont :

1. **Collecteurs de Données** (`sadie.data.collectors`)
   - Collecteurs de marché (order books, ticks, transactions)
   - Collecteurs alternatifs (Twitter, Reddit, News)
   - Gestion des WebSockets et connexions temps réel

2. **Système de Stockage** (`sadie.storage`)
   - Compression intelligente multi-algorithmes
   - Partitionnement adaptatif des données
   - Gestion des données chaudes/tièdes/froides

3. **Analyse** (`sadie.analysis`)
   - Métriques de marché en temps réel
   - Analyse de sentiment et engagement
   - Indicateurs techniques avancés

4. **Exécution** (`sadie.execution`)
   - Stratégies d'exécution optimisées
   - Gestion des ordres et du portefeuille
   - Backtesting et simulation

### Bonnes Pratiques

#### 1. Style de Code
- Suivre PEP 8
- Docstrings pour toutes les classes et méthodes publiques
- Type hints pour améliorer la lisibilité
- Maximum 88 caractères par ligne

```python
from typing import List, Dict, Optional

class DataCollector:
    """Base class for all data collectors.
    
    Attributes:
        name: Collector identifier
        is_running: Current running state
    """
    
    def __init__(self, name: str) -> None:
        self.name = name
        self.is_running = False
        
    def start(self) -> bool:
        """Start the data collection.
        
        Returns:
            bool: True if successfully started
        """
        if self.is_running:
            return False
        self.is_running = True
        return True
```

#### 2. Tests
- Tests unitaires pour chaque module
- Tests de performance avec métriques
- Tests d'intégration pour les workflows complets
- Coverage minimum de 80%

```python
def test_collector_initialization():
    """Test collector initialization and basic properties."""
    collector = DataCollector("test")
    assert collector.name == "test"
    assert not collector.is_running
```

#### 3. Performance
- Utiliser des structures de données optimisées
- Éviter les copies inutiles
- Profiler le code régulièrement
- Optimiser les requêtes et les accès disque

```python
from collections import deque
from typing import Deque

class TickBuffer:
    """Efficient tick data buffer using deque."""
    
    def __init__(self, maxlen: int = 1000):
        self.buffer: Deque = deque(maxlen=maxlen)
        
    def add(self, tick: dict) -> None:
        """Add tick to buffer efficiently."""
        self.buffer.append(tick)
```

#### 4. Gestion des Erreurs
- Exceptions personnalisées pour chaque type d'erreur
- Logging détaillé avec niveaux appropriés
- Retry patterns pour les opérations réseau
- Circuit breakers pour les services externes

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CollectorError(Exception):
    """Base exception for collector errors."""
    pass

class ConnectionError(CollectorError):
    """Raised when connection fails."""
    pass

def connect_with_retry(
    max_retries: int = 3,
    delay: float = 1.0
) -> Optional[Connection]:
    """Connect with retry pattern."""
    for attempt in range(max_retries):
        try:
            return establish_connection()
        except ConnectionError as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            time.sleep(delay * (attempt + 1))
    return None
```

### Workflow de Développement

1. **Création de Feature**
   ```bash
   git checkout -b feature/nom-feature
   ```

2. **Tests**
   ```bash
   # Tests unitaires
   pytest tests/unit
   
   # Tests de performance
   pytest tests/performance
   
   # Coverage
   pytest --cov=sadie tests/
   ```

3. **Documentation**
   - Mettre à jour la documentation technique
   - Ajouter des exemples d'utilisation
   - Documenter les changements dans CHANGELOG.md

4. **Review**
   - Créer une Pull Request
   - Attendre la review et les tests CI
   - Corriger les retours si nécessaire

### Outils de Développement

1. **Environnement**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements-dev.txt
   ```

2. **Linting & Formatting**
   ```bash
   # Vérifier le style
   flake8 src/sadie
   
   # Formatter le code
   black src/sadie
   
   # Vérifier les types
   mypy src/sadie
   ```

3. **Profiling**
   ```python
   import cProfile
   import pstats
   
   def profile_code():
       profiler = cProfile.Profile()
       profiler.enable()
       # Code à profiler
       profiler.disable()
       stats = pstats.Stats(profiler).sort_stats('cumtime')
       stats.print_stats()
   ```

### Déploiement

1. **Préparation**
   - Mettre à jour la version dans `setup.py`
   - Mettre à jour CHANGELOG.md
   - Créer un tag de version

2. **Tests de Production**
   ```bash
   # Tests complets
   pytest
   
   # Tests de charge
   python -m sadie.tests.load
   ```

3. **Documentation**
   ```bash
   # Générer la doc
   mkdocs build
   
   # Déployer la doc
   mkdocs gh-deploy
   ```

4. **Release**
   ```bash
   # Build
   python setup.py sdist bdist_wheel
   
   # Upload
   twine upload dist/*
   ``` 