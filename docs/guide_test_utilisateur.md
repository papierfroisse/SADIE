# Guide de test utilisateur pour sadie

Ce guide vous permettra de tester l'application sadie comme un utilisateur final. Il détaille les différentes étapes depuis l'authentification jusqu'à l'utilisation des fonctionnalités d'analyse technique.

## Prérequis

- Python 3.8+ installé
- Le serveur backend sadie est en cours d'exécution
- Les dépendances requises sont installées (`pip install -r requirements.txt`)

## Lancement du serveur

Si le serveur n'est pas déjà en cours d'exécution, démarrez-le avec la commande suivante :

```bash
cd sadie/web
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible à l'adresse http://localhost:8000

## Flux de test complet

### 1. Authentification (OAuth2)

Vous pouvez vous connecter soit via :

- **L'interface web** : Visitez http://localhost:8000/login dans votre navigateur
  - Utilisateur : `testuser`
  - Mot de passe : `password123`

- **Le script de test** : Exécutez le script automatisé pour tester l'API
  ```bash
  python scripts/test_user_flow.py
  ```

### 2. Configuration du profil

Après vous être connecté, accédez à la page de profil pour :

- Ajouter des clés API d'exchanges (pour des fins de test, vous pouvez utiliser des clés factices)
- Configurer vos préférences (theme, paire de trading par défaut, etc.)
- Définir vos préférences de notifications

### 3. Exploration des données de marché

Accédez à la section "Marché" pour :

- Visualiser les trades récents sur différentes paires
- Voir les chandeliers et données OHLCV pour diverses périodes
- Explorer les différentes paires disponibles

### 4. Analyse technique avancée

Utilisez la page d'analyse technique pour :

- Sélectionner un exchange et une paire de trading
- Choisir une période (1m, 5m, 15m, 1h, 4h, 1d)
- Ajouter des indicateurs techniques (SMA, EMA, etc.)
- Personnaliser les paramètres des indicateurs
- Sauvegarder votre configuration

### 5. Système d'alertes

Dans la section "Alertes", vous pouvez :

- Créer des alertes de prix
- Configurer les conditions de déclenchement
- Définir les méthodes de notification
- Gérer vos alertes existantes

## Test automatisé

Pour tester le flux complet de manière automatisée, utilisez le script `scripts/test_user_flow.py` :

```bash
python scripts/test_user_flow.py --username testuser --password password123
```

Ce script effectue les opérations suivantes :
1. Authentification avec OAuth2
2. Vérification du profil utilisateur
3. Configuration des préférences et des clés API
4. Récupération des données de marché
5. Récupération des données de chandeliers
6. Sauvegarde d'une configuration de graphique
7. Création et gestion d'alertes

## Points à vérifier

Pour s'assurer que l'application fonctionne correctement, vérifiez que :

1. L'authentification fonctionne et un jeton JWT est généré
2. Les données de profil sont correctement sauvegardées
3. Les données de marché s'affichent et se mettent à jour
4. Les indicateurs techniques s'appliquent correctement aux données
5. La configuration des graphiques est sauvegardée entre les sessions
6. Les alertes sont correctement créées et gérées

## Résolution des problèmes courants

### Problèmes d'authentification
- Assurez-vous que les utilisateurs de test existent dans la base de données
- Vérifiez que le service de tokens JWT fonctionne correctement

### Données de marché non disponibles
- Vérifiez la connexion à la base de données TimescaleDB
- Assurez-vous que les collecteurs de données fonctionnent

### Erreurs d'affichage des graphiques
- Vérifiez les erreurs de console dans le navigateur
- Assurez-vous que l'API renvoie des données dans le format attendu

### Problèmes d'indicateurs techniques
- Vérifiez que les bibliothèques de calcul d'indicateurs sont correctement installées
- Assurez-vous que les données sont au bon format pour les calculs

## Feedback et rapports de bugs

Si vous rencontrez des problèmes lors du test, veuillez les signaler en :
1. Créant une issue dans le dépôt GitHub
2. Incluant les étapes pour reproduire le problème
3. Joignant les logs pertinents (console navigateur, logs serveur) 