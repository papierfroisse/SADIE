import React from 'react';
import { useWebSocket } from '../context/WebSocketContext';
import './MarketOverview.css';

export function MarketOverview({ symbol }) {
  const { marketData } = useWebSocket();
  const data = marketData[symbol]?.data || {};

  const formatPrice = price => {
    return parseFloat(price).toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const formatChange = (current, previous) => {
    if (!previous) return '0.00%';
    const change = ((current - previous) / previous) * 100;
    return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
  };

  const getChangeClass = (current, previous) => {
    if (!previous) return '';
    return current >= previous ? 'positive' : 'negative';
  };

  return (
    <div className="market-overview">
      <h2>{symbol} Market Overview</h2>

      <div className="price-grid">
        <div className="price-item">
          <label>Last Price</label>
          <span className={getChangeClass(data.close, data.open)}>{formatPrice(data.close)}</span>
        </div>

        <div className="price-item">
          <label>24h Change</label>
          <span className={getChangeClass(data.close, data.open)}>
            {formatChange(data.close, data.open)}
          </span>
        </div>

        <div className="price-item">
          <label>24h High</label>
          <span>{formatPrice(data.high)}</span>
        </div>

        <div className="price-item">
          <label>24h Low</label>
          <span>{formatPrice(data.low)}</span>
        </div>

        <div className="price-item">
          <label>24h Volume</label>
          <span>{formatPrice(data.volume)}</span>
        </div>

        {data.indicators && (
          <>
            <div className="price-item">
              <label>RSI (14)</label>
              <span>{data.indicators.rsi?.toFixed(2)}</span>
            </div>

            <div className="price-item">
              <label>MACD</label>
              <span>{data.indicators.macd?.toFixed(2)}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
