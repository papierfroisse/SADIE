# Guide de Sécurité pour sadie

Ce document décrit les bonnes pratiques de sécurité pour l'utilisation, le déploiement et le développement du système sadie.

## Sécurisation des Clés API

sadie interagit avec plusieurs plateformes d'échange de cryptomonnaies qui nécessitent des clés API. La sécurisation de ces clés est primordiale.

### Stockage Sécurisé des Clés

1. **Ne jamais stocker les clés API en dur dans le code source**
   - Les clés API ne doivent jamais être codées en dur dans les fichiers source
   - Ne pas stocker les clés dans des fichiers de configuration versionnés

2. **Utiliser des variables d'environnement**
   - Stocker les clés API dans des variables d'environnement
   - Utiliser le fichier `.env` (jamais commité dans Git) pour le développement local
   - Utiliser `.env.example` comme modèle sans valeurs réelles

3. **Gestion des secrets en production**
   - Utiliser un gestionnaire de secrets (Vault, AWS Secrets Manager, etc.)
   - Mettre en place une rotation régulière des clés (au moins tous les 90 jours)
   - Limiter les permissions des clés API au strict nécessaire

### Exemple de Configuration Sécurisée

Dans le fichier `.env`:
```
# Clés API Exchange (ne jamais commiter ce fichier!)
BINANCE_API_KEY=votre_clé_api
BINANCE_API_SECRET=votre_secret
KRAKEN_API_KEY=votre_clé_api
KRAKEN_API_SECRET=votre_secret

# Limitation des permissions (lecture seule recommandée)
API_PERMISSIONS=read-only
```

Dans le code:
```python
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les clés de manière sécurisée
binance_api_key = os.getenv("BINANCE_API_KEY")
binance_api_secret = os.getenv("BINANCE_API_SECRET")

# Vérifier que les clés sont présentes
if not binance_api_key or not binance_api_secret:
    raise EnvironmentError("Clés API Binance manquantes. Veuillez configurer vos variables d'environnement.")
```

## Sécurité des Communications

### TLS/SSL

1. **Toujours utiliser HTTPS**
   - Configurer TLS 1.3 (minimum TLS 1.2) pour toutes les communications API
   - Rediriger automatiquement HTTP vers HTTPS
   - Mettre à jour régulièrement les certificats

2. **Validation des Certificats**
   - Toujours valider les certificats lors des appels API externes
   - Ne jamais désactiver la vérification des certificats (`verify=False`)

### Exemple de Client HTTP Sécurisé

```python
import requests
from urllib3.exceptions import InsecureRequestWarning

# Éviter les avertissements en cas de validation de certificat désactivée
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def secure_api_call(url, headers=None, params=None):
    """Effectue un appel API sécurisé avec validation de certificat."""
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            verify=True,  # Toujours valider le certificat SSL
            timeout=(5, 30)  # Timeout de connexion et de lecture
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.SSLError:
        logger.error("Erreur SSL lors de la connexion à %s", url)
        raise
    except requests.exceptions.RequestException as e:
        logger.error("Erreur lors de l'appel API: %s", str(e))
        raise
```

## Protection de l'API

### Authentification et Autorisation

1. **Authentification Robuste**
   - Utiliser JWT (JSON Web Tokens) avec expiration courte
   - Implémenter l'authentification à deux facteurs pour les utilisateurs privilégiés
   - Stocker les hash de mots de passe avec bcrypt ou Argon2

2. **Autorisation Granulaire**
   - Implémenter un système de rôles (admin, utilisateur, readonly, etc.)
   - Vérifier les autorisations pour chaque endpoint API
   - Appliquer le principe du moindre privilège

### Exemple de Middleware d'Authentification

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Informations d'identification invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user
```

### Protection contre les Attaques Courantes

1. **Limitation de Débit (Rate Limiting)**
   - Implémenter un rate limiting par IP et par utilisateur
   - Protéger les endpoints sensibles (authentification, inscription)
   - Surveillance des tentatives d'attaque par force brute

2. **Prévention des Injections et XSS**
   - Validation et assainissement de toutes les entrées utilisateur
   - Utilisation de paramètres préparés pour les requêtes SQL
   - Configuration des en-têtes de sécurité (CSP, X-XSS-Protection)

3. **Protection CSRF**
   - Utiliser des jetons CSRF pour les formulaires
   - Configurer SameSite=Strict pour les cookies de session

### Exemple d'Implementation de Rate Limiting

```python
from fastapi import FastAPI, Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/sensitive-data")
@limiter.limit("5/minute")
def get_sensitive_data(request: Request):
    # Logique métier protégée par rate limiting
    return {"data": "Données sensibles"}
```

## Surveillance et Journalisation

### Journalisation Sécurisée

1. **Bonnes Pratiques de Journalisation**
   - Ne jamais journaliser d'informations sensibles (mots de passe, jetons, clés API)
   - Utiliser des niveaux de journalisation appropriés
   - Mettre en place une rotation des journaux
   - Protection contre les attaques d'injection dans les journaux

2. **Audits de Sécurité**
   - Journaliser tous les événements liés à l'authentification (succès et échecs)
   - Tracer les modifications de données sensibles
   - Conserver les journaux pour une période appropriée (conformité)

### Exemple de Configuration de Journalisation

```python
import logging
import structlog
from pythonjsonlogger import jsonlogger

# Configuration de la journalisation structurée
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory()
)

# Logger pour les événements de sécurité
security_logger = structlog.get_logger("sadie.security")

def log_security_event(event_type, user_id=None, ip_address=None, success=True, **kwargs):
    """Journal d'événements de sécurité."""
    security_logger.info(
        event_type,
        user_id=user_id,
        ip_address=ip_address,
        success=success,
        **kwargs
    )
```

## Tests de Sécurité

### Analyse de Code Statique

1. **Outils d'Analyse**
   - Utiliser Bandit pour l'analyse de sécurité Python
   - Exécuter des analyses dans le pipeline CI/CD
   - Corriger toutes les vulnérabilités identifiées (sévérité moyenne et haute)

2. **Dépendances Sécurisées**
   - Scanner régulièrement les dépendances (safety, snyk)
   - Mettre à jour les dépendances vulnérables
   - Définir des versions spécifiques dans requirements.txt

### Tests de Pénétration

1. **Méthodologie de Test**
   - Effectuer des tests de pénétration réguliers
   - Suivre la méthodologie OWASP
   - Documenter et corriger les vulnérabilités identifiées

2. **Automatisation**
   - Utiliser des outils automatisés (OWASP ZAP, Burp Suite)
   - Intégrer des tests de sécurité dans le pipeline CI/CD

### Exemple de Configuration Bandit pour CI/CD

```yaml
# .github/workflows/security_scan.yml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install bandit safety
      - name: Run Bandit
        run: bandit -r ./sadie -f json -o bandit-results.json
      - name: Check dependencies
        run: safety check -r requirements.txt
```

## Sécurité en Production

### Déploiement Sécurisé

1. **Environnements Isolés**
   - Séparer les environnements de développement, test et production
   - Limiter l'accès aux environnements de production
   - Utiliser des conteneurs avec le principe de moindre privilège

2. **Gestion des Configurations**
   - Valider les configurations avant déploiement
   - Surveiller les dérives de configuration
   - Automatiser les déploiements pour éviter les erreurs humaines

### Continuité d'Activité

1. **Plan de Reprise d'Activité**
   - Sauvegardes régulières chiffrées
   - Tests de restauration
   - Documentation des procédures d'urgence

2. **Surveillance Proactive**
   - Alertes sur les comportements anormaux
   - Surveillance des ressources système
   - Détection des intrusions

## Conformité et Documentation

1. **Politiques de Sécurité**
   - Document de politique de sécurité
   - Procédures de réponse aux incidents
   - Guide de développement sécurisé

2. **Évaluation des Risques**
   - Identification des actifs et menaces
   - Analyse d'impact
   - Stratégies d'atténuation

## Ressources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Guide de Sécurité Python](https://python-security.readthedocs.io/)
- [Guide de Bonnes Pratiques pour les API REST](https://github.com/shieldfy/API-Security-Checklist)
- [Principes de Sécurité des Applications Cloud](https://www.ncsc.gov.uk/collection/cloud-security) 