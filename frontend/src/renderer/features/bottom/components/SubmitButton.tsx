import { FormEvent } from "react";

import { Send, Square } from "lucide-react";

import { cn } from "@lib/utils";

import { SubmitButtonProps } from "../types";

export function SubmitButton({ isRunning, hasInput, onStop, onSubmit }: SubmitButtonProps) {
  return (
    <button
      type="button"
      onClick={isRunning ? onStop : (e) => onSubmit(e as unknown as FormEvent)}
      disabled={!isRunning && !hasInput}
      className={cn(
        "flex items-center justify-center px-3 rounded-xl transition-all duration-200 relative overflow-hidden",
        isRunning
          ? "bg-destructive text-destructive-foreground hover:bg-destructive/90"
          : hasInput
            ? "bg-[hsl(199,65%,50%)] text-white shadow-sm hover:bg-[hsl(199,65%,45%)]"
            : "bg-transparent text-muted-foreground",
        "w-10 h-10 p-0 rounded-xl"
      )}
    >
      {/* Shimmer Overlay */}
      {!isRunning && hasInput && (
        <div className="absolute inset-[-100%] rotate-[25deg] pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-shimmer-slide" />
        </div>
      )}

      {isRunning ? (
        <Square className="w-6 h-6 fill-current relative z-10" />
      ) : (
        <Send className="w-6 h-6 relative z-10" />
      )}
    </button>
  );
}
