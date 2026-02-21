import { cn } from "@lib/utils";

import { useAppStore } from "@store/store";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useRef, useState } from "react";

import type { SidebarProps } from "../types";
import { StagesPanel } from "./StagesPanel";
import { ToolPreview } from "./ToolPreview";
import { ToolsPanel } from "./ToolsPanel";

export function Sidebar({ className }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const toolStates = useAppStore((s) => s.toolStates);
  const toolPlan = useAppStore((s) => s.stages);
  const currentStageIndex = useAppStore((s) => s.currentStageIndex);
  const completedStages = useAppStore((s) => s.completedStages);
  const errorStageIndex = useAppStore((s) => s.errorStageIndex);
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
        {isExpanded ? (
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
        ) : (
          <ChevronLeft className="w-4 h-4 text-muted-foreground" />
        )}
      </div>

      <StagesPanel
        stages={toolPlan}
        currentIndex={currentStageIndex}
        completedIndices={completedStages}
        errorStageIndex={errorStageIndex}
        isExpanded={isExpanded}
      />

      <ToolsPanel isExpanded={isExpanded} onToolClick={(tool) => setSelectedRunId(tool.run_id)} />

      {selectedTool && (
        <ToolPreview toolState={selectedTool} isOpen={!!selectedTool} onClose={() => setSelectedRunId(null)} />
      )}
    </aside>
  );
}
