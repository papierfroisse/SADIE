import styled from 'styled-components';
import type { TimeframeButtonProps as TimeframeProps, ToolButtonProps as ToolProps } from '../types/components';

export const TimeframeButton = styled.button.attrs<TimeframeProps>(() => ({
  type: 'button'
}))<TimeframeProps>`
  background: ${({ theme, isActive }) => isActive ? theme.buttonBackground : 'transparent'};
  color: ${({ theme, isActive }) => isActive ? theme.accent : theme.textPrimary};
  border: 1px solid ${({ theme, isActive }) => isActive ? theme.accent : theme.border};
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    background: ${({ theme }) => theme.hoverBackground};
    border-color: ${({ theme }) => theme.accent};
  }
`;

export const ToolButton = styled(TimeframeButton).attrs<ToolProps>(() => ({
  type: 'button'
}))<ToolProps>`
  padding: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  
  &:hover {
    background: ${({ theme }) => theme.hoverBackground};
  }
  
  &[data-active="true"] {
    background: ${({ theme }) => theme.buttonBackground};
    border-color: ${({ theme }) => theme.accent};
    color: ${({ theme }) => theme.accent};
  }
`; 