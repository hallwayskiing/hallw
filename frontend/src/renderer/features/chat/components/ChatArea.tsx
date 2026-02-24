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
  const messages = useAppStore((s) => s.messages);
  const streamingContent = useAppStore((s) => s.streamingContent);
  const streamingReasoning = useAppStore((s) => s.streamingReasoning);
  const isStreamingReasoning = useAppStore((s) => s.isStreamingReasoning);
  const _streamingMessageId = useAppStore((s) => s._streamingMessageId);
  const isRunning = useAppStore((s) => s.isRunning);
  const pendingConfirmation = useAppStore((s) => s.pendingConfirmation);
  const pendingDecision = useAppStore((s) => s.pendingDecision);
  const handleConfirmationDecision = useAppStore((s) => s.handleConfirmationDecision);
  const handleDecision = useAppStore((s) => s.handleDecision);
  const getProcessedMessages = useAppStore((s) => s.getProcessedMessages);

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
        isStreamingReasoning: isStreamingReasoning,
        isStreamingContent: !!streamingContent,
      });
    }
    return result;
  }, [messages, streamingContent, streamingReasoning, isStreamingReasoning, _streamingMessageId, getProcessedMessages]);

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
        className="flex flex-col h-full overflow-auto px-1 py-4 scroll-smooth"
      >
        <div className="w-full max-w-5xl mx-auto flex flex-col space-y-6 pb-4">
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
                choices={pendingDecision.choices}
                timeout={pendingDecision.timeout}
                onDecision={handleDecision}
              />
            </div>
          )}

          {isRunning && !streamingContent && !streamingReasoning && !pendingConfirmation && !pendingDecision && (
            <ThinkingIndicator key="thinking-indicator" />
          )}
        </div>
      </div>

      {showScrollButton && (
        <div className="absolute inset-x-0 bottom-6 z-10 pointer-events-none flex justify-center">
          <div className="w-full max-w-5xl flex justify-end px-20">
            <button
              type="button"
              onClick={scrollToBottom}
              className="p-2 bg-primary text-primary-foreground rounded-full shadow-lg hover:bg-primary/90 transition-all animate-in fade-in zoom-in duration-300 pointer-events-auto"
              aria-label="Scroll to bottom"
            >
              <ArrowDown className="w-5 h-5" />
            </button>
          </div>
        </div>
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
          choices={msg.choices}
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
