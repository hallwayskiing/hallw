import { cn } from '@lib/utils';
import { useAppStore } from '@store/store';

import { HeroSectionProps } from '../types';

export function HeroSection({ isLoaded }: HeroSectionProps) {
    const { theme } = useAppStore();

    return (
        <div className="flex-1 flex items-center justify-center z-10 pointer-events-none">
            <div className={cn(
                "flex flex-col items-center transition-all duration-700 ease-out",
                isLoaded ? "opacity-100 scale-100" : "opacity-0 scale-95"
            )}>

                {/* Elegant Glowing Orb */}
                <div className={cn(
                    "relative mb-8 transition-all duration-500 delay-100",
                    isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                )}>
                    <div className="relative w-24 h-24 flex items-center justify-center">
                        {/* Outer soft glow */}
                        <div className="absolute w-36 h-36 bg-amber-500/15 blur-2xl rounded-full" />

                        {/* Rotating ring */}
                        <div className="absolute w-24 h-24 rounded-full border border-amber-500/20 animate-spin-slow" />

                        {/* Inner Glow effects - Dark Mode Only */}
                        {theme === 'dark' && (
                            <>
                                <div className="absolute w-12 h-12 bg-amber-400/25 blur-xl rounded-full" />
                                <div className="absolute w-6 h-6 bg-amber-300/50 blur-md rounded-full" />
                            </>
                        )}

                        {/* Core orb - Dynamic in Dark Mode, Static in Light Mode */}
                        <div className={cn(
                            "relative w-4 h-4 rounded-full",
                            theme === 'dark' ? "bg-amber-400 animate-rainbow-pulse" : "bg-amber-400"
                        )} />
                    </div>
                </div>

                {/* Title */}
                <h1 className={cn(
                    "text-2xl font-light tracking-[0.3em] text-foreground/90 mb-1 transition-all duration-500 delay-200",
                    isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                )}>
                    HALLW
                </h1>

                {/* Tagline */}
                <p className={cn(
                    "text-xs text-muted-foreground/50 tracking-[0.2em] uppercase transition-all duration-500 delay-300",
                    isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
                )}>
                    Autonomous Workspace
                </p>
            </div>
        </div>
    );
}
