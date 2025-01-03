import { useRef, useCallback } from 'react';

interface AnimationState {
  startTime: number;
  startValue: number;
  endValue: number;
  duration: number;
  onUpdate: (value: number) => void;
}

export function useChartAnimation() {
  const animationRef = useRef<number>();
  const animationStateRef = useRef<AnimationState | null>(null);

  const animate = useCallback((
    startValue: number,
    endValue: number,
    duration: number,
    onUpdate: (value: number) => void
  ) => {
    // Annuler l'animation précédente si elle existe
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    // Initialiser l'état de l'animation
    animationStateRef.current = {
      startTime: performance.now(),
      startValue,
      endValue,
      duration,
      onUpdate
    };

    // Fonction d'animation
    const animateFrame = (currentTime: number) => {
      const state = animationStateRef.current;
      if (!state) return;

      const elapsed = currentTime - state.startTime;
      const progress = Math.min(elapsed / state.duration, 1);

      // Fonction d'easing
      const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);
      const easedProgress = easeOutCubic(progress);

      // Calculer la valeur courante
      const currentValue = state.startValue + (state.endValue - state.startValue) * easedProgress;
      state.onUpdate(currentValue);

      // Continuer l'animation si elle n'est pas terminée
      if (progress < 1) {
        animationRef.current = requestAnimationFrame(animateFrame);
      } else {
        animationStateRef.current = null;
      }
    };

    // Démarrer l'animation
    animationRef.current = requestAnimationFrame(animateFrame);
  }, []);

  const cancelAnimation = useCallback(() => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
      animationStateRef.current = null;
    }
  }, []);

  return {
    animate,
    cancelAnimation,
    isAnimating: !!animationStateRef.current
  };
} 