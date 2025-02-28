# SADIE - Suite d'outils d'optimisation

Ce document présente l'ensemble des outils d'optimisation développés pour la plateforme SADIE. Ces scripts PowerShell sont conçus pour améliorer les performances, optimiser la configuration, diagnostiquer les problèmes et faciliter la maintenance du système SADIE.

## Table des matières

1. [Interface principale](#interface-principale)
2. [Scripts de diagnostic](#scripts-de-diagnostic)
3. [Scripts d'optimisation du frontend](#scripts-doptimisation-du-frontend)
4. [Scripts de gestion des conteneurs](#scripts-de-gestion-des-conteneurs)
5. [Scripts d'optimisation réseau](#scripts-doptimisation-réseau)
6. [Installation et prérequis](#installation-et-prérequis)
7. [Dépannage courant](#dépannage-courant)

## Interface principale

### sadie-optimize.ps1

Script principal qui sert d'interface utilisateur pour accéder à toutes les fonctionnalités d'optimisation et de diagnostic. Il propose un menu interactif organisé en sections :

- Diagnostic du système
- Optimisation du frontend
- Optimisation de la configuration réseau
- Gestion des conteneurs
- Maintenance du système

**Utilisation :**
```powershell
./sadie-optimize.ps1
```

## Scripts de diagnostic

### diagnostic-complet.ps1

Analyse approfondie de l'infrastructure SADIE avec génération d'un rapport détaillé. Le script vérifie :

- Configuration système (OS, PowerShell, utilisateur)
- Installations Docker (version, ressources)
- Conteneurs, images et réseaux SADIE
- Espace disque et validité des fichiers de configuration
- Connexions réseau et disponibilité des ports
- Performances CPU et mémoire

**Utilisation :**
```powershell
./diagnostic-complet.ps1
```

**Sortie :**
Un rapport détaillé est généré dans un dossier `sadie-reports` avec horodatage.

## Scripts d'optimisation du frontend

### optimize-package-json.ps1

Optimise le fichier `package.json` du frontend en :
- Ajoutant la dépendance `cross-env` pour une meilleure gestion des variables d'environnement
- Intégrant des scripts de démarrage optimisés qui limitent la consommation mémoire
- Ajoutant des configurations pour désactiver les sourcemaps en production

**Utilisation :**
```powershell
./optimize-package-json.ps1
```

### optimize-dockerfile.ps1

Crée ou optimise le Dockerfile du frontend avec :
- Une image de base alpine plus légère
- Une meilleure organisation des couches pour optimiser le cache Docker
- Des variables d'environnement pour contrôler la mémoire et les performances
- Une configuration optimisée pour la production

**Utilisation :**
```powershell
./optimize-dockerfile.ps1
```

## Scripts de gestion des conteneurs

### restart-containers.ps1

Fournit une interface pour gérer les conteneurs Docker SADIE :
- Redémarrage du frontend uniquement
- Redémarrage de tous les conteneurs SADIE
- Vérification de l'état et affichage des logs
- Application des optimisations lors du redémarrage

**Utilisation :**
```powershell
./restart-containers.ps1
```

### restart-sadie.ps1

Script spécialisé pour redémarrer uniquement le frontend de SADIE avec vérification du succès du démarrage :
- Arrête et supprime le conteneur existant
- Reconstruit l'image si nécessaire
- Démarre le conteneur avec les optimisations
- Vérifie les logs pour confirmer le bon démarrage

**Utilisation :**
```powershell
./restart-sadie.ps1
```

## Scripts d'optimisation réseau

### optimize-network.ps1

Optimise la configuration réseau Docker pour SADIE :
- Création ou mise à jour du réseau `sadie-network`
- Optimisation des paramètres MTU et DNS
- Modification du docker-compose.yml pour utiliser le réseau optimisé
- Configuration des politiques de redémarrage pour une meilleure résilience

**Utilisation :**
```powershell
./optimize-network.ps1
```

## Installation et prérequis

### Prérequis
- PowerShell 5.1 ou supérieur
- Docker Desktop
- Docker Compose
- Node.js (pour les optimisations locales)

### Installation

1. Clonez ou téléchargez tous les scripts dans le répertoire racine de votre projet SADIE
2. Assurez-vous que les scripts ont les permissions d'exécution :
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
3. Lancez l'interface principale :
```powershell
./sadie-optimize.ps1
```

## Dépannage courant

### Le frontend ne démarre pas après optimisation

Vérifiez les logs Docker avec :
```powershell
docker logs sadie-frontend
```

Causes possibles :
- Mémoire insuffisante allouée à Docker Desktop
- Conflits de port (3000)
- Problèmes avec les nouvelles dépendances

### Erreurs de réseau Docker

Si vous rencontrez des problèmes de connexion entre conteneurs :
1. Exécutez le diagnostic complet
2. Vérifiez que `sadie-network` est correctement créé
3. Recréez le réseau avec `optimize-network.ps1`

### Performances toujours lentes après optimisation

1. Vérifiez les ressources allouées à Docker Desktop (augmentez si nécessaire)
2. Exécutez le nettoyage des images et conteneurs inutilisés
3. Considérez l'augmentation du NODE_OPTIONS dans le script de démarrage

---

© 2024 SADIE Optimization Tools 