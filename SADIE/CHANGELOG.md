# Changelog

## [0.2.0] - En cours

### Ajouts
- Système de collecte de données avancé
  - Collecteur tick-by-tick avec support WebSocket
  - Collecteur de transactions en temps réel
  - Analyseur d'order book avec métriques avancées
  - Tests de performance et résilience
- Système de stockage optimisé
  - Compression intelligente multi-algorithmes (LZ4, ZLIB, SNAPPY)
  - Profils de compression adaptés par type de données
  - Partitionnement adaptatif (temps/symbole/hybride)
  - Gestion des données chaudes/tièdes/froides
  - Tests unitaires complets

### Améliorations
- Optimisation des performances des collecteurs
- Meilleure gestion de la mémoire
- Support WebSocket amélioré
- Documentation technique détaillée
- Métriques de performance

### Corrections
- Gestion des erreurs WebSocket
- Fuites mémoire dans les collecteurs
- Problèmes de concurrence

## [0.2.1] - En cours

### Ajouts
- Collecteurs de données alternatives
  - Twitter : analyse de sentiment en temps réel
  - Reddit : analyse communautaire et engagement
  - NewsAPI : actualités et analyse multilingue
- Métriques avancées
  - Analyse de sentiment (polarité/subjectivité)
  - Engagement communautaire
  - Diversité des sources
  - Tests unitaires complets

### Améliorations
- Support multilingue
- Performance des collecteurs
- Documentation utilisateur
- Gestion de la mémoire

## [0.1.2] - 2024-01-15

### Ajouts
- Support des order books L2/L3
- Tests unitaires pour OrderBookCollector
- Tests de performance
- Documentation technique

### Améliorations
- Refactoring des collecteurs
- Optimisation des performances
- Documentation mise à jour

### Corrections
- Bugs WebSocket
- Problèmes de mémoire
- Erreurs de parsing JSON 