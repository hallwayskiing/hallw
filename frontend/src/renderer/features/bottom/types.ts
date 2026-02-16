import type { LucideIcon } from "lucide-react";
import type { FormEvent } from "react";

export interface ActionButtonProps {
  onClick: () => void;
  icon: LucideIcon;
  tooltip?: string;
  active?: boolean;
  className?: string;
}

export interface ChatInputProps {
  value: string;
  onChange: (val: string) => void;
  onKeyDown?: (e: React.KeyboardEvent) => void;
  disabled?: boolean;
  isFocused: boolean;
  placeholder?: string;
  onFocus?: () => void;
  onBlur?: () => void;
  className?: string;
}

export interface SubmitButtonProps {
  isRunning: boolean;
  hasInput: boolean;
  onStop: () => void;
  onSubmit: (e?: FormEvent) => void;
  className?: string;
}
