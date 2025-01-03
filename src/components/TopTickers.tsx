import React from 'react';

interface Ticker {
  symbol: string;
  name: string;
  price: number;
  change: number;
}

const topTickers: Ticker[] = [
  { symbol: 'BTCUSDT', name: 'Bitcoin', price: 47000.00, change: 2.73 },
  { symbol: 'ETHUSDT', name: 'Ethereum', price: 3200.00, change: -1.2 },
  { symbol: 'BNBUSDT', name: 'BNB', price: 420.00, change: 0.8 },
  { symbol: 'ADAUSDT', name: 'Cardano', price: 1.20, change: 5.3 },
  { symbol: 'SOLUSDT', name: 'Solana', price: 180.00, change: -2.1 },
  { symbol: 'XRPUSDT', name: 'Ripple', price: 0.85, change: 1.5 },
  { symbol: 'DOTUSDT', name: 'Polkadot', price: 25.40, change: -0.7 },
  { symbol: 'DOGEUSDT', name: 'Dogecoin', price: 0.15, change: 3.2 },
  { symbol: 'AVAXUSDT', name: 'Avalanche', price: 85.60, change: 4.1 },
  { symbol: 'LUNAUSDT', name: 'Terra', price: 95.30, change: -1.8 }
];

export function TopTickers() {
  return (
    <div style={{
      width: '100%',
      background: '#1E222D',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <div style={{
        padding: '8px 12px',
        borderBottom: '1px solid #2A2E39'
      }}>
        <input
          type="text"
          placeholder="Rechercher un symbole..."
          style={{
            width: '100%',
            padding: '6px 10px',
            background: '#131722',
            border: '1px solid #2A2E39',
            borderRadius: '4px',
            color: '#D1D4DC',
            fontSize: '13px',
            outline: 'none'
          }}
        />
      </div>
      <div style={{
        maxHeight: '300px',
        overflowY: 'auto'
      }}>
        {topTickers.map(ticker => (
          <div
            key={ticker.symbol}
            className="ticker-item"
            style={{
              padding: '8px 12px',
              borderBottom: '1px solid #2A2E39',
              cursor: 'pointer'
            }}
          >
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              marginBottom: '2px'
            }}>
              <div style={{ color: '#D1D4DC', fontWeight: 'bold', fontSize: '13px' }}>
                {ticker.symbol}
              </div>
              <div style={{ color: '#D1D4DC', fontSize: '13px' }}>
                ${ticker.price.toLocaleString()}
              </div>
            </div>
            <div style={{
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <div style={{ color: '#787B86', fontSize: '11px' }}>
                {ticker.name}
              </div>
              <div style={{
                color: ticker.change >= 0 ? '#26A69A' : '#EF5350',
                fontSize: '11px'
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
            background: #2A2E39;
          }
        `}
      </style>
    </div>
  );
} 