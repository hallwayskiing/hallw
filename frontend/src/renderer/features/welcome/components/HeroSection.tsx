import { cn } from "@lib/utils";

import { useAppStore } from "@store/store";
import { useState } from "react";

import type { HeroSectionProps } from "../types";

export function HeroSection({ isLoaded }: HeroSectionProps) {
  const { theme } = useAppStore();
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
            {isDark && (
              <>
                <div className="absolute w-40 h-40 rounded-full bg-sky-400/12 blur-3xl animate-stellar-halo" />
                <div className="absolute w-24 h-24 rounded-full bg-cyan-300/16 blur-2xl animate-stellar-halo" />
              </>
            )}

            <button
              type="button"
              key={spinTick}
              onClick={() => setSpinTick((v) => v + 1)}
              className="relative w-16 h-16 pointer-events-auto cursor-pointer animate-hero-spin-y"
            >
              <svg
                viewBox="0 0 100 100"
                className={cn(
                  "relative w-16 h-16",
                  isDark && "animate-stellar-flare drop-shadow-[0_0_16px_rgba(226,232,240,0.9)]"
                )}
                aria-hidden="true"
              >
                <path
                  d="M50 0 C53 16 58 32 96 50 C58 68 53 84 50 100 C47 84 42 68 4 50 C42 32 47 16 50 0 Z"
                  fill={isDark ? "rgba(241,245,249,0.92)" : "rgba(10,10,10,0.95)"}
                />
              </svg>
            </button>
          </div>
        </div>

        <h1
          className={cn(
            "text-2xl font-light tracking-[0.3em] text-foreground/95 mb-1 transition-all duration-500 delay-200",
            isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          )}
        >
          HALLW
        </h1>

        <p
          className={cn(
            "text-xs text-muted-foreground/60 tracking-[0.2em] uppercase transition-all duration-500 delay-300",
            isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
          )}
        >
          Autonomous Workspace
        </p>
      </div>
    </div>
  );
}
