import type { AppState } from "@store/store";

import type { SidebarSessionState } from "../types";

// ---------------------------------------------------------------------------
// Session factory
// ---------------------------------------------------------------------------

export function createEmptySidebarSession(): SidebarSessionState {
  return { toolStates: [], stages: [], currentStageIndex: -1, completedStages: [], errorStageIndex: -1 };
}

// ---------------------------------------------------------------------------
// Session map updater
// ---------------------------------------------------------------------------

export function patchSidebar(
  state: AppState,
  sessionId: string,
  updater: (s: SidebarSessionState) => SidebarSessionState
): Partial<AppState> {
  const current = state.sidebarSessions[sessionId] || createEmptySidebarSession();
  return { sidebarSessions: { ...state.sidebarSessions, [sessionId]: updater(current) } };
}

// ---------------------------------------------------------------------------
// Tool state helpers
// ---------------------------------------------------------------------------

export function setRunningToolToError(session: SidebarSessionState): SidebarSessionState {
  const toolStates = [...session.toolStates];
  if (toolStates.length > 0) {
    const last = toolStates.length - 1;
    if (toolStates[last].status === "running") {
      toolStates[last] = { ...toolStates[last], status: "error" };
    }
  }
  return { ...session, toolStates, errorStageIndex: session.currentStageIndex };
}
