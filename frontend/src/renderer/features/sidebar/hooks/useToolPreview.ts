import { Dispatch, SetStateAction, useCallback, useMemo, useState } from "react";

import { ToolState } from "../types";

export type PreviewEntry = [string, unknown];

// Helper: Parse JSON safely, handling markdown code blocks
function safeParse(input: unknown): unknown {
  if (typeof input !== "string") return input;

  const trimmed = input.trim();
  // Strip markdown code fences if present
  const content = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i)?.[1] || trimmed;

  try {
    return JSON.parse(content);
  } catch {
    return input;
  }
}

// Helper: Convert parsed value to entries for display
function toEntries(value: unknown): PreviewEntry[] {
  if (value === null || value === undefined) return [];
  if (Array.isArray(value)) return value.map((item, index) => [String(index), item]);
  if (typeof value === "object") return Object.entries(value as Record<string, unknown>);
  return [["value", value]];
}

export interface UseToolPreviewReturn {
  activeTab: "result" | "args";
  setActiveTab: Dispatch<SetStateAction<"result" | "args">>;
  copied: boolean;
  copyToClipboard: (text: string) => Promise<void>;
  isRunning: boolean;
  resultMessage: string;
  resultData: unknown;
  isSuccess: boolean;
  parsedArgs: PreviewEntry[];
}

export function useToolPreview(toolState: ToolState | null): UseToolPreviewReturn {
  const [activeTab, setActiveTab] = useState<"result" | "args">("result");
  const [copied, setCopied] = useState(false);

  const parsedResult = useMemo<{ resultMessage: string; resultData: unknown; isSuccess: boolean }>(() => {
    if (!toolState) return { resultMessage: "", resultData: null, isSuccess: false };

    let resultMessage: string = toolState.result || "";
    let resultData: unknown = null;
    let isSuccess = toolState.status === "success";

    const parsed = safeParse(toolState.result);

    // If result is an object, try to extract standard fields (message, data, success)
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      const obj = parsed as Record<string, unknown>;
      // Check if it looks like a standard response wrapper
      if ("message" in obj || "data" in obj || "success" in obj) {
        if (obj.message) resultMessage = String(obj.message);
        if (obj.data !== undefined) resultData = obj.data;
        if (obj.success !== undefined) isSuccess = Boolean(obj.success);
      } else {
        // Otherwise treat the whole object as data
        resultData = parsed;
      }
    } else if (parsed !== null && parsed !== undefined && parsed !== "") {
      // If parsed is array or primitive (and not empty string), treat as data
      resultData = parsed;
    }

    return { resultMessage, resultData, isSuccess };
  }, [toolState?.result, toolState?.status]);

  const parsedArgs = useMemo<PreviewEntry[]>(() => {
    if (toolState?.args === null || toolState?.args === undefined) return [];
    const parsed = safeParse(toolState.args);
    return toEntries(parsed);
  }, [toolState?.args]);

  const copyToClipboard = useCallback(async (text: string) => {
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy text: ", err);
    }
  }, []);

  return {
    activeTab,
    setActiveTab,
    copied,
    copyToClipboard,
    isRunning: toolState?.status === "running",
    resultMessage: parsedResult.resultMessage,
    resultData: parsedResult.resultData,
    isSuccess: parsedResult.isSuccess,
    parsedArgs,
  };
}
