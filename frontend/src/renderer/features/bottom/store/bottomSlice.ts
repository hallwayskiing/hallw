import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

export interface BottomSlice {
  input: string;
  setInput: (input: string) => void;
  submitInput: () => void;
}

export const createBottomSlice: StateCreator<AppState, [], [], BottomSlice> = (set, get) => ({
  input: "",
  setInput: (input) => set({ input }),
  submitInput: () => {
    const { input, startTask } = get();
    if (!input.trim() || get().isRunning) return;
    startTask(input);
    set({ input: "" });
  },
});
