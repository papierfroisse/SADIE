# Front SADIE — état des lieux et travail restant

Dernière vérification : 27/09/2026, à la racine `sadie/web/static` (Node 26, npm 11).

## État vérifié

| Contrôle | Commande | Résultat |
|---|---|---|
| Types | `npm run type-check` | **0 erreur** (14 avant) |
| Compilation | `npm run build` | **OK** — `build/` produit, `main.js` 391,5 kB |
| Lint | `npm run lint` | **270 erreurs**, 895 avertissements |
| Tests | `npm run test:ci` | **17 échecs / 20 succès** sur 37, 4 suites en échec |
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

10. **Contrat d'API front/back des alertes, rompu et rétabli.** Le modèle
    `Alert` de `sadie/web/app.py` est en **snake_case** (`notification_type`,
    `created_at` en millisecondes) alors que le front travaillait en camelCase :
    `alert.createdAt` restait `undefined`, d'où un `RangeError: Invalid time
    value` à l'affichage, et `createAlert` envoyait un payload rejeté en 422 par
    FastAPI. La traduction se fait maintenant dans la couche API
    (`versAlerte` / `versAlerteApi` dans `services/api.ts`), avec un test dédié
    (`src/services/__tests__/api.test.ts`).

11. **URL des WebSockets corrigée.** Le backend n'expose que
    `@app.websocket("/ws/market")` avec `exchange` et `symbols` en paramètres de
    requête ; le front ouvrait `.../ws/market/<symbole>`, une URL qui ne
    correspond à aucune route : aucun flux de marché ne s'ouvrait. La
    construction d'URL est corrigée. Le canal d'alerte, lui, n'existe pas côté
    serveur : le hook ouvrait une connexion par alerte sur une URL inexistante et
    testait `message.type === 'alert'`, une valeur que `Alert.type` ne peut jamais
    prendre — branche morte retirée (voir §3 du travail restant).

## Travail restant, par ordre de valeur

### 1. Lint — 270 erreurs, dont près de 190 dues au typage `any`

| Règle | Occurrences | Nature |
|---|---|---|
| `no-unsafe-member-access` | 77 | `any` venu d'axios / `JSON.parse` |
| `no-unused-vars` | 40 | corrections mécaniques |
| `no-unsafe-assignment` | 40 | idem `no-unsafe-*` |
| `no-unsafe-argument` | 36 | idem |
| `no-unsafe-call` | 26 | idem |
| `no-floating-promises` | 15 | promesses ignorées (vrai risque) |
| `require-await` | 14 | `async` sans `await` |
| `no-unsafe-return` | 9 | idem `no-unsafe-*` |

La majorité vient d'un point unique : **la couche API n'est pas typée**.
`services/api.ts` renvoie des `any` qui contaminent les pages (`Dashboard.tsx` :
59 erreurs, `Metrics.tsx` : 58). Typer les réponses de `api.ts` (`ApiResponse<T>`
existe déjà, il n'est pas utilisé) éteint la plus grande partie des 202 erreurs.
Ensuite : 42 `no-unused-vars` (mécanique), puis 15 `no-floating-promises` à
traiter au cas par cas, ce sont de vraies promesses non attendues.

Autocorrectibles, à passer en un commit séparé : `prettier/prettier` (743
avertissements), `import/order` (111), `sort-imports` (45).

### 2. Tests — 17 échecs sur 37

Corrigé dans cette passe : 4 fixtures qui étaient en snake_case alors que le mock
porte sur la couche API (donc sur le domaine en camelCase) — d'où les
`RangeError: Invalid time value` —, et le mock de `useWebSocket` dans
`Layout.test.tsx`, qui posait son implémentation sans jamais la remettre à zéro :
elle fuyait sur les tests suivants. Le fichier `services/__tests__/api.test.ts`
ajoute 4 tests sur la traduction du contrat.

Échecs restants, tous des **assertions écrites contre une version antérieure de
l'interface** :

| Suite | Échecs | Nature |
|---|---|---|
| `Layout.test.tsx` | 8 | attend « SADIE Trading » et « Connecté » alors que le composant affiche « En ligne » / « Hors ligne », et cherche `notification-button` / `notification-badge` : le composant n'expose **aucun `data-testid`** |
| `AlertList.test.tsx` | 5 | textes et rôles de l'UI actuelle (« Ajouter une alerte », bouton `/supprimer/i`), et un attendu de payload à revoir |
| `TradingChart.test.tsx` | 2 | cherche `[data-testid="chart-container"]`, absent du composant |
| `WebSocketContext.test.tsx` | 2 | `toHaveProperty` sur une structure qui a changé, et contenu de message d'erreur |

Deux suites de travail : ajouter les `data-testid` manquants dans les composants
(`Layout`, `TradingChart`) puis aligner les assertions ; pour `AlertList` et
`WebSocketContext`, vérifier au cas par cas si l'écart révèle une régression de
l'UI ou un test périmé. **Aucun de ces échecs ne vient du code applicatif** : le
build et les types sont verts.

### 3. Canal WebSocket d'alerte — à écrire côté serveur

`useAlerts` traitait un message si `message.type === 'alert'`, puis le convertissait
en `Alert`. Or `Alert.type` vaut `'price' | 'volume' | 'indicator'`, jamais
`'alert'` : la branche ne pouvait pas s'exécuter. Elle ouvrait en plus une
connexion par alerte sur `.../ws/market/alert/<id>`, une URL inexistante : aucun
endpoint WebSocket d'alerte n'existe (`sadie/web/stream_manager.py` ne diffuse que
du `market_data`). Ce code mort a été retiré plutôt que laissé en place.

Reste à faire : écrire le canal côté serveur (endpoint + payload documenté), puis
le rebrancher dans le front en réutilisant la traduction `versAlerte` déjà en
place. En attendant, les alertes passent par l'API REST.

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
  commit `ff3a9cf`. **Résultat mesuré après le rescan** : le dépôt passe de 278 à
  245 alertes, le front vivant de 120 à 87, et les alertes axios de 30 à 0 ; il
  reste 3 critiques (contre 4), sans effet sur les types, la compilation ni les
  tests.
- Les critiques restantes ne sont atteignables que par la chaîne d'outils de
  développement, d'après l'arbre npm : `shell-quote` 1.8.2
  (`react-dev-utils`, `webpack-dev-server`), `websocket-driver` 0.7.4 (`sockjs`,
  HMR) et `form-data` 3.0.2 (`jest` 27 → `jsdom` 16, chemin de test). `form-data`
  en version récente (`4.0.6`, via axios) n'est pas concerné. Le paquet livré au
  navigateur ne contient donc plus d'alerte critique.
- Le reste vient de cette même chaîne d'outils : `minimatch` (9), `node-forge`
  (7), `webpack-dev-server` (6), `postcss` (5), `svgo` (4), `ws` (3). Les traiter
  suppose de sortir de `react-scripts` (Vite) ou de figer des `overrides`.
- **157 des 278 alertes du dépôt** viennent de `old/SADIE_backup/`, une copie
  morte du front : leur suppression est un gain immédiat qui ne touche pas le
  code vivant.