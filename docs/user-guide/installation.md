# Guide d'Installation

Ce guide vous aidera à installer SADIE et à configurer votre environnement de développement.

## Prérequis

- Python 3.10 ou supérieur
- pip (gestionnaire de paquets Python)
- Git
- PostgreSQL 13 ou supérieur
- Docker (optionnel)

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/votre-username/SADIE.git
cd SADIE
```

### 2. Créer un environnement virtuel

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration de la base de données

1. Créer une base de données PostgreSQL :
```sql
CREATE DATABASE sadie_db;
CREATE USER sadie_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE sadie_db TO sadie_user;
```

2. Configurer les variables d'environnement :
```bash
cp .env.example .env
```

3. Éditer le fichier `.env` avec vos informations de connexion.

### 5. Installation avec Docker (Optionnel)

Si vous préférez utiliser Docker :

```bash
docker-compose up -d
```

## Vérification de l'installation

Pour vérifier que tout est correctement installé :

```bash
python -m pytest tests/
```

## Problèmes courants

### Erreur de connexion à la base de données
- Vérifiez que PostgreSQL est en cours d'exécution
- Vérifiez les informations de connexion dans `.env`
- Vérifiez les permissions de l'utilisateur

### Erreur lors de l'installation des dépendances
- Mettez à jour pip : `python -m pip install --upgrade pip`
- Installez les outils de build : `python -m pip install --upgrade setuptools wheel`

## Prochaines étapes

- [Configuration](configuration.md)
- [Guide d'utilisation](usage.md) 