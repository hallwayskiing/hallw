import type { ReactNode } from "react";

export type ColorName =
  | "emerald"
  | "orange"
  | "blue"
  | "purple"
  | "pink"
  | "cyan"
  | "amber"
  | "rose"
  | "teal"
  | "yellow";

export interface HistoryItemProps {
  id: string;
  title?: string;
  created_at?: string;
  metadata?: Record<string, unknown>;
}

export interface HistoryRowProps {
  item: HistoryItemProps;
  onLoad: () => void;
  onDelete: () => void;
}

export interface HeroSectionProps {
  isLoaded: boolean;
}

export interface QuickStartCardProps {
  icon: ReactNode;
  color: ColorName;
  text: string;
  onClick: (text: string) => void;
  delay: number;
  isLoaded: boolean;
}
