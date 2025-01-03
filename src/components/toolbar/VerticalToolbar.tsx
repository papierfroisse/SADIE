import React from 'react';
import styled from 'styled-components';
import { DrawingToolType } from '../../renderer/DrawingTools';

interface VerticalToolbarProps {
  selectedTool: DrawingToolType;
  onToolSelect: (tool: DrawingToolType) => void;
}

const Container = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1px;
  background: #1E222D;
  border-right: 1px solid #2A2E39;
  padding: 8px 4px;
  width: 40px;
`;

const Group = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1px;
  
  &:not(:last-child) {
    margin-bottom: 8px;
    padding-bottom: 8px;
    border-bottom: 1px solid #2A2E39;
  }
`;

const Button = styled.button<{ $active?: boolean }>`
  background: ${props => props.$active ? '#2962FF' : 'transparent'};
  border: none;
  color: ${props => props.$active ? '#FFFFFF' : '#787B86'};
  padding: 6px;
  font-size: 13px;
  cursor: pointer;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: ${props => props.$active ? '#2962FF' : '#363A45'};
    color: ${props => props.$active ? '#FFFFFF' : '#D1D4DC'};
  }

  svg {
    width: 20px;
    height: 20px;
  }
`;

export function VerticalToolbar({ selectedTool, onToolSelect }: VerticalToolbarProps) {
  return (
    <Container>
      <Group>
        <Button 
          $active={selectedTool === 'cursor'} 
          onClick={() => onToolSelect('cursor')}
          title="Curseur"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M13.64,21.97C13.14,22.21 12.54,22 12.31,21.5L10.13,16.76L7.62,18.78C7.45,18.92 7.24,19 7,19A1,1 0 0,1 6,18V3A1,1 0 0,1 7,2C7.24,2 7.47,2.09 7.64,2.23L7.65,2.22L19.14,11.86C19.57,12.22 19.62,12.85 19.27,13.27C19.12,13.45 18.91,13.57 18.7,13.61L15.54,14.23L17.74,18.96C18,19.46 17.76,20.05 17.26,20.28L13.64,21.97Z"/>
          </svg>
        </Button>
        <Button 
          $active={selectedTool === 'crosshair'} 
          onClick={() => onToolSelect('crosshair')}
          title="Réticule"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M3.05,13H1V11H3.05C3.5,6.83 6.83,3.5 11,3.05V1H13V3.05C17.17,3.5 20.5,6.83 20.95,11H23V13H20.95C20.5,17.17 17.17,20.5 13,20.95V23H11V20.95C6.83,20.5 3.5,17.17 3.05,13M12,5A7,7 0 0,0 5,12A7,7 0 0,0 12,19A7,7 0 0,0 19,12A7,7 0 0,0 12,5Z"/>
          </svg>
        </Button>
      </Group>

      <Group>
        <Button 
          $active={selectedTool === 'line'} 
          onClick={() => onToolSelect('line')}
          title="Ligne"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,13H5V11H19V13Z"/>
          </svg>
        </Button>
        <Button 
          $active={selectedTool === 'horizontalLine'} 
          onClick={() => onToolSelect('horizontalLine')}
          title="Ligne horizontale"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M22,12H2V14H22V12Z"/>
          </svg>
        </Button>
        <Button 
          $active={selectedTool === 'verticalLine'} 
          onClick={() => onToolSelect('verticalLine')}
          title="Ligne verticale"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M12,2V22H14V2H12Z"/>
          </svg>
        </Button>
        <Button 
          $active={selectedTool === 'rectangle'} 
          onClick={() => onToolSelect('rectangle')}
          title="Rectangle"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,3H5C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3M19,19H5V5H19V19Z"/>
          </svg>
        </Button>
        <Button 
          $active={selectedTool === 'fibonacci'} 
          onClick={() => onToolSelect('fibonacci')}
          title="Retracement de Fibonacci"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,4H5A2,2 0 0,0 3,6V18A2,2 0 0,0 5,20H19A2,2 0 0,0 21,18V6A2,2 0 0,0 19,4M19,18H5V6H19V18M7,8H17V10H7V8M7,12H17V14H7V12M7,16H14V18H7V16Z"/>
          </svg>
        </Button>
      </Group>

      <Group>
        <Button 
          $active={selectedTool === 'measure'} 
          onClick={() => onToolSelect('measure')}
          title="Mesure"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M1.39,18.36L3.16,16.6L4.58,18L5.64,16.95L4.22,15.54L5.64,14.12L8.11,16.6L9.17,15.54L6.7,13.06L8.11,11.65L9.53,13.06L10.59,12L9.17,10.59L10.59,9.17L13.06,11.65L14.12,10.59L11.65,8.11L13.06,6.7L14.47,8.11L15.54,7.05L14.12,5.64L15.54,4.22L18,6.7L19.07,5.64L17.66,4.22L19.07,2.81L20.14,3.88L21.19,2.81L13.06,10.94L13.06,10.94L3.88,20.12L2.81,19.07L3.88,18L2.81,16.95L4.22,15.54L2.81,14.47L1.39,18.36Z"/>
          </svg>
        </Button>
        <Button 
          $active={selectedTool === 'text'} 
          onClick={() => onToolSelect('text')}
          title="Texte"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M18.5,4L19.66,8.35L18.7,8.61C18.25,7.74 17.79,6.87 17.26,6.43C16.73,6 16.11,6 15.5,6H13V16.5C13,17 13,17.5 13.33,17.75C13.67,18 14.33,18 15,18V19H9V18C9.67,18 10.33,18 10.67,17.75C11,17.5 11,17 11,16.5V6H8.5C7.89,6 7.27,6 6.74,6.43C6.21,6.87 5.75,7.74 5.3,8.61L4.34,8.35L5.5,4H18.5Z"/>
          </svg>
        </Button>
      </Group>

      <Group>
        <Button 
          onClick={() => console.log('Zoom in')}
          title="Zoom avant"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z"/>
          </svg>
        </Button>
        <Button 
          onClick={() => console.log('Zoom out')}
          title="Zoom arrière"
        >
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M19,13H5V11H19V13Z"/>
          </svg>
        </Button>
      </Group>
    </Container>
  );
} 