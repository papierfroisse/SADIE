"""
Exemple d'utilisation du module de collecte de données.
"""

import os
import datetime
from dotenv import load_dotenv
import pandas as pd

from sadie.data.collectors.factory import DataCollectorFactory

def main():
    # Chargement des variables d'environnement
    load_dotenv()
    
    # Configuration
    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_SECRET_KEY")
    alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    # Création des collecteurs
    binance = DataCollectorFactory.create(
        source="binance",
        api_key=binance_api_key,
        api_secret=binance_api_secret
    )
    
    alpha_vantage = DataCollectorFactory.create(
        source="alpha_vantage",
        api_key=alpha_vantage_api_key
    )
    
    # Exemple avec Binance
    print("\nDonnées Binance :")
    
    # Prix actuel
    btc_price = binance.get_current_price("BTC/USDT")
    print(f"Prix BTC actuel : {btc_price} USDT")
    
    # Données historiques
    start_time = datetime.datetime.now() - datetime.timedelta(days=7)
    historical_data = binance.get_historical_data(
        symbol="BTC/USDT",
        interval="1h",
        start_time=start_time,
        limit=168  # 7 jours * 24 heures
    )
    
    # Conversion en DataFrame pour l'affichage
    df = pd.DataFrame(historical_data)
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
    print("\nDernières données historiques :")
    print(df[["datetime", "open", "high", "low", "close", "volume"]].tail())
    
    # Carnet d'ordres
    order_book = binance.get_order_book("BTC/USDT", limit=5)
    print("\nCarnet d'ordres (top 5) :")
    print("Ordres d'achat :")
    for price, qty in order_book["bids"]:
        print(f"Prix: {price}, Quantité: {qty}")
    print("\nOrdres de vente :")
    for price, qty in order_book["asks"]:
        print(f"Prix: {price}, Quantité: {qty}")
    
    # Exemple avec Alpha Vantage
    print("\nDonnées Alpha Vantage :")
    
    # Prix actuel
    btc_price_av = alpha_vantage.get_current_price("BTC/USD")
    print(f"Prix BTC actuel : {btc_price_av} USD")
    
    # Données historiques journalières
    historical_data_av = alpha_vantage.get_historical_data(
        symbol="BTC/USD",
        interval="daily",
        start_time=start_time,
        limit=7
    )
    
    # Conversion en DataFrame pour l'affichage
    df_av = pd.DataFrame(historical_data_av)
    df_av["datetime"] = pd.to_datetime(df_av["timestamp"], unit="s")
    print("\nDernières données historiques :")
    print(df_av[["datetime", "open", "high", "low", "close", "volume"]].tail())

if __name__ == "__main__":
    main() 