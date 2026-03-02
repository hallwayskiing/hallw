import { cn } from "@lib/utils";

import { Brain, ChevronDown, ChevronRight } from "lucide-react";
import { useEffect, useState } from "react";
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

  return (
    <div
      className={cn(
        "border rounded-lg overflow-hidden max-w-[85%] transition-colors",
        isStreaming ? "border-cyan-500/15 bg-background/30" : "border-teal-500/10 bg-teal-500/3"
      )}
    >
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-3 py-2 w-full transition-all text-left group",
          isStreaming ? "animate-gradient-wave" : "bg-teal-500/5 hover:bg-teal-500/8"
        )}
        style={
          isStreaming
            ? {
                background:
                  "linear-gradient(90deg, #10b98120 0%, #06b6d430 16.66%, #3b82f625 33.33%, #10b98120 50%, #06b6d430 66.66%, #3b82f625 83.33%, #10b98120 100%)",
                backgroundSize: "200% 100%",
              }
            : undefined
        }
      >
        {isOpen ? (
          <ChevronDown
            className={cn("w-4 h-4 shrink-0 transition-colors", isStreaming ? "text-cyan-400/70" : "text-teal-400/70")}
          />
        ) : (
          <ChevronRight
            className={cn("w-4 h-4 shrink-0 transition-colors", isStreaming ? "text-cyan-400/70" : "text-teal-400/70")}
          />
        )}
        <Brain
          className={cn(
            "w-4 h-4 shrink-0 transition-colors",
            isStreaming ? "text-cyan-400 animate-pulse" : "text-teal-400"
          )}
        />
        <div className="flex-1 min-w-0 flex items-center">
          <span
            className={cn(
              "text-xs font-medium leading-none transition-colors",
              isStreaming ? "text-cyan-400/80" : "text-teal-400/80"
            )}
          >
            {isStreaming ? "Thinking..." : "Thought Process"}
          </span>
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
