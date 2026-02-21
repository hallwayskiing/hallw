import { useCallback, useRef } from "react";

/**
 * Provides shell-like input history navigation with up/down arrow keys.
 * Only tracks messages submitted during the current app session (in-memory).
 */
export function useInputHistory() {
  const historyRef = useRef<string[]>([]); // session-only history
  const indexRef = useRef(-1); // -1 = not browsing history (current draft)
  const draftRef = useRef(""); // saves the current draft when entering history

  const pushHistory = useCallback((text: string) => {
    if (!text.trim()) return;
    // Avoid consecutive duplicates
    const history = historyRef.current;
    if (history.length === 0 || history[history.length - 1] !== text) {
      history.push(text);
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
