import { useRef, useEffect } from 'react';

interface ChartSyncOptions {
  onRangeChange?: (start: number, end: number) => void;
  onZoom?: (factor: number, center: number) => void;
  onPan?: (delta: number) => void;
}

export function useChartSync(options: ChartSyncOptions = {}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);
  const lastX = useRef(0);
  const visibleRange = useRef({ start: 0, end: 0 });
  const zoomLevel = useRef(1);

  useEffect(() => {
    if (!containerRef.current) return;

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();

      // Zoom
      if (e.ctrlKey) {
        const rect = containerRef.current!.getBoundingClientRect();
        const centerX = (e.clientX - rect.left) / rect.width;
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;

        zoomLevel.current *= zoomFactor;
        options.onZoom?.(zoomFactor, centerX);
      }
      // Pan horizontal
      else {
        const delta = e.deltaX;
        if (delta !== 0) {
          options.onPan?.(delta);
        }
      }
    };

    const handleMouseDown = (e: MouseEvent) => {
      isDragging.current = true;
      lastX.current = e.clientX;
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging.current) return;

      const deltaX = e.clientX - lastX.current;
      lastX.current = e.clientX;

      if (deltaX !== 0) {
        options.onPan?.(deltaX);
      }
    };

    const handleMouseUp = () => {
      isDragging.current = false;
    };

    const element = containerRef.current;
    element.addEventListener('wheel', handleWheel, { passive: false });
    element.addEventListener('mousedown', handleMouseDown);
    element.addEventListener('mousemove', handleMouseMove);
    element.addEventListener('mouseup', handleMouseUp);
    element.addEventListener('mouseleave', handleMouseUp);

    return () => {
      element.removeEventListener('wheel', handleWheel);
      element.removeEventListener('mousedown', handleMouseDown);
      element.removeEventListener('mousemove', handleMouseMove);
      element.removeEventListener('mouseup', handleMouseUp);
      element.removeEventListener('mouseleave', handleMouseUp);
    };
  }, [options]);

  const setVisibleRange = (start: number, end: number) => {
    visibleRange.current = { start, end };
    options.onRangeChange?.(start, end);
  };

  return {
    containerRef,
    visibleRange: visibleRange.current,
    zoomLevel: zoomLevel.current,
    setVisibleRange
  };
} 