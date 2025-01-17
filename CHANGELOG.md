# Changelog

Tous les changements notables de SADIE sont documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-17

### Ajouté
- Collecteur de trades haute performance (4800+ trades/sec)
- Interface web avec Tailwind CSS et Plotly
- Support WebSocket pour données temps réel
- Cache Redis pour optimisation
- Monitoring avec Prometheus/Grafana
- Documentation complète (API, modèles, monitoring)

### Changé
- Réorganisation complète du projet
- Migration vers pyproject.toml pour la gestion des dépendances
- Centralisation des configurations dans /config
- Standardisation de la structure des tests

### Supprimé
- Ancien système de configuration dispersé
- Fichiers de dépendances redondants (requirements.txt, setup.py)

### Sécurité
- Séparation des secrets dans .env
- Configuration sécurisée de Prometheus 