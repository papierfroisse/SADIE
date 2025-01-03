import React from 'react';
import styled from 'styled-components';

const LogoContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
`;

const LogoText = styled.span`
  color: #D1D4DC;
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.5px;
`;

const LogoIcon = styled.span`
  color: #2962FF;
  font-size: 24px;
`;

export function Logo() {
  return (
    <LogoContainer>
      <LogoIcon>📈</LogoIcon>
      <LogoText>CryptoChart Pro</LogoText>
    </LogoContainer>
  );
} 