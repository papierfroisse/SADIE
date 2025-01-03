import React, { useState } from 'react';

interface SymbolListProps {
  selectedSymbol: string;
  onSymbolSelect: (symbol: string) => void;
}

// Données d'exemple
const categories = [
  {
    name: 'Crypto',
    symbols: [
      { symbol: 'BTCUSDT', name: 'Bitcoin', price: 47000, change: 2.5 },
      { symbol: 'ETHUSDT', name: 'Ethereum', price: 3200, change: -1.2 },
      { symbol: 'BNBUSDT', name: 'Binance Coin', price: 420, change: 0.8 },
      { symbol: 'ADAUSDT', name: 'Cardano', price: 1.2, change: 5.3 },
      { symbol: 'SOLUSDT', name: 'Solana', price: 180, change: -2.1 }
    ]
  },
  {
    name: 'Forex',
    symbols: [
      { symbol: 'EURUSD', name: 'Euro/USD', price: 1.0923, change: 0.1 },
      { symbol: 'GBPUSD', name: 'GBP/USD', price: 1.2634, change: -0.2 },
      { symbol: 'USDJPY', name: 'USD/JPY', price: 148.12, change: 0.3 },
      { symbol: 'AUDUSD', name: 'AUD/USD', price: 0.6523, change: -0.4 },
      { symbol: 'USDCAD', name: 'USD/CAD', price: 1.3456, change: 0.2 }
    ]
  }
];

export function SymbolList({ selectedSymbol, onSymbolSelect }: SymbolListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Crypto');

  const filteredSymbols = categories
    .find(cat => cat.name === selectedCategory)
    ?.symbols.filter(s => 
      s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.name.toLowerCase().includes(searchQuery.toLowerCase())
    ) || [];

  return (
    <>
      <style>
        {`
          .category-button:hover {
            background: #363A45;
          }
          .category-button.active {
            background: #2962FF;
          }
          .symbol-row:hover {
            background: #2A2E39;
          }
        `}
      </style>
      <div style={{
        width: '300px',
        background: '#1E222D',
        borderRight: '1px solid #363A45',
        display: 'flex',
        flexDirection: 'column',
        height: '100%'
      }}>
        {/* Barre de recherche */}
        <div style={{
          padding: '16px',
          borderBottom: '1px solid #363A45'
        }}>
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Rechercher un symbole..."
            style={{
              width: '100%',
              padding: '8px 12px',
              background: '#2A2E39',
              border: '1px solid #363A45',
              borderRadius: '4px',
              color: '#D1D4DC',
              fontSize: '14px',
              outline: 'none'
            }}
          />
        </div>

        {/* Catégories */}
        <div style={{
          display: 'flex',
          gap: '8px',
          padding: '8px 16px',
          borderBottom: '1px solid #363A45'
        }}>
          {categories.map(category => (
            <button
              key={category.name}
              onClick={() => setSelectedCategory(category.name)}
              className={`category-button ${selectedCategory === category.name ? 'active' : ''}`}
              style={{
                padding: '6px 12px',
                background: selectedCategory === category.name ? '#2962FF' : '#2A2E39',
                border: 'none',
                borderRadius: '4px',
                color: '#D1D4DC',
                fontSize: '14px',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* Liste des symboles */}
        <div style={{
          flex: 1,
          overflowY: 'auto'
        }}>
          {filteredSymbols.map(symbol => (
            <div
              key={symbol.symbol}
              onClick={() => onSymbolSelect(symbol.symbol)}
              className="symbol-row"
              style={{
                display: 'flex',
                padding: '12px 16px',
                cursor: 'pointer',
                background: selectedSymbol === symbol.symbol ? '#2A2E39' : 'transparent',
                transition: 'background-color 0.2s'
              }}
            >
              <div style={{
                flex: 1
              }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: '#D1D4DC',
                  marginBottom: '4px'
                }}>
                  {symbol.symbol}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: '#787B86'
                }}>
                  {symbol.name}
                </div>
              </div>
              <div style={{
                textAlign: 'right'
              }}>
                <div style={{
                  fontSize: '14px',
                  color: '#D1D4DC',
                  marginBottom: '4px'
                }}>
                  ${symbol.price.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: symbol.change >= 0 ? '#26A69A' : '#EF5350'
                }}>
                  {symbol.change >= 0 ? '+' : ''}{symbol.change}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
} 