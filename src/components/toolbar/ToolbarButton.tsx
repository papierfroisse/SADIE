import React from 'react';
import styled from 'styled-components';

interface ToolbarButtonProps {
  icon?: React.ReactNode;
  label?: string;
  active?: boolean;
  onClick?: () => void;
  title?: string;
  disabled?: boolean;
}

const Button = styled.button<{ $active?: boolean }>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: ${props => props.children && typeof props.children === 'string' ? '6px 12px' : '6px'};
  background: ${props => props.$active ? '#2962FF' : 'transparent'};
  border: 1px solid ${props => props.$active ? '#2962FF' : '#363A45'};
  border-radius: 4px;
  color: ${props => props.$active ? '#FFFFFF' : '#D1D4DC'};
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: ${props => props.children && typeof props.children === 'string' ? 'auto' : '32px'};
  min-height: 32px;

  &:hover:not(:disabled) {
    background: ${props => props.$active ? '#2962FF' : '#2A2E39'};
    border-color: ${props => props.$active ? '#2962FF' : '#2962FF'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  svg {
    width: 16px;
    height: 16px;
  }
`;

export function ToolbarButton({ 
  icon, 
  label, 
  active, 
  onClick, 
  title,
  disabled
}: ToolbarButtonProps) {
  return (
    <Button
      onClick={onClick}
      $active={active}
      title={title}
      disabled={disabled}
    >
      {icon}
      {label}
    </Button>
  );
} 