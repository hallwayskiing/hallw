import { Minus, Square, X } from "lucide-react";

export function TitleBar() {
  return (
    <header
      className="fixed top-0 right-0 h-8 flex items-center justify-end select-none z-50"
      style={{ WebkitAppRegion: "drag", left: 0 } as React.CSSProperties}
    >
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
