# DevBook - Crypto Tracker

## État actuel du projet

### Fonctionnalités existantes
- ✅ Authentification (Google + Email/Password)
- ✅ Affichage des cryptos depuis Binance et Kraken
- ✅ Graphique en chandeliers basique
- ✅ Sélection des timeframes
- ✅ Mode sombre/clair
- ✅ Interface responsive

### Points à améliorer
1. **Performance**
   - Optimiser les appels API
   - Mettre en place un système de cache
   - Réduire les re-rendus inutiles

2. **Architecture**
   - Implémenter une meilleure gestion d'état (Redux/Zustand)
   - Améliorer la structure des composants
   - Ajouter des tests unitaires et d'intégration

## Roadmap des fonctionnalités

### Phase 1 : Améliorations de base
- [ ] Barre de recherche pour les cryptos
  - Recherche par nom/symbole
  - Filtres avancés
  - Historique des recherches

- [ ] Classement par Market Cap
  - Intégration des données de market cap
  - Tri dynamique
  - Filtres par catégorie

- [ ] Base de données
  - Mise en place de PostgreSQL
  - Schéma pour les données historiques
  - Système de backup

### Phase 2 : Outils de Trading
- [ ] Outils de dessin avancés
  - Lignes de tendance
  - Fibonacci
  - Rectangles et cercles
  - Texte et annotations
  - Sauvegarde des dessins

- [ ] Indicateurs techniques
  - Moyennes mobiles (SMA, EMA)
  - RSI, MACD, Stochastique
  - Bollinger Bands
  - Volume Profile
  - Personnalisation des indicateurs

### Phase 3 : Analyse et Machine Learning
- [ ] Analyse technique automatisée
  - Détection de patterns
  - Signaux de trading
  - Backtesting

- [ ] Intelligence artificielle
  - Prédiction de prix
  - Analyse de sentiment
  - Détection d'anomalies

## Architecture technique

### Base de données
```sql
-- Exemple de schéma
CREATE TABLE candles (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    exchange VARCHAR(20),
    timestamp TIMESTAMP,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume DECIMAL
);

CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20),
    market_cap DECIMAL,
    circulating_supply DECIMAL,
    total_supply DECIMAL,
    timestamp TIMESTAMP
);

CREATE TABLE user_drawings (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    symbol VARCHAR(20),
    drawing_type VARCHAR(20),
    coordinates JSONB,
    style JSONB,
    created_at TIMESTAMP
);
```

### API Endpoints prévus
```typescript
interface ApiEndpoints {
  // Market Data
  '/api/v1/market-data': {
    GET: { params: { symbol?: string } }
  },
  
  // Candles
  '/api/v1/candles': {
    GET: { 
      params: { 
        symbol: string,
        timeframe: string,
        from: string,
        to: string 
      }
    }
  },
  
  // User Drawings
  '/api/v1/drawings': {
    GET: { params: { symbol: string } },
    POST: { body: DrawingData },
    PUT: { params: { id: string }, body: DrawingData },
    DELETE: { params: { id: string } }
  }
}
```

## Tâches prioritaires

1. **Mise en place de la base de données**
   - Installation et configuration de PostgreSQL
   - Création des tables et indexes
   - Mise en place des migrations avec Prisma
   - Tests de performance

2. **Barre de recherche**
   - Composant de recherche avec auto-complétion
   - Filtres avancés
   - Optimisation des performances
   - Tests unitaires

3. **Market Cap et classement**
   - Intégration des données de CoinGecko/Messari
   - Système de cache pour les données
   - Tri et filtres
   - Tests d'intégration

4. **Outils de dessin**
   - Canvas personnalisé
   - Gestion des événements souris/tactile
   - Sauvegarde/chargement des dessins
   - Tests utilisateur

## Standards de code

### Conventions de nommage
```typescript
// Components
MyComponent.tsx
MyComponent.styles.ts
MyComponent.test.ts
MyComponent.types.ts

// Hooks
useMyHook.ts
useMyHook.test.ts

// Services
myService.ts
myService.test.ts
```

### Structure des dossiers
```
src/
├── components/
│   ├── common/
│   ├── chart/
│   ├── search/
│   └── trading/
├── hooks/
├── services/
├── store/
├── utils/
└── types/
```

### Tests
- Jest pour les tests unitaires
- React Testing Library pour les tests de composants
- Cypress pour les tests E2E

## Sécurité
- Rate limiting sur les API
- Validation des données
- Protection contre les injections SQL
- Authentification JWT
- Logs de sécurité

## Performance
- Lazy loading des composants
- Mise en cache des données
- Optimisation des requêtes SQL
- Compression des assets
- CDN pour les ressources statiques

## Monitoring
- Logs d'erreurs
- Métriques de performance
- Alertes en cas de problème
- Analytics utilisateur 