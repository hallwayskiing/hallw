import type { AppState } from "@store/store";
import { io, type Socket } from "socket.io-client";
import type { StateCreator } from "zustand";
import type { MessageRole } from "../../features/chat/types";
import type { ToolState } from "../../features/sidebar/types";

interface RawMessage {
  role: MessageRole;
  type: "text";
  content: string;
  reasoning: string;
}

interface SessionPayload {
  session_id?: string;
}

interface LlmReasoningPayload extends SessionPayload {
  reasoning?: string;
}

interface LlmTextPayload extends SessionPayload {
  text?: string;
}

interface FatalPayload extends SessionPayload {
  message?: string;
}

interface ConfirmationPayload extends SessionPayload {
  request_id: string;
  message: string;
  timeout?: number;
}

interface DecisionPayload extends SessionPayload {
  request_id: string;
  message: string;
  choices?: string[];
  timeout?: number;
}

interface CdpPayload extends SessionPayload {
  request_id: string;
  headless?: boolean;
  userDataDir?: string;
}

interface HistoryLoadedPayload extends SessionPayload {
  messages: RawMessage[];
  thread_id?: string;
  toolStates?: ToolState[];
}

export interface SocketSlice {
  isConnected: boolean;
  _socket: Socket | null;
  initSocket: () => () => void;
  getSocket: () => Socket | null;
}

function getSessionId(payload: unknown): string | null {
  if (payload && typeof payload === "object" && "session_id" in payload) {
    const value = (payload as SessionPayload).session_id;
    if (typeof value === "string" && value.trim()) return value;
  }
  return null;
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
    socket.on("llm_new_reasoning", (data: LlmReasoningPayload | string) => {
      const sessionId = getSessionId(data) || actions.activeSessionId;
      const reasoning = typeof data === "string" ? data : data?.reasoning || "";
      if (!sessionId || !reasoning) return;
      actions._onChatNewReasoning(sessionId, reasoning);
    });

    socket.on("llm_new_text", (data: LlmTextPayload | string) => {
      const sessionId = getSessionId(data) || actions.activeSessionId;
      const text = typeof data === "string" ? data : data?.text || "";
      if (!sessionId || !text) return;
      actions._onChatNewText(sessionId, text);
    });

    socket.on("task_started", (data: SessionPayload) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      actions._onChatTaskStarted(sessionId);
      actions._onSidebarTaskStarted(sessionId);
    });

    socket.on("task_finished", (data: SessionPayload) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      actions._onChatTaskFinished(sessionId);
    });

    socket.on("task_cancelled", (data: SessionPayload) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      actions._onChatTaskCancelled(sessionId);
      actions._onSidebarTaskCancelled(sessionId);
    });

    socket.on("fatal_error", (data: FatalPayload | string) => {
      const sessionId = getSessionId(data) || actions.activeSessionId;
      if (!sessionId) return;
      actions._onChatFatalError(sessionId, data);
      actions._onSidebarFatalError(sessionId, data);
    });

    socket.on("tool_error", (data: FatalPayload | string) => {
      const sessionId = getSessionId(data) || actions.activeSessionId;
      if (!sessionId) return;
      actions._onChatFatalError(sessionId, data);
      actions._onSidebarFatalError(sessionId, data);
    });

    socket.on("reset", (data: SessionPayload) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const shouldCloseCdp = actions.activeSessionId === sessionId;
      actions._onChatReset(sessionId);
      actions._onSidebarReset(sessionId);
      if (shouldCloseCdp) {
        void actions.destroyCdpView(sessionId);
      }
    });

    socket.on("request_confirmation", (data: ConfirmationPayload) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const normalizedData = {
        ...data,
        requestId: data.request_id,
      };
      actions._onChatRequestConfirmation(sessionId, normalizedData);
    });

    socket.on("request_user_decision", (data: DecisionPayload) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const normalizedData = {
        ...data,
        requestId: data.request_id,
      };
      actions._onChatRequestUserDecision(sessionId, normalizedData);
    });

    // Sidebar events
    socket.on("tool_state_update", (data: SessionPayload & Record<string, unknown>) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const { session_id: _sessionId, ...toolPayload } = data;
      actions._onToolStateUpdate(sessionId, toolPayload as unknown as ToolState);
    });
    socket.on("stages_built", (data: SessionPayload & Record<string, unknown>) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const { session_id: _sessionId, ...payload } = data;
      actions._onStagesBuilt(sessionId, payload as string[] | { stages?: string[] });
    });
    socket.on("stage_started", (data: SessionPayload & { stage_index: number }) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const { stage_index } = data;
      actions._onStageStarted(sessionId, { stage_index });
    });
    socket.on("stages_completed", (data: SessionPayload & { stage_indices: number[] }) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const { stage_indices } = data;
      actions._onStagesCompleted(sessionId, { stage_indices });
    });
    socket.on("stages_edited", (data: SessionPayload & { stages: string[]; current_index: number }) => {
      const sessionId = getSessionId(data);
      if (!sessionId) return;
      const { stages, current_index } = data;
      actions._onStagesEdited(sessionId, { stages, current_index });
    });

    // Welcome events
    socket.on("history_list", actions._onHistoryList);
    socket.on("history_loaded", (data: HistoryLoadedPayload) => {
      const sessionId = getSessionId(data) || data.thread_id;
      if (!sessionId) return;
      const normalizedData = {
        ...data,
        messages: data.messages.map((msg: RawMessage) => ({
          ...msg,
          id: crypto.randomUUID(),
          msgRole: msg.role,
        })),
        toolStates: Array.isArray(data.toolStates) ? data.toolStates : [],
      };
      actions._onChatHistoryLoaded(sessionId, normalizedData);
      actions._onSidebarHistoryLoaded(sessionId, normalizedData);
    });
    socket.on("history_deleted", actions._onHistoryDeleted);

    // Settings events
    socket.on("config_data", actions._onConfigData);
    socket.on("config_updated", actions._onConfigUpdated);

    // Browser/CDP events
    socket.on("request_cdp_page", async (data: CdpPayload) => {
      const sessionId = getSessionId(data);
      if (!sessionId) {
        socket.emit("resolve_cdp_page", { status: "error" });
        return;
      }

      // Mark the session as having a CDP view
      set((state) => {
        const existing = state.chatSessions[sessionId];
        if (!existing) return {};
        return {
          chatSessions: {
            ...state.chatSessions,
            [sessionId]: { ...existing, hasCdpView: true },
          },
        };
      });

      const latest = get();
      const shouldRender = latest.isChatting && latest.activeSessionId === sessionId;
      const headless = shouldRender ? (data?.headless ?? true) : true;
      await latest.showCdpViewForSession(sessionId, headless, data?.userDataDir);

      socket.emit("resolve_cdp_page", { session_id: sessionId, status: "success" });
    });

    set({ _socket: socket });

    return () => {
      socket.removeAllListeners();
      socket.close();
      set({ _socket: null, isConnected: false });
    };
  },
});
