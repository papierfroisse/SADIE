import React from 'react';
import styled from 'styled-components';
import { ChartTest } from './components/ChartTest';

const AppContainer = styled.div`
  width: 100vw;
  height: 100vh;
  background-color: #1e222d;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  box-sizing: border-box;
`;

function App() {
  return (
    <AppContainer>
      <ChartTest />
    </AppContainer>
  );
}

export default App; 