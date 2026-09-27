# Guide de qualité du code pour SADIE

Ce document décrit les outils et procédures à suivre pour maintenir une qualité de code élevée dans le projet SADIE.

## Outils de qualité de code

Le projet utilise les outils suivants pour assurer la qualité du code :

- **TypeScript** : Vérification statique des types
- **ESLint** : Analyse statique du code pour détecter les erreurs et les problèmes de style
- **Prettier** : Formatage automatique du code pour maintenir un style cohérent
- **Jest** : Tests unitaires
- **Cypress** : Tests end-to-end

## Commandes npm disponibles

### Validation de code

- `npm run validate:all` : Exécute toutes les validations (TypeScript, ESLint, Prettier) et génère un rapport complet
- `npm run type-check:report` : Vérifie les types TypeScript et génère un rapport détaillé
- `npm run lint:report` : Exécute ESLint et génère un rapport détaillé
- `npm run format:report` : Vérifie le formatage avec Prettier et génère un rapport
- `npm run stats` : Génère des statistiques sur le code (lignes, fichiers, complexité)

### Correction automatique

- `npm run fix-all` : Corrige automatiquement les problèmes de formatage et de linting
- `npm run format:fix` : Corrige automatiquement les problèmes de formatage
- `npm run lint:fix` : Corrige automatiquement les problèmes détectés par ESLint

### Tests

- `npm test` : Exécute les tests unitaires en mode watch
- `npm run test:ci` : Exécute les tests unitaires une seule fois (pour CI/CD)
- `npm run test:coverage` : Exécute les tests unitaires et génère un rapport de couverture
- `npm run test:e2e` : Exécute les tests end-to-end avec Cypress

### Hooks Git

- `npm run setup-hooks` : Configure les hooks Git pour vérifier la qualité du code avant chaque commit

## Rapports de validation

Tous les rapports de validation sont générés dans le répertoire `reports/` :

- `typescript-report.json` : Rapport des erreurs TypeScript
- `eslint-report.json` : Rapport des erreurs ESLint
- `prettier-report.json` : Rapport des erreurs de formatage
- `validation-summary.json` : Résumé de toutes les validations
- `code-stats.json` : Statistiques détaillées sur le code source

## Configuration des outils

### ESLint

Le projet utilise une configuration ESLint avancée dans le fichier `.eslintrc.js` avec les plugins suivants :
- react
- react-hooks
- @typescript-eslint
- jsx-a11y
- import
- prettier

### Prettier

La configuration Prettier est définie dans `.prettierrc` avec les paramètres suivants :
```json
{
  "semi": true,
  "tabWidth": 2,
  "printWidth": 100,
  "singleQuote": true,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "jsxSingleQuote": false,
  "jsxBracketSameLine": false,
  "endOfLine": "auto"
}
```

### Jest

Les tests unitaires utilisent Jest avec la configuration dans `jest.config.js`, incluant :
- Support pour TypeScript via ts-jest
- Support pour les composants React via jest-environment-jsdom
- Seuils de couverture de code (70% pour les branches, fonctions, lignes)
- Mocks pour les fichiers statiques et les styles CSS

## Bonnes pratiques de développement

### Structure des types

- Définir les interfaces et types dans des fichiers dédiés (`src/types/`)
- Utiliser des noms clairs et descriptifs pour les interfaces et les types
- Préférer les interfaces pour les objets et les types pour les unions et intersections

### Composants React

- Utiliser des composants fonctionnels avec des hooks
- Spécifier les types des props avec TypeScript
- Éviter les dépendances inutiles dans les hooks useEffect
- Utiliser des noms significatifs pour les variables et fonctions

### État de l'application

- Utiliser Redux pour l'état global de l'application
- Utiliser les hooks useState et useReducer pour l'état local des composants
- Éviter la duplication d'état entre différents niveaux de l'application

### Hooks personnalisés

- Extraire la logique réutilisable dans des hooks personnalisés
- Préfixer les noms des hooks personnalisés avec "use"
- Documenter les hooks personnalisés avec des commentaires JSDoc

### Tests

- Écrire des tests pour tous les composants et les fonctions importantes
- Utiliser des mocks pour isoler les composants lors des tests
- Tester les cas d'erreur et les cas limites
- Maintenir une couverture de code d'au moins 70%

## Intégration dans le flux de travail

Pour intégrer ces validations dans votre flux de travail :

1. Exécutez `npm run setup-hooks` pour configurer les hooks Git
2. Les validations seront automatiquement exécutées avant chaque commit
3. Utilisez `npm run fix-all` pour corriger automatiquement les problèmes détectés
4. Consultez les rapports détaillés dans le dossier `reports/` pour les problèmes qui ne peuvent pas être corrigés automatiquement
5. Résolvez manuellement les problèmes restants avant de soumettre votre code

## Mise à jour des dépendances

Pour une mise à jour sécurisée des dépendances, utilisez le script dédié :

```bash
node scripts/update-dependencies.js
```

Ce script analysera les dépendances obsolètes, les classera par niveau de risque et suggérera un plan de mise à jour progressif. 