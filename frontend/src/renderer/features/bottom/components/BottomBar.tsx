import { useAppStore } from "@store/store";
import { ArrowLeft, Paperclip, ScrollText, Settings, X, Zap } from "lucide-react";
import { type DragEvent, type SubmitEvent, useCallback, useEffect, useRef, useState } from "react";

import { useActiveSession } from "../../chat/hooks/useActiveSession";
import { useInputHistory } from "../hooks/useInputHistory";
import { ActionButton } from "./ActionButton";
import { ChatInput } from "./ChatInput";
import { SubmitButton } from "./SubmitButton";

const getDisplayNames = (files: { id: string; name: string; path: string | null }[]) => {
  const counts = new Map<string, number>();
  const totals = new Map<string, Set<string>>();

  for (const file of files) {
    const paths = totals.get(file.name) ?? new Set<string>();
    paths.add(file.path ?? file.id);
    totals.set(file.name, paths);
  }

  return new Map(
    files.map((file) => {
      const distinctPathCount = totals.get(file.name)?.size ?? 0;
      if (distinctPathCount <= 1) {
        return [file.id, file.name] as const;
      }

      const next = (counts.get(file.name) ?? 0) + 1;
      counts.set(file.name, next);
      return [file.id, `${file.name}(${next})`] as const;
    })
  );
};

export function BottomBar() {
  const input = useAppStore((s) => s.input);
  const isChatting = useAppStore((s) => s.isChatting);
  const session = useActiveSession();
  const isRunning = session?.isRunning ?? false;
  const isHistoryOpen = useAppStore((s) => s.isHistoryOpen);
  const setInput = useAppStore((s) => s.setInput);
  const submitInput = useAppStore((s) => s.submitInput);
  const stopTask = useAppStore((s) => s.stopTask);
  const resetSession = useAppStore((s) => s.resetSession);
  const toggleSettings = useAppStore((s) => s.toggleSettings);
  const toggleHistory = useAppStore((s) => s.toggleHistory);
  const attachedFiles = useAppStore((s) => s.attachedFiles);
  const addFiles = useAppStore((s) => s.addFiles);
  const addLocalPaths = useAppStore((s) => s.addLocalPaths);
  const removeFile = useAppStore((s) => s.removeFile);

  const [isFocused, setIsFocused] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const { handleHistoryNavigation, pushHistory } = useInputHistory();

  const inputRef = useRef<HTMLTextAreaElement>(null);
  const prevIsRunningRef = useRef(isRunning);

  const displayNames = getDisplayNames(attachedFiles);

  useEffect(() => {
    if (!isRunning && prevIsRunningRef.current) {
      setTimeout(() => inputRef.current?.focus(), 50);
    }
    prevIsRunningRef.current = isRunning;
  }, [isRunning]);

  const onSubmit = (e?: SubmitEvent) => {
    e?.preventDefault();
    if ((!input.trim() && attachedFiles.length === 0) || isRunning) return;
    pushHistory(input);
    submitInput();
  };

  // --- Paste handler ---
  const handlePaste = useCallback(
    (e: React.ClipboardEvent) => {
      const items = e.clipboardData?.items;
      if (!items) return;

      const files: File[] = [];
      for (const item of items) {
        if (item.kind === "file") {
          const file = item.getAsFile();
          if (file) files.push(file);
        }
      }

      if (files.length > 0) {
        e.preventDefault();
        void addFiles(files);
      }
    },
    [addFiles]
  );

  // --- Drag & Drop ---
  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);

      const files = e.dataTransfer?.files;
      if (files && files.length > 0) {
        void addFiles(Array.from(files));
      }
    },
    [addFiles]
  );

  // --- File picker ---
  const handleFilePickerClick = useCallback(async () => {
    const pickedPaths = (await window.api?.pickFiles?.()) ?? [];
    if (pickedPaths.length > 0) {
      addLocalPaths(pickedPaths);
    }
  }, []);

  return (
    <fieldset
      className="relative py-2.5 px-4 border-t border-border bg-background"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Floating Attached Files Display */}
      {attachedFiles.length > 0 && (
        <div className="absolute bottom-full mb-3 left-0 right-0 w-full px-4 pointer-events-none z-10 flex justify-center">
          <div className="w-full max-w-5xl flex flex-wrap gap-2 items-end justify-start pointer-events-auto">
            {attachedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-background/50 backdrop-blur-md border border-border/80 shadow-xs text-sm text-foreground/90 transition-all duration-200 hover:bg-background/70 group"
              >
                <div className="p-1.5 bg-muted/60 rounded-lg text-muted-foreground">
                  <Paperclip className="w-4 h-4" />
                </div>
                <div className="flex flex-col flex-1 min-w-0 max-w-37.5">
                  <span className="truncate font-medium text-xs">{displayNames.get(file.id) ?? file.name}</span>
                  {file.isSaving && (
                    <span className="text-[10px] text-muted-foreground/60 animate-pulse">saving...</span>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(file.id)}
                  className="ml-1 p-1 rounded-full text-muted-foreground hover:bg-foreground/10 hover:text-foreground transition-colors opacity-0 group-hover:opacity-100"
                  aria-label={`Remove ${displayNames.get(file.id) ?? file.name}`}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="w-full max-w-5xl mx-auto flex items-end gap-3">
        {/* Back / Settings Button */}
        <div className="pb-1 text-muted-foreground">
          <ActionButton
            onClick={isChatting ? resetSession : toggleSettings}
            icon={isChatting ? ArrowLeft : Settings}
            tooltip={isChatting ? "Back" : "Settings"}
          />
        </div>

        {/* History/QuickStart Toggle */}
        <div className="pb-1 text-muted-foreground">
          <ActionButton
            onClick={toggleHistory}
            icon={isHistoryOpen ? Zap : ScrollText}
            tooltip={isHistoryOpen ? "Back to Quick Start" : "View History"}
          />
        </div>

        {/* File Attachment Button */}
        <div className="pb-1 text-muted-foreground">
          <ActionButton
            onClick={handleFilePickerClick}
            icon={Paperclip}
            tooltip="Attach files"
            active={attachedFiles.length > 0}
          />
        </div>

        {/* Input Form Container */}
        <div className={`flex-1 relative z-20 ${isDragOver ? "ring-2 ring-ring ring-offset-1 rounded-2xl" : ""}`}>
          <ChatInput
            ref={inputRef}
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
            onPaste={handlePaste}
            disabled={isRunning}
            isFocused={isFocused}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={isDragOver ? "Drop files here..." : isRunning ? "Running..." : "Tell me what to do..."}
          />
        </div>

        {/* Action Button (Send/Stop) */}
        <div className="pb-1">
          <SubmitButton
            isRunning={isRunning}
            hasInput={!!input.trim() || attachedFiles.length > 0}
            onStop={stopTask}
            onSubmit={onSubmit}
          />
        </div>
      </div>
    </fieldset>
  );
}
