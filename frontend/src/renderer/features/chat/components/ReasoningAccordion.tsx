import { cn } from "@lib/utils";

import { Brain, ChevronDown, ChevronRight } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useAutoScroll } from "../hooks/useAutoScroll";
import { useSmoothTyping } from "../hooks/useSmoothTyping";
import { MarkdownContent } from "./MarkdownContent";

export function ReasoningAccordion({ content, isStreaming }: { content: string; isStreaming?: boolean }) {
  const [isOpen, setIsOpen] = useState(false);
  const smoothContent = useSmoothTyping(content, isStreaming || false);

  const { scrollRef, handleScroll, scrollToBottom } = useAutoScroll([smoothContent, isOpen]);

  useEffect(() => {
    if (isOpen && isStreaming) {
      scrollToBottom();
    }
  }, [isOpen, isStreaming, scrollToBottom]);

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
          isStreaming
            ? "bg-linear-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 animate-gradient-wave"
            : "bg-linear-to-r from-indigo-500/5 via-purple-500/5 to-pink-500/5"
        )}
      >
        {isOpen ? (
          <ChevronDown
            className={cn(
              "w-4 h-4 shrink-0 transition-colors",
              isStreaming ? "text-muted-foreground" : "text-foreground/70"
            )}
          />
        ) : (
          <ChevronRight
            className={cn(
              "w-4 h-4 shrink-0 transition-colors",
              isStreaming ? "text-muted-foreground" : "text-foreground/70"
            )}
          />
        )}
        <Brain
          className={cn(
            "w-4 h-4 shrink-0 transition-colors",
            isStreaming ? "text-purple-400 animate-pulse" : "text-purple-500"
          )}
        />
        <div className="flex-1 min-w-0 flex items-center">
          {!isOpen && isStreaming && summary ? (
            <span className="text-xs text-muted-foreground/80 truncate block font-mono leading-none">
              {summary.slice(0, 100)}
            </span>
          ) : (
            <span
              className={cn(
                "text-xs font-medium leading-none transition-colors",
                isStreaming ? "text-muted-foreground" : "text-foreground/70"
              )}
            >
              {isStreaming ? "Thinking..." : "Thought Process"}
            </span>
          )}
        </div>
      </button>
      {isOpen && (
        <div
          ref={scrollRef}
          onScroll={handleScroll}
          className={cn(
            "px-4 py-3 bg-muted/20 border-t border-border/30 text-xs animate-in slide-in-from-top-1 max-h-80 overflow-y-auto custom-scrollbar transition-colors",
            isStreaming ? "text-foreground/80" : "text-foreground"
          )}
        >
          <MarkdownContent content={isStreaming ? smoothContent : content} isStreaming={isStreaming} />
        </div>
      )}
    </div>
  );
}
