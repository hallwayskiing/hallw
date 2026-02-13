import { Zap, Clock } from 'lucide-react';
import { cn } from '@lib/utils';

interface WelcomeHeadersProps {
    isHistoryOpen: boolean;
    theme: string;
}

export function WelcomeHeaders({ isHistoryOpen, theme }: WelcomeHeadersProps) {
    return (
        <div className="flex items-center gap-2 relative h-6 w-48">
            {/* Quick Start Header */}
            <div className={cn(
                "flex items-center gap-2 transition-all duration-500 ease-in-out",
                isHistoryOpen ? "opacity-0 -translate-y-2 pointer-events-none" : "opacity-100 translate-y-0"
            )}>
                <div className="relative flex items-center justify-center w-5 h-5 shrink-0">
                    {theme === 'dark' && <div className="absolute inset-0 bg-amber-400/60 blur-lg rounded-full animate-pulse" />}
                    <Zap className={cn("relative w-3.5 h-3.5", theme === 'dark' ? "text-amber-400 drop-shadow-[0_0_4px_rgba(251,191,36,0.8)]" : "text-amber-600")} />
                </div>
                <span className={cn(
                    "text-[12px] uppercase tracking-[0.2em] whitespace-nowrap",
                    theme === 'dark' ? "font-light text-amber-300 drop-shadow-[0_0_8px_rgba(251,191,36,0.8)]" : "font-medium text-amber-600"
                )}>
                    Quick Start
                </span>
            </div>

            {/* History Header */}
            <div className={cn(
                "absolute inset-0 flex items-center gap-2 transition-all duration-500 ease-in-out",
                isHistoryOpen ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"
            )}>
                <div className="relative flex items-center justify-center w-5 h-5 shrink-0">
                    {theme === 'dark' && <div className="absolute inset-0 bg-emerald-400/60 blur-lg rounded-full animate-pulse" />}
                    <Clock className={cn("relative w-3.5 h-3.5", theme === 'dark' ? "text-emerald-400 drop-shadow-[0_0_4px_rgba(52,211,153,0.8)]" : "text-emerald-600")} />
                </div>
                <span className={cn(
                    "text-[12px] uppercase tracking-[0.2em] whitespace-nowrap",
                    theme === 'dark' ? "font-light text-emerald-300 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]" : "font-medium text-emerald-600"
                )}>
                    History
                </span>
            </div>
        </div>
    );
}
