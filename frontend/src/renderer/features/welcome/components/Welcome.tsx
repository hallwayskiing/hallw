import { RefreshCw } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useAppStore } from '@store/store';
import { HistoryList } from './HistoryList';
import { QuickStartList } from './QuickStartList';
import { cn } from '@lib/utils';
import { ParticleCanvas } from './ParticleCanvas';
import { HeroSection } from './HeroSection';
import { WelcomeHeaders } from './WelcomeHeaders';

export function Welcome() {
    const { theme, startTask } = useAppStore();
    const [isLoaded, setIsLoaded] = useState(false);
    const [refreshKey, setRefreshKey] = useState(0);

    const refreshQuickStarts = () => {
        setRefreshKey(prev => prev + 1);
    };

    const isHistoryOpen = useAppStore(s => s.isHistoryOpen);

    useEffect(() => {
        const timer = setTimeout(() => setIsLoaded(true), 50);
        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="flex-1 flex flex-col overflow-hidden relative">

            {/* Interactive Particle Canvas */}
            <ParticleCanvas />

            {/* Center Hero */}
            <HeroSection isLoaded={isLoaded} />

            {/* Bottom - Quick Start / History Toggle Area */}
            <div className={cn(
                "w-full max-w-2xl mx-auto px-6 pb-6 z-10 transition-all duration-700 delay-400",
                isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
            )}>
                <div className="flex items-center justify-between mb-4">
                    <WelcomeHeaders isHistoryOpen={isHistoryOpen} theme={theme} />

                    {!isHistoryOpen && (
                        <button
                            onClick={refreshQuickStarts}
                            className="group p-1.5 rounded-lg text-muted-foreground/40 hover:text-foreground/60 hover:bg-white/5 transition-all duration-200 active:scale-90"
                            title="Shuffle prompts"
                        >
                            <RefreshCw className="w-3.5 h-3.5 transition-transform duration-500 group-hover:rotate-180" />
                        </button>
                    )}
                </div>

                <div className="relative h-[192px] overflow-hidden pt-1">
                    {/* Quick Start List */}
                    <QuickStartList
                        onQuickStart={startTask}
                        isVisible={!isHistoryOpen}
                        refreshKey={refreshKey}
                    />

                    {/* History List */}
                    <HistoryList
                        isVisible={isHistoryOpen}
                    />
                </div>
            </div>
        </div>
    );
}
