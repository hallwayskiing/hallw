import type { AppState } from "@store/store";
import { io, type Socket } from "socket.io-client";
import type { StateCreator } from "zustand";

export interface SocketSlice {
  isConnected: boolean;
  _socket: Socket | null;
  initSocket: () => () => void;
  getSocket: () => Socket | null;
}

export const createSocketSlice: StateCreator<AppState, [], [], SocketSlice> = (set, get) => ({
  isConnected: false,
  _socket: null,

  getSocket: () => get()._socket,

  initSocket: () => {
    const socket = io("http://localhost:8000", {
      transports: ["websocket"],
      reconnection: true,
    });

    socket.on("connect", () => {
      console.log("Connected to backend");
      set({ isConnected: true });
    });

    socket.on("connect_error", (err) => {
      console.error("Connection failed:", err);
      set({ isConnected: false });
    });

    socket.on("disconnect", (reason) => {
      console.log("Disconnected from backend:", reason);
      set({ isConnected: false });
    });

    // Bind all event handlers
    const actions = get();

    // Chat events
    socket.on("user_message", actions._onChatUserMessage);
    socket.on("llm_new_reasoning", actions._onChatNewReasoning);
    socket.on("llm_new_text", actions._onChatNewText);

    socket.on("task_started", () => {
      actions._onChatTaskStarted();
      actions._onSidebarTaskStarted();
      actions.setIsChatting(true);
    });

    socket.on("task_finished", actions._onChatTaskFinished);

    socket.on("task_cancelled", () => {
      actions._onChatTaskCancelled();
      actions._onSidebarTaskCancelled();
    });

    socket.on("fatal_error", (data) => {
      actions._onChatFatalError(data);
      actions._onSidebarFatalError(data);
    });

    socket.on("tool_error", (data) => {
      actions._onChatFatalError(data);
      actions._onSidebarFatalError(data);
    });

    socket.on("reset", () => {
      actions._onChatReset();
      actions._onSidebarReset();
      actions.setIsChatting(false);
    });

    socket.on("request_confirmation", (data) => {
      const normalizedData = {
        ...data,
        requestId: data.request_id,
      };
      actions._onChatRequestConfirmation(normalizedData);
    });
    socket.on("request_user_decision", (data) => {
      const normalizedData = {
        ...data,
        requestId: data.request_id,
      };
      actions._onChatRequestUserDecision(normalizedData);
    });

    // Sidebar events
    socket.on("tool_state_update", actions._onToolStateUpdate);
    socket.on("stages_built", actions._onStagesBuilt);
    socket.on("stage_started", actions._onStageStarted);
    socket.on("stages_completed", actions._onStagesCompleted);
    socket.on("stages_edited", actions._onStagesEdited);

    // Welcome events
    socket.on("history_list", actions._onHistoryList);
    socket.on("history_loaded", (data) => {
      actions._onChatHistoryLoaded(data);
      actions._onSidebarHistoryLoaded(data);
      actions.setIsChatting(true);
    });
    socket.on("history_deleted", actions._onHistoryDeleted);

    // Settings events
    socket.on("config_data", actions._onConfigData);
    socket.on("config_updated", actions._onConfigUpdated);

    set({ _socket: socket });

    return () => {
      socket.removeAllListeners();
      socket.close();
      set({ _socket: null, isConnected: false });
    };
  },
});
