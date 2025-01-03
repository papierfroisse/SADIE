import React, { useRef, useEffect, useState } from 'react';
import styled from 'styled-components';

interface ResizablePanelProps {
  children: React.ReactNode;
  defaultHeight?: number;
  minHeight?: number;
  maxHeight?: number;
  onResize?: (height: number) => void;
}

const Container = styled.div<{ height: number }>`
  position: relative;
  width: 100%;
  height: ${props => props.height}px;
`;

const ResizeHandle = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: transparent;
  cursor: row-resize;
  z-index: 10;

  &:hover {
    background: rgba(41, 98, 255, 0.1);
  }

  &:active {
    background: rgba(41, 98, 255, 0.2);
  }

  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 30px;
    height: 2px;
    background: #2A2E39;
    border-radius: 1px;
  }
`;

export function ResizablePanel({
  children,
  defaultHeight = 200,
  minHeight = 100,
  maxHeight = 500,
  onResize
}: ResizablePanelProps) {
  const [height, setHeight] = useState(defaultHeight);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);
  const startY = useRef(0);
  const startHeight = useRef(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return;

      const deltaY = startY.current - e.clientY;
      const newHeight = Math.min(
        Math.max(startHeight.current + deltaY, minHeight),
        maxHeight
      );

      setHeight(newHeight);
      onResize?.(newHeight);
    };

    const handleMouseUp = () => {
      isDragging.current = false;
      document.body.style.cursor = 'default';
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [minHeight, maxHeight, onResize]);

  const handleMouseDown = (e: React.MouseEvent) => {
    isDragging.current = true;
    startY.current = e.clientY;
    startHeight.current = height;
    document.body.style.cursor = 'row-resize';
  };

  return (
    <Container ref={containerRef} height={height}>
      <ResizeHandle onMouseDown={handleMouseDown} />
      {children}
    </Container>
  );
} 