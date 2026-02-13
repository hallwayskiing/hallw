import { useEffect, useState } from 'react';
import { cn } from '@lib/utils';
import { ColorName, QuickStartCardProps } from '../types';
import { ALL_QUICK_STARTS, COLOR_MAP } from '../constants';


function QuickStartCard({ icon, color, text, onClick, delay, isLoaded }: QuickStartCardProps) {
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
            onClick={() => onClick(text)}
            className={
                cn(
                    "group w-full flex items-center gap-3 p-3 text-left rounded-xl",
                    "bg-card/20 backdrop-blur-sm border border-border/30",
                    "transition-all duration-400 ease-out",
                    colors.bg, colors.border,
                    "hover:shadow-lg hover:-translate-y-0.5",
                    "active:scale-[0.99]",
                    isVisible ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-8"
                )
            }
        >
            <div className={
                cn(
                    "flex items-center justify-center w-7 h-7 rounded-lg bg-white/5 flex-shrink-0",
                    "transition-all duration-200 group-hover:bg-white/10 group-hover:shadow-lg",
                    colors.icon,
                    colors.glow
                )
            }>
                {icon}
            </div>
            <span className="flex-1 text-sm text-muted-foreground/80 group-hover:text-foreground transition-colors duration-200" >
                {text}
            </span>
            <span className="text-muted-foreground/20 group-hover:text-foreground/40 transition-all duration-200" >
                →
            </span>
        </button>
    );
}

export function QuickStartList({ onQuickStart, isVisible, refreshKey }: { onQuickStart: (text: string) => void, isVisible: boolean, refreshKey: number }) {
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setIsLoaded(true), 50);
        return () => clearTimeout(timer);
    }, []);

    const getRandomQuickStarts = () => {
        const shuffled = [...ALL_QUICK_STARTS].sort(() => Math.random() - 0.5);
        return shuffled.slice(0, 3);
    };

    const [quickStarts, setQuickStarts] = useState(getRandomQuickStarts);

    useEffect(() => {
        setQuickStarts(getRandomQuickStarts());
    }, [refreshKey]);

    return (
        <div className={cn(
            "absolute inset-x-0 top-1 bottom-0 grid grid-cols-1 gap-3 transition-opacity transition-transform duration-500 ease-in-out px-1",
            !isVisible ? "opacity-0 scale-95 pointer-events-none -translate-x-8" : "opacity-100 scale-100 translate-x-0"
        )}>
            {quickStarts.map((item, idx) => (
                <QuickStartCard
                    key={`${refreshKey}-${idx}`}
                    icon={item.icon}
                    color={item.color as ColorName}
                    text={item.text}
                    onClick={onQuickStart}
                    delay={100 + idx * 80}
                    isLoaded={isLoaded}
                />
            ))}
        </div>
    );
}
