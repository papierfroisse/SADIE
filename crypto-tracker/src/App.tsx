import React, { useState } from 'react';
import styled from 'styled-components';
import PriceChart from './components/PriceChart';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: #171b26;
  color: #d1d4dc;
`;

const Header = styled.header`
  padding: 1rem;
  background: #1e222d;
  border-bottom: 1px solid #2b2b43;
`;

const Title = styled.h1`
  margin: 0;
  font-size: 1.5rem;
  color: #d1d4dc;
`;

const Main = styled.main`
  flex: 1;
  padding: 1rem;
`;

const Controls = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
`;

const Select = styled.select`
  padding: 0.5rem;
  background: #2b2b43;
  border: 1px solid #363a45;
  border-radius: 4px;
  color: #d1d4dc;
  cursor: pointer;

  &:hover {
    border-color: #4c525e;
  }
`;

const TimeframeButton = styled.button<{ active: boolean }>`
  padding: 0.5rem 1rem;
  background: ${props => props.active ? '#2962ff' : '#2b2b43'};
  border: 1px solid ${props => props.active ? '#2962ff' : '#363a45'};
  border-radius: 4px;
  color: #d1d4dc;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.active ? '#2962ff' : '#363a45'};
  }
`;

const App: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT');
  const [selectedExchange, setSelectedExchange] = useState('binance');
  const [selectedInterval, setSelectedInterval] = useState('1h');

  const symbols = [
    'BTCUSDT',
    'ETHUSDT',
    'BNBUSDT',
    'ADAUSDT',
    'DOGEUSDT',
    'XRPUSDT',
    'DOTUSDT',
    'UNIUSDT'
  ];

  const exchanges = [
    { value: 'binance', label: 'Binance' },
    { value: 'kraken', label: 'Kraken' }
  ];

  const intervals = [
    { value: '1m', label: '1m' },
    { value: '5m', label: '5m' },
    { value: '15m', label: '15m' },
    { value: '30m', label: '30m' },
    { value: '1h', label: '1h' },
    { value: '4h', label: '4h' },
    { value: '1d', label: '1D' }
  ];

  return (
    <AppContainer>
      <Header>
        <Title>Crypto Tracker</Title>
      </Header>
      <Main>
        <Controls>
          <Select
            value={selectedExchange}
            onChange={(e) => setSelectedExchange(e.target.value)}
          >
            {exchanges.map((exchange) => (
              <option key={exchange.value} value={exchange.value}>
                {exchange.label}
              </option>
            ))}
          </Select>

          <Select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
          >
            {symbols.map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol}
              </option>
            ))}
          </Select>

          {intervals.map((interval) => (
            <TimeframeButton
              key={interval.value}
              active={selectedInterval === interval.value}
              onClick={() => setSelectedInterval(interval.value)}
            >
              {interval.label}
            </TimeframeButton>
          ))}
        </Controls>

        <PriceChart
          symbol={selectedSymbol}
          exchange={selectedExchange}
          interval={selectedInterval}
        />
      </Main>
    </AppContainer>
  );
};

export default App; 