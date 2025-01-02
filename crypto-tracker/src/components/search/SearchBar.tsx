import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { FaSearch } from 'react-icons/fa';
import { ExchangeData } from '../../services/exchanges';

interface SearchBarProps {
  cryptos: ExchangeData[];
  onSelectCrypto: (symbol: string) => void;
}

const SearchContainer = styled.div`
  position: relative;
  width: 100%;
  margin-bottom: 1rem;
`;

const SearchInput = styled.input`
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid ${({ theme }) => theme.textSecondary};
  border-radius: 8px;
  background-color: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.textPrimary};
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.accent};
  }
`;

const SearchIcon = styled(FaSearch)`
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: ${({ theme }) => theme.textSecondary};
`;

const ResultsContainer = styled.div`
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background-color: ${({ theme }) => theme.background};
  border: 1px solid ${({ theme }) => theme.textSecondary};
  border-radius: 8px;
  margin-top: 0.5rem;
  z-index: 10;
  
  &:empty {
    display: none;
  }
`;

const ResultItem = styled.div<{ $isHighlighted: boolean }>`
  padding: 0.75rem 1rem;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: ${({ theme, $isHighlighted }) => 
    $isHighlighted ? theme.accent + '20' : 'transparent'};
  
  &:hover {
    background-color: ${({ theme }) => theme.accent + '20'};
  }
`;

const Symbol = styled.span`
  font-weight: 500;
`;

const BaseAsset = styled.span`
  color: ${({ theme }) => theme.textSecondary};
`;

const SearchBar: React.FC<SearchBarProps> = ({ cryptos, onSelectCrypto }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState<ExchangeData[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (searchTerm.trim() === '') {
      setResults([]);
      return;
    }

    const filtered = cryptos.filter(crypto => 
      crypto.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      crypto.baseAsset.toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, 10);

    setResults(filtered);
    setHighlightedIndex(-1);
  }, [searchTerm, cryptos]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex(prev => 
        prev < results.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex(prev => prev > 0 ? prev - 1 : -1);
    } else if (e.key === 'Enter' && highlightedIndex >= 0) {
      onSelectCrypto(results[highlightedIndex].symbol);
      setSearchTerm('');
      setResults([]);
    } else if (e.key === 'Escape') {
      setSearchTerm('');
      setResults([]);
    }
  };

  const handleClickOutside = (e: MouseEvent) => {
    if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
      setResults([]);
    }
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <SearchContainer ref={containerRef}>
      <SearchInput
        type="text"
        placeholder="Rechercher une crypto..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <SearchIcon />
      <ResultsContainer>
        {results.map((crypto, index) => (
          <ResultItem
            key={crypto.symbol}
            $isHighlighted={index === highlightedIndex}
            onClick={() => {
              onSelectCrypto(crypto.symbol);
              setSearchTerm('');
              setResults([]);
            }}
          >
            <Symbol>{crypto.symbol}</Symbol>
            <BaseAsset>{crypto.baseAsset}</BaseAsset>
          </ResultItem>
        ))}
      </ResultsContainer>
    </SearchContainer>
  );
};

export default SearchBar; 