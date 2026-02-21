import { cn } from "@lib/utils";

import { useAppStore } from "@store/store";
import { RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { HeroSection } from "./HeroSection";
import { HistoryList } from "./HistoryList";
import { ParticleCanvas } from "./ParticleCanvas";
import { QuickStartList } from "./QuickStartList";
import { WelcomeHeaders } from "./WelcomeHeaders";

export function Welcome() {
  const theme = useAppStore((s) => s.theme);
  const startTask = useAppStore((s) => s.startTask);
  const [isLoaded, setIsLoaded] = useState(false);
  const [refreshKey, setRefreshKey] = useState(1);

  const refreshQuickStarts = () => {
    setRefreshKey((prev) => prev + 1);
  };

  const isHistoryOpen = useAppStore((s) => s.isHistoryOpen);

  useEffect(() => {
    const timer = setTimeout(() => setIsLoaded(true), 50);
    return () => clearTimeout(timer);
  }, []);

  return (
    <div className="flex-1 flex flex-col overflow-hidden relative">
      {theme === "dark" && (
        <>
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(56,189,248,0.16),transparent_35%),radial-gradient(circle_at_82%_70%,rgba(168,85,247,0.14),transparent_32%),radial-gradient(circle_at_50%_110%,rgba(59,130,246,0.1),transparent_45%)]" />
            <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(2,6,23,0.22),rgba(2,6,23,0.45))] dark:bg-[linear-gradient(180deg,rgba(2,6,23,0.28),rgba(2,6,23,0.6))]" />
          </div>

          <ParticleCanvas />
        </>
      )}

      <HeroSection isLoaded={isLoaded} />

      <div
        className={cn(
          "w-full max-w-2xl mx-auto px-6 pb-6 z-10 transition-all duration-700 delay-400",
          isLoaded ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        )}
      >
        <div className="flex items-center justify-between mb-4 min-h-[30px]">
          <WelcomeHeaders isHistoryOpen={isHistoryOpen} theme={theme} />

          <button
            type="button"
            onClick={refreshQuickStarts}
            className={cn(
              "group p-1.5 rounded-lg text-muted-foreground/40 hover:text-foreground/60 hover:bg-white/5 transition-all duration-200 active:scale-90",
              isHistoryOpen ? "opacity-0 pointer-events-none" : "opacity-100"
            )}
            title="Shuffle prompts"
            disabled={isHistoryOpen}
            aria-hidden={isHistoryOpen}
          >
            <RefreshCw className="w-4.5 h-4.5 transition-transform duration-500 group-hover:rotate-180 " />
          </button>
        </div>

        <div className="relative h-48 overflow-hidden pt-1">
          <QuickStartList onQuickStart={startTask} isVisible={!isHistoryOpen} refreshKey={refreshKey} />

          <HistoryList isVisible={isHistoryOpen} />
        </div>
      </div>
    </div>
  );
}
