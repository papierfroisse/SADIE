import React from 'react';

interface MainHeaderProps {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
}

export function MainHeader({ symbol, price, change, changePercent }: MainHeaderProps) {
  return (
    <>
      <style>
        {`
          .nav-button:hover {
            background: #2A2E39;
          }
        `}
      </style>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        padding: '12px 16px',
        background: '#1E222D',
        borderBottom: '1px solid #363A45'
      }}>
        {/* Logo */}
        <div style={{
          fontSize: '24px',
          fontWeight: 'bold',
          color: '#2962FF',
          marginRight: '32px'
        }}>
          TradingView
        </div>

        {/* Symbole et prix */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px'
        }}>
          <div style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#D1D4DC'
          }}>
            {symbol}
          </div>

          <div style={{
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#D1D4DC'
          }}>
            ${price.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}
          </div>

          <div style={{
            fontSize: '16px',
            color: change >= 0 ? '#26A69A' : '#EF5350',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span>
              {change >= 0 ? '+' : ''}{change.toFixed(2)}
            </span>
            <span>
              ({changePercent >= 0 ? '+' : ''}{changePercent.toFixed(2)}%)
            </span>
          </div>
        </div>

        {/* Boutons de navigation */}
        <div style={{
          display: 'flex',
          gap: '8px',
          marginLeft: 'auto'
        }}>
          {['Graphiques', 'Screener', 'Marchés', 'Actualités', 'Plus'].map(item => (
            <button
              key={item}
              className="nav-button"
              style={{
                padding: '8px 16px',
                background: 'transparent',
                border: 'none',
                color: '#D1D4DC',
                fontSize: '14px',
                cursor: 'pointer',
                borderRadius: '4px',
                transition: 'background-color 0.2s'
              }}
            >
              {item}
            </button>
          ))}
        </div>
      </div>
    </>
  );
} 