# État des Lieux et Plan d'Action - CryptoChart Pro

## État Actuel

### Fonctionnalités Implémentées
- ✅ Affichage des chandeliers (CandlestickRenderer)
- ✅ Gestion des timeframes (1m, 5m, 15m, 30m, 1h, 4h, 1d)
- ✅ Liste des tickers avec prix et variations
- ✅ Thème sombre
- ✅ Authentification Firebase
- ✅ Gestion des données en temps réel
- ✅ Indicateurs techniques de base (RSI, MACD, Volume)

### Fonctionnalités Manquantes/À Restaurer
- ❌ Indicateurs en bas du graphique
- ❌ Section des exchanges sous les tickers
- ❌ Affichage des prix sur l'axe Y
- ❌ Affichage des dates sur l'axe X
- ❌ Toolbar complète avec tous les outils
- ❌ Layout exact correspondant au screenshot de référence

### Problèmes Identifiés
1. Perte de certaines fonctionnalités lors des dernières modifications
2. Structure de fichiers désorganisée
3. Manque de cohérence dans l'architecture
4. Certains composants doivent être restaurés

## Plan d'Action

### 1. Restructuration des Fichiers
- [ ] Créer un dossier `old/` pour archiver les anciennes versions
- [ ] Réorganiser les fichiers par domaine fonctionnel
- [ ] Nettoyer les imports et dépendances

### 2. Restauration des Fonctionnalités
- [ ] Réintégrer les indicateurs en bas du graphique
- [ ] Restaurer la section des exchanges
- [ ] Rétablir l'affichage correct des axes (prix et dates)
- [ ] Reconfigurer la toolbar complète

### 3. Améliorations UI/UX
- [ ] Aligner le layout sur le screenshot de référence
- [ ] Améliorer la cohérence visuelle
- [ ] Optimiser les transitions et animations

### 4. Documentation
- [ ] Mettre à jour le DEVBOOK.md
- [ ] Documenter l'architecture
- [ ] Créer des guides d'utilisation

## Structure des Dossiers Proposée

```
src/
├── components/
│   ├── chart/
│   ├── indicators/
│   ├── toolbar/
│   └── widgets/
├── services/
│   ├── api/
│   ├── websocket/
│   └── storage/
├── store/
├── utils/
├── types/
└── old/     # Archives
```

## Fichiers à Déplacer vers old/

### Dossiers Redondants
- `src/renderer/` → `src/old/renderer/`
- `src/renderers/` → `src/old/renderers/`

### Fichiers Obsolètes ou à Refactorer
- Tous les fichiers test (test.txt, test2, test)
- Les anciens fichiers de configuration non utilisés

## Organisation des Fichiers

### À Conserver et Améliorer
- `src/components/` - Composants React principaux
- `src/services/` - Services d'API et WebSocket
- `src/hooks/` - Custom hooks React
- `src/utils/` - Fonctions utilitaires
- `src/types/` - Types TypeScript
- `src/styles/` - Styles globaux et thèmes

### Nouveaux Dossiers à Créer
- `src/components/chart/` - Composants liés au graphique
- `src/components/indicators/` - Composants d'indicateurs
- `src/components/toolbar/` - Composants de la barre d'outils
- `src/components/widgets/` - Widgets réutilisables

## Prochaines Actions Immédiates

1. Créer la nouvelle structure de dossiers
2. Déplacer les fichiers vers leurs nouveaux emplacements
3. Mettre à jour les imports dans les fichiers
4. Restaurer les fonctionnalités manquantes

## Fonctionnalités à Restaurer en Priorité

1. Indicateurs en bas du graphique
   - Réintégrer le composant d'indicateurs
   - Restaurer le layout vertical
   - Rétablir la synchronisation avec le graphique principal

2. Section des exchanges
   - Restaurer le composant des exchanges
   - Réintégrer les données en temps réel
   - Rétablir le style et le layout

3. Affichage des axes
   - Restaurer l'affichage des prix sur l'axe Y
   - Restaurer l'affichage des dates sur l'axe X
   - Améliorer le formatage et le style

4. Toolbar
   - Restaurer tous les outils de dessin
   - Réintégrer les options d'indicateurs
   - Rétablir les fonctionnalités de zoom et navigation

## Plan de Réorganisation des Fichiers

### src/components/chart/
- Chart.tsx (base)
- ChartContainer.tsx (conteneur principal)
- PriceScale.tsx (à créer - axe des prix)
- TimeScale.tsx (à créer - axe temporel)

### src/components/indicators/
- TechnicalIndicators.tsx
- RSI.tsx (à extraire de TechnicalIndicators)
- MACD.tsx (à extraire de TechnicalIndicators)
- Volume.tsx (à extraire de TechnicalIndicators)

### src/components/toolbar/
- ChartToolbar.tsx
- DrawingToolbar.tsx
- TopToolbar.tsx
- ToolbarButton.tsx (à créer - composant réutilisable)

### src/components/widgets/
- TopTickers.tsx
- TickerList.tsx
- MarketInfoPanel.tsx
- SymbolList.tsx

### src/components/layout/
- AppLayout.tsx
- MainHeader.tsx
- Logo.tsx

### Fichiers à Archiver dans old/
- ChartTest.tsx (fichier de test)

## Plan de Restauration des Fonctionnalités

### 1. Restauration des Indicateurs
1. Refactorer TechnicalIndicators.tsx en composants séparés
2. Créer un layout flexible pour les indicateurs
3. Implémenter la synchronisation avec le graphique principal

### 2. Restauration des Axes
1. Créer PriceScale.tsx pour l'axe Y
2. Créer TimeScale.tsx pour l'axe X
3. Intégrer avec ChartContainer.tsx

### 3. Amélioration de la Toolbar
1. Créer ToolbarButton.tsx
2. Refactorer les toolbars existantes
3. Ajouter les fonctionnalités manquantes

## Suivi des Modifications

| Date | Description | Statut |
|------|-------------|--------|
| [DATE] | Création du plan d'action | ✅ |
| [DATE] | Identification des fichiers à déplacer | ✅ |
| [DATE] | Création de la nouvelle structure de dossiers | ✅ |
| [DATE] | Plan de réorganisation des fichiers | ✅ |
| [DATE] | Déplacement des fichiers | ⏳ |
| [DATE] | Restauration des indicateurs | ⏳ | 