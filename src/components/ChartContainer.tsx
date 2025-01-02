import styled from 'styled-components';

export const ChartContainer = styled.div`
  width: 100%;
  height: 600px;
  background-color: ${({ theme }) => theme.background};
  border: 1px solid ${({ theme }) => theme.textSecondary};
  border-radius: 8px;
  overflow: hidden;
`; 