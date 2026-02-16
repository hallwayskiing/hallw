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
  options?: string[];
  result: string;
  status: DecisionStatus;
}

export interface StatusMessage extends BaseMessage {
  type: "status";
  variant: "completed" | "cancelled";
}

export type Message = TextMessage | ErrorMessage | ConfirmationMessage | DecisionMessage | StatusMessage;

export interface ConfirmationRequest {
  requestId: string;
  message: string;
  timeout?: number;
}

export interface DecisionRequest {
  requestId: string;
  message: string;
  options?: string[];
  timeout?: number;
  initialStatus?: DecisionStatus;
  initialValue?: string;
  onDecision?: (status: DecisionStatus, value: string) => void;
}

export interface StatusIndicatorProps {
  variant: "completed" | "cancelled";
}

export interface AvatarProps {
  msgRole: MessageRole;
}

export interface MessageBubbleProps {
  msgRole: MessageRole;
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
