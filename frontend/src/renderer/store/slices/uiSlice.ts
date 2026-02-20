import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

export interface UISlice {
  theme: "light" | "dark";
  isSettingsOpen: boolean;
  isChatting: boolean;
  showCdpView: boolean;
  setTheme: (theme: "light" | "dark") => void;
  toggleTheme: () => void;
  toggleSettings: () => void;
  setIsChatting: (isChatting: boolean) => void;
  toggleCdpView: (show: boolean, headless?: boolean, userDataDir?: string) => Promise<void>;
}

export const createUISlice: StateCreator<AppState, [], [], UISlice> = (set) => ({
  theme: "dark",
  isSettingsOpen: false,
  isChatting: false,
  showCdpView: false,
  setTheme: (theme) => set({ theme }),
  toggleTheme: () =>
    set((state) => {
      const newTheme = state.theme === "light" ? "dark" : "light";
      localStorage.setItem("theme", newTheme);
      document.documentElement.classList.toggle("dark", newTheme === "dark");
      return { theme: newTheme };
    }),
  toggleSettings: () => set((state) => ({ isSettingsOpen: !state.isSettingsOpen })),
  setIsChatting: (isChatting) => set({ isChatting }),
  toggleCdpView: async (show, headless = false, userDataDir) => {
    try {
      if (window.api?.resizeCdpWindow) {
        await window.api.resizeCdpWindow(show, headless, userDataDir);
      }
    } catch (e) {
      console.error("Failed to resize window for CDP view", e);
    }
    set({ showCdpView: show && !headless });
  },
});
