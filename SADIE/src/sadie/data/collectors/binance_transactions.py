"""Binance-specific transaction collector implementation."""
import json
import logging
import websockets
from typing import Optional
from datetime import datetime

from sadie.data.collectors.transactions import (
    Transaction,
    TransactionCollector
)

logger = logging.getLogger(__name__)

class BinanceTransactionCollector(TransactionCollector):
    """Transaction collector implementation for Binance."""
    
    WEBSOCKET_URL = "wss://stream.binance.com:9443/ws"
    
    async def _connect_websocket(self, symbol: str):
        """Create WebSocket connection for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
        """
        stream = f"{symbol.lower()}@trade"
        ws_url = f"{self.WEBSOCKET_URL}/{stream}"
        
        try:
            async with websockets.connect(ws_url) as ws:
                # Subscribe to trade stream
                subscribe_msg = {
                    "method": "SUBSCRIBE",
                    "params": [stream],
                    "id": 1
                }
                await ws.send(json.dumps(subscribe_msg))
                
                # Process subscription response
                response = await ws.recv()
                if not self._verify_subscription(response):
                    raise ConnectionError(f"Failed to subscribe to {stream}")
                    
                logger.info(f"Successfully subscribed to {stream}")
                
                # Return WebSocket for message processing
                return ws
                
        except Exception as e:
            logger.error(f"Error connecting to Binance WebSocket: {str(e)}")
            raise
            
    def _parse_transaction(self, symbol: str, message: str) -> Optional[Transaction]:
        """Parse transaction from Binance WebSocket message.
        
        Args:
            symbol: Trading pair symbol
            message: Raw WebSocket message
            
        Returns:
            Parsed Transaction object or None if invalid
        """
        try:
            data = json.loads(message)
            
            # Verify message type
            if "e" not in data or data["e"] != "trade":
                return None
                
            # Parse trade data
            return Transaction(
                symbol=symbol,
                timestamp=data["T"] / 1000.0,  # Convert to seconds
                price=float(data["p"]),
                quantity=float(data["q"]),
                is_buyer_maker=data["m"],
                trade_id=data["t"]
            )
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Error parsing transaction message: {str(e)}")
            return None
            
    def _verify_subscription(self, response: str) -> bool:
        """Verify WebSocket subscription response.
        
        Args:
            response: Subscription response message
            
        Returns:
            True if subscription successful, False otherwise
        """
        try:
            data = json.loads(response)
            return "result" in data and data["result"] is None
        except (json.JSONDecodeError, KeyError):
            return False
            
    async def get_historical_trades(
        self,
        symbol: str,
        limit: int = 1000
    ) -> list[Transaction]:
        """Get historical trades from REST API.
        
        Args:
            symbol: Trading pair symbol
            limit: Number of trades to retrieve (max 1000)
            
        Returns:
            List of historical transactions
        """
        # TODO: Implement REST API call to /api/v3/historicalTrades
        # This requires API key with permission to read historical trades
        raise NotImplementedError("Historical trades not yet implemented") 