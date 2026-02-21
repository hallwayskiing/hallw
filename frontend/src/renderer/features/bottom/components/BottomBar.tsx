import { useAppStore } from "@store/store";
import { ArrowLeft, Clock, Settings, Zap } from "lucide-react";
import { type FormEvent, useState } from "react";

import { useInputHistory } from "../hooks/useInputHistory";
import { ActionButton } from "./ActionButton";
import { ChatInput } from "./ChatInput";
import { SubmitButton } from "./SubmitButton";

export function BottomBar() {
  const input = useAppStore((s) => s.input);
  const isChatting = useAppStore((s) => s.isChatting);
  const isRunning = useAppStore((s) => s.isRunning);
  const isHistoryOpen = useAppStore((s) => s.isHistoryOpen);
  const setInput = useAppStore((s) => s.setInput);
  const submitInput = useAppStore((s) => s.submitInput);
  const stopTask = useAppStore((s) => s.stopTask);
  const resetSession = useAppStore((s) => s.resetSession);
  const toggleSettings = useAppStore((s) => s.toggleSettings);
  const toggleHistory = useAppStore((s) => s.toggleHistory);

  const [isFocused, setIsFocused] = useState(false);
  const { handleHistoryNavigation, pushHistory } = useInputHistory();

  const onSubmit = (e?: FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isRunning) return;
    pushHistory(input);
    submitInput();
  };

  return (
    <div className="p-4 border-t border-border bg-background">
      <div className="w-full max-w-5xl mx-auto flex items-center gap-3">
        {/* Back / Settings Button */}
        <ActionButton
          onClick={isChatting ? resetSession : toggleSettings}
          icon={isChatting ? ArrowLeft : Settings}
          tooltip={isChatting ? "Back" : "Settings"}
        />

        {/* History/QuickStart Toggle */}
        <ActionButton
          onClick={toggleHistory}
          icon={isHistoryOpen ? Zap : Clock}
          tooltip={isHistoryOpen ? "Back to Quick Start" : "View History"}
        />

        {/* Input Form Container */}
        <div className="flex-1 relative h-11 z-20">
          <ChatInput
            value={input}
            onChange={setInput}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSubmit();
              } else {
                handleHistoryNavigation(e, input, setInput);
              }
            }}
            disabled={isRunning}
            isFocused={isFocused}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={isRunning ? "Running..." : "Tell me what to do..."}
          />
        </div>

        {/* Action Button (Send/Stop) */}
        <SubmitButton isRunning={isRunning} hasInput={!!input.trim()} onStop={stopTask} onSubmit={onSubmit} />
      </div>
    </div>
  );
}
