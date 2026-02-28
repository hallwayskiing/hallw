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
  showCdpViewForSession: (sessionId: string, headless?: boolean, userDataDir?: string) => Promise<void>;
  hideCdpView: () => Promise<void>;
  destroyCdpView: (sessionId: string) => Promise<void>;
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
  showCdpViewForSession: async (sessionId, headless = false, userDataDir) => {
    try {
      if (window.api?.cdpCreateOrShow) {
        await window.api.cdpCreateOrShow(sessionId, headless, userDataDir);
      }
    } catch (e) {
      console.error("Failed to create/show CDP view", e);
    }
    set({ showCdpView: !headless });
  },
  hideCdpView: async () => {
    try {
      if (window.api?.cdpHide) {
        await window.api.cdpHide();
      }
    } catch (e) {
      console.error("Failed to hide CDP view", e);
    }
    set({ showCdpView: false });
  },
  destroyCdpView: async (sessionId) => {
    try {
      if (window.api?.cdpDestroy) {
        await window.api.cdpDestroy(sessionId);
      }
    } catch (e) {
      console.error("Failed to destroy CDP view", e);
    }
    set((state) => {
      const session = state.chatSessions?.[sessionId];
      if (!session) return { showCdpView: false };
      return {
        showCdpView: false,
        chatSessions: {
          ...state.chatSessions,
          [sessionId]: { ...session, hasCdpView: false },
        },
      };
    });
  },
});
