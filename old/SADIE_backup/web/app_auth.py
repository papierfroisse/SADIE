"""Application FastAPI avec authentification et autorisation."""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .auth import (
    authenticate_user, create_access_token, get_current_active_user,
    get_read_data_user, get_write_data_user, get_admin_user,
    Token, User, fake_users_db, ACCESS_TOKEN_EXPIRE_MINUTES
)

# Configuration du logging
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="SADIE API",
    description="API pour le Système d'Analyse et de Détection d'Indicateurs pour l'Échange",
    version="0.2.1",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint d'authentification pour obtenir un token
@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint pour l'authentification et l'obtention d'un token JWT."""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint pour tester l'authentification
@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Endpoint pour récupérer les informations de l'utilisateur connecté."""
    return current_user

# API publique (sans authentification)
@app.get("/api/healthcheck")
async def health_check():
    """Endpoint public pour vérifier la santé de l'API."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.2.1"
    }

# API protégée pour la lecture de données
@app.get("/api/market-data", tags=["data"])
async def get_market_data(current_user: User = Depends(get_read_data_user)):
    """Endpoint protégé pour lire les données de marché (lecture seule)."""
    return {
        "data": "Données de marché simulées",
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user.username
    }

# API protégée pour la configuration
@app.post("/api/configuration", tags=["data"])
async def update_configuration(
    config: Dict[str, Any],
    current_user: User = Depends(get_write_data_user)
):
    """Endpoint protégé pour mettre à jour la configuration (écriture)."""
    return {
        "status": "Configuration mise à jour",
        "config": config,
        "timestamp": datetime.utcnow().isoformat(),
        "user": current_user.username
    }

# API d'administration
@app.get("/api/users", tags=["admin"])
async def list_users(current_user: User = Depends(get_admin_user)):
    """Endpoint protégé pour lister les utilisateurs (admin uniquement)."""
    return {
        "users": list(fake_users_db.keys()),
        "count": len(fake_users_db),
        "timestamp": datetime.utcnow().isoformat(),
        "admin": current_user.username
    }

# WebSocket sécurisé
class AuthWebSocketManager:
    """Gestionnaire de WebSockets avec authentification."""
    
    def __init__(self):
        """Initialisation du gestionnaire."""
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def authenticate(self, websocket: WebSocket, token: str) -> Optional[User]:
        """Authentifie une connexion WebSocket via un token JWT."""
        try:
            # Utilisation de la fonction d'authentification existante
            # Cette implémentation est simplifiée et devrait être améliorée
            from jwt import PyJWTError
            import jwt
            from .auth import SECRET_KEY, ALGORITHM
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            
            if username and username in fake_users_db:
                return User(**{k: v for k, v in fake_users_db[username].items() 
                              if k != "hashed_password"})
            return None
        except (PyJWTError, Exception):
            return None
    
    async def connect(self, websocket: WebSocket, token: str) -> Optional[User]:
        """Connecte un client WebSocket après authentification."""
        user = await self.authenticate(websocket, token)
        
        if not user:
            await websocket.close(code=1008)  # Policy Violation
            return None
        
        await websocket.accept()
        self.active_connections[user.username] = websocket
        return user
    
    async def disconnect(self, username: str):
        """Déconnecte un client WebSocket."""
        if username in self.active_connections:
            del self.active_connections[username]
    
    async def send_message(self, username: str, message: str):
        """Envoie un message à un client spécifique."""
        if username in self.active_connections:
            await self.active_connections[username].send_text(message)
    
    async def broadcast(self, message: str):
        """Diffuse un message à tous les clients connectés."""
        for connection in self.active_connections.values():
            await connection.send_text(message)

# Instance du gestionnaire WebSocket
websocket_manager = AuthWebSocketManager()

@app.websocket("/ws/secure")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint WebSocket sécurisé."""
    # Attente du message d'authentification initial
    await websocket.accept()
    
    try:
        auth_message = await websocket.receive_json()
        token = auth_message.get("token")
        
        if not token:
            await websocket.send_json({"error": "Token d'authentification manquant"})
            await websocket.close(code=1008)
            return
        
        # Authentification
        user = await websocket_manager.authenticate(websocket, token)
        
        if not user:
            await websocket.send_json({"error": "Authentification échouée"})
            await websocket.close(code=1008)
            return
        
        # Enregistrement de la connexion
        websocket_manager.active_connections[user.username] = websocket
        
        # Confirmation de connexion
        await websocket.send_json({
            "status": "connected",
            "user": user.username,
            "scopes": user.scopes
        })
        
        # Boucle de traitement des messages
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message reçu: {data}")
            
    except WebSocketDisconnect:
        if user and user.username in websocket_manager.active_connections:
            await websocket_manager.disconnect(user.username)
    except Exception as e:
        logger.error(f"Erreur WebSocket: {str(e)}")
        if websocket.client_state.CONNECTED:
            await websocket.close(code=1011)  # Server Error

# Configuration du dossier static (après les routes API)
static_dir = os.path.join(os.path.dirname(__file__), "static", "build")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    logger.warning(f"Dossier static non trouvé: {static_dir}") 