import { useAppStore } from "@store/store";
import { Minus, Monitor, Square, X } from "lucide-react";

export function TitleBar() {
  const showCdpView = useAppStore((s) => s.showCdpView);
  const activeSessionId = useAppStore((s) => s.activeSessionId);
  const destroyCdpView = useAppStore((s) => s.destroyCdpView);

  return (
    <header
      className="fixed top-0 right-0 h-8 flex items-center justify-between select-none z-50"
      style={{ WebkitAppRegion: "drag", left: 0 } as React.CSSProperties}
    >
      {/* Left: CDP indicator + close, only when CDP view is active */}
      <div
        className="flex items-center h-full gap-1 pl-3"
        style={{ WebkitAppRegion: "no-drag" } as React.CSSProperties}
      >
        {showCdpView && (
          <>
            <span className="text-[11px] font-medium text-muted-foreground flex items-center gap-1.5">
              <Monitor className="w-3 h-3 text-blue-400" />
              <span className="opacity-70">Live</span>
            </span>
            <button
              type="button"
              onClick={() => activeSessionId && destroyCdpView(activeSessionId)}
              className="ml-1 p-0.5 hover:bg-destructive/20 text-muted-foreground hover:text-destructive rounded transition-colors"
              title="Close CDP View"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </>
        )}
      </div>

      {/* Right: Window controls */}
      <div className="flex h-full" style={{ WebkitAppRegion: "no-drag" } as React.CSSProperties}>
        <button
          type="button"
          onClick={() => window.api.windowMinimize()}
          className="w-11 h-full flex items-center justify-center text-muted-foreground/50 hover:text-muted-foreground transition-colors"
          aria-label="Minimize"
        >
          <Minus className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => window.api.windowMaximize()}
          className="w-11 h-full flex items-center justify-center text-muted-foreground/50 hover:text-muted-foreground transition-colors"
          aria-label="Maximize"
        >
          <Square className="w-3 h-3" />
        </button>
        <button
          type="button"
          onClick={() => window.api.windowClose()}
          className="w-11 h-full flex items-center justify-center text-muted-foreground/50 hover:text-red-400 transition-colors"
          aria-label="Close"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
