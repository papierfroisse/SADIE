"""Module de gestion des transactions."""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from decimal import Decimal, InvalidOperation

from ...core.monitoring import get_logger
from ..exceptions import DataError
from .base import DataCollector

logger = get_logger(__name__)

class Trade:
    """Représentation d'une transaction."""
    
    def __init__(
        self,
        trade_id: str,
        symbol: str,
        price: Decimal,
        amount: Decimal,
        side: str,
        timestamp: datetime,
        maker_order_id: Optional[str] = None,
        taker_order_id: Optional[str] = None
    ):
        """Initialise une transaction.
        
        Args:
            trade_id: Identifiant unique
            symbol: Symbole de trading
            price: Prix d'exécution
            amount: Quantité échangée
            side: Direction (buy/sell)
            timestamp: Horodatage
            maker_order_id: ID de l'ordre maker
            taker_order_id: ID de l'ordre taker
        """
        self.trade_id = trade_id
        self.symbol = symbol
        try:
            self.price = Decimal(str(price))
            self.amount = Decimal(str(amount))
        except InvalidOperation as e:
            raise DataError(f"Valeur numérique invalide: {e}")
        self.side = side.lower()
        self.timestamp = timestamp
        self.maker_order_id = maker_order_id
        self.taker_order_id = taker_order_id
        
    @property
    def value(self) -> Decimal:
        """Valeur totale de la transaction."""
        return self.price * self.amount
        
    def to_dict(self) -> Dict:
        """Convertit la transaction en dictionnaire."""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "price": str(self.price),
            "amount": str(self.amount),
            "value": str(self.value),
            "side": self.side,
            "timestamp": self.timestamp.isoformat(),
            "maker_order_id": self.maker_order_id,
            "taker_order_id": self.taker_order_id
        }

class TradeManager:
    """Gestionnaire de transactions."""
    
    def __init__(self, symbol: str, max_trades: int = 1000):
        """Initialise le gestionnaire.
        
        Args:
            symbol: Symbole de trading
            max_trades: Nombre maximum de transactions à conserver
        """
        self.symbol = symbol
        self.max_trades = max_trades
        self.trades: List[Trade] = []
        self.last_trade_id: Optional[str] = None
        self.logger = get_logger(f"trades.{symbol}")
        
    def add_trade(self, trade_data: Dict) -> None:
        """Ajoute une nouvelle transaction.
        
        Args:
            trade_data: Données de la transaction
        """
        try:
            # Vérification de la séquence
            if (
                self.last_trade_id and
                trade_data.get("trade_id") <= self.last_trade_id
            ):
                return
                
            # Création de la transaction
            trade = Trade(
                trade_id=trade_data["trade_id"],
                symbol=self.symbol,
                price=trade_data["price"],
                amount=trade_data["amount"],
                side=trade_data["side"],
                timestamp=datetime.fromisoformat(trade_data["timestamp"])
                if isinstance(trade_data["timestamp"], str)
                else trade_data["timestamp"],
                maker_order_id=trade_data.get("maker_order_id"),
                taker_order_id=trade_data.get("taker_order_id")
            )
            
            # Ajout et gestion de la taille maximale
            self.trades.append(trade)
            if len(self.trades) > self.max_trades:
                self.trades = self.trades[-self.max_trades:]
                
            self.last_trade_id = trade.trade_id
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout d'une transaction: {e}")
            raise DataError(f"Erreur d'ajout de transaction: {e}")
            
    def get_trades(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Trade]:
        """Récupère les transactions dans une fenêtre temporelle.
        
        Args:
            start_time: Début de la fenêtre
            end_time: Fin de la fenêtre
            
        Returns:
            Liste des transactions
        """
        if not (start_time or end_time):
            return self.trades.copy()
            
        filtered_trades = []
        for trade in self.trades:
            if start_time and trade.timestamp < start_time:
                continue
            if end_time and trade.timestamp > end_time:
                continue
            filtered_trades.append(trade)
            
        return filtered_trades
        
    def get_statistics(
        self,
        window: Optional[int] = None
    ) -> Dict:
        """Calcule des statistiques sur les transactions.
        
        Args:
            window: Nombre de transactions à considérer
            
        Returns:
            Statistiques calculées
        """
        trades = self.trades[-window:] if window else self.trades
        if not trades:
            return {}
            
        volumes = {
            "buy": Decimal("0"),
            "sell": Decimal("0")
        }
        values = {
            "buy": Decimal("0"),
            "sell": Decimal("0")
        }
        prices = []
        
        for trade in trades:
            volumes[trade.side] += trade.amount
            values[trade.side] += trade.value
            prices.append(float(trade.price))
            
        return {
            "count": len(trades),
            "volume": {
                "buy": str(volumes["buy"]),
                "sell": str(volumes["sell"]),
                "total": str(volumes["buy"] + volumes["sell"])
            },
            "value": {
                "buy": str(values["buy"]),
                "sell": str(values["sell"]),
                "total": str(values["buy"] + values["sell"])
            },
            "price": {
                "first": str(trades[0].price),
                "last": str(trades[-1].price),
                "min": str(min(t.price for t in trades)),
                "max": str(max(t.price for t in trades)),
                "change": float(
                    (trades[-1].price - trades[0].price) /
                    trades[0].price * 100
                )
            }
        }

class TradeCollector(DataCollector):
    """Collecteur de transactions en temps réel."""
    
    def __init__(
        self,
        name: str,
        symbols: List[str],
        update_interval: float = 1.0,
        max_trades: int = 1000
    ):
        """Initialise le collecteur.
        
        Args:
            name: Nom du collecteur
            symbols: Liste des symboles à suivre
            update_interval: Intervalle de mise à jour en secondes
            max_trades: Nombre maximum de transactions par symbole
        """
        super().__init__(name)
        self.symbols = symbols
        self.update_interval = update_interval
        self.max_trades = max_trades
        self.managers: Dict[str, TradeManager] = {}
        self._websocket = None
        self._initialize_managers()
        
    def _initialize_managers(self) -> None:
        """Initialise les gestionnaires de transactions."""
        for symbol in self.symbols:
            self.managers[symbol] = TradeManager(
                symbol,
                max_trades=self.max_trades
            )
            
    async def _create_websocket(self):
        """Crée une connexion WebSocket."""
        # Cette méthode serait normalement implémentée avec une vraie connexion WebSocket
        # Pour les tests, elle sera mockée
        pass
            
    async def connect(self) -> None:
        """Établit la connexion au flux de données."""
        try:
            self._websocket = await self._create_websocket()
            if hasattr(self._websocket, 'connect'):
                await self._websocket.connect()
            await self._subscribe_trades()
            self.logger.info(f"Connecté au flux de données pour {len(self.symbols)} symboles")
        except Exception as e:
            self._websocket = None
            self.logger.error(f"Erreur de connexion: {e}")
            raise ConnectionError(f"Erreur de connexion: {e}")
            
    async def disconnect(self) -> None:
        """Ferme la connexion au flux de données."""
        if self._websocket and hasattr(self._websocket, 'disconnect'):
            await self._websocket.disconnect()
        self._websocket = None
            
    def is_connected(self) -> bool:
        """Vérifie si le collecteur est connecté."""
        if not self._websocket:
            return False
        return hasattr(self._websocket, 'connected') and self._websocket.connected
            
    async def _subscribe_trades(self) -> None:
        """Souscrit aux flux de transactions."""
        if not self.is_connected():
            raise ConnectionError("Non connecté")
        # Implémentation spécifique à la source de données
        pass
        
    async def process_message(self, message: Dict) -> None:
        """Traite un message reçu.
        
        Args:
            message: Message à traiter
        """
        try:
            symbol = message.get("symbol")
            if symbol not in self.managers:
                self.logger.warning(f"Symbol inconnu reçu: {symbol}")
                return
                
            manager = self.managers[symbol]
            manager.add_trade(message)
            
        except Exception as e:
            self.logger.error(f"Erreur de traitement: {e}")
            # Ne pas propager l'erreur pour maintenir la résilience
            
    async def collect(self) -> Dict:
        """Collecte les données de transactions.
        
        Returns:
            Données collectées
        """
        if not self.is_connected():
            raise ConnectionError("Non connecté")
            
        try:
            data = {}
            for symbol, manager in self.managers.items():
                trades = manager.get_trades()
                data[symbol] = {
                    "trades": [t.to_dict() for t in trades[-100:]],  # 100 dernières transactions
                    "statistics": manager.get_statistics(window=100)
                }
            return data
        except Exception as e:
            self.logger.error(f"Erreur lors de la collecte: {e}")
            raise 