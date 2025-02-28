from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
import json
import random
import os
import uvicorn
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel

# Création de l'application FastAPI
app = FastAPI(title="SADIE Mock API", description="API de test pour le dashboard SADIE")

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

# Démarrer le serveur
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 