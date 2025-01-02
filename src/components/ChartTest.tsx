import React from 'react';
import styled from 'styled-components';
import { Chart } from './Chart';
import { Candle } from '../renderer/CandlestickRenderer';

const TestContainer = styled.div`
  width: 1200px;
  height: 800px;
  background-color: #131722;
  border: 1px solid #2a2a2a;
  border-radius: 4px;
  overflow: hidden;
`;

// Génération de données de test
const generateTestData = (count: number): Candle[] => {
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;
  const data: Candle[] = [];

  let lastClose = 100;
  const baseVolume = 1000000;

  for (let i = 0; i < count; i++) {
    const time = now - (count - i) * oneDay;
    const volatility = 2;
    const change = (Math.random() - 0.5) * volatility;
    const open = lastClose;
    const close = open * (1 + change);
    const high = Math.max(open, close) * (1 + Math.random() * 0.003);
    const low = Math.min(open, close) * (1 - Math.random() * 0.003);
    const volume = baseVolume * (1 + Math.random());

    data.push({
      time,
      open,
      high,
      low,
      close,
      volume
    });

    lastClose = close;
  }

  return data;
};

export const ChartTest: React.FC = () => {
  const testData = generateTestData(200);  // 200 jours de données

  return (
    <TestContainer>
      <Chart 
        symbol="BTC/USD"
        interval="1D"
        candles={testData}
      />
    </TestContainer>
  );
}; 