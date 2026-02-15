import { useEffect } from "react";

import { useAppStore } from "@store/store";
import { AlertCircle, Check, Loader2 } from "lucide-react";

export function SaveStatusIndicator() {
  const { saveStatus, statusMsg, setSaveStatus } = useAppStore();

  // Auto-clear success status
  useEffect(() => {
    if (saveStatus === "success") {
      const timer = setTimeout(() => setSaveStatus("idle"), 3000);
      return () => clearTimeout(timer);
    }
  }, [saveStatus, setSaveStatus]);

  if (saveStatus === "idle") return null;

  return (
    <div className="flex items-center gap-2 px-4 py-3 text-xs font-medium animate-in fade-in duration-200">
      {saveStatus === "saving" && (
        <>
          <Loader2 className="w-3.5 h-3.5 animate-spin text-muted-foreground" />
          <span className="text-muted-foreground">Saving...</span>
        </>
      )}
      {saveStatus === "success" && (
        <>
          <Check className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-emerald-400 text-sm">Saved</span>
        </>
      )}
      {saveStatus === "error" && (
        <>
          <AlertCircle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" />
          <span className="text-red-400 truncate">{statusMsg}</span>
        </>
      )}
    </div>
  );
}
