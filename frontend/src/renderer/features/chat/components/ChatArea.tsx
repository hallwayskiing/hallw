import { useEffect, useMemo } from 'react';
import { Message } from '../types';
import { useAppStore } from '@store/store';
import { Confirmation } from './Confirmation';
import { RuntimeInput } from './RuntimeInput';
import { MessageBubble } from './MessageBubble';
import { ErrorCard } from './ErrorCard';
import { useAutoScroll } from '../hooks/useAutoScroll';
import { ThinkingIndicator, StatusIndicator } from './Indicators';

export function ChatArea() {
    const {
        messages, streamingContent, streamingReasoning, isRunning, pendingConfirmation, pendingInput,
        handleConfirmationDecision, handleInputDecision, getProcessedMessages
    } = useAppStore();

    // 1. Data Processing Logic (Memoized)
    const processedMessages = useMemo(() => getProcessedMessages(messages), [messages, getProcessedMessages]);

    // 2. Custom Scroll Hook
    const { scrollRef, handleScroll, scrollToBottom } = useAutoScroll([
        processedMessages.length,
        streamingContent,
        streamingReasoning
    ]);

    useEffect(() => {
        if (isRunning && !streamingContent && !streamingReasoning) {
            scrollToBottom();
        }
    }, [isRunning, scrollToBottom]);

    if (processedMessages.length === 0 && !streamingContent && !isRunning) {
        return null;
    }

    return (
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

            {pendingInput && (
                <div className="animate-in slide-in-from-bottom-2 duration-300">
                    <RuntimeInput
                        key={pendingInput.requestId}
                        requestId={pendingInput.requestId}
                        message={pendingInput.message}
                        timeout={pendingInput.timeout}
                        onDecision={handleInputDecision}
                    />
                </div>
            )}

            {isRunning && !streamingContent && !streamingReasoning && <ThinkingIndicator />}

            <div className="h-4 w-full shrink-0" />
        </div>
    );
}

function renderMessage(msg: Message) {
    switch (msg.type) {
        case 'confirmation':
            return <Confirmation requestId={msg.requestId} message={msg.command} initialStatus={msg.status} />;
        case 'user_input':
            return <RuntimeInput requestId={msg.requestId} message={msg.prompt} initialStatus={msg.status} initialValue={msg.result} />;
        case 'status':
            return <StatusIndicator variant={msg.variant} />;
        case 'error':
            return <ErrorCard content={msg.content} />;
        case 'text':
        default:
            return <MessageBubble role={msg.role} content={msg.content} reasoning={msg.reasoning} />;
    }
}
