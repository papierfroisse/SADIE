# Front SADIE — état des lieux et travail restant

Dernière vérification : 03/10/2026, à la racine `sadie/web/static` (Node 26, npm 11).

## État vérifié

| Contrôle | Commande | Résultat |
|---|---|---|
| Types | `npm run type-check` | **0 erreur** (14 avant) |
| Compilation | `npm run build` | **OK** — `build/` produit, `main.js` 396,86 kB |
| Tests | `npm run test:ci` | **34 succès sur 34**, 5 suites (avant : 17 échecs sur 37) |
| Lint | `npm run lint` | **220 erreurs**, 703 avertissements (359 / 1003 avant retrait des modules morts) |
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
   d'un passif de lint (359 erreurs au plus haut de la passe) : le lint redevient une étape à part
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

12. **Le menu de notifications n'était plus rendu.** `Layout.tsx` gardait la
    cloche, le badge, le son, `notificationAnchorEl`, `isNotificationMenuOpen` et
    `formatNotificationTime`… mais aucun `<Menu>` : cliquer sur la cloche
    n'ouvrait rien, et `Menu` / `MenuItem` étaient importés sans usage. Le menu est
    rendu à nouveau (liste plafonnée à dix entrées, horodatage relatif, message
    quand la liste est vide).

13. **Même alerte comptée plusieurs fois.** L'effet de notification ne mémorisait
    aucun identifiant traité et dépendait de l'identité de `lastAlert`, que le
    fournisseur peut recréer à chaque rendu : la même alerte pouvait être
    recomptée et remplir la liste de doublons. Une garde par identifiant d'alerte
    a été ajoutée, avec le test qui la couvre.

14. **`audio.play()` non tolérant.** `audio.play().catch(...)` levait
    `TypeError: Cannot read properties of undefined (reading 'catch')` dès que
    `play()` ne renvoie pas de promesse (jsdom, moteurs anciens), ce qui cassait
    tout le rendu à la première alerte. Le `catch` n'est plus rattaché que si une
    promesse est retournée.

15. **Indicateur de connexion du graphique.** `TradingChart` déstructurait
    `isConnected` sans jamais s'en servir ; le statut (🟢 / 🔴) est désormais
    affiché à côté du symbole, et `data-testid="chart-container"` a été ajouté sur
    la zone de graphique, faute de rôle accessible pour la cibler.

16. **Boutons icône sans nom accessible.** La cloche de notifications, la
    suppression d'alerte et le filtre n'exposaient aucun `aria-label` : un lecteur
    d'écran annonçait « bouton » sans plus. Corrigé ; le compteur de notifications
    non lues est maintenant annoncé, ce qui rend « compteur remis à zéro »
    vérifiable sans dépendre des classes internes de MUI `Badge`.

17. **Neuf modules morts supprimés** (≈ 50 ko, 136 erreurs de lint) :
    `components/Sidebar.tsx`, `components/TechnicalAnalysis.jsx`,
    `components/ChartContainer.jsx` (et son `.css`), `components/MarketOverview.jsx`
    (et son `.css`), `pages/TradingView.tsx`, `pages/AdvancedTradingView.tsx`,
    `hooks/useAlerts.ts`, `hooks/useMarketData.ts`. Aucun n'était atteignable
    depuis `index.tsx` → `App.tsx` ; la seule occurrence restante de chacun était
    le fichier lui-même (ou son propre import CSS).

## Travail restant, par ordre de valeur

### 1. Lint — 220 erreurs, dont 159 dues au typage `any`

| Règle | Occurrences | Nature |
|---|---|---|
| `no-unsafe-member-access` | 66 | `any` venu d'axios / `JSON.parse` |
| `no-unsafe-argument` | 34 | idem `no-unsafe-*` |
| `no-unsafe-assignment` | 29 | idem |
| `no-unused-vars` | 25 | corrections mécaniques |
| `no-unsafe-call` | 21 | idem |
| `require-await` | 13 | `async` sans `await` |
| `no-floating-promises` | 9 | promesses ignorées (vrai risque) |
| `no-unsafe-return` | 9 | idem `no-unsafe-*` |

La majorité vient d'un point unique : **la couche API n'est pas typée**.
`services/api.ts` renvoie des `any` qui contaminent les pages (`Dashboard.tsx` :
53 erreurs, `Metrics.tsx` : 58). Typer les réponses de `api.ts` (`ApiResponse<T>`
existe déjà, il n'est pas utilisé) éteint la plus grande partie des 159 erreurs.
Ensuite : 25 `no-unused-vars` (mécanique), puis 9 `no-floating-promises` à
traiter au cas par cas, ce sont de vraies promesses non attendues.

Autocorrectibles, à passer en un commit séparé : `prettier/prettier` (561
avertissements), `import/order` (76), `sort-imports` (39).

### 2. Tests — résolu (34 verts sur 34)

Le point de départ — 17 échecs sur 37 — mélangeait deux causes qu'il fallait
séparer.

**De vrais défauts de composant**, révélés par les échecs :

- `Layout` ne rendait plus son `<Menu>` de notifications (§12) : deux échecs ne
  pouvaient pas passer.
- `audio.play().catch(...)` (§14) levait un `TypeError` qui cassait quatre autres
  tests de notifications.
- `TradingChart` ne rendait ni statut de connexion ni conteneur ciblable, et
  `isConnected` était déstructuré sans usage (§15).
- les boutons icône de `AlertList` et `Layout` n'exposaient aucun nom accessible
  (§16).

**De vrais tests périmés**, à réécrire :

- `AlertList.test.tsx` : une `describe` entière testait une version du composant
  qui consommait le hook `useAlerts`, alors que le composant appelle `api`
  directement — ces six tests ne couvraient donc rien du code réel.
- deux tests de notifications enchaînaient 4 puis 15 `render` : autant de
  composants montés simultanément, pour une seule instance attendue.
- `WebSocketContext.test.tsx` : le faux socket n'appelait jamais `onmessage` et
  émettait un payload imbriqué `{ type, data }` que le fournisseur ignore ; le
  test d'erreur déclenchait `onerror` sur un socket détaché, sans effet sur
  l'état.

Résultat : **34 tests verts sur 34**. Aucun test n'a été désactivé ni mis en
`skip`.

### 3. Canal WebSocket d'alerte — à écrire côté serveur

L'ancien hook `useAlerts` (supprimé, voir §17) traitait un message si
`message.type === 'alert'`, puis le convertissait en `Alert`. Or `Alert.type` vaut
`'price' | 'volume' | 'indicator'`, jamais
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
- `react-scripts` 5.0.1 est sa dernière version : CRA est abandonné. Tant qu'il
  reste en place, l'alerte `webpack-dev-middleware` est infermable et le job
  Dependabot échoue à chaque poussée sur `main` (§6). Deux issues : sortir de
  `react-scripts` (Vite), la seule qui règle la cause, ou des `overrides` npm,
  qui masquent l'alerte sans toucher la chaîne et restent à valider sur
  `npm start` — le paquet ne sert qu'au serveur de développement.

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

### 6. Dépendances vulnérables (Dependabot, relevés des 01/10 et 03/10/2026)

- Le front vivant (`sadie/web/static`) porte **la totalité des alertes ouvertes du
  dépôt** : 87 au relevé du 01/10 (3 critiques, 40 hautes, 36 moyennes, 8 basses),
  88 au relevé du 03/10 (3 / 41 / 36 / 8). Toutes sont sur
  `sadie/web/static/package-lock.json` ; le backend (Python) n'en a plus aucune.
  Le total bouge d'une unité sans qu'aucune dépendance ne change : GitHub révise
  son propre avis sur un paquet. Un chiffre recopié dans un document est donc
  toujours périmé — `gh api .../dependabot/alerts` reste la référence.
  Les trois critiques sont nommées : `websocket-driver` (« Message corruption via
  abuse of protocol length headers »), `shell-quote` (« quote() does not escape
  newlines ») et `form-data` (« unsafe random function »).
- **axios concentrait à lui seul 30 alertes**, dont des critiques remontées par
  ses dépendances (`form-data`, `qs`). Il est monté de 1.7.9 à 1.20.0 dans le
  commit `ff3a9cf`. **Résultat mesuré après le rescan** : le dépôt passe de 278 à
  87 alertes, le front vivant de 120 à 87, et les alertes axios de 30 à 0 ; il
  reste 3 critiques (contre 4), sans effet sur les types, la compilation ni les
  tests.
- Les alertes restantes ne sont atteignables que par la chaîne d'outils de
  développement, d'après l'arbre npm : `shell-quote` 1.8.2
  (`react-dev-utils`, `webpack-dev-server`), `websocket-driver` 0.7.4 (`sockjs`,
  HMR) et `form-data` 3.0.2 (`jest` 27 → `jsdom` 16, chemin de test). `form-data`
  en version récente (`4.0.6`, via axios) n'est pas concerné. Le paquet livré au
  navigateur ne contient donc plus d'alerte critique.
- Le reste vient de cette même chaîne d'outils : `minimatch` (9), `node-forge`
  (7), `webpack-dev-server` (6), `postcss` (5), `svgo` (4), `ws` (3). Les traiter
  suppose de sortir de `react-scripts` (Vite) ou de figer des `overrides`.
  `qs` (4 alertes) n'est d'ailleurs plus atteint par axios — corrigé — mais par
  `cypress` et par `react-scripts` → `webpack-dev-server` → `express` →
  `body-parser`, d'après `npm ls qs`.
- **Une alerte que Dependabot ne peut pas fermer** — et qui fait échouer son
  propre job. Le journal du run « Dependabot Updates » du 01/10
  (`gh run view 36896169779`, log privé récupéré via
  `curl -H "Authorization: Bearer $(gh auth token)" .../actions/runs/<id>/logs`)
  donne la cause mot pour mot : « A patched version exists for
  webpack-dev-middleware, but the available update path would downgrade
  react-scripts from 5.0.1 to 0.0.0 ». La chaîne est
  `react-scripts` 5.0.1 → `webpack-dev-server` 4.15.2 → `webpack-dev-middleware`
  `^5.3.4`. L'outil conseille lui-même soit de mettre `react-scripts` à jour —
  aucune version publiée ne le permet, CRA est abandonné — soit d'ajouter un
  `overrides`. C'est la décision du point 4, mais elle a désormais une preuve :
  tant que `react-scripts` reste en place, ce job échoue à chaque poussée sur
  `main` (échecs constatés les 27/09 et 01/10, pas une régression de cette passe).
- **157 des 278 alertes initiales du dépôt** venaient de `old/SADIE_backup/`, une
  copie morte du front, depuis supprimée : leur disparition ne touchait pas le
  code vivant.