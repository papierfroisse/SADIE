# API Reference - Analysis

## Indicateurs Techniques

::: sadie.analysis.indicators.TechnicalIndicators
    handler: python
    selection:
      members:
        - __init__
        - bollinger_bands
        - macd
        - stochastic
        - rsi
        - atr
        - volume_profile
        - fibonacci_levels
        - detect_divergences

## Patterns Harmoniques

### Types de Patterns

::: sadie.analysis.harmonic_patterns.PatternType
    handler: python

### Types de Tendance

::: sadie.analysis.harmonic_patterns.TrendType
    handler: python

### Pattern Harmonique

::: sadie.analysis.harmonic_patterns.HarmonicPattern
    handler: python

### Analyseur de Patterns

::: sadie.analysis.harmonic_patterns.HarmonicAnalyzer
    handler: python
    selection:
      members:
        - __init__
        - identify_patterns
        - _find_swing_points
        - _calculate_ratio
        - _check_pattern_ratios

## Visualisation

::: sadie.analysis.visualization.ChartVisualizer
    handler: python
    selection:
      members:
        - __init__
        - create_chart 