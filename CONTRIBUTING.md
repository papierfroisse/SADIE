# Guide de Contribution à SADIE

## Introduction

Merci de votre intérêt pour contribuer à SADIE (Smart AI-Driven Investment Engine). Ce document fournit les lignes directrices pour contribuer au projet.

## Comment Contribuer

### 1. Configuration de l'Environnement de Développement

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/SADIE.git
cd SADIE
```

2. Créez un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

### 2. Structure du Code

- Suivez la structure de projet existante
- Placez les nouveaux modèles dans `src/models/`
- Placez les tests dans `tests/`
- Documentez votre code avec des docstrings

### 3. Style de Code

- Suivez PEP 8
- Utilisez Black pour le formatage
- Utilisez isort pour l'organisation des imports
- Utilisez flake8 pour la vérification du style

### 4. Process de Contribution

1. Créez une nouvelle branche :
```bash
git checkout -b feature/nom-de-votre-feature
```

2. Faites vos modifications

3. Testez votre code :
```bash
pytest tests/
```

4. Committez vos changements :
```bash
git add .
git commit -m "Description claire des changements"
```

5. Poussez vos modifications :
```bash
git push origin feature/nom-de-votre-feature
```

6. Créez une Pull Request

### 5. Guidelines pour les Pull Requests

- Décrivez clairement les changements
- Référencez les issues concernées
- Incluez des tests
- Assurez-vous que tous les tests passent
- Mettez à jour la documentation si nécessaire

### 6. Rapporter des Bugs

Utilisez le système d'issues de GitHub en incluant :
- Description détaillée du bug
- Étapes pour reproduire
- Comportement attendu vs observé
- Screenshots si pertinent
- Environnement (OS, versions, etc.)

## Standards de Code

### Python

```python
def example_function(parameter: str) -> bool:
    """
    Description claire de la fonction.

    Args:
        parameter (str): Description du paramètre

    Returns:
        bool: Description de la valeur de retour
    """
    # Votre code ici
    return True
```

### Documentation

- Documentez toutes les fonctions/classes avec des docstrings
- Maintenez le README.md à jour
- Ajoutez des commentaires pour le code complexe

### Tests

- Écrivez des tests unitaires pour toutes les nouvelles fonctionnalités
- Maintenez une couverture de code > 80%
- Utilisez pytest pour les tests

## Questions et Support

- Utilisez les issues GitHub pour les questions
- Consultez la documentation existante
- Rejoignez notre canal de discussion [lien à venir]

## Licence

En contribuant, vous acceptez que votre code soit sous la même licence que le projet. 