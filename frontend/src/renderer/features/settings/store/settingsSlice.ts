import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

import type { Config, SaveStatus, ServerResponse } from "../types";

export interface SettingsSlice {
  config: Config;
  isLoading: boolean;
  saveStatus: SaveStatus;
  statusMsg: string;
  setSaveStatus: (status: SaveStatus) => void;
  updateConfigLocal: (key: string, value: unknown) => void;
  _onConfigData: (data: Config) => void;
  _onConfigUpdated: (response: ServerResponse) => void;
}

export const createSettingsSlice: StateCreator<AppState, [], [], SettingsSlice> = (set) => ({
  config: {},
  isLoading: true,
  saveStatus: "idle" as SaveStatus,
  statusMsg: "",

  setSaveStatus: (status) => set({ saveStatus: status }),

  updateConfigLocal: (key, value) =>
    set((state) => ({
      config: { ...state.config, [key]: value },
    })),

  _onConfigData: (data) =>
    set({
      config: data,
      isLoading: false,
    }),

  _onConfigUpdated: (response) => {
    if (response.success) {
      set({ saveStatus: "success", statusMsg: "" });
    } else {
      set({ saveStatus: "error", statusMsg: `Error: ${response.error}` });
    }
  },
});
