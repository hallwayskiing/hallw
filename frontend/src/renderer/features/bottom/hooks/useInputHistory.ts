import { useCallback, useRef } from "react";

const INPUT_HISTORY_KEY = "chat_input_history";
const MAX_INPUT_HISTORY = 50;

function readHistory(): string[] {
  try {
    const raw = localStorage.getItem(INPUT_HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((item): item is string => typeof item === "string") : [];
  } catch {
    return [];
  }
}

function writeHistory(history: string[]) {
  localStorage.setItem(INPUT_HISTORY_KEY, JSON.stringify(history));
}

/**
 * Provides shell-like input history navigation with up/down arrow keys.
 * Persists submitted messages in localStorage for cross-session navigation.
 */
export function useInputHistory() {
  const historyRef = useRef<string[]>(readHistory());
  const indexRef = useRef(-1); // -1 = not browsing history (current draft)
  const draftRef = useRef(""); // saves the current draft when entering history

  const pushHistory = useCallback((text: string) => {
    const trimmed = text.trim();
    if (!trimmed) return;
    // Avoid consecutive duplicates
    const history = historyRef.current;
    if (history.length === 0 || history[history.length - 1] !== trimmed) {
      history.push(trimmed);
      if (history.length > MAX_INPUT_HISTORY) {
        history.splice(0, history.length - MAX_INPUT_HISTORY);
      }
      writeHistory(history);
    }
    indexRef.current = -1;
  }, []);

  const handleHistoryNavigation = useCallback(
    (e: React.KeyboardEvent, currentValue: string, setInput: (val: string) => void) => {
      if (e.key === "ArrowUp") {
        e.preventDefault();
        const history = historyRef.current;
        if (history.length === 0) return;

        if (indexRef.current === -1) {
          draftRef.current = currentValue;
        }
        const nextIndex = Math.min(indexRef.current + 1, history.length - 1);
        indexRef.current = nextIndex;
        setInput(history[history.length - 1 - nextIndex]);
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        if (indexRef.current === -1) return;

        const history = historyRef.current;
        const nextIndex = indexRef.current - 1;
        if (nextIndex < 0) {
          indexRef.current = -1;
          setInput(draftRef.current);
        } else {
          indexRef.current = nextIndex;
          setInput(history[history.length - 1 - nextIndex]);
        }
      } else {
        indexRef.current = -1;
      }
    },
    []
  );

  return { handleHistoryNavigation, pushHistory };
}
