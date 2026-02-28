import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

import {
  buildSessionTitle,
  DEFAULT_SESSION_TITLE_PREFIX,
  deriveTitleFromMessages,
  flushStreamingMessage,
  getPreviewText,
  patchSession,
  removeSession,
  resolveRequestExpiresAt,
} from "../lib/utils";
import type { ChatSessionState, ChatSlice, ConfirmationStatus, DecisionStatus } from "../types";

// Re-export for consumers
export type { ChatSessionState, ChatSlice, RunningSessionPreview } from "../types";

// ---------------------------------------------------------------------------
// Slice implementation
// ---------------------------------------------------------------------------

export const createChatSlice: StateCreator<AppState, [], [], ChatSlice> = (set, get) => {
  // --- Pending-request timer management ---

  type PendingRequestType = "confirmation" | "decision";
  const pendingExpiryTimers = new Map<string, ReturnType<typeof setTimeout>>();

  const timerKey = (sid: string, type: PendingRequestType) => `${sid}:${type}`;

  const clearTimer = (sid: string, type: PendingRequestType) => {
    const key = timerKey(sid, type);
    const t = pendingExpiryTimers.get(key);
    if (t) {
      clearTimeout(t);
      pendingExpiryTimers.delete(key);
    }
  };

  const clearAllTimers = (sid: string) => {
    clearTimer(sid, "confirmation");
    clearTimer(sid, "decision");
  };

  const updateSession = (sessionId: string, updater: (s: ChatSessionState) => ChatSessionState): boolean => {
    if (!get().chatSessions[sessionId]) return false;
    set((state) => patchSession(state, sessionId, updater));
    return true;
  };

  // --- Confirmation / Decision resolution ---

  const resolveConfirmation = (
    sessionId: string,
    status: ConfirmationStatus,
    opts?: { requestId?: string; emitBackend?: boolean }
  ): boolean => {
    const session = get().chatSessions[sessionId];
    const pending = session?.pendingConfirmation;
    if (!session || !pending) return false;
    if (opts?.requestId && pending.requestId !== opts.requestId) return false;

    clearTimer(sessionId, "confirmation");

    if (opts?.emitBackend !== false) {
      get()._socket?.emit("resolve_confirmation", {
        session_id: sessionId,
        request_id: pending.requestId,
        status,
      });
    }

    set((state) => {
      const target = state.chatSessions[sessionId]?.pendingConfirmation;
      if (!target) return {};
      if (opts?.requestId && target.requestId !== opts.requestId) return {};

      return patchSession(state, sessionId, (s) => ({
        ...s,
        messages: [
          ...s.messages,
          {
            id: crypto.randomUUID(),
            type: "confirmation",
            msgRole: "system",
            requestId: target.requestId,
            command: target.message,
            status,
          },
        ],
        pendingConfirmation: null,
        updatedAt: Date.now(),
      }));
    });
    return true;
  };

  const resolveDecision = (
    sessionId: string,
    status: DecisionStatus,
    value = "",
    opts?: { requestId?: string; emitBackend?: boolean }
  ): boolean => {
    const session = get().chatSessions[sessionId];
    const pending = session?.pendingDecision;
    if (!session || !pending) return false;
    if (opts?.requestId && pending.requestId !== opts.requestId) return false;

    clearTimer(sessionId, "decision");
    const resolvedValue = status === "submitted" ? value : "";

    if (opts?.emitBackend !== false) {
      get()._socket?.emit("resolve_user_decision", {
        session_id: sessionId,
        request_id: pending.requestId,
        status,
        value: resolvedValue,
      });
    }

    set((state) => {
      const target = state.chatSessions[sessionId]?.pendingDecision;
      if (!target) return {};
      if (opts?.requestId && target.requestId !== opts.requestId) return {};

      return patchSession(state, sessionId, (s) => ({
        ...s,
        messages: [
          ...s.messages,
          {
            id: crypto.randomUUID(),
            type: "decision",
            msgRole: "system",
            requestId: target.requestId,
            prompt: target.message,
            choices: target.choices,
            result: resolvedValue,
            status,
          },
        ],
        pendingDecision: null,
        updatedAt: Date.now(),
      }));
    });
    return true;
  };

  const scheduleExpiry = (sid: string, type: PendingRequestType, requestId: string, expiresAt?: number) => {
    clearTimer(sid, type);
    if (typeof expiresAt !== "number" || !Number.isFinite(expiresAt) || expiresAt <= 0) return;
    const delayMs = Math.max(0, expiresAt - Date.now());
    const t = setTimeout(() => {
      clearTimer(sid, type);
      if (type === "confirmation") {
        resolveConfirmation(sid, "timeout", { requestId, emitBackend: true });
      } else {
        resolveDecision(sid, "timeout", "", { requestId, emitBackend: true });
      }
    }, delayMs);
    pendingExpiryTimers.set(timerKey(sid, type), t);
  };

  // -----------------------------------------------------------------------
  // Slice return
  // -----------------------------------------------------------------------

  return {
    activeSessionId: null,
    chatSessions: {},
    sessionOrder: [],

    // --- Pure function: merge reasoning-only messages ---
    getProcessedMessages: (messages) => {
      const result: import("../types").Message[] = [];
      let reasoningBuffer: string[] = [];
      let firstReasoningId: string | null = null;

      for (const msg of messages) {
        const isReasoningOnly = msg.type === "text" && !msg.content?.trim() && !!msg.reasoning;
        const isAssistantContent = msg.type === "text" && msg.msgRole === "assistant" && !!msg.content?.trim();

        if (isReasoningOnly) {
          if (!firstReasoningId) firstReasoningId = msg.id;
          if (msg.reasoning) reasoningBuffer.push(msg.reasoning);
        } else if (isAssistantContent) {
          const combined = [...reasoningBuffer, msg.reasoning].filter(Boolean).join("\n\n");
          result.push({ ...msg, reasoning: combined || undefined });
          reasoningBuffer = [];
          firstReasoningId = null;
        } else {
          if (reasoningBuffer.length > 0) {
            result.push({
              id: firstReasoningId || `merged-reasoning-${result.length}`,
              type: "text",
              msgRole: "assistant",
              content: "",
              reasoning: reasoningBuffer.join("\n\n"),
            });
            reasoningBuffer = [];
            firstReasoningId = null;
          }
          result.push(msg);
        }
      }

      if (reasoningBuffer.length > 0) {
        result.push({
          id: firstReasoningId || "merged-reasoning-end",
          type: "text",
          msgRole: "assistant",
          content: "",
          reasoning: reasoningBuffer.join("\n\n"),
        });
      }
      return result;
    },

    getRunningSessions: () => {
      const state = get();
      return state.sessionOrder
        .map((id) => state.chatSessions[id])
        .filter((s): s is ChatSessionState => !!s && (s.isRunning || s.isClosed || s.messages.length > 0))
        .map((s) => ({ sessionId: s.id, title: s.title, preview: getPreviewText(s), updatedAt: s.updatedAt }));
    },

    // --- Session lifecycle ---

    openHistorySession: (threadId) => {
      const { _socket, chatSessions } = get();
      const existing = Object.values(chatSessions).find((s) => s.threadId === threadId || s.id === threadId);
      if (existing) {
        get().resumeSession(existing.id);
        return;
      }

      const sessionId = threadId;
      const fallbackTitle = `${DEFAULT_SESSION_TITLE_PREFIX} ${threadId.slice(0, 8)}`;

      set((state) => ({
        ...patchSession(
          state,
          sessionId,
          (s) => ({
            ...s,
            threadId,
            title: s.title || fallbackTitle,
            isRunning: false,
            hasFatalError: false,
            updatedAt: Date.now(),
          }),
          fallbackTitle
        ),
        activeSessionId: sessionId,
        isChatting: true,
      }));

      _socket?.emit("load_history", { thread_id: threadId, session_id: sessionId });
    },

    resumeSession: (sessionId) => {
      const session = get().chatSessions[sessionId];
      if (!session) return;

      set({ activeSessionId: sessionId, isChatting: true });

      if (session.hasCdpView) {
        void get().showCdpViewForSession(sessionId);
      } else {
        void get().hideCdpView();
      }
    },

    endSession: (sessionId) => {
      const { _socket } = get();
      _socket?.emit("reset_session", { session_id: sessionId });
      clearAllTimers(sessionId);
      void get().destroyCdpView(sessionId);
      set((state) => removeSession(state, sessionId));
    },

    startTask: (task) => {
      const { _socket, activeSessionId, isChatting, chatSessions } = get();
      if (!_socket) return;

      const activeSession = activeSessionId ? chatSessions[activeSessionId] : null;
      const sessionId =
        !isChatting || !activeSessionId || activeSession?.isClosed ? crypto.randomUUID() : activeSessionId;
      const title = buildSessionTitle(task, sessionId);
      clearAllTimers(sessionId);

      set((state) => ({
        ...patchSession(
          state,
          sessionId,
          (s) => ({
            ...s,
            title: s.messages.length === 0 ? title : s.title,
            isClosed: false,
            hasFatalError: false,
            messages: [...s.messages, { id: crypto.randomUUID(), type: "text", msgRole: "user", content: task }],
            isRunning: true,
            isStreamingReasoning: false,
            streamingContent: "",
            streamingReasoning: "",
            pendingConfirmation: null,
            pendingDecision: null,
            _streamingContentRef: "",
            _streamingMessageId: crypto.randomUUID(),
            updatedAt: Date.now(),
          }),
          title
        ),
        activeSessionId: sessionId,
        isChatting: true,
      }));

      _socket.emit("start_task", { task, session_id: sessionId });
    },

    stopTask: () => {
      const { _socket, activeSessionId } = get();
      if (!_socket || !activeSessionId) return;
      _socket.emit("stop_task", { session_id: activeSessionId });
      updateSession(activeSessionId, (s) => ({ ...s, isRunning: false, updatedAt: Date.now() }));
    },

    resetSession: () => {
      set({ isChatting: false, activeSessionId: null });
      void get().hideCdpView();
    },

    handleConfirmationDecision: (status) => {
      const { activeSessionId } = get();
      if (!activeSessionId) return;
      resolveConfirmation(activeSessionId, status, { emitBackend: true });
    },

    handleDecision: (status, value) => {
      const { activeSessionId } = get();
      if (!activeSessionId) return;
      resolveDecision(activeSessionId, status, value || "", { emitBackend: true });
    },

    // --- Socket event handlers ---

    _onChatNewReasoning: (sessionId, reasoning) => {
      updateSession(sessionId, (s) => ({
        ...s,
        isClosed: false,
        hasFatalError: false,
        isRunning: true,
        streamingReasoning: s.streamingReasoning + reasoning,
        isStreamingReasoning: true,
        updatedAt: Date.now(),
      }));
    },

    _onChatNewText: (sessionId, text) => {
      updateSession(sessionId, (s) => {
        const newContent = s.streamingContent + text;
        return {
          ...s,
          isClosed: false,
          hasFatalError: false,
          isRunning: true,
          streamingContent: newContent,
          _streamingContentRef: newContent,
          isStreamingReasoning: false,
          updatedAt: Date.now(),
        };
      });
    },

    _onChatTaskStarted: (sessionId) => {
      clearAllTimers(sessionId);
      updateSession(sessionId, (s) => ({
        ...s,
        isClosed: false,
        hasFatalError: false,
        isRunning: true,
        pendingConfirmation: null,
        pendingDecision: null,
        updatedAt: Date.now(),
      }));
    },

    _onChatTaskFinished: (sessionId) => {
      clearAllTimers(sessionId);
      updateSession(sessionId, (s) => {
        const flushed = flushStreamingMessage(s);
        return { ...flushed, isClosed: false, hasFatalError: false, isRunning: false, updatedAt: Date.now() };
      });
    },

    _onChatTaskCancelled: (sessionId) => {
      clearAllTimers(sessionId);
      updateSession(sessionId, (s) => {
        const flushed = flushStreamingMessage(s);
        return {
          ...flushed,
          isClosed: false,
          hasFatalError: false,
          isRunning: false,
          pendingConfirmation: null,
          pendingDecision: null,
          updatedAt: Date.now(),
        };
      });
    },

    _onChatFatalError: (sessionId, data) => {
      clearAllTimers(sessionId);
      const content = typeof data === "string" ? data : (data as { message?: string }).message || JSON.stringify(data);
      updateSession(sessionId, (s) => {
        const flushed = flushStreamingMessage(s);
        return {
          ...flushed,
          isClosed: false,
          hasFatalError: true,
          isRunning: false,
          messages: [...flushed.messages, { id: crypto.randomUUID(), type: "error", msgRole: "system", content }],
          updatedAt: Date.now(),
        };
      });
    },

    _onChatReset: (sessionId) => {
      clearAllTimers(sessionId);
      void get().destroyCdpView(sessionId);
      const exists = updateSession(sessionId, (s) => {
        const flushed = flushStreamingMessage(s);
        return {
          ...flushed,
          isRunning: false,
          isClosed: true,
          hasFatalError: false,
          hasCdpView: false,
          pendingConfirmation: null,
          pendingDecision: null,
          updatedAt: Date.now(),
        };
      });
      if (!exists) return;
      get()._onSidebarReset(sessionId);
    },

    _onChatHistoryLoaded: (sessionId, data) => {
      clearAllTimers(sessionId);
      const titleFallback = `${DEFAULT_SESSION_TITLE_PREFIX} ${sessionId.slice(0, 8)}`;
      const nextTitle = deriveTitleFromMessages(data.messages, titleFallback);

      set((state) => ({
        ...patchSession(
          state,
          sessionId,
          (s) => ({
            ...s,
            threadId: data.thread_id || s.threadId,
            title: nextTitle,
            isClosed: false,
            hasFatalError: false,
            messages: data.messages,
            isRunning: false,
            isStreamingReasoning: false,
            streamingContent: "",
            streamingReasoning: "",
            pendingConfirmation: null,
            pendingDecision: null,
            _streamingContentRef: "",
            _streamingMessageId: crypto.randomUUID(),
            updatedAt: Date.now(),
          }),
          nextTitle
        ),
        activeSessionId: sessionId,
        isChatting: true,
      }));
    },

    _onChatRequestConfirmation: (sessionId, data) => {
      const expiresAt = resolveRequestExpiresAt(data.timeout, data.expiresAt);
      clearTimer(sessionId, "confirmation");
      const exists = updateSession(sessionId, (s) => {
        const flushed = flushStreamingMessage(s);
        return {
          ...flushed,
          pendingConfirmation: { requestId: data.requestId, message: data.message, timeout: data.timeout, expiresAt },
          updatedAt: Date.now(),
        };
      });
      if (!exists) return;
      scheduleExpiry(sessionId, "confirmation", data.requestId, expiresAt);
    },

    _onChatRequestUserDecision: (sessionId, data) => {
      const expiresAt = resolveRequestExpiresAt(data.timeout, data.expiresAt);
      clearTimer(sessionId, "decision");
      const exists = updateSession(sessionId, (s) => {
        const flushed = flushStreamingMessage(s);
        return {
          ...flushed,
          pendingDecision: {
            requestId: data.requestId,
            message: data.message,
            choices: data.choices,
            timeout: data.timeout,
            expiresAt,
          },
          updatedAt: Date.now(),
        };
      });
      if (!exists) return;
      scheduleExpiry(sessionId, "decision", data.requestId, expiresAt);
    },
  };
};
