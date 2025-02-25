# Guide de contribution

## Introduction

Merci de votre intérêt pour contribuer à SADIE ! Ce document fournit les lignes directrices pour contribuer au projet.

## Table des matières

1. [Code de conduite](#code-de-conduite)
2. [Comment contribuer](#comment-contribuer)
3. [Style de code](#style-de-code)
4. [Tests](#tests)
5. [Documentation](#documentation)
6. [Processus de revue](#processus-de-revue)

## Code de conduite

Ce projet adhère au [Contributor Covenant](https://www.contributor-covenant.org/). En participant, vous devez respecter ce code.

## Comment contribuer

### Signaler des bugs

1. Vérifiez que le bug n'a pas déjà été signalé
2. Créez une issue en utilisant le template de bug
3. Incluez :
   - Version de SADIE
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Logs pertinents
   - Environnement (OS, Python, Node.js)

### Proposer des améliorations

1. Ouvrez une issue de discussion
2. Attendez la validation de l'équipe
3. Créez une Pull Request

### Processus de développement

1. Fork du projet
2. Création d'une branche
   ```bash
   git checkout -b feature/ma-fonctionnalite
   # ou
   git checkout -b fix/mon-correctif
   ```
3. Développement avec tests
4. Commit avec messages conventionnels
   ```bash
   feat: ajout de la fonctionnalité X
   fix: correction du bug Y
   docs: mise à jour de la documentation Z
   ```
5. Push et création de la Pull Request

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

### TypeScript/React

- ESLint avec configuration Airbnb
- Prettier pour le formatage
- Types explicites
- Composants fonctionnels avec hooks
- Props typées avec interfaces

```typescript
interface Props {
  data: MarketData;
  onUpdate: (data: MarketData) => void;
}

const MarketView: React.FC<Props> = ({ data, onUpdate }) => {
  const handleChange = useCallback((newData: MarketData) => {
    onUpdate(newData);
  }, [onUpdate]);

  return (
    <div>
      {/* JSX */}
    </div>
  );
};
```

## Tests

### Backend

- Tests unitaires avec pytest
- Tests d'intégration pour l'API
- Couverture minimale de 80%

```bash
# Tests unitaires
pytest tests/unit

# Tests d'intégration
pytest tests/integration

# Couverture
pytest --cov=sadie
```

### Frontend

- Tests unitaires avec Jest
- Tests de composants avec Testing Library
- Tests d'intégration avec Cypress

```bash
# Tests unitaires
npm test

# Tests d'intégration
npm run test:e2e
```

## Documentation

### API

- Documentation OpenAPI/Swagger
- Exemples pour chaque endpoint
- Description des modèles de données
- Codes d'erreur documentés

### Code

- Docstrings Python (Google style)
- JSDoc pour TypeScript
- README à jour
- Commentaires pertinents

## Processus de revue

### Critères de validation

1. Tests passent
2. Couverture maintenue
3. Style de code respecté
4. Documentation à jour
5. Pas de régressions

### Checklist de revue

- [ ] Code lisible et maintenable
- [ ] Tests appropriés
- [ ] Documentation mise à jour
- [ ] Messages de commit clairs
- [ ] Pas de code mort
- [ ] Performance acceptable
- [ ] Sécurité vérifiée

## Déploiement

1. Mise à jour de la version
   ```bash
   bump2version patch  # ou minor/major
   ```

2. Création du tag
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   ```

3. Push
   ```bash
   git push origin main --tags
   ```

## Questions

Pour toute question :
1. Vérifier la documentation
2. Chercher dans les issues
3. Ouvrir une nouvelle issue

## Remerciements

Merci à tous les contributeurs qui aident à améliorer SADIE ! 