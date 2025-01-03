import React from 'react';

interface TopTickersProps {
  // Props futures pour la personnalisation
}

export function TopTickers({}: TopTickersProps) {
  // Données de test
  const tickers = [
    { symbol: 'BTC/USD', name: 'Bitcoin', price: 43250.50, change: 2.5, volume: '12.5B' },
    { symbol: 'ETH/USD', name: 'Ethereum', price: 2250.75, change: -1.2, volume: '8.2B' },
    { symbol: 'BNB/USD', name: 'Binance Coin', price: 305.25, change: 0.8, volume: '1.5B' },
    { symbol: 'XRP/USD', name: 'Ripple', price: 0.55, change: -0.5, volume: '2.1B' },
    { symbol: 'SOL/USD', name: 'Solana', price: 98.75, change: 5.2, volume: '3.8B' },
  ];

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      maxHeight: '50%',
      background: '#1E222D',
      color: '#D1D4DC'
    }}>
      {/* En-tête */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid #2A2E39',
        fontSize: '16px',
        fontWeight: 'bold'
      }}>
        Ticker
      </div>

      {/* Liste des tickers */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '8px 0'
      }}>
        {tickers.map((ticker, index) => (
          <div
            key={ticker.symbol}
            className="ticker-item"
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr auto',
              gap: '8px',
              padding: '8px 16px',
              cursor: 'pointer',
              transition: 'background-color 0.2s'
            }}
          >
            <div>
              <div style={{
                fontSize: '14px',
                fontWeight: 'bold',
                marginBottom: '4px'
              }}>
                {ticker.symbol}
              </div>
              <div style={{
                fontSize: '12px',
                color: '#787B86'
              }}>
                {ticker.name}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{
                fontSize: '14px',
                marginBottom: '4px'
              }}>
                ${ticker.price.toLocaleString()}
              </div>
              <div style={{
                fontSize: '12px',
                color: ticker.change >= 0 ? '#26A69A' : '#EF5350'
              }}>
                {ticker.change >= 0 ? '+' : ''}{ticker.change}%
              </div>
            </div>
          </div>
        ))}
      </div>

      <style>
        {`
          .ticker-item:hover {
            background-color: #2A2E39;
          }
        `}
      </style>
    </div>
  );
} 