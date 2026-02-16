import { useAppStore } from "@store/store";
import { AlertTriangle, Check, X } from "lucide-react";
import { memo, useState } from "react";

import { useCountdown } from "../hooks/useCountdown";
import type { ConfirmationProps, ConfirmationStatus } from "../types";

export const Confirmation = memo(({ requestId, message, timeout, initialStatus, onDecision }: ConfirmationProps) => {
  const { handleConfirmationDecision } = useAppStore();
  const [status, setStatus] = useState<ConfirmationStatus>(initialStatus || "pending");

  const handleTimeout = () => {
    if (status === "pending") {
      handleDecision("timeout");
    }
  };

  const timeLeft = useCountdown(timeout, handleTimeout, status === "pending");

  const handleDecision = (_status: ConfirmationStatus) => {
    setStatus(_status);
    handleConfirmationDecision(_status);
    onDecision?.(_status);
  };

  const getStatusContent = () => {
    switch (status) {
      case "approved":
        return (
          <div className="flex gap-3 w-full p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 items-center animate-in fade-in">
            <Check className="w-5 h-5 shrink-0" />
            <span className="text-sm font-medium">Confirmation approved.</span>
          </div>
        );
      case "rejected":
        return (
          <div className="flex gap-3 w-full p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 items-center animate-in fade-in">
            <X className="w-5 h-5 shrink-0" />
            <span className="text-sm font-medium">Confirmation rejected.</span>
          </div>
        );
      case "timeout":
        return (
          <div className="flex gap-3 w-full p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 items-center animate-in fade-in">
            <X className="w-5 h-5 shrink-0" />
            <span className="text-sm font-medium">Confirmation timed out.</span>
          </div>
        );
      default:
        return (
          <div className="flex gap-3 pt-1">
            <button
              type="button"
              onClick={() => handleDecision("approved")}
              className="flex-1 flex items-center justify-center gap-2 bg-amber-500 text-black font-semibold py-2 rounded-lg hover:bg-amber-400 transition-colors text-sm"
            >
              <Check className="w-4 h-4" />
              Approve
            </button>
            <button
              type="button"
              onClick={() => handleDecision("rejected")}
              className="flex-1 flex items-center justify-center gap-2 bg-muted hover:bg-muted/80 text-foreground font-medium py-2 rounded-lg transition-colors text-sm border border-border"
            >
              <X className="w-4 h-4" />
              Reject
            </button>
          </div>
        );
    }
  };

  return (
    <div
      key={requestId}
      className="flex flex-col gap-4 max-w-3xl mx-auto w-full p-5 rounded-xl bg-amber-500/10 border border-amber-500/20 animate-in slide-in-from-bottom-2"
    >
      <div className="flex items-center gap-3 text-amber-500">
        <AlertTriangle className="w-5 h-5" />
        <span className="font-semibold text-sm tracking-wide uppercase">Confirmation</span>
        {timeLeft > 0 && status === "pending" && (
          <span className="ml-auto text-xs font-mono bg-amber-500/20 px-2 py-1 rounded">Expires in {timeLeft}s</span>
        )}
      </div>

      <div className="space-y-2">
        <p className="text-sm text-foreground/80">The agent wants your confirmation:</p>
        <div className="bg-background/50 rounded-lg p-3 border border-border/50 font-mono text-xs overflow-x-auto">
          {message}
        </div>
      </div>

      {getStatusContent()}
    </div>
  );
});
