# Guide de contribution à SADIE

Nous sommes ravis que vous souhaitiez contribuer à SADIE ! Ce document fournit les lignes directrices pour contribuer au projet.

## Code de conduite

Ce projet et tous ses participants sont régis par notre [Code de conduite](CODE_OF_CONDUCT.md). En participant, vous acceptez de respecter ce code.

## Comment puis-je contribuer ?

### Signaler des bugs

Les bugs sont suivis comme des [issues GitHub](https://github.com/radiofrance/sadie/issues). Avant de créer une issue :

1. Vérifiez si le bug n'a pas déjà été signalé
2. Créez une issue en utilisant le template "Bug Report"
3. Incluez autant de détails que possible :
   - Version de SADIE
   - Système d'exploitation
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Logs pertinents

### Suggérer des améliorations

Les suggestions d'amélioration sont également suivies via les issues GitHub :

1. Vérifiez si l'amélioration n'a pas déjà été suggérée
2. Créez une issue en utilisant le template "Feature Request"
3. Décrivez clairement :
   - Le problème que résout cette amélioration
   - La solution proposée
   - Les alternatives considérées

### Pull Requests

1. Fork le repository
2. Créez une branche pour votre modification
3. Écrivez des tests pour vos modifications
4. Assurez-vous que tous les tests passent
5. Mettez à jour la documentation si nécessaire
6. Créez la Pull Request

## Style de code

### Python

- Suivez [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Utilisez [Black](https://github.com/psf/black) pour le formatage
- Utilisez [isort](https://pycqa.github.io/isort/) pour trier les imports
- Utilisez [mypy](http://mypy-lang.org/) pour le typage statique

### Documentation

- Utilisez [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) pour les docstrings
- Mettez à jour la documentation dans `docs/` si nécessaire
- Ajoutez des exemples dans `examples/` pour les nouvelles fonctionnalités

## Processus de développement

### Installation de l'environnement de développement

```bash
# Cloner le repository
git clone https://github.com/radiofrance/sadie.git
cd sadie

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows

# Installer les dépendances de développement
pip install -e ".[dev]"
```

### Tests

```bash
# Exécuter tous les tests
pytest

# Exécuter les tests avec couverture
pytest --cov=sadie

# Exécuter les tests en parallèle
pytest -n auto
```

### Vérification du style

```bash
# Formatter le code
black .

# Trier les imports
isort .

# Vérifier le typage
mypy src tests

# Vérifier le style
flake8
```

### Documentation

```bash
# Générer la documentation
cd docs
make html
```

## Structure du projet

```
sadie/
├── .github/            # Configuration GitHub (CI/CD, etc.)
├── config/            # Fichiers de configuration
├── data/             # Données (ignorées par Git)
├── docs/             # Documentation
├── examples/         # Exemples d'utilisation
├── models/           # Modèles entraînés
├── notebooks/        # Notebooks Jupyter
├── requirements/     # Fichiers de dépendances
├── scripts/          # Scripts utilitaires
├── src/             # Code source
│   └── sadie/
│       ├── analysis/    # Analyse des données
│       ├── data/        # Collecte des données
│       ├── storage/     # Stockage des données
│       └── utils/       # Utilitaires
└── tests/           # Tests
    ├── integration/  # Tests d'intégration
    ├── performance/  # Tests de performance
    └── unit/        # Tests unitaires
```

## Versionnement

Nous utilisons [SemVer](http://semver.org/) pour le versionnement. Pour les versions disponibles, voir les [tags sur ce repository](https://github.com/radiofrance/sadie/tags).

## Licence

En contribuant à SADIE, vous acceptez que vos contributions soient sous licence MIT. 