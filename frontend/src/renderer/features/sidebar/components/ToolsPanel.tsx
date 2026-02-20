import { cn } from "@lib/utils";
import { useAppStore } from "@store/store";
import { Activity, Loader2 } from "lucide-react";

import type { ToolItemProps, ToolsPanelProps } from "../types";

function ToolItem({ state, isExpanded, onClick }: ToolItemProps) {
  const { tool_name, status } = state;

  const statusColor = {
    running: "bg-blue-500",
    success: "bg-green-500",
    error: "bg-red-500",
  }[status];

  const borderColor = {
    running: "border-blue-500",
    success: "border-green-500",
    error: "border-red-500",
  }[status];

  const StatusIcon = status === "running" ? <Loader2 className="w-3 h-3 animate-spin text-blue-500" /> : null;

  if (!isExpanded) {
    return (
      <div className="flex justify-center">
        <div className={cn("w-2 h-2 rounded-full", statusColor)} />
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "w-full group relative pl-4 border-l-2 transition-colors cursor-pointer hover:bg-secondary/20 rounded-r-sm py-1 pr-2",
        borderColor
      )}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium text-[15px] text-foreground group-hover:text-primary transition-colors">
          {tool_name}
        </span>
        {StatusIcon}
      </div>
    </button>
  );
}

export function ToolsPanel({ isExpanded, onToolClick }: Omit<ToolsPanelProps, "toolStates">) {
  const getVisibleTools = useAppStore((s) => s.getVisibleTools);
  const visibleTools = getVisibleTools();

  return (
    <div
      className={cn(
        "flex-1 min-h-0 overflow-y-auto overflow-x-hidden bg-background/50 transition-all duration-300",
        isExpanded ? "p-4" : "p-2"
      )}
    >
      <h2
        className={cn(
          "text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2",
          !isExpanded && "justify-center"
        )}
      >
        <Activity className="w-3 h-3 shrink-0" />
        {isExpanded && <span>Execution</span>}
      </h2>
      <div className="space-y-3">
        {visibleTools.length === 0
          ? isExpanded && <p className="text-sm text-muted-foreground italic">Ready to execute.</p>
          : [...visibleTools]
              .reverse()
              .map((state) => (
                <ToolItem key={state.run_id} state={state} isExpanded={isExpanded} onClick={() => onToolClick(state)} />
              ))}
      </div>
    </div>
  );
}
