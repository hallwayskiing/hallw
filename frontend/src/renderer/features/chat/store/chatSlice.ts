import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";
import type { ConfirmationRequest, ConfirmationStatus, DecisionRequest, DecisionStatus, Message } from "../types";

export interface ChatSlice {
  messages: Message[];
  isRunning: boolean;
  isStreamingReasoning: boolean;
  streamingContent: string;
  streamingReasoning: string;
  pendingConfirmation: ConfirmationRequest | null;
  pendingDecision: DecisionRequest | null;
  _streamingContentRef: string;
  _streamingMessageId: string;

  getProcessedMessages: (messages: Message[]) => Message[];

  startTask: (task: string) => void;
  stopTask: () => void;
  resetSession: () => void;
  handleConfirmationDecision: (status: ConfirmationStatus) => void;
  handleDecision: (status: DecisionStatus, value?: string) => void;

  _onChatNewReasoning: (reasoning: string) => void;
  _onChatNewText: (text: string) => void;
  _onChatTaskStarted: () => void;
  _onChatTaskFinished: () => void;
  _onChatTaskCancelled: () => void;
  _onChatFatalError: (data: unknown) => void;
  _onChatReset: () => void;
  _onChatHistoryLoaded: (data: { messages: Message[] }) => void;
  _onChatRequestConfirmation: (data: ConfirmationRequest) => void;
  _onChatRequestUserDecision: (data: DecisionRequest) => void;
}

export const createChatSlice: StateCreator<AppState, [], [], ChatSlice> = (set, get) => ({
  messages: [],
  isRunning: false,
  isStreamingReasoning: false,
  streamingContent: "",
  streamingReasoning: "",
  pendingConfirmation: null,
  pendingDecision: null,
  _streamingContentRef: "",
  _streamingMessageId: crypto.randomUUID(),

  getProcessedMessages: (messages: Message[]) => {
    const result: Message[] = [];
    let reasoningBuffer: string[] = [];
    let firstReasoningId: string | null = null;

    for (const msg of messages) {
      const isReasoningOnly = msg.type === "text" && !msg.content?.trim() && !!msg.reasoning;
      const isAssistantContentMsg = msg.type === "text" && msg.msgRole === "assistant" && !!msg.content?.trim();

      if (isReasoningOnly) {
        if (!firstReasoningId) firstReasoningId = msg.id;
        if (msg.reasoning) reasoningBuffer.push(msg.reasoning);
      } else if (isAssistantContentMsg) {
        const combinedReasoning = [...reasoningBuffer, msg.reasoning].filter(Boolean).join("\n\n");
        result.push({ ...msg, reasoning: combinedReasoning || undefined });
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
      let merged = false;
      for (let i = result.length - 1; i >= 0; i--) {
        const msg = result[i];
        if (msg.type === "text" && msg.msgRole === "assistant" && !!msg.content?.trim()) {
          result[i] = {
            ...msg,
            reasoning: [msg.reasoning, ...reasoningBuffer].filter(Boolean).join("\n\n") || undefined,
          };
          merged = true;
          break;
        }
      }
      if (!merged) {
        result.push({
          id: firstReasoningId || `merged-reasoning-end`,
          type: "text",
          msgRole: "assistant",
          content: "",
          reasoning: reasoningBuffer.join("\n\n"),
        });
      }
    }
    return result;
  },

  startTask: (task) => {
    const { _socket } = get();
    if (!_socket) return;
    set((state) => ({
      messages: [...state.messages, { id: crypto.randomUUID(), type: "text", msgRole: "user", content: task }],
      isChatting: true,
      isRunning: true,
      isStreamingReasoning: false,
      streamingContent: "",
      streamingReasoning: "",
      pendingConfirmation: null,
      pendingDecision: null,
      _streamingContentRef: "",
      _streamingMessageId: crypto.randomUUID(),
    }));
    _socket.emit("start_task", { task });
  },

  stopTask: () => {
    const { _socket } = get();
    if (!_socket) return;
    _socket.emit("stop_task");
    set({ isRunning: false });
  },

  resetSession: () => {
    const { _socket } = get();
    if (!_socket) return;
    _socket.emit("reset_session");
    set({
      isRunning: false,
      isStreamingReasoning: false,
      messages: [],
      streamingContent: "",
      streamingReasoning: "",
      pendingConfirmation: null,
      pendingDecision: null,
      _streamingContentRef: "",
      _streamingMessageId: crypto.randomUUID(),
    });
  },

  handleConfirmationDecision: (status) => {
    const { pendingConfirmation, _socket } = get();
    if (!pendingConfirmation) return;

    if (_socket) {
      _socket.emit("resolve_confirmation", {
        request_id: pendingConfirmation.requestId,
        status,
      });
    }

    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          type: "confirmation",
          msgRole: "system",
          requestId: pendingConfirmation.requestId,
          command: pendingConfirmation.message,
          status,
        },
      ],
      pendingConfirmation: null,
    }));
  },

  handleDecision: (status, value) => {
    const { pendingDecision, _socket } = get();
    if (!pendingDecision) return;

    if (_socket) {
      _socket.emit("resolve_user_decision", {
        request_id: pendingDecision.requestId,
        status,
        value: value || "",
      });
    }

    set((state) => ({
      messages: [
        ...state.messages,
        {
          id: crypto.randomUUID(),
          type: "decision",
          msgRole: "system",
          requestId: pendingDecision.requestId,
          prompt: pendingDecision.message,
          options: pendingDecision.options,
          result: value || "",
          status,
        },
      ],
      pendingDecision: null,
    }));
  },

  _onChatNewReasoning: (reasoning) => {
    set((state) => ({
      streamingReasoning: state.streamingReasoning + reasoning,
      isStreamingReasoning: true,
    }));
  },

  _onChatNewText: (text) => {
    set((state) => {
      const newContent = state.streamingContent + text;
      return {
        streamingContent: newContent,
        _streamingContentRef: newContent,
        isStreamingReasoning: false,
      };
    });
  },

  _onChatTaskStarted: () => {
    set({
      isRunning: true,
    });
  },

  _onChatTaskFinished: () => {
    set((state) => {
      const content = state._streamingContentRef;
      const newMessages = [...state.messages];
      const reasoning = state.streamingReasoning;

      if (content || reasoning) {
        const last = state.messages[state.messages.length - 1];
        if (
          !(
            last?.type === "text" &&
            last.msgRole === "assistant" &&
            last.content === content &&
            last.reasoning === reasoning
          )
        ) {
          newMessages.push({
            id: state._streamingMessageId,
            type: "text",
            msgRole: "assistant",
            content,
            reasoning,
          });
        }
      }
      return {
        messages: newMessages,
        streamingContent: "",
        streamingReasoning: "",
        _streamingContentRef: "",
        _streamingMessageId: crypto.randomUUID(),
        isRunning: false,
        isStreamingReasoning: false,
      };
    });
  },

  _onChatTaskCancelled: () => {
    set((state) => {
      if (!state.isChatting) return {};

      const content = state._streamingContentRef;
      const newMessages = [...state.messages];
      const reasoning = state.streamingReasoning;

      if (content || reasoning) {
        const last = state.messages[state.messages.length - 1];
        if (
          !(
            last?.type === "text" &&
            last.msgRole === "assistant" &&
            last.content === content &&
            last.reasoning === reasoning
          )
        ) {
          newMessages.push({
            id: state._streamingMessageId,
            type: "text",
            msgRole: "assistant",
            content,
            reasoning,
          });
        }
      }

      return {
        messages: newMessages,
        streamingContent: "",
        streamingReasoning: "",
        _streamingContentRef: "",
        _streamingMessageId: crypto.randomUUID(),
        isRunning: false,
        isStreamingReasoning: false,
        pendingConfirmation: null,
        pendingDecision: null,
      };
    });
  },

  _onChatFatalError: (data) => {
    const content = typeof data === "string" ? data : (data as { message?: string }).message || JSON.stringify(data);
    set((state) => {
      const newMessages = [...state.messages];

      const pendingContent = state._streamingContentRef;
      const pendingReasoning = state.streamingReasoning;

      if (pendingContent || pendingReasoning) {
        const last = state.messages[state.messages.length - 1];
        if (
          !(
            last?.type === "text" &&
            last.msgRole === "assistant" &&
            last.content === pendingContent &&
            last.reasoning === pendingReasoning
          )
        ) {
          newMessages.push({
            id: state._streamingMessageId,
            type: "text",
            msgRole: "assistant",
            content: pendingContent,
            reasoning: pendingReasoning,
          });
        }
      }

      return {
        messages: [...newMessages, { id: crypto.randomUUID(), type: "error", msgRole: "system", content }],
        streamingContent: "",
        streamingReasoning: "",
        _streamingContentRef: "",
        _streamingMessageId: crypto.randomUUID(),
        isRunning: false,
        isStreamingReasoning: false,
      };
    });
  },

  _onChatReset: () => {
    set({
      messages: [],
      streamingContent: "",
      _streamingContentRef: "",
      _streamingMessageId: crypto.randomUUID(),
      isRunning: false,
      isStreamingReasoning: false,
      pendingConfirmation: null,
      pendingDecision: null,
    });
  },

  _onChatHistoryLoaded: (data) => {
    set({
      messages: data.messages,
      isRunning: false,
      isStreamingReasoning: false,
      streamingContent: "",
      streamingReasoning: "",
      _streamingContentRef: "",
      _streamingMessageId: crypto.randomUUID(),
    });
  },

  _onChatRequestConfirmation: (data: ConfirmationRequest) => {
    set((state) => {
      const content = state._streamingContentRef;
      const reasoning = state.streamingReasoning;
      const newMessages = [...state.messages];
      if (content || reasoning) {
        const last = state.messages[state.messages.length - 1];
        if (
          !(
            last?.type === "text" &&
            last.msgRole === "assistant" &&
            last.content === content &&
            last.reasoning === reasoning
          )
        ) {
          newMessages.push({
            id: state._streamingMessageId,
            type: "text",
            msgRole: "assistant",
            content,
            reasoning,
          });
        }
      }
      return {
        messages: newMessages,
        streamingContent: "",
        streamingReasoning: "",
        _streamingContentRef: "",
        _streamingMessageId: crypto.randomUUID(),
        isStreamingReasoning: false,
        pendingConfirmation: {
          requestId: data.requestId,
          message: data.message,
          timeout: data.timeout,
        },
      };
    });
  },

  _onChatRequestUserDecision: (data: DecisionRequest) => {
    set((state) => {
      const content = state._streamingContentRef;
      const reasoning = state.streamingReasoning;
      const newMessages = [...state.messages];
      if (content || reasoning) {
        const last = state.messages[state.messages.length - 1];
        if (
          !(
            last?.type === "text" &&
            last.msgRole === "assistant" &&
            last.content === content &&
            last.reasoning === reasoning
          )
        ) {
          newMessages.push({
            id: state._streamingMessageId,
            type: "text",
            msgRole: "assistant",
            content,
            reasoning,
          });
        }
      }
      return {
        messages: newMessages,
        streamingContent: "",
        streamingReasoning: "",
        _streamingContentRef: "",
        _streamingMessageId: crypto.randomUUID(),
        isStreamingReasoning: false,
        pendingDecision: {
          requestId: data.requestId,
          message: data.message,
          options: data.options,
          timeout: data.timeout,
        },
      };
    });
  },
});
