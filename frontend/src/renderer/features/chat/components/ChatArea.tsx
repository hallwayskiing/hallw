import { useAppStore } from "@store/store";
import { ArrowDown } from "lucide-react";
import { useEffect, useMemo } from "react";

import { useAutoScroll } from "../hooks/useAutoScroll";
import type { Message } from "../types";
import { Confirmation } from "./Confirmation";
import { Decision } from "./Decision";
import { ErrorCard } from "./ErrorCard";
import { ThinkingIndicator } from "./Indicators";
import { MessageBubble } from "./MessageBubble";

export function ChatArea() {
  const {
    messages,
    streamingContent,
    streamingReasoning,
    _streamingMessageId,
    isRunning,
    pendingConfirmation,
    pendingDecision,
    handleConfirmationDecision,
    handleDecision,
    getProcessedMessages,
  } = useAppStore();

  // 1. Data Processing Logic (Memoized)
  const processedMessages = useMemo(() => {
    const result = getProcessedMessages(messages);
    if (streamingContent || streamingReasoning) {
      result.push({
        id: _streamingMessageId,
        type: "text",
        msgRole: "assistant",
        content: streamingContent,
        reasoning: streamingReasoning,
        isStreamingReasoning: !!streamingReasoning && !streamingContent,
        isStreamingContent: !!streamingContent,
      });
    }
    return result;
  }, [messages, streamingContent, streamingReasoning, _streamingMessageId, getProcessedMessages]);

  // 2. Custom Scroll Hook
  const { scrollRef, handleScroll, scrollToBottom, showScrollButton } = useAutoScroll([
    processedMessages.length,
    streamingContent,
    streamingReasoning,
    pendingConfirmation,
    pendingDecision,
  ]);

  useEffect(() => {
    if (isRunning && !streamingContent && !streamingReasoning && !pendingDecision && !pendingConfirmation) {
      scrollToBottom();
    }
  }, [isRunning, scrollToBottom, pendingDecision, pendingConfirmation, streamingContent, streamingReasoning]);

  if (processedMessages.length === 0 && !streamingContent && !streamingReasoning && !isRunning) {
    return null;
  }

  return (
    <div className="relative h-full w-full">
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex flex-col h-full overflow-y-auto p-4 space-y-6 scroll-smooth"
      >
        {processedMessages.map((msg: Message) => (
          <div key={msg.id} className="space-y-4">
            {renderMessage(msg)}
          </div>
        ))}

        {pendingConfirmation && (
          <div
            key={`pending-confirmation-${pendingConfirmation.requestId}`}
            className="animate-in slide-in-from-bottom-2 duration-300"
          >
            <Confirmation
              requestId={pendingConfirmation.requestId}
              message={pendingConfirmation.message}
              timeout={pendingConfirmation.timeout}
              onDecision={handleConfirmationDecision}
            />
          </div>
        )}

        {pendingDecision && (
          <div
            key={`pending-decision-${pendingDecision.requestId}`}
            className="animate-in slide-in-from-bottom-2 duration-300"
          >
            <Decision
              requestId={pendingDecision.requestId}
              message={pendingDecision.message}
              options={pendingDecision.options}
              timeout={pendingDecision.timeout}
              onDecision={handleDecision}
            />
          </div>
        )}

        {isRunning && !streamingContent && !streamingReasoning && !pendingConfirmation && !pendingDecision && (
          <ThinkingIndicator key="thinking-indicator" />
        )}

        <div key="chat-bottom-spacer" className="h-4 w-full shrink-0" />
      </div>

      {showScrollButton && (
        <button
          type="button"
          onClick={scrollToBottom}
          className="absolute bottom-6 right-6 p-2 bg-primary text-primary-foreground rounded-full shadow-lg hover:bg-primary/90 transition-all animate-in fade-in zoom-in duration-300 z-10"
          aria-label="Scroll to bottom"
        >
          <ArrowDown className="w-5 h-5" />
        </button>
      )}
    </div>
  );
}

function renderMessage(msg: Message) {
  switch (msg.type) {
    case "confirmation":
      return <Confirmation requestId={msg.requestId} message={msg.command} initialStatus={msg.status} />;
    case "decision":
      return (
        <Decision
          requestId={msg.requestId}
          message={msg.prompt}
          options={msg.options}
          initialStatus={msg.status}
          initialValue={msg.result}
        />
      );
    case "error":
      return <ErrorCard content={msg.content} />;
    default:
      return (
        <MessageBubble
          msgRole={msg.msgRole}
          content={msg.content}
          reasoning={msg.reasoning}
          isStreamingReasoning={"isStreamingReasoning" in msg ? msg.isStreamingReasoning : false}
          isStreamingContent={"isStreamingContent" in msg ? msg.isStreamingContent : false}
        />
      );
  }
}
