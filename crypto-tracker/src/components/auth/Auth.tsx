import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Login from './Login';
import Register from './Register';

const AuthContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ theme }) => theme.background};
`;

const Auth: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);

  useEffect(() => {
    console.log('Auth component mounted');
  }, []);

  console.log('Auth component rendering, isLogin:', isLogin);

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