# SADIE - Système d'Analyse de Données et d'Intelligence Économique

## Description
SADIE est un système d'analyse de données financières et économiques qui collecte, traite et analyse des données en temps réel à partir de diverses sources.

## Prérequis
- Python 3.9+
- PostgreSQL 14+
- TimescaleDB 2.10+

## Installation de PostgreSQL et TimescaleDB

### Windows
1. Téléchargez et installez PostgreSQL depuis [le site officiel](https://www.postgresql.org/download/windows/)
2. Téléchargez et installez TimescaleDB depuis [le site officiel](https://docs.timescale.com/install/latest/self-hosted/installation-windows/)

### Linux (Ubuntu/Debian)
```bash
# Ajout du dépôt TimescaleDB
sudo sh -c 'echo "deb https://packagecloud.io/timescale/timescaledb/ubuntu/ $(lsb_release -c -s) main" > /etc/apt/sources.list.d/timescaledb.list'
wget --quiet -O - https://packagecloud.io/timescale/timescaledb/gpgkey | sudo apt-key add -
sudo apt update

# Installation de PostgreSQL et TimescaleDB
sudo apt install -y postgresql-14 timescaledb-2-postgresql-14

# Configuration de TimescaleDB
sudo timescaledb-tune
sudo systemctl restart postgresql
```

### macOS
```bash
# Installation via Homebrew
brew tap timescale/tap
brew install timescaledb
timescaledb-tune
brew services restart postgresql
```

## Configuration de la base de données
1. Créez un fichier `.env` à partir du modèle `.env.example`
2. Exécutez le script de création de la base de données :
```bash
psql -U postgres -f scripts/create_database.sql
```

## Installation des dépendances Python
```bash
pip install -r requirements.txt
```

## Initialisation de la base de données
```bash
alembic upgrade head
```

## Tests
```bash
pytest
```

## Documentation
La documentation complète est disponible dans le dossier `docs/`. 