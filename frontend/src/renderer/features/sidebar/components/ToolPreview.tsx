import { Check, CheckCircle2, Copy, Loader2, X, XCircle } from "lucide-react";

import { cn } from "@lib/utils";

import { useToolPreview } from "../hooks/useToolPreview";
import { ToolPreviewProps } from "../types";

export function ToolPreview({ toolState, isOpen, onClose }: ToolPreviewProps) {
  const {
    activeTab,
    setActiveTab,
    copied,
    copyToClipboard,
    isRunning,
    resultMessage,
    resultData,
    isSuccess,
    parsedArgs,
  } = useToolPreview(toolState);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-in fade-in-0">
      <div className="w-full max-w-2xl bg-card border border-border rounded-lg shadow-lg flex flex-col max-h-[80vh] animate-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "p-2 rounded-full",
                isRunning
                  ? "bg-blue-500/10 text-blue-500"
                  : isSuccess
                    ? "bg-green-500/10 text-green-500"
                    : "bg-red-500/10 text-red-500"
              )}
            >
              {isRunning ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : isSuccess ? (
                <CheckCircle2 className="w-5 h-5" />
              ) : (
                <XCircle className="w-5 h-5" />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-lg">{toolState.tool_name}</h3>
              <p className="text-xs text-muted-foreground font-mono">{toolState.run_id}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-full transition-colors">
            <X className="w-5 h-5 text-muted-foreground" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border px-4">
          <button
            onClick={() => setActiveTab("result")}
            className={cn(
              "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
              activeTab === "result"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            Result
          </button>
          <button
            onClick={() => setActiveTab("args")}
            className={cn(
              "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
              activeTab === "args"
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            Arguments
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden flex flex-col">
          {activeTab === "result" && (
            <div className="p-4 space-y-4 overflow-y-auto">
              {/* Message Section */}
              <div className="space-y-1">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Message</span>
                <div className="text-sm p-3 bg-muted/30 rounded-md border border-border/50 min-h-[40px]">
                  {resultMessage || <span className="text-muted-foreground italic">No message recorded.</span>}
                </div>
              </div>

              {/* Data Section */}
              {!!resultData && (
                <div className="space-y-1 flex-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Data</span>
                    <button
                      onClick={() => copyToClipboard(JSON.stringify(resultData, null, 2))}
                      className="text-xs flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors"
                    >
                      {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                      {copied ? "Copied" : "Copy"}
                    </button>
                  </div>
                  <pre className="text-xs font-mono p-4 bg-muted/50 rounded-md border border-border overflow-x-auto">
                    {JSON.stringify(resultData, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}

          {activeTab === "args" && (
            <div className="p-4 flex-1 flex flex-col overflow-hidden">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Input Arguments
                </span>
                <button
                  onClick={() => copyToClipboard(toolState.args || "")}
                  className="text-xs flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors"
                >
                  {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  {copied ? "Copied" : "Copy"}
                </button>
              </div>
              <div className="flex-1 overflow-auto p-2 space-y-2">
                {parsedArgs.length === 0 ? (
                  <div className="text-sm text-muted-foreground italic p-3 bg-muted/30 rounded-md border border-border/50">
                    No arguments recorded.
                  </div>
                ) : (
                  parsedArgs.map(([key, value]: [string, any]) => (
                    <div key={key} className="flex items-start gap-3 w-full group">
                      <div className="w-[15%] text-[13px] font-bold text-muted-foreground uppercase tracking-tight font-mono truncate text-right shrink-0 pt-2">
                        {key}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="w-full bg-muted/40 border border-border/60 rounded px-3 py-2 text-[13px] font-mono text-foreground overflow-x-auto whitespace-pre no-scrollbar min-h-[38px] flex items-center">
                          {typeof value === "object" ? JSON.stringify(value, null, 2) : String(value)}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-border bg-muted/10 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
