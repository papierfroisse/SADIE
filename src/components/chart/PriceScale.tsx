import React from 'react';
import styled from 'styled-components';

interface PriceScaleProps {
  min: number;
  max: number;
  height: number;
  position?: 'left' | 'right';
}

const ScaleContainer = styled.div<{ position: 'left' | 'right' }>`
  position: absolute;
  top: 0;
  ${props => props.position}: 0;
  width: 50px;
  height: 100%;
  background: #131722;
  border-${props => props.position}: 1px solid #2A2E39;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 0;
  z-index: 2;
`;

const PriceLabel = styled.div<{ position: 'left' | 'right' }>`
  color: #787B86;
  font-size: 11px;
  padding: 2px 8px;
  text-align: ${props => props.position};
  white-space: nowrap;
`;

export function PriceScale({ min, max, height, position = 'right' }: PriceScaleProps) {
  const priceRange = max - min;
  const numLabels = Math.floor(height / 50); // Un label tous les 50px environ
  const step = priceRange / (numLabels - 1);

  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return price.toLocaleString(undefined, { maximumFractionDigits: 0 });
    }
    if (price >= 1) {
      return price.toLocaleString(undefined, { maximumFractionDigits: 2 });
    }
    return price.toLocaleString(undefined, { maximumFractionDigits: 6 });
  };

  return (
    <ScaleContainer position={position}>
      {Array.from({ length: numLabels }).map((_, i) => {
        const price = max - (i * step);
        return (
          <PriceLabel key={i} position={position}>
            {formatPrice(price)}
          </PriceLabel>
        );
      })}
    </ScaleContainer>
  );
} 