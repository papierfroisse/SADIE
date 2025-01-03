import React from 'react';
import styled from 'styled-components';
import { Logo } from './Logo';

interface AppLayoutProps {
  children: React.ReactNode;
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #131722;
`;

const Header = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
  padding: 0 16px;
  background: #1E222D;
  border-bottom: 1px solid #2A2E39;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
  gap: 48px;
`;

const Navigation = styled.nav`
  display: flex;
  gap: 24px;
`;

const NavLink = styled.a<{ active?: boolean }>`
  color: ${props => props.active ? '#D1D4DC' : '#787B86'};
  text-decoration: none;
  font-size: 14px;
  
  &:hover {
    color: #D1D4DC;
  }
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const LoginButton = styled.button`
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #2962FF;
  border-radius: 4px;
  color: #2962FF;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: rgba(41, 98, 255, 0.1);
  }
`;

const SettingsButton = styled.button`
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #787B86;
  cursor: pointer;
  font-size: 18px;
  
  &:hover {
    color: #D1D4DC;
  }
`;

const Main = styled.main`
  flex: 1;
  overflow: hidden;
`;

export function AppLayout({ children }: AppLayoutProps) {
  return (
    <Container>
      <Header>
        <LeftSection>
          <Logo />
          <Navigation>
            <NavLink href="#" active>Graphiques</NavLink>
            <NavLink href="#">Screener</NavLink>
            <NavLink href="#">Marchés</NavLink>
            <NavLink href="#">Actualités</NavLink>
            <NavLink href="#">Plus</NavLink>
          </Navigation>
        </LeftSection>

        <RightSection>
          <LoginButton>Se connecter</LoginButton>
          <SettingsButton>⚙️</SettingsButton>
        </RightSection>
      </Header>

      <Main>
        {children}
      </Main>
    </Container>
  );
} 