"""Module d'authentification et d'autorisation pour l'API."""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration de la sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "d1ff1cult_s3cr3t_k3y_f0r_d3v3l0pm3nt")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexte de hachage pour les mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Endpoint d'authentification
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/token",
    scopes={
        "read:data": "Lire les données de marché et les métriques",
        "write:data": "Configurer et modifier les collecteurs",
        "admin": "Accès administrateur complet"
    }
)

# Modèles de données pour l'authentification
class Token(BaseModel):
    """Modèle pour un token d'accès."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Modèle pour les données contenues dans un token."""
    username: Optional[str] = None
    scopes: List[str] = []
    exp: Optional[datetime] = None

class User(BaseModel):
    """Modèle pour un utilisateur."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    scopes: List[str] = []

class UserInDB(User):
    """Modèle pour un utilisateur en base de données (avec hachage mot de passe)."""
    hashed_password: str

# Base de données simulée d'utilisateurs (à remplacer par une vraie BD en production)
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Administrateur",
        "email": "admin@example.com",
        "hashed_password": pwd_context.hash("adminpassword"),
        "disabled": False,
        "scopes": ["read:data", "write:data", "admin"]
    },
    "analyst": {
        "username": "analyst",
        "full_name": "Analyste",
        "email": "analyst@example.com",
        "hashed_password": pwd_context.hash("analystpassword"),
        "disabled": False,
        "scopes": ["read:data"]
    },
    "operator": {
        "username": "operator",
        "full_name": "Opérateur",
        "email": "operator@example.com",
        "hashed_password": pwd_context.hash("operatorpassword"),
        "disabled": False,
        "scopes": ["read:data", "write:data"]
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe correspond à un hachage."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Génère un hachage à partir d'un mot de passe."""
    return pwd_context.hash(password)

def get_user(db: Dict, username: str) -> Optional[UserInDB]:
    """Récupère un utilisateur par son nom d'utilisateur."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(db: Dict, username: str, password: str) -> Union[UserInDB, bool]:
    """Authentifie un utilisateur avec son nom d'utilisateur et mot de passe."""
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(
    data: Dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Crée un token JWT avec les données spécifiées."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    """Récupère l'utilisateur actuel à partir du token JWT."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Impossible de valider les identifiants",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except (JWTError, ValidationError):
        logger.exception("Erreur lors de la validation du token")
        raise credentials_exception
    
    user = get_user(fake_users_db, token_data.username)
    if user is None:
        raise credentials_exception
    
    # Vérification des scopes requis
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            logger.warning(f"Utilisateur {user.username} sans le scope requis: {scope}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissions insuffisantes. Scope requis: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Vérifie que l'utilisateur actuel est actif."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Utilisateur inactif")
    return current_user

# Dépendances pour les différents niveaux d'accès
async def get_read_data_user(
    security_scopes: SecurityScopes = SecurityScopes(["read:data"]),
    current_user: User = Depends(get_current_user)
) -> User:
    """Dépendance pour l'accès en lecture."""
    return current_user

async def get_write_data_user(
    security_scopes: SecurityScopes = SecurityScopes(["write:data"]),
    current_user: User = Depends(get_current_user)
) -> User:
    """Dépendance pour l'accès en écriture."""
    return current_user

async def get_admin_user(
    security_scopes: SecurityScopes = SecurityScopes(["admin"]),
    current_user: User = Depends(get_current_user)
) -> User:
    """Dépendance pour l'accès administrateur."""
    return current_user 