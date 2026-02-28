import { useAppStore } from "@store/store";

import type { ChatSessionState } from "../store/chatSlice";

/**
 * Derives the active session's state directly from `chatSessions[activeSessionId]`.
 * Returns null when no session is active.
 */
export function useActiveSession(): ChatSessionState | null {
  return useAppStore((s) => {
    const id = s.activeSessionId;
    return id ? (s.chatSessions[id] ?? null) : null;
  });
}
