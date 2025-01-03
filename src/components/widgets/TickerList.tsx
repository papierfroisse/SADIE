import React, { useState } from 'react';

interface Ticker {
  symbol: string;
  name: string;
  price: number;
  change: number;
  volume: number;
}

const tickers: Ticker[] = [
  { symbol: 'BTCUSDT', name: 'Bitcoin', price: 47000.00, change: 2.73, volume: 1.23e9 },
  { symbol: 'ETHUSDT', name: 'Ethereum', price: 3200.00, change: -1.2, volume: 5.67e8 },
  { symbol: 'BNBUSDT', name: 'Binance Coin', price: 420.00, change: 0.8, volume: 1.23e8 },
  { symbol: 'ADAUSDT', name: 'Cardano', price: 1.20, change: -5.3, volume: 4.56e7 },
  { symbol: 'SOLUSDT', name: 'Solana', price: 180.00, change: -2.1, volume: 3.45e7 }
];

const tickerItemStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  padding: '12px 16px',
  borderBottom: '1px solid #2A2E39',
  cursor: 'pointer',
  transition: 'background-color 0.2s'
};

const tickerItemHoverStyle: React.CSSProperties = {
  ...tickerItemStyle,
  backgroundColor: '#2A2E39'
};

export function TickerList() {
  const [hoveredTicker, setHoveredTicker] = useState<string | null>(null);

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      background: '#1E222D',
      overflow: 'hidden'
    }}>
      {/* En-tête */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid #2A2E39'
      }}>
        <div style={{
          fontSize: '16px',
          fontWeight: 'bold',
          color: '#D1D4DC',
          marginBottom: '8px'
        }}>
          Tickers
        </div>
      </div>

      {/* Liste des tickers */}
      <div style={{
        flex: 1,
        overflowY: 'auto'
      }}>
        {tickers.map(ticker => (
          <div
            key={ticker.symbol}
            style={hoveredTicker === ticker.symbol ? tickerItemHoverStyle : tickerItemStyle}
            onMouseEnter={() => setHoveredTicker(ticker.symbol)}
            onMouseLeave={() => setHoveredTicker(null)}
          >
            <div style={{
              flex: 1
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                marginBottom: '4px'
              }}>
                <span style={{
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: '#D1D4DC'
                }}>
                  {ticker.symbol}
                </span>
                <span style={{
                  fontSize: '12px',
                  color: '#787B86'
                }}>
                  {ticker.name}
                </span>
              </div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span style={{
                  fontSize: '14px',
                  color: '#D1D4DC'
                }}>
                  ${ticker.price.toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </span>
                <span style={{
                  fontSize: '12px',
                  color: ticker.change >= 0 ? '#26A69A' : '#EF5350'
                }}>
                  {ticker.change >= 0 ? '+' : ''}{ticker.change.toFixed(2)}%
                </span>
              </div>
            </div>
            <div style={{
              textAlign: 'right'
            }}>
              <div style={{
                fontSize: '12px',
                color: '#787B86',
                marginBottom: '4px'
              }}>
                Vol
              </div>
              <div style={{
                fontSize: '12px',
                color: '#D1D4DC'
              }}>
                ${(ticker.volume / 1e6).toFixed(1)}M
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pied de liste */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid #2A2E39',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        color: '#787B86',
        fontSize: '12px'
      }}>
        <span>Volumes par exchange</span>
        <div style={{
          display: 'flex',
          gap: '8px'
        }}>
          <div>Binance 45%</div>
          <div>Coinbase 25%</div>
          <div>FTX 15%</div>
        </div>
      </div>
    </div>
  );
} 