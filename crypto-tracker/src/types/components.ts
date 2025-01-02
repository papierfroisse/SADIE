import { Theme } from '../theme';

export interface TimeframeButtonProps {
  theme: Theme;
  isActive?: boolean;
}

export interface ToolButtonProps extends TimeframeButtonProps {
  'data-active'?: boolean;
} 