export type MessageRole = "user" | "assistant" | "system";
export type ConfirmationStatus = "pending" | "approved" | "rejected" | "timeout";
export type DecisionStatus = "pending" | "submitted" | "rejected" | "timeout";

export interface BaseMessage {
  msgRole: MessageRole;
  id: string;
}

export interface TextMessage extends BaseMessage {
  type: "text";
  content: string;
  reasoning?: string;
  isStreamingReasoning?: boolean;
  isStreamingContent?: boolean;
}

export interface ErrorMessage extends BaseMessage {
  type: "error";
  content: string;
  reasoning?: string;
}

export interface ConfirmationMessage extends BaseMessage {
  type: "confirmation";
  requestId: string;
  command: string;
  status: ConfirmationStatus;
}

export interface DecisionMessage extends BaseMessage {
  type: "decision";
  requestId: string;
  prompt: string;
  choices?: string[];
  result: string;
  status: DecisionStatus;
}

export type Message = TextMessage | ErrorMessage | ConfirmationMessage | DecisionMessage;

export interface ConfirmationRequest {
  requestId: string;
  message: string;
  timeout?: number;
  expiresAt?: number;
}

export interface DecisionRequest {
  requestId: string;
  message: string;
  choices?: string[];
  timeout?: number;
  expiresAt?: number;
  initialStatus?: DecisionStatus;
  initialValue?: string;
  onDecision?: (status: DecisionStatus, value: string) => void;
}

export interface AvatarProps {
  msgRole: MessageRole;
}

export interface MessageBubbleProps {
  msgRole: MessageRole;
  content: string;
  reasoning?: string;
  isStreamingReasoning?: boolean;
  isStreamingContent?: boolean;
}

export interface ConfirmationProps {
  requestId: string;
  message: string;
  timeout?: number;
  initialStatus?: ConfirmationStatus;
  onDecision?: (status: ConfirmationStatus) => void;
}

// ---------------------------------------------------------------------------
// Session state — the single source of truth for each session
// ---------------------------------------------------------------------------

export interface ChatSessionState {
  id: string;
  threadId?: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  isClosed: boolean;
  hasFatalError: boolean;
  hasCdpView: boolean;
  messages: Message[];
  isRunning: boolean;
  isStreamingReasoning: boolean;
  streamingContent: string;
  streamingReasoning: string;
  pendingConfirmation: ConfirmationRequest | null;
  pendingDecision: DecisionRequest | null;
  _streamingContentRef: string;
  _streamingMessageId: string;
}

export interface RunningSessionPreview {
  sessionId: string;
  title: string;
  preview: string;
  updatedAt: number;
}

// ---------------------------------------------------------------------------
// Slice interface
// ---------------------------------------------------------------------------

export interface ChatSlice {
  activeSessionId: string | null;
  chatSessions: Record<string, ChatSessionState>;
  sessionOrder: string[];

  getProcessedMessages: (messages: Message[]) => Message[];
  getRunningSessions: () => RunningSessionPreview[];
  openHistorySession: (threadId: string) => void;
  resumeSession: (sessionId: string) => void;
  endSession: (sessionId: string) => void;

  startTask: (task: string) => void;
  stopTask: () => void;
  resetSession: () => void;
  handleConfirmationDecision: (status: ConfirmationStatus) => void;
  handleDecision: (status: DecisionStatus, value?: string) => void;

  _onChatNewReasoning: (sessionId: string, reasoning: string) => void;
  _onChatNewText: (sessionId: string, text: string) => void;
  _onChatTaskStarted: (sessionId: string) => void;
  _onChatTaskFinished: (sessionId: string) => void;
  _onChatTaskCancelled: (sessionId: string) => void;
  _onChatFatalError: (sessionId: string, data: unknown) => void;
  _onChatReset: (sessionId: string) => void;
  _onChatHistoryLoaded: (sessionId: string, data: { messages: Message[]; thread_id?: string }) => void;
  _onChatRequestConfirmation: (sessionId: string, data: ConfirmationRequest) => void;
  _onChatRequestUserDecision: (sessionId: string, data: DecisionRequest) => void;
}
