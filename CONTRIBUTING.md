# Guide de contribution à SADIE

## Introduction

Merci de votre intérêt pour contribuer à SADIE ! Ce document fournit les lignes directrices pour contribuer au projet efficacement.

## Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Mise en place de l'environnement de développement](#mise-en-place-de-lenvironnement-de-développement)
3. [Comment contribuer](#comment-contribuer)
4. [Structure du projet](#structure-du-projet)
5. [Style de code](#style-de-code)
6. [Tests](#tests)
7. [Documentation](#documentation)
8. [Processus de revue](#processus-de-revue)
9. [Collecteurs de données](#collecteurs-de-données)

## Code de conduite

Ce projet adhère au [Contributor Covenant](https://www.contributor-covenant.org/). En participant, vous devez respecter ce code.

## Mise en place de l'environnement de développement

1. Fork et clone du dépôt
   ```bash
   git clone https://github.com/votre-username/sadie.git
   cd sadie
   ```

2. Installation des dépendances
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Configuration de l'environnement
   ```bash
   cp .env.example .env
   # Modifier .env avec vos paramètres
   ```

4. Créer une branche pour votre travail
   ```bash
   git checkout -b feature/votre-fonctionnalite
   ```

## Comment contribuer

### Signaler des bugs

1. Vérifiez que le bug n'a pas déjà été signalé
2. Créez une issue en utilisant le template de bug
3. Incluez :
   - Version de SADIE
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Logs pertinents
   - Environnement (OS, Python, dépendances)

### Proposer des améliorations

1. Ouvrez une issue de discussion
2. Attendez la validation de l'équipe
3. Créez une Pull Request

### Processus de développement

1. Développement avec tests
2. Commit avec messages conventionnels
   ```bash
   feat: ajout de la fonctionnalité X
   fix: correction du bug Y
   docs: mise à jour de la documentation Z
   test: ajout de tests pour le module A
   refactor: amélioration du code B sans modification de comportement
   ```
3. Push et création de la Pull Request

## Structure du projet

Le projet est organisé comme suit :

```
sadie/
├── core/           # Logique métier principale
│   ├── collectors/  # Collecteurs des données (version actuelle)
│   ├── models/      # Modèles de données
│   └── utils/       # Utilitaires partagés
├── data/           # Gestion des données (ancienne version, en cours de migration)
│   ├── collectors/  # Collecteurs obsolètes (utiliser core.collectors à la place)
│   └── storage/     # Stockage des données
├── web/            # Interface web et API
│   ├── static/      # Application front-end React
│   └── app.py       # API FastAPI
├── analysis/       # Analyse technique et indicateurs
└── tests/          # Tests unitaires et d'intégration
    ├── unit/       # Tests unitaires
    ├── integration/ # Tests d'intégration
    └── stress/      # Tests de performance et de charge
```

## Style de code

### Python

- Suivre PEP 8
- Utiliser Black pour le formatage
- Docstrings pour toutes les fonctions/classes
- Type hints obligatoires
- Maximum 88 caractères par ligne

```python
from typing import List, Optional

def calculate_average(values: List[float]) -> Optional[float]:
    """Calcule la moyenne d'une liste de valeurs.
    
    Args:
        values: Liste des valeurs à moyenner
        
    Returns:
        La moyenne ou None si la liste est vide
    """
    if not values:
        return None
    return sum(values) / len(values)
```

## Tests

Tous les nouveaux ajouts ou modifications doivent être accompagnés de tests.

### Exécution des tests

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit/

# Tests d'intégration uniquement
pytest tests/integration/

# Tests avec couverture
pytest --cov=sadie tests/
```

### Écrire des tests pour les collecteurs

Lors de l'écriture de tests pour les collecteurs de données, assurez-vous de :

1. **Mocker les API externes** : Ne jamais appeler des API réelles dans les tests
2. **Tester la gestion d'erreurs** : Simuler des erreurs réseau, des timeouts, des erreurs API
3. **Vérifier le traitement des données** : S'assurer que les données sont correctement parsées
4. **Tester les reconnexions** : Vérifier que le collecteur gère correctement les déconnexions
5. **Tester les limites** : Vérifier le comportement avec des limites de taux, des données invalides, etc.

Exemple de test pour un collecteur :

```python
@pytest.mark.asyncio
async def test_error_handling(collector):
    """Test de la gestion des erreurs."""
    with patch.object(collector, '_run', side_effect=[
        ConnectionError("Test connection error"),
        asyncio.TimeoutError("Test timeout"),
        None  # Troisième appel réussi
    ]):
        await collector.start()
        await asyncio.sleep(0.5)
        
        # Vérifier que le collecteur est toujours en cours d'exécution
        assert collector._running is True
        
        await collector.stop()
```

## Documentation

### Code

- Docstrings pour toutes les classes, méthodes et fonctions
- README à jour
- Exemples d'utilisation
- Type hints

### Nouvelle fonctionnalité

Toute nouvelle fonctionnalité doit être accompagnée de :
1. Mise à jour du README
2. Docstrings complètes
3. Exemples d'utilisation
4. Tests

## Collecteurs de données

Le développement de nouveaux collecteurs doit suivre certaines règles pour garantir la cohérence et la qualité.

### Architecture des collecteurs

Tous les nouveaux collecteurs doivent :
1. Être placés dans `sadie/core/collectors/`
2. Hériter de `BaseCollector` ou d'une classe spécialisée
3. Mettre en œuvre la gestion d'erreur robuste
4. Inclure des logs détaillés
5. Suivre les conventions de nommage

### Modèle pour un nouveau collecteur

```python
from typing import List, Dict, Any, Optional
import logging
import asyncio

from sadie.core.collectors.base import BaseCollector

class NewExchangeCollector(BaseCollector):
    """Collecteur pour l'exchange X.
    
    Args:
        name: Nom du collecteur
        symbols: Liste des symboles à suivre
        update_interval: Intervalle de mise à jour en secondes
        api_key: Clé API facultative
        api_secret: Secret API facultatif
        max_retries: Nombre maximal de tentatives de reconnexion
        retry_delay: Délai entre les tentatives en secondes
        connection_timeout: Timeout de connexion en secondes
        logger: Logger optionnel
    """
    
    def __init__(
        self,
        name: str,
        symbols: List[str],
        update_interval: float = 1.0,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        max_retries: int = 5,
        retry_delay: float = 1.0,
        connection_timeout: float = 10.0,
        logger: Optional[logging.Logger] = None,
    ):
        super().__init__(name, symbols, update_interval, logger)
        self.api_key = api_key
        self.api_secret = api_secret
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_timeout = connection_timeout
        # Initialisation spécifique
        
    async def _run(self) -> None:
        """Exécute la boucle principale du collecteur."""
        # Implémentation de la méthode
```

## Processus de revue

### Critères de validation

1. Tests passent
2. Couverture maintenue ou améliorée
3. Style de code respecté
4. Documentation à jour
5. Pas de régressions

### Checklist de revue

- [ ] Code lisible et maintenable
- [ ] Tests appropriés
- [ ] Documentation mise à jour
- [ ] Messages de commit clairs
- [ ] Gestion des erreurs
- [ ] Performance acceptable
- [ ] Sécurité vérifiée

## Questions

Pour toute question :
1. Vérifier la documentation
2. Chercher dans les issues
3. Ouvrir une nouvelle issue

## Remerciements

Merci à tous les contributeurs qui aident à améliorer SADIE ! 