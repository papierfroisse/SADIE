# Guide de Contribution

Nous sommes ravis que vous souhaitiez contribuer à SADIE ! Ce guide vous aidera à comprendre notre processus de développement.

## Processus de développement

### 1. Git Flow

Nous utilisons une version simplifiée de Git Flow :

- `main` : version stable
- `develop` : développement principal
- `feature/*` : nouvelles fonctionnalités
- `hotfix/*` : corrections urgentes
- `release/*` : préparation des versions

### 2. Processus de contribution

1. Fork le dépôt
2. Créer une branche depuis `develop`
3. Développer la fonctionnalité
4. Soumettre une Pull Request

### 3. Standards de code

#### Style
- Nous utilisons Black pour le formatage
- Isort pour l'organisation des imports
- Pylint pour l'analyse statique
- Mypy pour le typage statique

#### Tests
- Tests unitaires obligatoires
- Tests d'intégration si nécessaire
- Tests de performance pour les optimisations
- Couverture minimale : 80%

#### Documentation
- Docstrings pour toutes les classes et méthodes
- Documentation des API
- Exemples de code
- Mise à jour du changelog

## Workflow de développement

### 1. Préparation de l'environnement

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/SADIE.git
cd SADIE

# Créer une branche
git checkout -b feature/ma-fonctionnalite

# Installer les dépendances de développement
pip install -r requirements/dev.txt
```

### 2. Développement

```bash
# Formater le code
black SADIE/
isort SADIE/

# Vérifier le typage
mypy SADIE/

# Lancer les tests
pytest tests/
```

### 3. Commit

Format des messages :
```
type(scope): description

Corps du message (optionnel)

Footer (optionnel)
```

Types :
- `feat` : nouvelle fonctionnalité
- `fix` : correction de bug
- `docs` : documentation
- `style` : formatage
- `refactor` : refactoring
- `test` : tests
- `chore` : maintenance

Exemple :
```bash
git commit -m "feat(collector): add retry mechanism for network errors

- Add exponential backoff
- Implement max retries
- Add logging for retry attempts

Closes #123"
```

### 4. Pull Request

1. Pousser les changements :
```bash
git push origin feature/ma-fonctionnalite
```

2. Créer une Pull Request sur GitHub :
   - Titre clair et descriptif
   - Description détaillée des changements
   - Référence aux issues concernées
   - Screenshots/captures si pertinent

3. Répondre aux revues de code

## Bonnes pratiques

### Code
- DRY (Don't Repeat Yourself)
- SOLID principles
- Commentaires pertinents
- Noms de variables explicites
- Gestion des erreurs appropriée

### Tests
- Tests indépendants
- Utilisation de fixtures
- Mocks pour les services externes
- Tests de cas limites

### Performance
- Profiling avant optimisation
- Benchmarks comparatifs
- Documentation des optimisations
- Tests de charge

## CI/CD

Notre pipeline CI/CD vérifie :

1. Style de code
2. Tests
3. Couverture de code
4. Documentation
5. Performance

## Support

Pour toute question :

1. Issues GitHub
2. Discussions GitHub
3. Canal Discord
4. Email : dev@sadie-project.com

## Licence

En contribuant, vous acceptez que votre code soit sous licence MIT. 