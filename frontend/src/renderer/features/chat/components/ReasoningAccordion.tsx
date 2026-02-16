import { cn } from "@lib/utils";

import { Brain, ChevronDown, ChevronRight } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { useSmoothTyping } from "../hooks/useSmoothTyping";
import { MarkdownContent } from "./MarkdownContent";

export function ReasoningAccordion({ content, isStreaming }: { content: string; isStreaming?: boolean }) {
  const [isOpen, setIsOpen] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const smoothContent = useSmoothTyping(content, isStreaming || false);

  useEffect(() => {
    if (isOpen && isStreaming) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [isOpen, isStreaming]);

  const summary = useMemo(() => {
    return (
      content
        .split("\n")
        .filter((line) => line.trim() !== "")
        .pop() || ""
    );
  }, [content]);

  return (
    <div className="border border-border/50 rounded-lg overflow-hidden bg-background/50 max-w-[90%]">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-3 py-2 w-full hover:bg-muted/30 transition-all text-left group",
          !isOpen &&
            isStreaming &&
            "bg-linear-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 animate-gradient-wave"
        )}
      >
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0" />
        ) : (
          <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />
        )}
        <Brain className={cn("w-4 h-4 text-purple-400 shrink-0", isStreaming && "animate-pulse")} />
        <div className="flex-1 min-w-0">
          {!isOpen && isStreaming && summary ? (
            <span className="text-xs text-muted-foreground/80 truncate block font-mono">{summary.slice(0, 100)}</span>
          ) : (
            <span className="text-xs font-medium text-muted-foreground">
              {isStreaming ? "Thinking..." : "Thought Process"}
            </span>
          )}
        </div>
      </button>
      {isOpen && (
        <div className="px-4 py-3 bg-muted/20 border-t border-border/30 text-xs text-foreground/80 animate-in slide-in-from-top-1 max-h-80 overflow-y-auto custom-scrollbar">
          <MarkdownContent content={isStreaming ? smoothContent : content} isStreaming={isStreaming} />
          <div ref={bottomRef} className="h-0 w-0" />
        </div>
      )}
    </div>
  );
}
