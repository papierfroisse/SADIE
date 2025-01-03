import React from 'react';

interface TopTickersProps {
  onSymbolSelect: (symbol: string) => void;
}

const topSymbols = [
  { symbol: 'BTCUSDT', name: 'Bitcoin', price: '50000', change: '+2.5%' },
  { symbol: 'ETHUSDT', name: 'Ethereum', price: '3000', change: '+1.8%' },
  { symbol: 'BNBUSDT', name: 'BNB', price: '400', change: '-0.5%' },
  { symbol: 'SOLUSDT', name: 'Solana', price: '100', change: '+3.2%' },
  { symbol: 'ADAUSDT', name: 'Cardano', price: '0.5', change: '-1.2%' }
];

export function TopTickers({ onSymbolSelect }: TopTickersProps) {
  return (
    <div style={{
      padding: '16px'
    }}>
      <h2 style={{
        margin: '0 0 16px',
        color: '#D1D4DC',
        fontSize: '16px',
        fontWeight: 'normal'
      }}>
        Top Cryptos
      </h2>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        {topSymbols.map(ticker => (
          <button
            key={ticker.symbol}
            onClick={() => onSymbolSelect(ticker.symbol)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '12px',
              background: 'transparent',
              border: '1px solid #2A2E39',
              borderRadius: '4px',
              cursor: 'pointer',
              width: '100%',
              textAlign: 'left'
            }}
          >
            <div>
              <div style={{ color: '#D1D4DC', fontSize: '14px', marginBottom: '4px' }}>
                {ticker.name}
              </div>
              <div style={{ color: '#787B86', fontSize: '12px' }}>
                {ticker.symbol}
              </div>
            </div>
            <div>
              <div style={{ color: '#D1D4DC', fontSize: '14px', marginBottom: '4px', textAlign: 'right' }}>
                ${ticker.price}
              </div>
              <div style={{ 
                color: ticker.change.startsWith('+') ? '#26A69A' : '#EF5350',
                fontSize: '12px',
                textAlign: 'right'
              }}>
                {ticker.change}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
} 