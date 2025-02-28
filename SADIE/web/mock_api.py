from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime, timedelta
import json
import random
import os
import uvicorn
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel

# Création de l'application FastAPI
app = FastAPI(
    title="SADIE Mock API", 
    description="API de test pour le dashboard SADIE",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")

# Modèles de données
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None

class RegisterResponse(BaseModel):
    success: bool
    message: str
    user: Optional[User] = None
    error: Optional[str] = None

# Utilisateurs de test
users_db = {
    "testuser": {
        "username": "testuser",
        "full_name": "Test User",
        "email": "test@example.com",
        "hashed_password": "password123",
        "disabled": False,
    }
}

# Fonction d'authentification
def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user:
        return False
    if user["hashed_password"] != password:
        return False
    return user

# Création d'un utilisateur
def create_user(user_data: UserRegister):
    if user_data.username in users_db:
        return False, "Nom d'utilisateur déjà utilisé"
    
    users_db[user_data.username] = {
        "username": user_data.username,
        "full_name": user_data.full_name,
        "email": user_data.email,
        "hashed_password": user_data.password,  # Dans un système réel, le mot de passe serait haché
        "disabled": False
    }
    return True, "Utilisateur créé avec succès"

# Création du token
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = json.dumps(to_encode)  # Simplifié pour le mock
    return encoded_jwt

# Routes API
@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=User)
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = json.loads(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = users_db.get(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/api/register", response_model=RegisterResponse)
async def register_user(user_data: UserRegister):
    # Vérifier si l'utilisateur existe déjà
    if user_data.username in users_db:
        return {
            "success": False,
            "message": "Échec de l'inscription",
            "error": "Nom d'utilisateur déjà utilisé"
        }
    
    # Créer l'utilisateur
    success, message = create_user(user_data)
    
    if success:
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            disabled=False
        )
        return {
            "success": True,
            "message": "Inscription réussie",
            "user": user
        }
    else:
        return {
            "success": False,
            "message": "Échec de l'inscription",
            "error": message
        }

# Données simulées pour les métriques
@app.get("/api/metrics/collectors")
async def get_collectors_metrics(
    collector_name: Optional[str] = None,
    exchange: Optional[str] = None,
    metric_type: Optional[str] = None,
    symbol: Optional[str] = None,
    timeframe: Optional[str] = "1h",
    aggregation: Optional[str] = "avg",
    token: str = Depends(oauth2_scheme)
):
    # Vérification simplifiée du token
    try:
        payload = json.loads(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Génération de données simulées
    now = datetime.now()
    metrics = {}
    
    # Créer des points de données pour les dernières 24 heures
    for i in range(24):
        timestamp = (now - timedelta(hours=i)).isoformat()
        
        # Données différentes selon le type de métrique
        if metric_type == "throughput":
            metrics[timestamp] = {
                "binance": random.uniform(80, 150),
                "kraken": random.uniform(60, 120)
            }
        elif metric_type == "latency":
            metrics[timestamp] = {
                "binance": random.uniform(20, 80),
                "kraken": random.uniform(30, 100)
            }
        elif metric_type == "error_rate":
            metrics[timestamp] = {
                "binance": random.uniform(0, 2),
                "kraken": random.uniform(0, 3)
            }
        elif metric_type == "health":
            metrics[timestamp] = {
                "binance": random.uniform(90, 100),
                "kraken": random.uniform(85, 100)
            }
        else:
            # Données par défaut
            metrics[timestamp] = {
                "binance": random.uniform(0, 100),
                "kraken": random.uniform(0, 100)
            }
    
    return {
        "success": True,
        "metrics": metrics
    }

# Page d'accueil de l'API
@app.get("/", response_class=HTMLResponse)
async def get_api_home():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SADIE API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #2980b9;
                margin-top: 30px;
            }
            .endpoint {
                background-color: #f8f9fa;
                border-left: 4px solid #3498db;
                padding: 10px 15px;
                margin: 15px 0;
                border-radius: 0 4px 4px 0;
            }
            .method {
                font-weight: bold;
                display: inline-block;
                min-width: 80px;
            }
            .get { color: #27ae60; }
            .post { color: #e74c3c; }
            .put { color: #f39c12; }
            .delete { color: #c0392b; }
            .path {
                font-family: monospace;
                background-color: #ecf0f1;
                padding: 2px 5px;
                border-radius: 3px;
            }
            .description {
                margin-top: 5px;
                color: #555;
            }
            .links {
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }
            a {
                color: #3498db;
                text-decoration: none;
                margin-right: 15px;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>SADIE API - Documentation</h1>
        <p>
            Bienvenue sur l'API du système SADIE (Système d'Analyse et de Détection d'Indicateurs pour l'Échange).
            Cette API permet d'accéder aux fonctionnalités de collecte, d'analyse et de visualisation des données de marché.
        </p>
        
        <h2>Authentification</h2>
        <div class="endpoint">
            <div><span class="method post">POST</span> <span class="path">/api/token</span></div>
            <div class="description">Obtenir un token d'authentification. Utilisez le nom d'utilisateur "testuser" et le mot de passe "password123" pour les tests.</div>
        </div>
        
        <h2>Informations Utilisateur</h2>
        <div class="endpoint">
            <div><span class="method get">GET</span> <span class="path">/api/users/me</span></div>
            <div class="description">Obtenir les informations de l'utilisateur actuellement authentifié.</div>
        </div>
        
        <h2>Métriques</h2>
        <div class="endpoint">
            <div><span class="method get">GET</span> <span class="path">/api/metrics/collectors</span></div>
            <div class="description">Obtenir les métriques des collecteurs de données. Paramètres: collector_name, exchange, metric_type, symbol, timeframe, aggregation.</div>
        </div>
        
        <div class="endpoint">
            <div><span class="method get">GET</span> <span class="path">/api/metrics/exchanges</span></div>
            <div class="description">Obtenir les métriques des échanges. Paramètres: exchange, metric_type, symbol, timeframe, aggregation.</div>
        </div>
        
        <h2>Données de Marché</h2>
        <div class="endpoint">
            <div><span class="method get">GET</span> <span class="path">/api/data/ohlcv</span></div>
            <div class="description">Obtenir les données OHLCV (Open, High, Low, Close, Volume). Paramètres: symbol, exchange, timeframe, limit.</div>
        </div>
        
        <div class="endpoint">
            <div><span class="method get">GET</span> <span class="path">/api/data/trades</span></div>
            <div class="description">Obtenir les dernières transactions. Paramètres: symbol, exchange, limit.</div>
        </div>
        
        <div class="links">
            <a href="/docs">Documentation Swagger</a>
            <a href="/redoc">Documentation ReDoc</a>
            <a href="https://github.com/sadie-project/sadie">GitHub</a>
        </div>
    </body>
    </html>
    """
    return html_content

# Endpoint pour lister tous les endpoints disponibles
@app.get("/api/endpoints", response_class=JSONResponse)
async def get_endpoints():
    endpoints = [
        {
            "path": "/api/token",
            "method": "POST",
            "description": "Authentification et obtention d'un token JWT",
            "requires_auth": False
        },
        {
            "path": "/api/register",
            "method": "POST",
            "description": "Inscription d'un nouvel utilisateur",
            "requires_auth": False
        },
        {
            "path": "/api/users/me",
            "method": "GET",
            "description": "Informations sur l'utilisateur connecté",
            "requires_auth": True
        },
        {
            "path": "/api/metrics/collectors",
            "method": "GET",
            "description": "Métriques des collecteurs de données",
            "requires_auth": True
        },
        {
            "path": "/api/metrics/exchanges",
            "method": "GET",
            "description": "Métriques des échanges",
            "requires_auth": True
        },
        {
            "path": "/api/data/ohlcv",
            "method": "GET",
            "description": "Données OHLCV (Open, High, Low, Close, Volume)",
            "requires_auth": True
        },
        {
            "path": "/api/data/trades",
            "method": "GET",
            "description": "Dernières transactions",
            "requires_auth": True
        },
        {
            "path": "/api/endpoints",
            "method": "GET",
            "description": "Liste des endpoints disponibles",
            "requires_auth": False
        }
    ]
    
    return {"endpoints": endpoints, "count": len(endpoints)}

# Démarrer le serveur
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 