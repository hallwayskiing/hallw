import { AppState } from "@store/store";
import { StateCreator } from "zustand";

import { HIDDEN_TOOLS } from "../constants";
import { ToolState } from "../types";

export interface SidebarSlice {
  toolStates: ToolState[];
  stages: string[];
  currentStageIndex: number;
  completedStages: number[];
  errorStageIndex: number;

  getVisibleTools: () => ToolState[];

  _onToolStateUpdate: (state: ToolState) => void;
  _onStagesBuilt: (data: string[] | { stages?: string[] }) => void;
  _onStageStarted: (data: { stage_index: number }) => void;
  _onStagesCompleted: (data: { stage_indices: number[] }) => void;
  _onStagesEdited: (data: { stages: string[]; current_index: number }) => void;

  // Lifecycle handlers
  _onSidebarTaskStarted: () => void;
  _onSidebarTaskCancelled: () => void;
  _onSidebarFatalError: (data: any) => void;
  _onSidebarReset: () => void;
  _onSidebarHistoryLoaded: (data: { toolStates?: ToolState[] }) => void;
}

export const createSidebarSlice: StateCreator<AppState, [], [], SidebarSlice> = (set, get) => ({
  toolStates: [],
  stages: [],
  currentStageIndex: -1,
  completedStages: [],
  errorStageIndex: -1,

  getVisibleTools: () => {
    return get().toolStates.filter((t: ToolState) => !HIDDEN_TOOLS.includes(t.tool_name));
  },

  _onToolStateUpdate: (state) => {
    if (!state) return;
    set((prev: SidebarSlice) => {
      const { run_id } = state;
      if (!run_id) return { toolStates: [...prev.toolStates, state] };
      const idx = prev.toolStates.findIndex((t) => t.run_id === run_id);
      if (idx >= 0) {
        const updated = [...prev.toolStates];
        updated[idx] = { ...updated[idx], ...state };
        return { toolStates: updated };
      }
      return { toolStates: [...prev.toolStates, state] };
    });
  },

  _onStagesBuilt: (data) => {
    const stages = Array.isArray(data) ? data : data?.stages || [];
    set({ stages: stages });
  },

  _onStageStarted: (data) => {
    set({ currentStageIndex: data.stage_index });
  },

  _onStagesCompleted: (data) => {
    set((state: SidebarSlice) => ({
      completedStages: [...new Set([...state.completedStages, ...data.stage_indices])],
    }));
  },

  _onStagesEdited: (data) => {
    set((state: SidebarSlice) => ({
      stages: data.stages,
      currentStageIndex: data.current_index,
      // Keep only completed indices that are still within bounds
      completedStages: state.completedStages.filter((i) => i < data.current_index),
      errorStageIndex: -1,
    }));
  },

  _onSidebarTaskStarted: () => {
    set({
      stages: [],
      currentStageIndex: -1,
      completedStages: [],
      errorStageIndex: -1,
    });
  },

  _onSidebarTaskCancelled: () => {
    set((state: SidebarSlice) => {
      const updatedToolStates = [...state.toolStates];
      if (updatedToolStates.length > 0) {
        const lastIdx = updatedToolStates.length - 1;
        if (updatedToolStates[lastIdx].status === "running") {
          updatedToolStates[lastIdx] = {
            ...updatedToolStates[lastIdx],
            status: "error",
          };
        }
      }
      return {
        toolStates: updatedToolStates,
        errorStageIndex: state.currentStageIndex,
      };
    });
  },

  _onSidebarFatalError: () => {
    set((state: SidebarSlice) => {
      const updatedToolStates = [...state.toolStates];
      if (updatedToolStates.length > 0) {
        const lastIdx = updatedToolStates.length - 1;
        if (updatedToolStates[lastIdx].status === "running") {
          updatedToolStates[lastIdx] = {
            ...updatedToolStates[lastIdx],
            status: "error",
          };
        }
      }
      return {
        toolStates: updatedToolStates,
        errorStageIndex: state.currentStageIndex,
      };
    });
  },

  _onSidebarReset: () => {
    set({
      toolStates: [],
      stages: [],
      currentStageIndex: -1,
      completedStages: [],
      errorStageIndex: -1,
    });
  },

  _onSidebarHistoryLoaded: (data) => {
    set({
      toolStates: data.toolStates || [],
      stages: [],
      currentStageIndex: -1,
      completedStages: [],
      errorStageIndex: -1,
    });
  },
});
