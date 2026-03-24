import { cn } from "@lib/utils";
import { useAppStore } from "@store/store";
import { Activity } from "lucide-react";

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
        "w-full group relative border-l-2 transition-colors cursor-pointer hover:bg-secondary/20 rounded-r-sm px-3 py-2",
        borderColor
      )}
    >
      <div className="flex items-center">
        <span className="min-w-0 truncate text-[15px] font-medium text-foreground transition-colors group-hover:text-primary leading-5">
          {tool_name}
        </span>
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
        "flex-1 basis-0 min-h-0 overflow-x-hidden transition-all duration-300 py-3",
        isExpanded ? "px-4 overflow-y-auto" : "px-2 overflow-hidden"
      )}
    >
      <h2
        className={cn(
          "text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2",
          !isExpanded && "justify-center"
        )}
      >
        <Activity className="w-3.5 h-3.5 shrink-0" />
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
