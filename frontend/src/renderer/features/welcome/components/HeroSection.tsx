import { cn } from "@lib/utils";

import { useAppStore } from "@store/store";
import { useState } from "react";

import type { HeroSectionProps } from "../types";

export function HeroSection({ isLoaded }: HeroSectionProps) {
  const theme = useAppStore((s) => s.theme);
  const [spinTick, setSpinTick] = useState(0);
  const isDark = theme === "dark";

  return (
    <div className="flex-1 flex items-center justify-center z-10 pointer-events-none">
      <div
        className={cn(
          "flex flex-col items-center transition-all duration-700 ease-out",
          isLoaded ? "opacity-100 scale-100" : "opacity-0 scale-95"
        )}
      >
        <div
          className={cn(
            "relative mb-8 transition-all duration-500 delay-100",
            isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          )}
        >
          <div
            className={cn(
              "relative w-28 h-28 flex items-center justify-center perspective-midrange",
              isDark && "animate-hero-drift"
            )}
          >
            {/* Stable Gradient Definition */}
            <svg className="absolute w-0 h-0" aria-hidden="true">
              <defs>
                <linearGradient id="hero-gradient" x1="0" y1="0" x2="0" y2="200" gradientUnits="userSpaceOnUse">
                  <stop offset="0" stopColor="#05B6FF" />
                  <stop offset="0.166" stopColor="#8D46FF" />
                  <stop offset="0.333" stopColor="#FF5B37" />
                  <stop offset="0.5" stopColor="#05B6FF" />
                  <stop offset="0.666" stopColor="#8D46FF" />
                  <stop offset="0.833" stopColor="#FF5B37" />
                  <stop offset="1" stopColor="#05B6FF" />
                  <animateTransform
                    attributeName="gradientTransform"
                    type="translate"
                    from="0 0"
                    to="0 -100"
                    dur="30s"
                    repeatCount="indefinite"
                  />
                </linearGradient>
              </defs>
            </svg>

            <button
              type="button"
              key={spinTick}
              onClick={() => setSpinTick((v) => v + 1)}
              className="relative w-18 h-18 pointer-events-auto cursor-pointer animate-hero-spin-y"
            >
              <svg viewBox="0 0 100 100" className="relative w-18 h-18" aria-hidden="true">
                <path
                  d="M50 0 C53 16 58 32 96 50 C58 68 53 84 50 100 C47 84 42 68 4 50 C42 32 47 16 50 0 Z"
                  fill="url(#hero-gradient)"
                />
              </svg>
            </button>
          </div>
        </div>

        <h1
          className={cn(
            "text-[28px] font-light tracking-[0.3em] text-foreground/95 mb-1 transition-all duration-500 delay-200",
            isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          )}
        >
          HALLW
        </h1>

        <p
          className={cn(
            "text-[12px] text-muted-foreground/60 tracking-[0.2em] uppercase transition-all duration-500 delay-300",
            isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          )}
        >
          Autonomous Workspace
        </p>
      </div>
    </div>
  );
}
