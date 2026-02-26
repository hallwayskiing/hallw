import { Key, MessageSquare, Send, X } from "lucide-react";
import { memo, useState } from "react";

import { useCountdown } from "../hooks/useCountdown";
import type { DecisionRequest, DecisionStatus } from "../types";
import { MarkdownContent } from "./MarkdownContent";

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
            <div className="flex gap-3 w-full p-4 rounded-xl bg-green-500/10 border border-green-500/15 text-green-400/80 items-center animate-in fade-in shadow-sm shadow-green-500/3">
              <Key className="w-5 h-5 shrink-0" />
              <div className="flex flex-col">
                <span className="text-xs opacity-90 mt-1">{input}</span>
              </div>
            </div>
          );
        case "rejected":
          return (
            <div className="flex gap-3 w-full p-4 rounded-xl bg-red-500/10 border border-red-500/15 text-red-400/80 items-center animate-in fade-in shadow-sm shadow-red-500/3">
              <X className="w-5 h-5 shrink-0" />
              <span className="text-sm font-medium">Input request rejected.</span>
            </div>
          );
        case "timeout":
          return (
            <div className="flex gap-3 w-full p-4 rounded-xl bg-red-500/10 border border-red-500/15 text-red-400/80 items-center animate-in fade-in shadow-sm shadow-red-500/3">
              <X className="w-5 h-5 shrink-0" />
              <span className="text-sm font-medium">Input request timed out.</span>
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
                      className="w-full text-left px-4 py-3 backdrop-blur-sm bg-blue-500/3 hover:bg-blue-500/7 text-blue-400/80 border border-blue-500/10 rounded-xl text-sm font-medium transition-all flex items-center gap-3 group active:scale-[0.99] shadow-sm shadow-blue-500/3"
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
                  className="flex-1 backdrop-blur-sm bg-white/2 border border-white/5 rounded-xl px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 placeholder:text-foreground/25 transition-all"
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
                  className="flex items-center justify-center gap-2 backdrop-blur-sm bg-white/3 hover:bg-white/5 text-foreground/60 font-medium px-4 py-2 rounded-xl transition-all text-sm border border-white/8 active:scale-[0.98]"
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
      <div
        id={requestId}
        className="flex flex-col gap-4 w-[640px] mx-auto min-w-0 p-5 rounded-2xl backdrop-blur-xl bg-linear-to-br from-blue-500/7 to-blue-600/3 border border-blue-500/10 shadow-sm shadow-blue-500/3 animate-in slide-in-from-bottom-2 duration-300"
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
          <div className="text-sm wrap-break-word">
            <MarkdownContent content={message} />
          </div>
        </div>

        {getStatusContent()}
      </div>
    );
  }
);
