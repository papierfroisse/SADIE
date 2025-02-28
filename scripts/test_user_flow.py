#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test du flux utilisateur complet pour l'application SADIE.

Ce script simule les interactions d'un utilisateur avec l'application :
1. Authentification avec OAuth2
2. Configuration du profil utilisateur
3. Accès aux données de marché
4. Utilisation des fonctionnalités d'analyse technique
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
import argparse

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Couleurs pour les logs
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_step(message):
    """Affiche un message d'étape formaté."""
    print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")

def log_success(message):
    """Affiche un message de succès."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def log_warning(message):
    """Affiche un avertissement."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def log_error(message):
    """Affiche une erreur."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def log_info(message):
    """Affiche une information."""
    print(f"{Colors.BLUE}ℹ {message}{Colors.ENDC}")

def log_response(response, label="Réponse"):
    """Affiche une réponse HTTP."""
    try:
        response_json = response.json()
        print(f"{Colors.CYAN}{label} ({response.status_code}):{Colors.ENDC}")
        print(json.dumps(response_json, indent=2, ensure_ascii=False))
    except:
        print(f"{Colors.CYAN}{label} ({response.status_code}):{Colors.ENDC}")
        print(response.text)

class SadieClient:
    """Client API pour interagir avec l'application sadie."""
    
    def __init__(self, base_url=BASE_URL):
        """Initialise le client API."""
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
        self.token = None
        self.session = requests.Session()
    
    def login(self, username, password):
        """Authentifie l'utilisateur et récupère un token."""
        log_step("1. Authentification de l'utilisateur")
        
        try:
            # Utilisation du flux OAuth2 (password grant)
            response = self.session.post(
                f"{self.api_base}/token", 
                data={
                    "username": username,
                    "password": password,
                    "grant_type": "password"
                }
            )
            
            response.raise_for_status()
            data = response.json()
            self.token = data.get("access_token")
            
            if self.token:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                log_success(f"Authentification réussie pour l'utilisateur '{username}'")
                log_response(response)
                return True
            else:
                log_error("Token non trouvé dans la réponse")
                return False
                
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de l'authentification: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return False
    
    def check_user_profile(self):
        """Vérifie le profil de l'utilisateur."""
        log_step("2. Vérification du profil utilisateur")
        
        try:
            response = self.session.get(f"{self.api_base}/users/me")
            response.raise_for_status()
            
            log_success("Profil utilisateur récupéré avec succès")
            log_response(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de la récupération du profil: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return None
    
    def save_user_configuration(self, api_keys=None):
        """Sauvegarde la configuration de l'utilisateur."""
        log_step("3. Configuration du profil utilisateur")
        
        if api_keys is None:
            api_keys = {
                "binance": {
                    "api_key": "DEMO_API_KEY_BINANCE",
                    "api_secret": "DEMO_API_SECRET_BINANCE"
                },
                "kraken": {
                    "api_key": "DEMO_API_KEY_KRAKEN",
                    "api_secret": "DEMO_API_SECRET_KRAKEN"
                }
            }
        
        config = {
            "api_keys": api_keys,
            "preferences": {
                "default_exchange": "binance",
                "default_pair": "BTC/USDT",
                "default_timeframe": "1h",
                "theme": "dark",
                "notifications_enabled": True
            }
        }
        
        try:
            response = self.session.post(
                f"{self.api_base}/configuration",
                json=config
            )
            response.raise_for_status()
            
            log_success("Configuration utilisateur sauvegardée avec succès")
            log_response(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de la sauvegarde de la configuration: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return None
    
    def get_market_data(self, exchange="binance", symbol="BTC/USDT"):
        """Récupère les données de marché."""
        log_step("4. Récupération des données de marché")
        
        try:
            # Formater le symbole pour l'API (retirer le "/")
            formatted_symbol = symbol.replace("/", "")
            
            response = self.session.get(
                f"{self.api_base}/market/{exchange}/{formatted_symbol}/trades",
                params={"limit": 5}
            )
            response.raise_for_status()
            
            log_success(f"Données de marché récupérées pour {symbol} sur {exchange}")
            log_response(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de la récupération des données de marché: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return None
    
    def get_klines_data(self, exchange="binance", symbol="BTC/USDT", interval="1h", limit=10):
        """Récupère les données de chandeliers."""
        log_step("5. Récupération des données de chandeliers")
        
        try:
            # Formater le symbole pour l'API (retirer le "/")
            formatted_symbol = symbol.replace("/", "")
            
            response = self.session.get(
                f"{self.api_base}/market/{exchange}/{formatted_symbol}/klines",
                params={"interval": interval, "limit": limit}
            )
            response.raise_for_status()
            
            log_success(f"Données de chandeliers récupérées pour {symbol} sur {exchange} (intervalle: {interval})")
            log_response(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de la récupération des chandeliers: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return None
    
    def save_chart_configuration(self, config=None):
        """Sauvegarde une configuration de graphique."""
        log_step("6. Sauvegarde d'une configuration de graphique")
        
        if config is None:
            config = {
                "exchange": "binance",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "chartType": "candlestick",
                "indicators": [
                    {
                        "id": "sma-1",
                        "name": "Moyenne Mobile Simple",
                        "type": "overlay",
                        "parameters": [
                            {"name": "période", "type": "number", "value": 20}
                        ],
                        "color": "#2196F3",
                        "visible": True
                    },
                    {
                        "id": "ema-1",
                        "name": "Moyenne Mobile Exponentielle",
                        "type": "overlay",
                        "parameters": [
                            {"name": "période", "type": "number", "value": 50}
                        ],
                        "color": "#FF5722",
                        "visible": True
                    }
                ]
            }
        
        try:
            response = self.session.post(
                f"{self.api_base}/user/chart-config",
                json=config
            )
            response.raise_for_status()
            
            log_success("Configuration du graphique sauvegardée avec succès")
            log_response(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de la sauvegarde de la configuration du graphique: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return None
    
    def create_alert(self, alert=None):
        """Crée une alerte de prix."""
        log_step("7. Création d'une alerte de prix")
        
        if alert is None:
            alert = {
                "exchange": "binance",
                "symbol": "BTC/USDT",
                "price": 32000,
                "condition": "above",  # "above" ou "below"
                "notification_type": "email",
                "active": True
            }
        
        try:
            response = self.session.post(
                f"{self.api_base}/alerts",
                json=alert
            )
            response.raise_for_status()
            
            log_success("Alerte créée avec succès")
            log_response(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de la création de l'alerte: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return None
    
    def get_alerts(self):
        """Récupère la liste des alertes."""
        log_step("8. Récupération des alertes")
        
        try:
            response = self.session.get(f"{self.api_base}/alerts")
            response.raise_for_status()
            
            log_success("Alertes récupérées avec succès")
            log_response(response)
            return response.json()
            
        except requests.exceptions.RequestException as e:
            log_error(f"Erreur lors de la récupération des alertes: {str(e)}")
            if hasattr(e, "response"):
                log_response(e.response, "Erreur")
            return None

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description="Test du flux utilisateur pour l'application sadie")
    parser.add_argument("--username", default="testuser", help="Nom d'utilisateur")
    parser.add_argument("--password", default="password123", help="Mot de passe")
    parser.add_argument("--base-url", default=BASE_URL, help="URL de base de l'API")
    args = parser.parse_args()
    
    client = SadieClient(base_url=args.base_url)
    
    # Étape 1: Authentification
    if not client.login(args.username, args.password):
        log_error("Impossible de continuer sans authentification")
        sys.exit(1)
    
    # Étape 2: Vérification du profil
    profile = client.check_user_profile()
    if not profile:
        log_warning("Impossible de récupérer le profil utilisateur, mais on continue")
    
    # Étape 3: Configuration du profil
    config = client.save_user_configuration()
    if not config:
        log_warning("Impossible de sauvegarder la configuration, mais on continue")
    
    # Étape 4: Données de marché
    market_data = client.get_market_data()
    if not market_data:
        log_warning("Impossible de récupérer les données de marché, mais on continue")
    
    # Étape 5: Données de chandeliers
    klines_data = client.get_klines_data()
    if not klines_data:
        log_warning("Impossible de récupérer les données de chandeliers, mais on continue")
    
    # Étape 6: Configuration de graphique
    chart_config = client.save_chart_configuration()
    if not chart_config:
        log_warning("Impossible de sauvegarder la configuration du graphique, mais on continue")
    
    # Étape 7: Création d'alerte
    alert = client.create_alert()
    if not alert:
        log_warning("Impossible de créer une alerte, mais on continue")
    
    # Étape 8: Récupération des alertes
    alerts = client.get_alerts()
    if not alerts:
        log_warning("Impossible de récupérer les alertes")
    
    # Résumé
    log_step("Résumé du test")
    if all([profile, config, market_data, klines_data, chart_config, alert, alerts]):
        log_success("✅ Toutes les étapes du flux utilisateur ont réussi!")
    else:
        log_warning("⚠️ Certaines étapes ont échoué, mais le test s'est terminé")
    
    # Liste des composants testés
    components = [
        ("Authentification OAuth2", bool(client.token)),
        ("Profil utilisateur", bool(profile)),
        ("Configuration utilisateur", bool(config)),
        ("Données de marché", bool(market_data)),
        ("Données de chandeliers", bool(klines_data)),
        ("Configuration de graphique", bool(chart_config)),
        ("Création d'alerte", bool(alert)),
        ("Récupération d'alertes", bool(alerts))
    ]
    
    print("\nRésultats par composant:")
    for name, success in components:
        if success:
            print(f"{Colors.GREEN}✓ {name}{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}✗ {name}{Colors.ENDC}")

if __name__ == "__main__":
    main() 