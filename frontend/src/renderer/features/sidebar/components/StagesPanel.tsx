import { cn } from "@lib/utils";
import { CheckCircle2, ListChecks, Loader2, XCircle } from "lucide-react";
import type { StageItemProps, StagesPanelProps } from "../types";

function StageItem({ index, label, isCurrent, isCompleted, isError, isExpanded }: StageItemProps) {
  const StatusIcon = isCompleted ? (
    <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />
  ) : isError ? (
    <XCircle className="w-4 h-4 text-red-500 shrink-0" />
  ) : isCurrent ? (
    <Loader2 className="w-4 h-4 text-blue-500 animate-spin shrink-0" />
  ) : (
    <div className="w-4 h-4 rounded-full border border-muted-foreground/30 shrink-0" />
  );

  if (!isExpanded) {
    return <div className="flex justify-center">{StatusIcon}</div>;
  }

  return (
    <div
      className={cn(
        "text-sm flex items-start justify-between gap-3",
        isError ? "text-red-500" : isCurrent ? "text-foreground font-medium" : "text-foreground/80"
      )}
    >
      <div className="flex min-w-0 flex-1 items-start gap-2">
        <span className="shrink-0 text-muted-foreground leading-5">{index + 1}.</span>
        <span className="leading-5 wrap-break-word text-left min-w-0">{label}</span>
      </div>
      <div className="shrink-0 pt-0.5">{StatusIcon}</div>
    </div>
  );
}

export function StagesPanel({ stages, currentIndex, completedIndices, errorStageIndex, isExpanded }: StagesPanelProps) {
  return (
    <div
      className={cn(
        "flex-1 basis-0 min-h-0 overflow-y-auto overflow-x-hidden transition-all duration-300 py-3",
        isExpanded ? "px-4 overflow-y-auto" : "px-2 overflow-y-hidden"
      )}
    >
      <h2
        className={cn(
          "text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2",
          !isExpanded && "justify-center"
        )}
      >
        <ListChecks className="w-3.5 h-3.5 shrink-0" />
        {isExpanded && <span>Plan</span>}
      </h2>
      <div className="space-y-4">
        {stages.length === 0
          ? isExpanded && <p className="text-sm text-muted-foreground italic">No active plan.</p>
          : stages.map((step, idx) => (
              <StageItem
                key={step}
                index={idx}
                label={step}
                isCurrent={idx === currentIndex}
                isCompleted={completedIndices.includes(idx)}
                isError={errorStageIndex === idx}
                isExpanded={isExpanded}
              />
            ))}
      </div>
    </div>
  );
}
