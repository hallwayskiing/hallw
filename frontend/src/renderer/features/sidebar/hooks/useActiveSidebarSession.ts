import { useAppStore } from "@store/store";

import type { SidebarSessionState } from "../types";

/**
 * Derives the active sidebar session directly from `sidebarSessions[activeSessionId]`.
 */
export function useActiveSidebarSession(): SidebarSessionState | null {
  return useAppStore((s) => {
    const id = s.activeSessionId;
    return id ? (s.sidebarSessions[id] ?? null) : null;
  });
}
