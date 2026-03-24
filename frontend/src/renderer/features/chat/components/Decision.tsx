import { Key, MessageSquare, Send, X } from "lucide-react";
import { memo, useState } from "react";

import { useCountdown } from "../hooks/useCountdown";
import type { DecisionRequest, DecisionStatus } from "../types";
import { MarkdownContent } from "./MarkdownContent";
import { Avatar } from "./MessageBubble";

export const Decision = memo(
  ({ requestId, message, choices, timeout, initialStatus, initialValue, onDecision }: DecisionRequest) => {
    const [status, setStatus] = useState<DecisionStatus>(initialStatus || "pending");
    const [input, setInput] = useState(initialValue || "");

    const handleDecision = (newStatus: DecisionStatus, value: string) => {
      setStatus(newStatus);
      setInput(value);
      onDecision?.(newStatus, value);
    };

    const handleTimeout = () => {
      if (status === "pending") {
        handleDecision("timeout", "");
      }
    };

    const timeLeft = useCountdown(timeout, handleTimeout, status === "pending");

    const getStatusContent = () => {
      switch (status) {
        case "submitted":
          return (
            <div className="flex w-full items-center gap-3 rounded-xl border border-green-500/10 bg-green-500/15 p-4 text-green-700 dark:text-green-400/80 animate-in fade-in shadow-sm shadow-green-500/3">
              <div className="flex h-5 w-5 shrink-0 items-center justify-center">
                <Key className="h-4 w-4" />
              </div>
              <div className="min-w-0">
                <span className="block text-sm leading-5 opacity-90">{input}</span>
              </div>
            </div>
          );
        case "rejected":
          return (
            <div className="flex w-full items-center gap-3 rounded-xl border border-red-500/10 bg-red-500/15 p-4 text-red-500 dark:text-red-400/80 animate-in fade-in shadow-sm shadow-red-500/3">
              <div className="flex h-5 w-5 shrink-0 items-center justify-center">
                <X className="h-4 w-4" />
              </div>
              <span className="text-sm font-medium leading-5">Input request rejected.</span>
            </div>
          );
        case "timeout":
          return (
            <div className="flex w-full items-center gap-3 rounded-xl border border-red-500/10 bg-red-500/15 p-4 text-red-500 dark:text-red-400/80 animate-in fade-in shadow-sm shadow-red-500/3">
              <div className="flex h-5 w-5 shrink-0 items-center justify-center">
                <X className="h-4 w-4" />
              </div>
              <span className="text-sm font-medium leading-5">Input request timed out.</span>
            </div>
          );
        default:
          return (
            <div className="space-y-4 pt-1">
              {choices && choices.length > 0 && (
                <div className="flex flex-col gap-2">
                  {choices.map((choice, index) => (
                    <button
                      type="button"
                      key={`${choice}`}
                      onClick={() => handleDecision("submitted", choice)}
                      className="flex w-full items-center gap-3 rounded-xl border border-blue-500/15 bg-blue-500/6 px-4 py-3 text-left text-sm font-medium text-blue-500 transition-all shadow-sm shadow-blue-500/3 group active:scale-[0.99] hover:bg-blue-500/10 dark:text-blue-400/80"
                    >
                      <span className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-500/10 text-blue-500 text-xs font-bold group-hover:bg-blue-500/20 transition-colors">
                        {index + 1}
                      </span>
                      {choice}
                    </button>
                  ))}
                </div>
              )}
              <form
                className="flex gap-2"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (input.trim()) handleDecision("submitted", input);
                }}
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={choices?.length ? "Or type your own response..." : "Type your response..."}
                  className="flex-1 backdrop-blur-sm bg-foreground/4 dark:bg-white/2 border border-foreground/8 dark:border-white/5 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 placeholder:text-foreground/25 transition-all"
                />
                <button
                  type="submit"
                  disabled={!input.trim()}
                  className="flex items-center justify-center gap-2 bg-blue-500 text-white font-semibold px-4 py-2 rounded-xl hover:bg-blue-600 disabled:opacity-40 disabled:cursor-not-allowed transition-all text-sm shadow-sm shadow-blue-500/15 active:scale-[0.98]"
                >
                  <Send className="w-4 h-4" />
                  Send
                </button>
                <button
                  type="button"
                  onClick={() => handleDecision("rejected", "")}
                  className="flex items-center justify-center gap-2 backdrop-blur-sm bg-foreground/5 dark:bg-white/3 hover:bg-foreground/8 dark:hover:bg-white/5 text-foreground/60 font-medium px-4 py-2 rounded-xl transition-all text-sm border border-foreground/10 dark:border-white/8 active:scale-[0.98]"
                >
                  <X className="w-4 h-4" />
                  Reject
                </button>
              </form>
            </div>
          );
      }
    };

    return (
      <div className="flex gap-4 max-w-4xl mx-auto w-full animate-in fade-in duration-300">
        <Avatar msgRole="assistant" />
        <div className="flex-1 space-y-2 min-w-0 text-left">
          <div className="font-semibold text-xs uppercase tracking-wider text-muted-foreground/60">HALLW</div>
          <div
            id={requestId}
            className="flex max-w-[85%] flex-col gap-4 rounded-2xl border border-blue-500/14 bg-linear-to-br from-blue-500/10 to-blue-600/5 p-5 shadow-sm shadow-blue-500/3 animate-in slide-in-from-bottom-2 duration-300 dark:border-blue-500/10 dark:from-blue-500/7 dark:to-blue-600/3"
          >
            <div className="flex items-center gap-3 text-blue-500">
              <MessageSquare className="w-5 h-5" />
              <span className="font-semibold text-sm tracking-wide uppercase">Decision Required</span>
              {timeLeft > 0 && status === "pending" && (
                <span className="ml-auto text-xs font-mono backdrop-blur-sm bg-blue-500/10 border border-blue-500/15 px-2 py-1 rounded-md">
                  Expires in {timeLeft}s
                </span>
              )}
            </div>

            <div className="space-y-2">
              <div className="text-sm text-foreground/85 wrap-break-word">
                <MarkdownContent content={message} />
              </div>
            </div>

            {getStatusContent()}
          </div>
        </div>
      </div>
    );
  }
);
