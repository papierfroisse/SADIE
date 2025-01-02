import styled from 'styled-components';
import { Theme } from '../theme';

export const TimeframeButton = styled.button<{ active?: boolean; theme: Theme }>`
  background: ${({ active, theme }) => active ? theme.accent : theme.buttonBackground};
  color: ${({ active, theme }) => active ? '#ffffff' : theme.buttonText};
  border: 1px solid ${({ theme }) => theme.border};
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${({ active, theme }) => active ? theme.accent : theme.hoverBackground};
  }
`;

export const ToolButton = styled.button<{ active?: boolean; theme: Theme }>`
  background: ${({ active, theme }) => active ? theme.accent : 'transparent'};
  color: ${({ active, theme }) => active ? '#ffffff' : theme.buttonText};
  border: none;
  padding: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  width: 100%;

  &:hover {
    background: ${({ theme }) => theme.hoverBackground};
  }
`; 