import React from 'react';
import styled from 'styled-components';

interface CryptoData {
  symbol: string;
  name: string;
  price: string;
  change: string;
}

const Container = styled.div`
  background: #1E222D;
  border-left: 1px solid #2A2E39;
  width: 160px;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  padding: 6px 12px;
  border-bottom: 1px solid #2A2E39;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 32px;
`;

const Title = styled.div`
  color: #787B86;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
`;

const List = styled.div`
  flex: 1;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: #363A45;
    border-radius: 2px;
  }
`;

const CryptoItem = styled.div`
  padding: 6px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  cursor: pointer;
  border-bottom: 1px solid #2A2E39;
  font-size: 12px;

  &:hover {
    background: #2A2E39;
  }
`;

const SymbolRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Symbol = styled.div`
  color: #D1D4DC;
  font-weight: 500;
`;

const Price = styled.div`
  color: #D1D4DC;
  font-size: 12px;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Name = styled.div`
  color: #787B86;
  font-size: 11px;
`;

interface StyledChangeProps {
  $positive: boolean;
}

const Change = styled.div<StyledChangeProps>`
  color: ${props => props.$positive ? '#26A69A' : '#EF5350'};
  font-size: 11px;
`;

const mockData: CryptoData[] = [
  { symbol: 'BTC', name: 'Bitcoin', price: '$50,000', change: '+2.5%' },
  { symbol: 'ETH', name: 'Ethereum', price: '$3,000', change: '+1.8%' },
  { symbol: 'BNB', name: 'BNB', price: '$400', change: '-0.5%' },
  { symbol: 'SOL', name: 'Solana', price: '$100', change: '+3.2%' },
  { symbol: 'ADA', name: 'Cardano', price: '$0.5', change: '-1.2%' },
];

interface TopCryptosProps {
  onSelect?: (symbol: string) => void;
}

export const TopCryptos: React.FC<TopCryptosProps> = ({ onSelect }) => {
  return (
    <Container>
      <Header>
        <Title>Top Cryptos</Title>
      </Header>
      <List>
        {mockData.map(crypto => (
          <CryptoItem 
            key={crypto.symbol}
            onClick={() => onSelect?.(crypto.symbol + 'USDT')}
          >
            <SymbolRow>
              <Symbol>{crypto.symbol}</Symbol>
              <Price>{crypto.price}</Price>
            </SymbolRow>
            <InfoRow>
              <Name>{crypto.name}</Name>
              <Change $positive={crypto.change.startsWith('+')}>
                {crypto.change}
              </Change>
            </InfoRow>
          </CryptoItem>
        ))}
      </List>
    </Container>
  );
}; 