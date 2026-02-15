export type MessageRole = "user" | "assistant" | "system";
export type ConfirmationStatus = "pending" | "approved" | "rejected" | "timeout";
export type RuntimeInputStatus = "pending" | "submitted" | "rejected" | "timeout";

export interface BaseMessage {
  role: MessageRole;
}

export interface TextMessage extends BaseMessage {
  type: "text";
  content: string;
  reasoning?: string;
}

export interface ErrorMessage extends BaseMessage {
  type: "error";
  content: string;
}

export interface ConfirmationMessage extends BaseMessage {
  type: "confirmation";
  requestId: string;
  command: string;
  status: ConfirmationStatus;
}

export interface UserInputMessage extends BaseMessage {
  type: "user_input";
  requestId: string;
  prompt: string;
  result: string;
  status: RuntimeInputStatus;
}

export interface StatusMessage extends BaseMessage {
  type: "status";
  variant: "completed" | "cancelled";
}

export type Message = TextMessage | ErrorMessage | ConfirmationMessage | UserInputMessage | StatusMessage;

export interface ConfirmationRequest {
  requestId: string;
  message: string;
  timeout?: number;
}

export interface RuntimeInputRequest {
  requestId: string;
  message: string;
  timeout?: number;
  initialStatus?: RuntimeInputStatus;
  initialValue?: string;
  onDecision?: (status: RuntimeInputStatus, value: string) => void;
}

export interface UserInputRequest {
  requestId: string;
  message: string;
  timeout?: number;
}

export interface StatusIndicatorProps {
  variant: "completed" | "cancelled";
}

export interface AvatarProps {
  role: MessageRole;
}

export interface MessageBubbleProps {
  role: MessageRole;
  content: string;
  reasoning?: string;
  isStreaming?: boolean;
}

export interface ConfirmationProps {
  requestId: string;
  message: string;
  timeout?: number;
  initialStatus?: ConfirmationStatus;
  onDecision?: (status: ConfirmationStatus) => void;
}
