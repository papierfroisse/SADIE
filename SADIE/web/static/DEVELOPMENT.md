# Guide de développement pour SADIE Dashboard

Ce document présente les bonnes pratiques à suivre pour le développement de SADIE Dashboard, ainsi que les outils et procédures mis en place pour assurer la qualité du code.

## Architecture et organisation du code

SADIE Dashboard suit une architecture modulaire avec la structure suivante:

```
sadie/web/static/
├── public/             # Fichiers statiques accessibles publiquement
├── src/                # Code source de l'application
│   ├── components/     # Composants React réutilisables
│   ├── context/        # Contextes React (état global)
│   ├── hooks/          # Hooks React personnalisés
│   ├── pages/          # Composants de page (routes)
│   ├── services/       # Services pour la communication avec les API
│   └── types/          # Définitions TypeScript
├── scripts/            # Scripts utilitaires
└── tests/              # Tests unitaires et d'intégration
```

## Conventions et bonnes pratiques

### TypeScript

- **Toujours définir les types** : Évitez l'utilisation de `any` et favorisez des types précis.
- **Interface vs Type** : Utilisez `interface` pour les objets qui peuvent être étendus et `type` pour les unions, intersections ou types plus complexes.
- **Props des composants** : Définissez toujours une interface pour les props de vos composants.
- **Nommage des types** : Utilisez PascalCase pour les noms d'interfaces et de types.

```typescript
// Exemple de définition de props
interface ButtonProps {
  text: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
}

const Button: React.FC<ButtonProps> = ({ text, onClick, variant = 'primary' }) => {
  // ...
};
```

### Composants React

- **Fonctions vs Classes** : Privilégiez les composants fonctionnels avec les hooks.
- **Cohérence des noms** : Utilisez PascalCase pour les composants et camelCase pour les fonctions et variables.
- **Un composant par fichier** : Chaque fichier ne doit contenir qu'un seul composant exporté.
- **Tests unitaires** : Chaque composant doit avoir des tests associés.

### Style et formatage

- **Prettier** : Utilisez la configuration Prettier fournie pour un formatage cohérent.
- **ESLint** : Suivez les règles ESLint configurées pour maintenir la qualité du code.
- **Importations** : Organisez vos importations par catégorie (React, bibliothèques externes, composants internes).

## Outils de qualité du code

### Validation TypeScript

Le script `validate-types.js` permet de vérifier la validité des types dans votre projet:

```bash
npm run type-check:report
```

Ce script génère un rapport détaillé des erreurs TypeScript dans le dossier `reports/`.

### Correction automatique

En cas d'erreurs TypeScript courantes, vous pouvez utiliser le script de correction automatique:

```bash
node scripts/fix-typescript-errors.js
```

Ce script corrige automatiquement certaines erreurs courantes comme:
- Renommage des propriétés incohérentes
- Ajout de variables manquantes
- Correction des imports

### ESLint et Prettier

Pour formater votre code:

```bash
npm run format
```

Pour vérifier les erreurs de style:

```bash
npm run lint
```

### Tests unitaires

Pour exécuter les tests:

```bash
npm run test
```

Pour générer un rapport de couverture:

```bash
npm run test:coverage
```

## Workflow de développement recommandé

1. **Avant de commencer à coder**:
   - Tirez les dernières modifications (`git pull`)
   - Installez les dépendances si nécessaire (`npm install`)
   - Vérifiez que tous les tests passent (`npm run test`)

2. **Pendant le développement**:
   - Créez des composants réutilisables
   - Définissez les types pour toutes les props, états et fonctions
   - Écrivez des tests pour chaque nouvelle fonctionnalité

3. **Avant de commiter**:
   - Exécutez la validation des types (`npm run type-check:report`)
   - Formatez votre code (`npm run format`)
   - Vérifiez qu'il n'y a pas d'erreurs de lint (`npm run lint`)
   - Exécutez les tests (`npm run test`)

4. **En cas de problèmes**:
   - Consultez les rapports générés dans `reports/`
   - Utilisez les scripts de correction automatique
   - Référez-vous à la documentation TypeScript ou React si nécessaire

## Résolution des problèmes courants

### Erreurs TypeScript

- **Propriétés non reconnues** : Assurez-vous que vos définitions de types sont à jour et correspondent à l'utilisation dans le code.
- **Types incompatibles** : Vérifiez les conversions de type et utilisez les assertions de type avec parcimonie.
- **Imports manquants** : Assurez-vous que tous les types sont correctement exportés et importés.

### Problèmes Docker

- **Conteneur qui s'arrête** : Vérifiez les logs avec `docker logs sadie-frontend`.
- **Redémarrage du conteneur** : Utilisez le script `restart-sadie.ps1` pour un redémarrage propre.

### Ressources et références

- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)
- [ESLint Rules](https://eslint.org/docs/rules/)
- [Prettier Options](https://prettier.io/docs/en/options.html) 