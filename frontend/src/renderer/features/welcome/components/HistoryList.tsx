import { cn } from "@lib/utils";

import { useAppStore } from "@store/store";
import { Clock, Trash2 } from "lucide-react";
import { useEffect } from "react";

import type { HistoryRowProps } from "../types";
import { EmptyHistory } from "./EmptyHistory";

function HistoryRow({ item, onLoad, onDelete }: HistoryRowProps) {
  const dateStr = item.created_at || item.metadata?.created_at;
  const date = dateStr ? new Date(dateStr as string).toLocaleString() : "";
  const title = item.title || (item.metadata?.title as string) || `Conversation ${item.id.slice(0, 8)}`;

  return (
    <button
      type="button"
      onClick={onLoad}
      className={cn(
        "group w-full flex items-center gap-3 p-3 text-left rounded-xl transition-all duration-400 ease-out",
        "bg-card/20 backdrop-blur-sm border border-border/30",
        "hover:bg-emerald-500/5 hover:border-emerald-500/30 hover:shadow-lg hover:-translate-y-0.5",
        "active:scale-[0.99] cursor-pointer"
      )}
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
      <div className="flex-1 min-w-0">
        <span className="block text-sm font-medium text-foreground/90 group-hover:text-foreground truncate transition-colors duration-200">
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
      <div className="flex items-center gap-2 shrink-0">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
          className="p-1.5 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 transition-all duration-200"
          title="Delete thread"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
        <span className="text-muted-foreground/20 group-hover:text-foreground/40 transition-all duration-200">→</span>
      </div>
    </button>
  );
}

export function HistoryList({ isVisible }: { isVisible: boolean }) {
  const history = useAppStore((s) => s.history);
  const loadHistory = useAppStore((s) => s.loadHistory);
  const deleteHistory = useAppStore((s) => s.deleteHistory);
  const fetchHistory = useAppStore((s) => s.fetchHistory);

  useEffect(() => {
    if (isVisible) {
      fetchHistory();
    }
  }, [isVisible, fetchHistory]);

  return (
    <div
      className={cn(
        "absolute inset-x-0 top-1 bottom-0 flex flex-col gap-3 transition-opacity duration-500 ease-in-out overflow-y-auto custom-scrollbar pr-1 px-1 pt-1",
        isVisible ? "opacity-100 scale-100 translate-x-0" : "opacity-0 scale-95 pointer-events-none translate-x-8"
      )}
    >
      {history.length === 0 ? (
        <EmptyHistory />
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
  );
}
