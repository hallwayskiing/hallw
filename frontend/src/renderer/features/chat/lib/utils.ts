import type { AppState } from "@store/store";
import type { ChatSessionState, Message } from "../types";

export const DEFAULT_SESSION_TITLE_PREFIX = "Session";

const DEFAULT_SESSION_STATE: ChatSessionState = {
  id: "",
  threadId: undefined,
  title: "",
  messages: [],
  isRunning: false,
  isClosed: false,
  hasFatalError: false,
  hasCdpView: false,
  isStreamingReasoning: false,
  streamingContent: "",
  streamingReasoning: "",
  pendingConfirmation: null,
  pendingDecision: null,
  _streamingContentRef: "",
  _streamingMessageId: "",
  updatedAt: 0,
  createdAt: 0,
};

export function buildSessionTitle(task: string, sessionId: string): string {
  if (task.trim()) {
    // Take first sentence or up to 50 characters, whichever is shorter
    const firstSentence = task.split(/[.!?]/)[0].trim();
    return firstSentence.length > 50 ? `${firstSentence.slice(0, 47)}...` : firstSentence;
  }
  return `${DEFAULT_SESSION_TITLE_PREFIX} ${sessionId.slice(0, 8)}`;
}

export function deriveTitleFromMessages(messages: Message[], fallback: string): string {
  const firstUserMessage = messages.find(
    (m) => m.msgRole === "user" && m.type === "text" && "content" in m && m.content?.trim()
  );
  if (firstUserMessage && "content" in firstUserMessage && firstUserMessage.content) {
    const text = firstUserMessage.content.trim();
    const firstSentence = text.split(/[.!?]/)[0].trim();
    return firstSentence.length > 50 ? `${firstSentence.slice(0, 47)}...` : firstSentence;
  }
  return fallback;
}

export function flushStreamingMessage(session: ChatSessionState): ChatSessionState {
  if (!session.streamingContent && !session.streamingReasoning) return session;

  const newMessage: Message = {
    id: session._streamingMessageId || crypto.randomUUID(),
    type: "text",
    msgRole: "assistant",
    content: session.streamingContent,
    reasoning: session.streamingReasoning || undefined,
  };

  return {
    ...session,
    messages: [...session.messages, newMessage],
    streamingContent: "",
    streamingReasoning: "",
    isStreamingReasoning: false,
    _streamingContentRef: "",
    _streamingMessageId: "",
  };
}

export function getPreviewText(session: ChatSessionState): string {
  if (session.messages.length === 0) return "No messages yet.";
  const lastMessage = session.messages[session.messages.length - 1];

  if (lastMessage.type === "text" && "content" in lastMessage) {
    return (
      lastMessage.content || ("reasoning" in lastMessage ? lastMessage.reasoning : "Empty message") || "Empty message"
    );
  } else if (lastMessage.type === "error" && "content" in lastMessage) {
    return lastMessage.content || "Error occurred";
  } else if (lastMessage.type === "confirmation" && "status" in lastMessage) {
    return `Confirmation: ${lastMessage.status}`;
  } else if (lastMessage.type === "decision" && "status" in lastMessage) {
    return `Decision: ${lastMessage.status}`;
  }
  return "Complex message";
}

export function patchSession(
  state: AppState,
  sessionId: string,
  updater: (s: ChatSessionState) => ChatSessionState,
  fallbackTitle?: string
): Pick<AppState, "chatSessions" | "sessionOrder"> {
  const prev = state.chatSessions[sessionId];
  let sessionState = prev;
  let newOrder = state.sessionOrder;

  if (!prev) {
    sessionState = {
      ...DEFAULT_SESSION_STATE,
      id: sessionId,
      title: fallbackTitle || `${DEFAULT_SESSION_TITLE_PREFIX} ${sessionId.slice(0, 8)}`,
      updatedAt: Date.now(),
    };
    newOrder = [sessionId, ...state.sessionOrder];
  }

  const nextSessionState = updater(sessionState);

  // If updated, move to top of order (unless it was just created)
  if (prev && nextSessionState.updatedAt > prev.updatedAt) {
    newOrder = [sessionId, ...state.sessionOrder.filter((id) => id !== sessionId)];
  }

  return {
    chatSessions: {
      ...state.chatSessions,
      [sessionId]: nextSessionState,
    },
    sessionOrder: newOrder,
  };
}

export function removeSession(
  state: AppState,
  sessionId: string
): Pick<AppState, "chatSessions" | "sessionOrder" | "activeSessionId"> {
  const newSessions = { ...state.chatSessions };
  delete newSessions[sessionId];

  const newOrder = state.sessionOrder.filter((id) => id !== sessionId);

  let newActiveId = state.activeSessionId;
  if (state.activeSessionId === sessionId) {
    newActiveId = newOrder.length > 0 ? newOrder[0] : null;
  }

  return {
    chatSessions: newSessions,
    sessionOrder: newOrder,
    activeSessionId: newActiveId,
  };
}

export function resolveRequestExpiresAt(timeoutSeconds?: number, explicitExpiresAt?: number): number | undefined {
  if (explicitExpiresAt && explicitExpiresAt > 0) return explicitExpiresAt;
  if (timeoutSeconds && timeoutSeconds > 0) {
    return Date.now() + timeoutSeconds * 1000;
  }
  return undefined;
}
