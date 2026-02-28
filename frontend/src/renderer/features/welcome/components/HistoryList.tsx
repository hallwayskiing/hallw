import { cn } from "@lib/utils";

import { useAppStore } from "@store/store";
import { Clock, Loader2, Scroll, ScrollText, Trash2 } from "lucide-react";
import { useEffect } from "react";

import type { HistoryRowProps } from "../types";

function HistoryRow({ item, onLoad, onDelete }: HistoryRowProps) {
  const dateStr = item.created_at || item.metadata?.created_at;
  const date = dateStr ? new Date(dateStr as string).toLocaleString() : "";
  const title = item.title || (item.metadata?.title as string) || `Conversation ${item.id.slice(0, 8)}`;

  return (
    <div
      className={cn(
        "group w-full flex items-center gap-3 p-3 text-left rounded-xl transition-all duration-400 ease-out",
        "bg-card/20 backdrop-blur-sm border border-border/30",
        "hover:bg-emerald-500/5 hover:border-emerald-500/30 hover:shadow-lg hover:-translate-y-0.5",
        "active:scale-[0.99]"
      )}
    >
      <button
        type="button"
        onClick={onLoad}
        className="flex-1 flex items-center gap-3 min-w-0 cursor-pointer outline-none"
      >
        <div
          className={cn(
            "flex items-center justify-center w-7 h-7 rounded-lg bg-white/5 shrink-0",
            "transition-all duration-200 group-hover:bg-white/10 group-hover:shadow-lg group-hover:shadow-emerald-500/50",
            "text-emerald-400"
          )}
        >
          <Clock className="w-3.5 h-3.5" />
        </div>
        <div className="flex-1 min-w-0 text-left">
          <span className="block text-[14px] font-medium text-foreground/90 group-hover:text-foreground truncate transition-colors duration-200">
            {title}
          </span>
          <div className="flex items-center gap-2 text-[10px] text-muted-foreground/50 uppercase tracking-widest mt-0.5">
            <span className="font-mono">{item.id.slice(0, 8)}</span>
            {date && (
              <>
                <span>•</span>
                <span>{date}</span>
              </>
            )}
          </div>
        </div>
      </button>

      <div className="flex items-center gap-2 shrink-0">
        <button
          type="button"
          onClick={onDelete}
          className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 transition-all duration-200"
          title="Delete thread"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
        <span className="text-muted-foreground/20 group-hover:text-foreground/40 transition-all duration-200">→</span>
      </div>
    </div>
  );
}

export function HistoryList({ isVisible }: { isVisible: boolean }) {
  const history = useAppStore((s) => s.history);
  const isHistoryLoading = useAppStore((s) => s.isHistoryLoading);
  const loadHistory = useAppStore((s) => s.loadHistory);
  const deleteHistory = useAppStore((s) => s.deleteHistory);
  const fetchHistory = useAppStore((s) => s.fetchHistory);
  const theme = useAppStore((s) => s.theme);

  useEffect(() => {
    if (isVisible) {
      fetchHistory();
    }
  }, [isVisible, fetchHistory]);

  return (
    <div
      className={cn(
        "absolute inset-x-0 top-0 bottom-0 flex flex-col px-1 transition-all duration-500",
        !isVisible ? "opacity-0 pointer-events-none z-0" : "opacity-100 z-10"
      )}
    >
      {/* Header */}
      <div
        className={cn(
          "flex items-center justify-between mb-4 min-h-[30px] transition-all duration-500 ease-in-out",
          isVisible ? "translate-y-0" : "translate-y-2"
        )}
      >
        <div className="flex items-center gap-2">
          <div className="relative flex items-center justify-center w-5 h-5 shrink-0">
            {theme === "dark" && (
              <div className="absolute inset-0 bg-emerald-400/60 blur-lg rounded-full animate-pulse" />
            )}
            <ScrollText
              className={cn(
                "relative w-3.5 h-3.5",
                theme === "dark" ? "text-emerald-400 drop-shadow-[0_0_4px_rgba(52,211,153,0.8)]" : "text-emerald-600"
              )}
            />
          </div>
          <span
            className={cn(
              "text-[13px] uppercase tracking-[0.2em] whitespace-nowrap",
              theme === "dark"
                ? "font-light text-emerald-300 drop-shadow-[0_0_8px_rgba(52,211,153,0.8)]"
                : "font-medium text-emerald-600"
            )}
          >
            History
          </span>
        </div>
      </div>
      {/* Main Area */}
      <div
        className={cn(
          "flex flex-col gap-3 overflow-y-auto custom-scrollbar pr-1 pt-1 pb-4 transition-all duration-500 ease-in-out",
          isVisible ? "scale-100 translate-x-0" : "scale-95 translate-x-8"
        )}
      >
        {/* History Loading */}
        {isHistoryLoading ? (
          <div className="flex-1 flex flex-col items-center justify-center min-h-[140px] animate-in fade-in duration-300">
            <Loader2 className="w-6 h-6 animate-spin text-emerald-500 mb-3 opacity-80" />
            <span className="text-[15px] text-muted-foreground/60 tracking-tight">Fetching history...</span>
          </div>
        ) : history.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-[140px] gap-3 opacity-30">
            <Scroll className="w-5 h-5" strokeWidth={1.5} />
            <p className="text-[13px] tracking-[0.3em] uppercase whitespace-nowrap">No History Found</p>
          </div>
        ) : (
          history.map((item) => (
            <HistoryRow
              key={item.id}
              item={item}
              onLoad={() => loadHistory(item.id)}
              onDelete={() => deleteHistory(item.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}
