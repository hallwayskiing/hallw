import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

import type { HistoryItemProps } from "../types";

export interface WelcomeSlice {
  history: HistoryItemProps[];
  isHistoryOpen: boolean;
  isHistoryLoading: boolean;

  toggleHistory: () => void;
  fetchHistory: () => void;
  loadHistory: (id: string) => void;
  deleteHistory: (id: string) => void;

  _onHistoryList: (list: HistoryItemProps[]) => void;
  _onHistoryDeleted: (data: { thread_id: string }) => void;
}

export const createWelcomeSlice: StateCreator<AppState, [], [], WelcomeSlice> = (set, get) => ({
  history: [],
  isHistoryOpen: false,
  isHistoryLoading: false,

  toggleHistory: () => {
    set((state: WelcomeSlice) => {
      const newState = !state.isHistoryOpen;
      if (newState) {
        get().fetchHistory();
      }
      return { isHistoryOpen: newState };
    });
  },

  fetchHistory: () => {
    set({ isHistoryLoading: true });
    const { _socket } = get();
    if (!_socket) {
      set({ isHistoryLoading: false });
      return;
    }
    _socket.emit("get_history");
  },

  loadHistory: (id) => {
    get().openHistorySession(id);
  },

  deleteHistory: (id) => {
    set((state: WelcomeSlice) => ({
      history: state.history.filter((h) => h.id !== id),
    }));

    const { _socket } = get();
    if (!_socket) return;
    _socket.emit("delete_history", { thread_id: id });
  },

  _onHistoryList: (list) => {
    set({ history: list, isHistoryLoading: false });
  },

  _onHistoryDeleted: (data) => {
    set((state: WelcomeSlice) => ({
      history: state.history.filter((h) => h.id !== data.thread_id),
    }));
  },
});
