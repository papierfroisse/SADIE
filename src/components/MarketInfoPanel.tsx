import React from 'react';

interface MarketInfo {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high24h: number;
  low24h: number;
  marketCap: number;
  totalVolume: number;
}

interface MarketInfoPanelProps {
  data: MarketInfo;
}

export function MarketInfoPanel({ data }: MarketInfoPanelProps) {
  const formatNumber = (num: number, decimals: number = 2): string => {
    if (Math.abs(num) >= 1_000_000_000) {
      return `${(num / 1_000_000_000).toFixed(decimals)}B`;
    }
    if (Math.abs(num) >= 1_000_000) {
      return `${(num / 1_000_000).toFixed(decimals)}M`;
    }
    if (Math.abs(num) >= 1_000) {
      return `${(num / 1_000).toFixed(decimals)}K`;
    }
    return num.toFixed(decimals);
  };

  const InfoRow = ({ label, value, color = '#D1D4DC' }: { label: string; value: string; color?: string }) => (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '4px 0'
    }}>
      <span style={{ color: '#787B86', fontSize: '12px' }}>{label}</span>
      <span style={{ color, fontSize: '12px', fontWeight: 'bold' }}>{value}</span>
    </div>
  );

  return (
    <div style={{
      width: '300px',
      background: '#1E222D',
      borderLeft: '1px solid #363A45',
      height: '100%',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* En-tête */}
      <div style={{
        padding: '16px',
        borderBottom: '1px solid #363A45'
      }}>
        <div style={{
          fontSize: '20px',
          fontWeight: 'bold',
          color: '#D1D4DC',
          marginBottom: '8px'
        }}>
          Aperçu du marché
        </div>
        <div style={{
          fontSize: '24px',
          fontWeight: 'bold',
          color: '#D1D4DC',
          marginBottom: '4px'
        }}>
          ${data.price.toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          })}
        </div>
        <div style={{
          fontSize: '14px',
          color: data.change >= 0 ? '#26A69A' : '#EF5350'
        }}>
          {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)} ({data.changePercent.toFixed(2)}%)
        </div>
      </div>

      {/* Statistiques */}
      <div style={{ padding: '16px' }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#D1D4DC',
          marginBottom: '12px'
        }}>
          Statistiques
        </div>

        <InfoRow 
          label="Volume 24h" 
          value={`$${formatNumber(data.volume)}`} 
        />
        <InfoRow 
          label="Plus haut 24h" 
          value={`$${formatNumber(data.high24h)}`}
          color="#26A69A" 
        />
        <InfoRow 
          label="Plus bas 24h" 
          value={`$${formatNumber(data.low24h)}`}
          color="#EF5350" 
        />
        <InfoRow 
          label="Cap. marché" 
          value={`$${formatNumber(data.marketCap)}`} 
        />
        <InfoRow 
          label="Volume total" 
          value={`$${formatNumber(data.totalVolume)}`} 
        />
      </div>

      {/* Graphiques supplémentaires */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid #363A45',
        marginTop: 'auto'
      }}>
        <div style={{
          fontSize: '14px',
          fontWeight: 'bold',
          color: '#D1D4DC',
          marginBottom: '12px'
        }}>
          Volumes par exchange
        </div>

        {/* Mini graphique en barres */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          {[
            { name: 'Binance', volume: 45 },
            { name: 'Coinbase', volume: 25 },
            { name: 'FTX', volume: 15 },
            { name: 'Kraken', volume: 10 },
            { name: 'Autres', volume: 5 }
          ].map(exchange => (
            <div key={exchange.name} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                flex: 1,
                height: '24px',
                background: '#2A2E39',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  width: `${exchange.volume}%`,
                  height: '100%',
                  background: '#2962FF',
                  transition: 'width 0.3s ease'
                }} />
              </div>
              <span style={{ color: '#787B86', fontSize: '12px', minWidth: '60px' }}>
                {exchange.name}
              </span>
              <span style={{ color: '#D1D4DC', fontSize: '12px', minWidth: '40px', textAlign: 'right' }}>
                {exchange.volume}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 