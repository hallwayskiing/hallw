import { cn } from "@lib/utils";

import { ChevronLeft } from "lucide-react";
import { useRef, useState } from "react";

import { useActiveSidebarSession } from "../hooks/useActiveSidebarSession";
import type { SidebarProps } from "../types";
import { StagesPanel } from "./StagesPanel";
import { ToolPreview } from "./ToolPreview";
import { ToolsPanel } from "./ToolsPanel";

export function Sidebar({ className }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const sidebar = useActiveSidebarSession();
  const toolStates = sidebar?.toolStates ?? [];
  const toolPlan = sidebar?.stages ?? [];
  const currentStageIndex = sidebar?.currentStageIndex ?? -1;
  const completedStages = sidebar?.completedStages ?? [];
  const errorStageIndex = sidebar?.errorStageIndex ?? -1;
  const selectedTool = selectedRunId ? toolStates.find((t) => t.run_id === selectedRunId) : null;

  const handleMouseEnter = () => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
    hoverTimeoutRef.current = setTimeout(() => {
      setIsExpanded(true);
    }, 300); // 300ms delay to prevent accidental trigger near scrollbar
  };

  const handleMouseLeave = () => {
    if (hoverTimeoutRef.current) clearTimeout(hoverTimeoutRef.current);
    setIsExpanded(false);
  };

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-secondary/30 border-l border-border transition-all duration-300 ease-in-out overflow-x-hidden",
        isExpanded ? "w-64" : "w-12",
        className
      )}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="flex items-center justify-center h-10 border-b border-border shrink-0">
        <ChevronLeft
          className={cn("w-5 h-5 text-muted-foreground transition-transform duration-300", isExpanded && "rotate-180")}
        />
      </div>

      <StagesPanel
        stages={toolPlan}
        currentIndex={currentStageIndex}
        completedIndices={completedStages}
        errorStageIndex={errorStageIndex}
        isExpanded={isExpanded}
      />

      <div className="mx-1 my-1 h-px shrink-0 bg-linear-to-r from-transparent via-muted-foreground/20 to-transparent" />

      <ToolsPanel isExpanded={isExpanded} onToolClick={(tool) => setSelectedRunId(tool.run_id)} />

      {selectedTool && (
        <ToolPreview toolState={selectedTool} isOpen={!!selectedTool} onClose={() => setSelectedRunId(null)} />
      )}
    </aside>
  );
}
