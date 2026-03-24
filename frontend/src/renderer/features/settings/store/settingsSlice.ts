import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

import type { Config, SaveStatus, ServerResponse } from "../types";

const MODEL_RECENT_USED_KEY = "model_recent_used";
const MAX_RECENT_MODELS = 10;

function readRecentModels(): string[] {
  try {
    const raw = localStorage.getItem(MODEL_RECENT_USED_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((item): item is string => typeof item === "string") : [];
  } catch {
    return [];
  }
}

function writeRecentModels(models: string[]) {
  localStorage.setItem(MODEL_RECENT_USED_KEY, JSON.stringify(models));
}

function updateRecentModels(models: string[], modelName: string) {
  const nextModel = modelName.trim();
  if (!nextModel) return models;

  const deduped = models.filter((model) => model !== nextModel);
  return [nextModel, ...deduped].slice(0, MAX_RECENT_MODELS);
}

export interface SettingsSlice {
  config: Config;
  recentModels: string[];
  isLoading: boolean;
  saveStatus: SaveStatus;
  statusMsg: string;
  setSaveStatus: (status: SaveStatus) => void;
  updateConfigLocal: (key: string, value: unknown) => void;
  addRecentModelLocal: (modelName: string) => void;
  removeRecentModelLocal: (modelName: string) => void;
  _onConfigData: (data: Config) => void;
  _onConfigUpdated: (response: ServerResponse) => void;
}

export const createSettingsSlice: StateCreator<AppState, [], [], SettingsSlice> = (set) => ({
  config: {},
  recentModels: readRecentModels(),
  isLoading: true,
  saveStatus: "idle" as SaveStatus,
  statusMsg: "",

  setSaveStatus: (status) => set({ saveStatus: status }),

  updateConfigLocal: (key, value) =>
    set((state) => ({
      config: { ...state.config, [key]: value },
    })),

  addRecentModelLocal: (modelName) =>
    set(() => {
      const nextRecentModels = updateRecentModels(readRecentModels(), modelName);
      writeRecentModels(nextRecentModels);
      return { recentModels: nextRecentModels };
    }),

  removeRecentModelLocal: (modelName) =>
    set((state) => {
      const nextRecentModels = state.recentModels.filter((model) => model !== modelName);
      writeRecentModels(nextRecentModels);
      return { recentModels: nextRecentModels };
    }),

  _onConfigData: (data) =>
    set({
      config: data,
      recentModels: readRecentModels(),
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
