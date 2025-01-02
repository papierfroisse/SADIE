import React, { useState } from 'react';
import styled from 'styled-components';
import Login from './Login';
import Register from './Register';

const AuthContainer = styled.div`
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: ${({ theme }) => theme.background};
  color: ${({ theme }) => theme.textPrimary};
`;

const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <AuthContainer>
      {isLogin ? (
        <Login onSwitchToRegister={() => setIsLogin(false)} />
      ) : (
        <Register onSwitchToLogin={() => setIsLogin(true)} />
      )}
    </AuthContainer>
  );
};

export default Auth; 