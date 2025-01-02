import React from 'react';
import styled from 'styled-components';
import { ExchangeData } from '../services/exchanges';

interface CryptoListProps {
  cryptos: ExchangeData[];
  selectedCrypto: string;
  onSelectCrypto: (symbol: string) => void;
}

interface StyledProps {
  $isSelected?: boolean;
  $isPositive?: boolean;
}

const ListContainer = styled.div`
  background-color: ${({ theme }) => theme.background};
  border: 1px solid ${({ theme }) => theme.textSecondary};
  border-radius: 8px;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const ListHeader = styled.div`
  padding: 1rem;
  border-bottom: 1px solid ${({ theme }) => theme.textSecondary};
  font-weight: bold;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1rem;
`;

const ScrollableList = styled.div`
  flex: 1;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${({ theme }) => theme.background};
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${({ theme }) => theme.textSecondary};
    border-radius: 4px;
  }
`;

const CryptoItem = styled.div<StyledProps>`
  padding: 1rem;
  cursor: pointer;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 1rem;
  background-color: ${({ theme, $isSelected }) => 
    $isSelected ? theme.accent + '20' : 'transparent'};
  border-left: 4px solid ${({ theme, $isSelected }) => 
    $isSelected ? theme.accent : 'transparent'};

  &:hover {
    background-color: ${({ theme }) => theme.accent + '10'};
  }
`;

const Symbol = styled.div`
  font-weight: 500;
`;

const Price = styled.div`
  text-align: right;
`;

const Change = styled.div<StyledProps>`
  text-align: right;
  color: ${({ theme, $isPositive }) => 
    $isPositive ? '#4caf50' : '#f44336'};
`;

const formatPrice = (price: number): string => {
  if (price < 1) return price.toFixed(6);
  if (price < 100) return price.toFixed(4);
  return price.toFixed(2);
};

const formatChange = (change: number): string => {
  return (change > 0 ? '+' : '') + change.toFixed(2) + '%';
};

const CryptoList: React.FC<CryptoListProps> = ({ 
  cryptos, 
  selectedCrypto, 
  onSelectCrypto 
}) => {
  return (
    <ListContainer>
      <ListHeader>
        <div>Crypto</div>
        <div style={{ textAlign: 'right' }}>Prix</div>
        <div style={{ textAlign: 'right' }}>24h %</div>
      </ListHeader>
      <ScrollableList>
        {cryptos.map((crypto) => (
          <CryptoItem
            key={crypto.symbol}
            $isSelected={crypto.symbol === selectedCrypto}
            onClick={() => onSelectCrypto(crypto.symbol)}
          >
            <Symbol>{crypto.baseAsset}</Symbol>
            <Price>${formatPrice(crypto.price)}</Price>
            <Change $isPositive={crypto.priceChangePercent >= 0}>
              {formatChange(crypto.priceChangePercent)}
            </Change>
          </CryptoItem>
        ))}
      </ScrollableList>
    </ListContainer>
  );
};

export default CryptoList; 