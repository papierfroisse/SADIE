# Guide d'Installation

Ce guide vous aidera à installer et configurer SADIE sur votre système.

## Prérequis

### Système
- Python 3.9 ou supérieur
- Redis 6.0 ou supérieur
- 4GB RAM minimum (8GB recommandé)
- 2 cœurs CPU minimum (4 recommandés)

### Services externes
- Compte sur les exchanges supportés (Binance, etc.)
- Clés API avec permissions de lecture

## Installation

### 1. Cloner le dépôt
```bash
git clone https://github.com/yourusername/SADIE.git
cd SADIE
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur Linux/MacOS
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Installer Redis

#### Windows
1. Télécharger Redis pour Windows depuis [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
2. Installer le fichier .msi
3. Redis devrait démarrer automatiquement comme service Windows

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# CentOS/RHEL
sudo yum install epel-release
sudo yum install redis
sudo systemctl start redis
sudo systemctl enable redis
```

#### MacOS
```bash
brew install redis
brew services start redis
```

### 5. Configuration

1. Copier le fichier de configuration exemple :
```bash
cp config.example.yml config.yml
```

2. Éditer `config.yml` avec vos paramètres :
```yaml
exchanges:
  binance:
    api_key: "votre_api_key"
    api_secret: "votre_api_secret"

redis:
  host: "localhost"
  port: 6379
  db: 0

web:
  host: "0.0.0.0"
  port: 8000
```

## Vérification de l'installation

1. Vérifier Redis :
```bash
redis-cli ping
# Devrait répondre PONG
```

2. Vérifier Python et les dépendances :
```bash
python -c "import redis; redis.Redis().ping()"
# Ne devrait pas afficher d'erreur
```

3. Lancer les tests :
```bash
pytest tests/
```

## Démarrage

1. Lancer l'application :
```bash
python scripts/run_web.py
```

2. Accéder à l'interface web : [http://localhost:8000](http://localhost:8000)

## Résolution des problèmes courants

### Redis ne démarre pas
1. Vérifier le statut du service :
```bash
# Windows
sc query redis
# Linux
systemctl status redis
```

2. Vérifier les logs :
```bash
# Windows
type "C:\Program Files\Redis\logs\redis.log"
# Linux
journalctl -u redis
```

### Erreurs de dépendances Python
1. Vérifier la version de Python :
```bash
python --version
# Doit être 3.9 ou supérieur
```

2. Mettre à jour pip :
```bash
python -m pip install --upgrade pip
```

3. Réinstaller les dépendances :
```bash
pip install -r requirements.txt --force-reinstall
```

## Support

Si vous rencontrez des problèmes :

1. Consultez les [Issues GitHub](https://github.com/yourusername/SADIE/issues)
2. Vérifiez les logs dans `logs/sadie.log`
3. Contactez le support : support@sadie-project.com 