import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

import { HIDDEN_TOOLS } from "../constants";
import { patchSidebar, setRunningToolToError } from "../lib/utils";
import type { SidebarSlice } from "../types";

export type { SidebarSessionState, SidebarSlice } from "../types";

export const createSidebarSlice: StateCreator<AppState, [], [], SidebarSlice> = (set, get) => ({
  sidebarSessions: {},

  getVisibleTools: () => {
    const { activeSessionId, sidebarSessions } = get();
    const session = activeSessionId ? sidebarSessions[activeSessionId] : null;
    if (!session) return [];
    return session.toolStates.filter((t) => !HIDDEN_TOOLS.includes(t.tool_name));
  },

  _onToolStateUpdate: (sessionId, nextToolState) => {
    if (!nextToolState || !sessionId || !get().chatSessions[sessionId]) return;
    set((state) =>
      patchSidebar(state, sessionId, (s) => {
        const { run_id } = nextToolState;
        if (!run_id) return { ...s, toolStates: [...s.toolStates, nextToolState] };

        const idx = s.toolStates.findIndex((t) => t.run_id === run_id);
        if (idx >= 0) {
          const updated = [...s.toolStates];
          updated[idx] = { ...updated[idx], ...nextToolState };
          return { ...s, toolStates: updated };
        }
        return { ...s, toolStates: [...s.toolStates, nextToolState] };
      })
    );
  },

  _onStagesBuilt: (sessionId, data) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    const nextStages = Array.isArray(data) ? data : data?.stages || [];
    set((state) => patchSidebar(state, sessionId, (s) => ({ ...s, stages: nextStages })));
  },

  _onStageStarted: (sessionId, data) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    set((state) => patchSidebar(state, sessionId, (s) => ({ ...s, currentStageIndex: data.stage_index })));
  },

  _onStagesCompleted: (sessionId, data) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    set((state) =>
      patchSidebar(state, sessionId, (s) => ({
        ...s,
        completedStages: [...new Set([...s.completedStages, ...data.stage_indices])],
      }))
    );
  },

  _onStagesEdited: (sessionId, data) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    set((state) =>
      patchSidebar(state, sessionId, (s) => ({
        ...s,
        stages: data.stages,
        currentStageIndex: data.current_index,
        completedStages: s.completedStages.filter((i) => i < data.current_index),
        errorStageIndex: -1,
      }))
    );
  },

  _onSidebarTaskStarted: (sessionId) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    set((state) =>
      patchSidebar(state, sessionId, (s) => ({
        ...s,
        stages: [],
        currentStageIndex: -1,
        completedStages: [],
        errorStageIndex: -1,
      }))
    );
  },

  _onSidebarTaskCancelled: (sessionId) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    set((state) => patchSidebar(state, sessionId, setRunningToolToError));
  },

  _onSidebarFatalError: (sessionId) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    set((state) => patchSidebar(state, sessionId, setRunningToolToError));
  },

  _onSidebarReset: (sessionId) => {
    if (!sessionId || !get().sidebarSessions[sessionId]) return;
    set((state) => patchSidebar(state, sessionId, (s) => ({ ...setRunningToolToError(s), currentStageIndex: -1 })));
  },

  _onSidebarHistoryLoaded: (sessionId, data) => {
    if (!sessionId || !get().chatSessions[sessionId]) return;
    set((state) =>
      patchSidebar(state, sessionId, () => ({
        toolStates: data.toolStates || [],
        stages: [],
        currentStageIndex: -1,
        completedStages: [],
        errorStageIndex: -1,
      }))
    );
  },
});
