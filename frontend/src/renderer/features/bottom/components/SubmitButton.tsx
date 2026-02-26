import { cn } from "@lib/utils";
import { Send, Square } from "lucide-react";
import { type SubmitEvent, useEffect, useRef, useState } from "react";
import type { SubmitButtonProps } from "../types";

export function SubmitButton({ isRunning, hasInput, onStop, onSubmit }: SubmitButtonProps) {
  const isActive = !isRunning && hasInput;
  const [flashing, setFlashing] = useState(false);
  const prevHasInput = useRef(hasInput);

  useEffect(() => {
    if (!prevHasInput.current && hasInput) {
      setFlashing(true);
      const t = setTimeout(() => setFlashing(false), 600);
      return () => clearTimeout(t);
    }
    prevHasInput.current = hasInput;
  }, [hasInput]);

  return (
    <button
      type="button"
      onClick={isRunning ? onStop : (e) => onSubmit(e as unknown as SubmitEvent)}
      className={cn(
        "group relative flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-200 overflow-hidden select-none",
        isRunning && "bg-destructive/90 text-white hover:bg-destructive",
        isActive && "bg-linear-to-br from-sky-400 to-blue-600 text-white",
        !isRunning && !hasInput && "bg-transparent text-muted-foreground pointer-events-none cursor-default"
      )}
    >
      {/* One-shot shimmer flash: white stripe sweeps top-left → bottom-right */}
      {flashing && (
        <span className="absolute inset-0 pointer-events-none z-20 overflow-hidden rounded-xl">
          <span
            className="absolute h-[200%] w-[35%]"
            style={{
              top: "-50%",
              left: "-40%",
              transform: "rotate(25deg)",
              background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.75), transparent)",
              animation: "shimmer-flash 0.45s ease-in-out forwards",
            }}
          />
        </span>
      )}

      {/* Icon wrapper */}
      <div
        className={cn(
          "relative z-10 flex items-center justify-center transition-transform duration-200",
          isActive && "group-hover:scale-110 group-active:scale-100"
        )}
      >
        {isRunning ? <Square className="w-5 h-5 fill-current" /> : <Send className="w-6 h-6" />}
      </div>
    </button>
  );
}
