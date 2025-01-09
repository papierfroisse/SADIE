# Data Collectors Documentation

## Overview
The data collectors module provides a flexible and extensible framework for collecting market data from various sources. The system is built around a base collector class that handles common functionality, with specific collectors implementing source-specific logic.

## Base Collector
The `BaseCollector` class provides the foundation for all data collectors. It handles:
- Connection management
- Error handling and logging
- Resource cleanup
- State management

### Key Methods
- `start()`: Initialize and start data collection
- `stop()`: Stop data collection and cleanup resources
- `is_running()`: Check collector status
- `get_status()`: Get detailed collector status

## OrderBook Collector
The `OrderBookCollector` class implements real-time order book data collection from cryptocurrency exchanges.

### Features
- Real-time L2 market depth data
- Efficient WebSocket connections
- Automatic reconnection handling
- Data persistence with TimescaleDB

### Configuration
```python
collector = OrderBookCollector(
    db_manager=db_manager,
    symbols=["BTCUSDT", "ETHUSDT"],  # Trading pairs to monitor
    depth_level="L2",                 # Order book depth (L1, L2, L3)
    update_interval=1.0,              # Update frequency in seconds
    exchange="binance",               # Exchange name
    config={...}                      # Additional configuration
)
```

### Data Format
Order book data is stored in the following format:
```json
{
    "symbol": "BTCUSDT",
    "timestamp": "2024-01-10T12:00:00Z",
    "exchange": "binance",
    "depth_level": "L2",
    "bids": [
        ["50000.00", "1.000"],  // [price, quantity]
        ["49999.00", "2.000"]
    ],
    "asks": [
        ["50001.00", "0.500"],
        ["50002.00", "1.500"]
    ]
}
```

### Database Schema
The order book data is stored in a TimescaleDB hypertable with the following optimizations:
- Automatic partitioning by time
- Data retention policy (90 days)
- Compression after 7 days
- Indexes on symbol, timestamp, and exchange

### Usage Example
```python
import asyncio
from sadie.storage import DatabaseManager
from sadie.data.collectors import OrderBookCollector

async def main():
    # Initialize database manager
    db_manager = DatabaseManager()
    await db_manager.connect()
    
    # Create and start collector
    collector = OrderBookCollector(
        db_manager=db_manager,
        symbols=["BTCUSDT", "ETHUSDT"],
        update_interval=1.0
    )
    
    try:
        await collector.start()
        # Run for 1 hour
        await asyncio.sleep(3600)
    finally:
        await collector.stop()
        await db_manager.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Error Handling
The collector implements comprehensive error handling:
- WebSocket connection errors
- Data validation errors
- Database connection issues
- Resource cleanup

### Performance Considerations
- Memory usage scales with number of symbols
- Network bandwidth depends on update frequency
- Database write load increases with number of symbols
- Consider batching for high-frequency updates

## Best Practices
1. **Resource Management**
   - Always use async context managers
   - Properly close connections
   - Handle cleanup in error cases

2. **Configuration**
   - Start with conservative update intervals
   - Monitor system resources
   - Adjust batch sizes based on load

3. **Monitoring**
   - Log important state changes
   - Track connection status
   - Monitor data quality
   - Set up alerts for failures

## Future Enhancements
- Support for more exchanges
- Advanced order book analytics
- Real-time data validation
- Performance optimizations
- Data quality metrics 