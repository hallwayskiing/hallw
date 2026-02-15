import { useEffect, useMemo } from "react";

import { useAppStore } from "@store/store";
import { ArrowDown } from "lucide-react";

import { useAutoScroll } from "../hooks/useAutoScroll";
import { Message } from "../types";
import { Confirmation } from "./Confirmation";
import { Decision } from "./Decision";
import { ErrorCard } from "./ErrorCard";
import { StatusIndicator, ThinkingIndicator } from "./Indicators";
import { MessageBubble } from "./MessageBubble";

export function ChatArea() {
  const {
    messages,
    streamingContent,
    streamingReasoning,
    isRunning,
    pendingConfirmation,
    pendingDecision,
    handleConfirmationDecision,
    handleDecision,
    getProcessedMessages,
  } = useAppStore();

  // 1. Data Processing Logic (Memoized)
  const processedMessages = useMemo(() => getProcessedMessages(messages), [messages, getProcessedMessages]);

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
  }, [isRunning, scrollToBottom, pendingDecision, pendingConfirmation]);

  if (processedMessages.length === 0 && !streamingContent && !isRunning) {
    return null;
  }

  return (
    <div className="relative h-full w-full">
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex flex-col h-full overflow-y-auto p-4 space-y-6 scroll-smooth"
      >
        {processedMessages.map((msg, idx) => (
          <div key={idx} className="space-y-4">
            {renderMessage(msg)}
          </div>
        ))}

        {(streamingContent || streamingReasoning) && (
          <MessageBubble
            role="assistant"
            content={streamingContent}
            reasoning={streamingReasoning}
            isStreaming={true}
          />
        )}

        {pendingConfirmation && (
          <div className="animate-in slide-in-from-bottom-2 duration-300">
            <Confirmation
              key={pendingConfirmation.requestId}
              requestId={pendingConfirmation.requestId}
              message={pendingConfirmation.message}
              timeout={pendingConfirmation.timeout}
              onDecision={handleConfirmationDecision}
            />
          </div>
        )}

        {pendingDecision && (
          <div className="animate-in slide-in-from-bottom-2 duration-300">
            <Decision
              key={pendingDecision.requestId}
              requestId={pendingDecision.requestId}
              message={pendingDecision.message}
              options={pendingDecision.options}
              timeout={pendingDecision.timeout}
              onDecision={handleDecision}
            />
          </div>
        )}

        {isRunning && !streamingContent && !streamingReasoning && <ThinkingIndicator />}

        <div className="h-4 w-full shrink-0" />
      </div>

      {showScrollButton && (
        <button
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
    case "status":
      return <StatusIndicator variant={msg.variant} />;
    case "error":
      return <ErrorCard content={msg.content} />;
    case "text":
    default:
      return <MessageBubble role={msg.role} content={msg.content} reasoning={msg.reasoning} />;
  }
}
