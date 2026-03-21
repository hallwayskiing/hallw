import { cn } from "@lib/utils";

import { useState } from "react";

import type { HeroSectionProps } from "../types";

export function HeroSection({ isLoaded }: HeroSectionProps) {
  const [isSpinning, setIsSpinning] = useState(false);

  const handleSpin = () => {
    setIsSpinning(false);
    // Double requestAnimationFrame to ensure the class is removed and then re-added
    // which restarts the one-shot animation
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        setIsSpinning(true);
      });
    });
  };

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
          <div className="relative w-28 h-28 flex items-center justify-center perspective-midrange">
            <button
              type="button"
              onClick={handleSpin}
              onAnimationEnd={() => setIsSpinning(false)}
              className={cn(
                "relative w-18 h-18 pointer-events-auto cursor-pointer",
                isSpinning && "animate-hero-spin-y"
              )}
            >
                <div
                  className="w-full h-full animate-hero-gradient blur-xs opacity-80 absolute inset-0 rounded-full"
                  style={{
                    background: 'linear-gradient(to bottom, #05B6FF, #4B5EFC, #8D46FF, #D146FF, #FF5B37, #FF8B37, #05B6FF)',
                    backgroundSize: '100% 300%',
                    maskImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50 0 C53 16 58 32 96 50 C58 68 53 84 50 100 C47 84 42 68 4 50 C42 32 47 16 50 0 Z'/%3E%3C/svg%3E")`,
                    maskRepeat: 'no-repeat',
                    maskPosition: 'center',
                    maskSize: 'contain',
                    WebkitMaskImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50 0 C53 16 58 32 96 50 C58 68 53 84 50 100 C47 84 42 68 4 50 C42 32 47 16 50 0 Z'/%3E%3C/svg%3E")`,
                    WebkitMaskRepeat: 'no-repeat',
                    WebkitMaskPosition: 'center',
                    WebkitMaskSize: 'contain'
                  }}
                />
                <div
                  className="w-full h-full animate-hero-gradient"
                  style={{
                    background: 'linear-gradient(to bottom, #05B6FF, #4B5EFC, #8D46FF, #D146FF, #FF5B37, #FF8B37, #05B6FF)',
                    backgroundSize: '100% 300%',
                    maskImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50 0 C53 16 58 32 96 50 C58 68 53 84 50 100 C47 84 42 68 4 50 C42 32 47 16 50 0 Z'/%3E%3C/svg%3E")`,
                    maskRepeat: 'no-repeat',
                    maskPosition: 'center',
                    maskSize: 'contain',
                    WebkitMaskImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Cpath d='M50 0 C53 16 58 32 96 50 C58 68 53 84 50 100 C47 84 42 68 4 50 C42 32 47 16 50 0 Z'/%3E%3C/svg%3E")`,
                    WebkitMaskRepeat: 'no-repeat',
                    WebkitMaskPosition: 'center',
                    WebkitMaskSize: 'contain'
                  }}
                />
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
