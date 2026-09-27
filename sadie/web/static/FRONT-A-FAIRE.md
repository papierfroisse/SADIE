# Front SADIE — état des lieux et travail restant

Dernière vérification : 27/09/2026, à la racine `sadie/web/static` (Node 26, npm 11).

## État vérifié

| Contrôle | Commande | Résultat |
|---|---|---|
| Types | `npm run type-check` | **0 erreur** (14 avant) |
| Compilation | `npm run build` | **OK** — `build/` produit, `main.js` 391,5 kB |
| Lint | `npm run lint` | **286 erreurs**, 941 avertissements |
| Tests | `npm run test:ci` | **20 échecs / 13 succès**, 4 suites en échec |
| Installation reproductible | `npm ci` | OK (le lock est cohérent) |

Avant cette passe, **aucune chaîne ne vérifiait ce front** : ni la CI Python, ni
un job Node. Le défaut le plus grave était invisible — le projet ne compilait
plus du tout.

## Ce qui a été corrigé

1. **MUI v4 déclaré mais inutilisé.** `@material-ui/core` et `@material-ui/icons`
   étaient dans `package.json` alors que le code n'importe que `@mui/*` (62
   imports, 0 pour v4) : la migration était faite, les paquets oubliés. Ils
   exigent en plus React 17 alors que le projet est en React 18, ce qui faisait
   échouer `npm install` en `ERESOLVE`. Ils sont retirés ; MUI v4 n'est plus
   présent dans `node_modules` (vérifié).

2. **Types React incohérents avec le runtime.** `@types/react@^17.0.83` et
   `@types/react-dom@^19.0.3` pour un React 18.3.1 : types alignés sur 18.
   `@types/testing-library__react` (paquet stub obsolète) supprimé ; il était la
   seconde source de conflit `ERESOLVE`.

3. **Deux fichiers de types concurrents.** `src/types.ts` **et**
   `src/types/index.ts` déclaraient les mêmes noms avec des formes différentes :
   `Alert` en camelCase d'un côté, `Order` avec `timestamp` au lieu de
   `createdAt`/`updatedAt` de l'autre, `TechnicalIndicator` sans `color` ni
   `signal`. TypeScript résout un fichier avant un dossier homonyme : tous les
   imports `'../types'` tombaient sur `types.ts` et le second contrat n'était
   **jamais lu**. Les deux sont fusionnés dans `src/types.ts`, `src/types/`
   supprimé.

4. **14 erreurs TypeScript réelles** corrigées : `IndicatorPanel` (champs
   absents du type fantôme), `OrderPanel` (le type de la commande exigeait des
   champs que le client ne peut pas connaître), `useAlerts` (`WebSocketMessage`
   utilisé sans import), `Dashboard` (spread sur `unknown`, valeurs de `Select`
   non converties vers les unions `Widget`), fixtures de `AlertList.test.tsx`
   (en snake_case) et de `WebSocketContext.test.tsx` (`data:` imbriqué,
   `connect()` appelé avec un seul argument).

5. **Deux configurations mortes supprimées.** `.eslintrc.json` (ESLint 8 lit
   `.eslintrc.js` en premier, le `.json` n'était jamais appliqué) et
   `jest.config.js` (`react-scripts` ne lit que le champ `jest` de
   `package.json`, et seulement pour une liste d'options autorisées — `testTimeout`,
   `setupFiles`, `watchPlugins` n'y figurent pas). Ces fichiers donnaient
   l'illusion de réglages actifs : même famille de bug que les types fantômes,
   une configuration qui ne s'applique pas silencieusement.

6. **Résolveur d'import manquant.** `.eslintrc.js` demandait le résolveur
   `typescript` sans que `eslint-import-resolver-typescript` soit installé : la
   règle `import/no-unresolved` signalait `@mui/material` comme introuvable dans
   tous les fichiers. La règle est désactivée avec justification : l'ajouter
   entre en conflit avec `react-scripts` 5 (qui impose `@typescript-eslint` 5
   face au 6 du projet) et TypeScript couvre déjà ce contrôle via
   `npm run type-check`.

7. **`cross-env` manquant** alors que `start:safe` et `start:fast` l'utilisent :
   ajouté en dépendance de développement.

8. **Lint découplé de la compilation.** `npm run build` n'échoue plus à cause
   d'un passif de lint de 286 erreurs : le lint redevient une étape à part
   entière (`npm run lint`), au lieu d'un bloqueur muet sur la compilation. Un
   script `npm run check` (build + lint + types) sert de cible pour rendre le
   lint bloquant quand le passif sera traité.

9. **Garde-fou CI ajouté** (`.github/workflows/ci.yml`, job `frontend`) :
   `npm ci`, `npm run type-check`, `npm run build`. C'est ce qui est vert
   aujourd'hui, donc ce qui peut être verrouillé sans mentir.

## Travail restant, par ordre de valeur

### 1. Lint — 286 erreurs, dont 202 dues au typage `any`

| Règle | Occurrences | Nature |
|---|---|---|
| `no-unsafe-member-access` | 80 | `any` venu d'axios / `JSON.parse` |
| `no-unused-vars` | 42 | corrections mécaniques |
| `no-unsafe-assignment` | 42 | idem `no-unsafe-*` |
| `no-unsafe-argument` | 40 | idem |
| `no-unsafe-call` | 27 | idem |
| `no-floating-promises` | 15 | promesses ignorées (vrai risque) |
| `require-await` | 14 | `async` sans `await` |
| `no-unsafe-return` | 13 | idem `no-unsafe-*` |

La majorité vient d'un point unique : **la couche API n'est pas typée**.
`services/api.ts` renvoie des `any` qui contaminent les pages (`Dashboard.tsx` :
59 erreurs, `Metrics.tsx` : 58). Typer les réponses de `api.ts` (`ApiResponse<T>`
existe déjà, il n'est pas utilisé) éteint la plus grande partie des 202 erreurs.
Ensuite : 42 `no-unused-vars` (mécanique), puis 15 `no-floating-promises` à
traiter au cas par cas, ce sont de vraies promesses non attendues.

Autocorrectibles, à passer en un commit séparé : `prettier/prettier` (743
avertissements), `import/order` (111), `sort-imports` (45).

### 2. Tests — 20 échecs sur 33

Suites en échec : `TradingChart.test.tsx`, `Layout.test.tsx`,
`AlertList.test.tsx`, `WebSocketContext.test.tsx`. À traiter après le typage :
les fixtures touchées ici montrent que ces tests ont été écrits contre les
anciens contrats de données et n'ont jamais tourné depuis.

### 3. Contrat des messages WebSocket d'alerte — indécis

`useAlerts` traite un message quand `message.type === 'alert'`, puis le convertit
en `Alert`. Or `Alert.type` vaut `'price' | 'volume' | 'indicator'`, jamais
`'alert'` : soit le serveur envoie l'alerte à plat dans une enveloppe
`{ type: 'alert', ... }`, soit **la branche ne se déclenche jamais** et les
alertes temps réel sont silencieusement ignorées. Aucun endpoint WebSocket
d'alerte n'existe côté backend (`sadie/web/stream_manager.py` ne diffuse que du
`market_data`) : le contrat doit être écrit côté serveur, puis le front aligné.

### 4. Décisions à prendre

- `DISABLE_ESLINT_PLUGIN=true` dans `build` : solution d'attente assumée tant que
  le passif de lint existe. À retirer quand `npm run check` passera.
- Cible Node : le poste est en Node 26, la CI en Node 20. À figer (`.nvmrc` +
  `engines`) au prochain passage sur le front.

### 5. Image Docker : le front n'y est jamais construit

`Dockerfile` et `Dockerfile.backend` ne contiennent aucune référence à Node ou
npm. Une image déployée ne peut donc pas contenir `sadie/web/static/build`
(dossier ignoré par git) : l'API retombe sur le placeholder
`static/index.html`. Il reste à ajouter une étape de construction du front dans
l'image. Non fait ici : Docker n'est pas installé sur le poste, une modification
non testée serait pire que le manque documenté.

Vérification faite après compilation locale (`TestClient`) : `GET /` renvoie 200
avec la racine React (pas le placeholder), `/static/js/main.<hash>.js` renvoie
200, et `/package.json`, `/src/index.tsx`, `/Dockerfile` renvoient 404 — la fuite
de l'ancien montage statique (qui exposait les sources) est bien fermée.

### 6. Dépendances vulnérables (Dependabot, relevé du 27/09/2026)

- Front vivant (`sadie/web/static`) : **120 alertes ouvertes** — 4 critiques,
  54 hautes, 53 moyennes, 9 basses.
- **axios concentrait à lui seul 30 alertes**, dont des critiques remontées par
  ses dépendances (`form-data`, `qs`). Il est monté de 1.7.9 à 1.20.0 dans le
  commit `ff3a9cf`, sans effet sur les types, la compilation ni les tests.
- Les autres critiques : `shell-quote`, `websocket-driver` (chaîne d'outils de
  `react-scripts` 5, donc dépendances de développement).
- Le reste vient de cette même chaîne d'outils : `minimatch` (9), `node-forge`
  (7), `webpack-dev-server` (6), `postcss` (5), `svgo` (4), `ws` (3). Les traiter
  suppose de sortir de `react-scripts` (Vite) ou de figer des `overrides`.
- **157 des 278 alertes du dépôt** viennent de `old/SADIE_backup/`, une copie
  morte du front : leur suppression est un gain immédiat qui ne touche pas le
  code vivant.