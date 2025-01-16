# SADIE - Système Avancé d'Intelligence et d'Exploration des Données

## Description
SADIE est une bibliothèque Python pour l'analyse avancée des marchés financiers, combinant des techniques d'analyse statistique, de détection de patterns et d'apprentissage automatique.

## Fonctionnalités Principales

### Analyse Statistique
- Analyse complète de la distribution des prix
- Calcul des rendements et de la volatilité
- Détection des valeurs aberrantes
- Métriques de risque (VaR, CVaR)
- Ratios de performance (Sharpe, Sortino)
- Analyse des cycles de marché
- Tests de normalité et stationnarité

### Analyse des Cycles et Patterns
- Décomposition des cycles de marché
- Détection automatique des patterns (ABC, ABCD, Head & Shoulders)
- Analyse des divergences prix-volume
- Clustering des cycles similaires
- Analyse des corrélations entre cycles
- Prévision des caractéristiques du prochain cycle
- Métriques de qualité des cycles

### Visualisation Interactive
- Graphiques multi-panneaux
- Marquage des patterns et zones de cycle
- Indicateurs de changement de régime
- Métriques glissantes
- Personnalisation des styles et couleurs

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Analyse Statistique
```python
from SADIE.analysis.statistical import StatisticalAnalyzer

analyzer = StatisticalAnalyzer(data)
stats = analyzer.analyze()
print(stats.summary())
```

### Analyse des Cycles
```python
from SADIE.analysis.pattern_cycles import CyclePatternAnalyzer

analyzer = CyclePatternAnalyzer(data)
patterns = analyzer.identify_patterns()
divergences = analyzer.detect_divergences()
clusters = analyzer.cluster_cycles()
```

### Visualisation
```python
from SADIE.visualization import plot_patterns

plot_patterns(data, analyzer)
```

## Structure du Projet
```
SADIE/
├── analysis/
│   ├── statistical.py    # Analyse statistique
│   ├── technical.py      # Indicateurs techniques
│   ├── market_cycles.py  # Analyse des cycles
│   └── pattern_cycles.py # Détection des patterns
├── core/
│   ├── models/          # Modèles de données
│   └── utils/           # Utilitaires
└── visualization/       # Outils de visualisation
```

## Contribution
Les contributions sont les bienvenues ! Consultez notre guide de contribution pour plus de détails.

## Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails. 