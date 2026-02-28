import { cn } from "@lib/utils";
import { useAppStore } from "@store/store";
import { RefreshCw, Zap } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { ALL_QUICK_STARTS, COLOR_MAP } from "../constants";
import type { ColorName, QuickStartCardProps } from "../types";

function QuickStartCard({ icon, color, text, onClick, delay, isLoaded, disabled }: QuickStartCardProps) {
  const colors = COLOR_MAP[color] || COLOR_MAP.blue;
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isLoaded) {
      const timer = setTimeout(() => setIsVisible(true), delay);
      return () => clearTimeout(timer);
    } else {
      setIsVisible(false);
    }
  }, [isLoaded, delay]);

  return (
    <button
      type="button"
      onClick={() => !disabled && onClick(text)}
      disabled={disabled}
      className={cn(
        "group w-full flex items-center gap-3 p-3 text-left rounded-xl",
        "bg-card/20 backdrop-blur-sm border border-border/30",
        "transition-all duration-400 ease-out",
        colors.bg,
        colors.border,
        "hover:shadow-lg hover:-translate-y-0.5",
        "active:scale-[0.99]",
        isVisible ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-8",
        disabled && "opacity-50 cursor-not-allowed pointer-events-none"
      )}
    >
      <div
        className={cn(
          "flex items-center justify-center w-7 h-7 rounded-lg bg-white/5 shrink-0",
          "transition-all duration-200 group-hover:bg-white/10 group-hover:shadow-lg",
          colors.icon,
          colors.glow
        )}
      >
        {icon}
      </div>
      <span className="flex-1 text-[14px] text-muted-foreground/80 group-hover:text-foreground transition-colors duration-200">
        {text}
      </span>
      <span className="text-muted-foreground/20 group-hover:text-foreground/40 transition-all duration-200">→</span>
    </button>
  );
}

export function QuickStartList({
  onQuickStart,
  isVisible,
  disabled,
}: {
  onQuickStart: (text: string) => void;
  isVisible: boolean;
  disabled?: boolean;
}) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [refreshKey, setRefreshKey] = useState(1);
  const [rotation, setRotation] = useState(0);
  const theme = useAppStore((s) => s.theme);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const getRandomQuickStarts = useCallback(() => {
    const shuffled = [...ALL_QUICK_STARTS].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, 3);
  }, []);

  const [quickStarts, setQuickStarts] = useState(getRandomQuickStarts);

  const handleRefresh = (e: React.MouseEvent) => {
    e.stopPropagation();
    setRefreshKey((prev) => prev + 1);
    setRotation((prev) => prev + 180);
    setQuickStarts(getRandomQuickStarts());
  };

  return (
    <div
      className={cn(
        "absolute inset-x-0 top-0 bottom-0 flex flex-col px-1 transition-all duration-500",
        !isVisible ? "opacity-0 pointer-events-none z-0" : "opacity-100 z-10"
      )}
    >
      <div
        className={cn(
          "flex items-center justify-between mb-4 min-h-[30px] transition-all duration-500 ease-in-out",
          !isVisible ? "-translate-y-2" : "translate-y-0"
        )}
      >
        {/* Header */}
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center w-5 h-5 shrink-0">
            {theme === "dark" && (
              <div className="absolute inset-0 bg-amber-400/60 blur-lg rounded-full animate-pulse" />
            )}
            <Zap
              className={cn(
                "relative w-3.5 h-3.5",
                theme === "dark" ? "text-amber-400 drop-shadow-[0_0_4px_rgba(251,191,36,0.8)]" : "text-amber-600"
              )}
            />
          </div>
          <span
            className={cn(
              "text-[13px] uppercase tracking-[0.2em] whitespace-nowrap",
              theme === "dark"
                ? "font-light text-amber-300 drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]"
                : "font-medium text-amber-600"
            )}
          >
            Quick Start
          </span>
        </div>
        {/* Refresh Button */}
        <button
          type="button"
          onClick={handleRefresh}
          className={cn(
            "group p-1.5 rounded-lg text-muted-foreground/40 hover:text-foreground/60 hover:bg-white/5 transition-all duration-200 active:scale-90",
            !isVisible ? "opacity-0 pointer-events-none" : "opacity-100"
          )}
          title="Shuffle prompts"
        >
          <RefreshCw
            className="w-4.5 h-4.5 transition-transform duration-500"
            style={{ transform: `rotate(${rotation}deg)` }}
          />
        </button>
      </div>
      {/* Main Area */}
      <div
        className={cn(
          "grid grid-cols-1 gap-3 transition-all duration-500 ease-in-out",
          !isVisible ? "scale-95 -translate-x-8" : "scale-100 translate-x-0"
        )}
      >
        {quickStarts.map((item, idx) => (
          <QuickStartCard
            key={`${refreshKey}-${item.text}`}
            icon={item.icon}
            color={item.color as ColorName}
            text={item.text}
            onClick={onQuickStart}
            delay={100 + idx * 100}
            isLoaded={isLoaded}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  );
}
