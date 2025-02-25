# Fonctionnalités Avancées du Système de Métriques

Ce document décrit les fonctionnalités avancées du système de métriques de SADIE, incluant les alertes automatiques, les tableaux de bord personnalisables, l'exportation des données et l'intégration avec Prometheus/Grafana.

## Table des matières
1. [Alertes Automatiques](#alertes-automatiques)
2. [Tableaux de Bord Personnalisables](#tableaux-de-bord-personnalisables)
3. [Exportation des Données](#exportation-des-données)
4. [Intégration Prometheus/Grafana](#intégration-prometheusgrafana)

## Alertes Automatiques

Le système d'alertes automatiques permet de surveiller les métriques de performance des collecteurs de données et de déclencher des notifications lorsque certaines conditions sont remplies.

### Création d'une alerte

Pour créer une alerte basée sur les performances :

1. Accédez à l'interface d'alertes (/alerts)
2. Cliquez sur "Créer une alerte de performance"
3. Configurez les paramètres suivants :
   - Nom de l'alerte
   - Collecteur(s) à surveiller
   - Exchange(s) à surveiller
   - Symbole(s) à surveiller
   - Seuils :
     - Type de métrique (débit, latence, taux d'erreur, santé)
     - Opérateur de comparaison (>, <, =, >=, <=)
     - Valeur seuil
     - Durée (pendant combien de temps la condition doit être maintenue)
     - Période de refroidissement (délai avant qu'une alerte puisse être redéclenchée)
   - Canaux de notification

### Gestion des alertes

Les alertes peuvent être activées, désactivées, modifiées ou supprimées à tout moment via l'interface d'administration.

### API REST pour les alertes

Les alertes peuvent également être gérées via l'API REST :

- `POST /api/alerts` : Créer une nouvelle alerte
- `GET /api/alerts` : Obtenir toutes les alertes
- `GET /api/alerts/{alert_id}` : Obtenir une alerte spécifique
- `PATCH /api/alerts/{alert_id}` : Mettre à jour une alerte
- `DELETE /api/alerts/{alert_id}` : Supprimer une alerte
- `GET /api/alerts/history` : Obtenir l'historique des alertes déclenchées

## Tableaux de Bord Personnalisables

Les tableaux de bord personnalisables permettent de visualiser les métriques selon vos préférences, en créant des widgets pour différents types de visualisations.

### Création d'un tableau de bord

1. Accédez à l'interface des tableaux de bord (/dashboard)
2. Cliquez sur "Créer un tableau de bord"
3. Donnez un nom au tableau de bord
4. Cliquez sur "Ajouter un widget" pour commencer à ajouter des visualisations

### Types de widgets disponibles

- **Graphique linéaire** : Affiche l'évolution d'une métrique dans le temps
- **Graphique à barres** : Compare les valeurs de métriques entre collecteurs ou exchanges
- **Graphique circulaire** : Visualise la répartition des métriques
- **Tableau** : Affiche les données de métriques sous forme de tableau
- **Valeur unique** : Affiche une seule valeur avec une tendance

### Personnalisation des widgets

Chaque widget peut être personnalisé :
- Titre
- Type de métrique à afficher
- Collecteurs, exchanges et symboles à inclure
- Taille (petit, moyen, grand)
- Période de temps (5m, 15m, 1h, 6h, 24h, 7d)

### Gestion des tableaux de bord

Vous pouvez créer plusieurs tableaux de bord et basculer entre eux. Chaque tableau de bord peut être :
- Modifié
- Dupliqué
- Supprimé
- Défini comme tableau de bord par défaut

## Exportation des Données

Le système permet d'exporter les données de métriques pour une analyse externe.

### Exportation via l'interface utilisateur

À partir de n'importe quel tableau de bord :
1. Cliquez sur le bouton "Exporter" dans le coin supérieur droit
2. Choisissez le format d'exportation (JSON ou CSV)
3. Sélectionnez les filtres souhaités (collecteurs, exchanges, symboles, période)
4. Cliquez sur "Exporter"

### API REST pour l'exportation

Les données de métriques peuvent également être exportées via l'API REST :

- `GET /api/export/metrics/json` : Exporter les métriques au format JSON
- `GET /api/export/metrics/csv` : Exporter les métriques au format CSV

Paramètres de requête :
- `collector_name` : Filtrer par nom de collecteur
- `exchange` : Filtrer par exchange
- `metric_type` : Filtrer par type de métrique
- `symbol` : Filtrer par symbole
- `timeframe` : Fenêtre temporelle (5m, 15m, 1h, 6h, 24h, 7d)

## Intégration Prometheus/Grafana

SADIE peut exposer ses métriques dans un format compatible avec Prometheus, ce qui permet une intégration avec des outils de surveillance comme Grafana.

### Configuration de l'exportateur Prometheus

1. Accédez à l'interface d'administration (/settings/prometheus)
2. Activez l'exportateur Prometheus
3. Configurez le port sur lequel les métriques seront exposées (par défaut : 9090)
4. Cliquez sur "Enregistrer"

### Métriques exposées

Les métriques suivantes sont exposées au format Prometheus :

- `sadie_collector_throughput` : Débit du collecteur en messages par seconde
- `sadie_collector_latency` : Latence du collecteur en millisecondes
- `sadie_collector_error_rate` : Taux d'erreurs du collecteur en pourcentage
- `sadie_collector_health` : Santé du collecteur (1: sain, 0: défaillant)
- `sadie_collector_total_messages` : Nombre total de messages traités par le collecteur
- `sadie_collector_total_errors` : Nombre total d'erreurs rencontrées par le collecteur

Chaque métrique est étiquetée avec :
- `collector_name` : Nom du collecteur
- `exchange` : Exchange concerné
- `symbol` : Symbole concerné

### Configuration de Prometheus

Pour que Prometheus puisse scraper les métriques SADIE, ajoutez la configuration suivante à votre fichier `prometheus.yml` :

```yaml
scrape_configs:
  - job_name: 'sadie'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 15s
```

### Création d'un tableau de bord Grafana

1. Ajoutez votre instance Prometheus comme source de données dans Grafana
2. Créez un nouveau tableau de bord ou importez l'exemple fourni dans l'interface d'administration
3. Utilisez les métriques SADIE dans vos panneaux Grafana

### API REST pour Prometheus

- `POST /api/prometheus/config` : Configurer l'exportateur Prometheus
- `GET /api/prometheus/status` : Obtenir le statut de l'exportateur Prometheus 