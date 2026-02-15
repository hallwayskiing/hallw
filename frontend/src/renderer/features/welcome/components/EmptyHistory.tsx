export function EmptyHistory() {
  return (
    <div className="flex flex-col items-center justify-center h-full border border-dashed border-border/40 rounded-xl bg-muted/5 transition-colors hover:bg-muted/10">
      <div className="flex flex-col items-center gap-3 opacity-60">
        {/* Animated Clock Icon */}
        <div className="relative w-8 h-8 rounded-full border-[1.5px] border-muted-foreground/40">
          {/* Minute Hand Container - Fast Rotation */}
          <div className="absolute inset-0 animate-[spin_5s_linear_infinite]">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[80%] w-[1.5px] h-3 bg-muted-foreground/60 rounded-full origin-bottom" />
          </div>
          {/* Hour Hand Container - Slow Rotation */}
          <div className="absolute inset-0 animate-[spin_60s_linear_infinite]">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-[80%] w-[1.5px] h-2 bg-muted-foreground/60 rounded-full origin-bottom" />
          </div>
          {/* Center Dot */}
          <div className="absolute w-1 h-1 bg-muted-foreground/60 rounded-full top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
        </div>
        <p className="text-[12px] font-medium tracking-[0.25em] text-muted-foreground uppercase">
          Start Your First Task
        </p>
      </div>
    </div>
  );
}
