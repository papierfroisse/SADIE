# Configuration SADIE

Ce dossier contient tous les fichiers de configuration du projet SADIE.

## Structure

```
config/
├── .env                # Variables d'environnement actives
├── .env.example        # Template des variables d'environnement
├── prometheus.yml      # Configuration Prometheus
├── config.yml         # Configuration principale de SADIE
└── README.md          # Ce fichier
```

## Configuration Principale (config.yml)

Contient la configuration générale de SADIE :
- Paramètres des collecteurs
- Configuration des exchanges
- Paramètres de performance
- Configuration des logs

## Variables d'Environnement (.env)

### Variables Requises
- `DATABASE_URL` : URL de connexion à la base de données
- `DEBUG` : Mode debug (True/False)
- `LOG_LEVEL` : Niveau de log (INFO, DEBUG, etc.)
- `REDIS_*` : Configuration Redis
- `*_API_KEY` : Clés API des exchanges

### Utilisation
1. Copier `.env.example` vers `.env`
2. Remplir les valeurs requises
3. Ne jamais commiter `.env` dans Git

## Prometheus (prometheus.yml)

Configuration du monitoring Prometheus :
- Intervalle de scraping : 15s
- Endpoints monitorés :
  - SADIE (`:8000/metrics`)
  - Redis Exporter (`:9121`)
  - Node Exporter (`:9100`)
- Configuration des alertes

## Bonnes Pratiques

1. **Sécurité**
   - Ne jamais commiter de secrets
   - Utiliser `.env` pour les données sensibles
   - Vérifier les permissions des fichiers

2. **Maintenance**
   - Documenter tout changement de configuration
   - Mettre à jour `.env.example` si nécessaire
   - Vérifier la cohérence avec la documentation

3. **Déploiement**
   - Valider les configurations avant déploiement
   - Maintenir des configurations par environnement
   - Sauvegarder les configurations critiques 