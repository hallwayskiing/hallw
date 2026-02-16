import { cn } from "@lib/utils";
import { Bot, User } from "lucide-react";

import { useSmoothTyping } from "../hooks/useSmoothTyping";
import type { AvatarProps, MessageBubbleProps } from "../types";
import { MarkdownContent } from "./MarkdownContent";
import { ReasoningAccordion } from "./ReasoningAccordion";

export function Avatar({ msgRole: role }: AvatarProps) {
  const isUser = role === "user";
  return (
    <div
      className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border shadow-md transition-all duration-300",
        isUser
          ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400 shadow-indigo-500/10"
          : "bg-teal-500/10 border-teal-500/20 text-teal-400 shadow-teal-500/10"
      )}
    >
      {isUser ? <User className="w-4 h-4" /> : <Bot className="w-5 h-5" />}
    </div>
  );
}

export function MessageBubble({ msgRole, content, reasoning, isStreaming }: MessageBubbleProps) {
  const isUser = msgRole === "user";
  const smoothContent = useSmoothTyping(content, isStreaming || false);

  return (
    <div
      className={cn(
        "flex gap-4 max-w-3xl mx-auto w-full animate-in fade-in duration-300",
        isUser && "flex-row-reverse"
      )}
    >
      <Avatar msgRole={msgRole} />
      <div className={cn("flex-1 space-y-2 min-w-0", isUser ? "text-right" : "text-left")}>
        <div className="font-semibold text-xs uppercase tracking-wider text-muted-foreground/60">
          {isUser ? "You" : "HALLW"}
        </div>
        {reasoning && <ReasoningAccordion content={reasoning} isStreaming={isStreaming} />}
        {(isStreaming || content) && (
          <div
            className={cn(
              "inline-block rounded-2xl max-w-[90%] text-left",
              isUser
                ? "bg-linear-to-br from-indigo-500/15 to-indigo-600/5 border border-indigo-500/15 text-foreground/95 px-4 py-2.5 shadow-sm shadow-indigo-500/5"
                : "bg-white/2 border border-white/4 text-foreground/90 px-5 py-3 shadow-lg shadow-black/5",
              isStreaming && "min-h-[40px]"
            )}
          >
            <MarkdownContent content={isStreaming ? smoothContent : content} isStreaming={isStreaming} />
          </div>
        )}
      </div>
    </div>
  );
}
