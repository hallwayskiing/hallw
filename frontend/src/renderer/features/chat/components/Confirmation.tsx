import { useAppStore } from "@store/store";
import { AlertTriangle, Check, X } from "lucide-react";
import { memo, useState } from "react";

import { useCountdown } from "../hooks/useCountdown";
import type { ConfirmationProps, ConfirmationStatus } from "../types";

export const Confirmation = memo(({ requestId, message, timeout, initialStatus, onDecision }: ConfirmationProps) => {
  const handleConfirmationDecision = useAppStore((s) => s.handleConfirmationDecision);
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
          <div className="flex gap-3 w-full p-4 rounded-xl bg-green-500/10 border border-green-500/15 text-green-400/80 items-center animate-in fade-in shadow-sm shadow-green-500/3">
            <Check className="w-5 h-5 shrink-0" />
            <span className="text-sm font-medium">Confirmation approved.</span>
          </div>
        );
      case "rejected":
        return (
          <div className="flex gap-3 w-full p-4 rounded-xl bg-red-500/10 border border-red-500/15 text-red-400/80 items-center animate-in fade-in shadow-sm shadow-red-500/3">
            <X className="w-5 h-5 shrink-0" />
            <span className="text-sm font-medium">Confirmation rejected.</span>
          </div>
        );
      case "timeout":
        return (
          <div className="flex gap-3 w-full p-4 rounded-xl bg-red-500/10 border border-red-500/15 text-red-400/80 items-center animate-in fade-in shadow-sm shadow-red-500/3">
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
              className="flex-1 flex items-center justify-center gap-2 bg-amber-500 text-black font-semibold py-2 rounded-lg hover:bg-amber-400 active:scale-[0.98] transition-all text-sm shadow-sm shadow-amber-500/20"
            >
              <Check className="w-4 h-4" />
              Approve
            </button>
            <button
              type="button"
              onClick={() => handleDecision("rejected")}
              className="flex-1 flex items-center justify-center gap-2 backdrop-blur-sm bg-white/3 hover:bg-white/5 text-foreground/60 font-medium py-2 rounded-lg transition-all text-sm border border-white/8 active:scale-[0.98]"
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
      className="flex flex-col gap-4 w-[640px] mx-auto min-w-0 p-5 rounded-2xl backdrop-blur-xl bg-linear-to-br from-amber-500/7 to-amber-600/3 border border-amber-500/10 shadow-sm shadow-amber-500/3 animate-in slide-in-from-bottom-2 duration-300"
    >
      <div className="flex items-center gap-3 text-amber-500">
        <AlertTriangle className="w-5 h-5" />
        <span className="font-semibold text-sm tracking-wide uppercase">Confirmation</span>
        {timeLeft > 0 && status === "pending" && (
          <span className="ml-auto text-xs font-mono backdrop-blur-sm bg-amber-500/10 border border-amber-500/15 px-2 py-1 rounded-md">
            Expires in {timeLeft}s
          </span>
        )}
      </div>

      <div className="space-y-2">
        <p className="text-sm text-foreground/80">System command needs your confirmation:</p>
        <div className="backdrop-blur-sm bg-white/2 rounded-xl p-3 border border-white/5 font-mono text-xs break-all whitespace-pre-wrap text-foreground/70">
          {message}
        </div>
      </div>

      {getStatusContent()}
    </div>
  );
});
