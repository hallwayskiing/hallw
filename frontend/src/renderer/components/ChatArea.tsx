import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useEffect, useRef } from 'react';
import { useAppStore, Message } from '../stores/appStore';
import { cn } from '../lib/utils';
import { Bot, User, AlertTriangle } from 'lucide-react';
import { Confirmation } from './Confirmation';
import { RuntimeInput } from './RuntimeInput';

// ============================================================================
// Types
// ============================================================================

type MessageRole = 'user' | 'assistant' | 'system';

// ============================================================================
// Main Component
// ============================================================================

export function ChatArea() {
    const messages = useAppStore(s => s.messages);
    const streamingContent = useAppStore(s => s.streamingContent);
    const isProcessing = useAppStore(s => s.isProcessing);
    const pendingConfirmation = useAppStore(s => s.pendingConfirmation);
    const pendingInput = useAppStore(s => s.pendingInput);
    const handleConfirmationDecision = useAppStore(s => s.handleConfirmationDecision);
    const handleInputDecision = useAppStore(s => s.handleInputDecision);

    const bottomRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, streamingContent, isProcessing, pendingConfirmation, pendingInput]);

    // Empty state
    if (messages.length === 0 && !streamingContent && !isProcessing) {
        return null;
    }

    return (
        <div className="flex flex-col h-full overflow-y-auto p-4 space-y-6 scroll-smooth">
            {/* Rendered Messages */}
            {messages.map((msg, idx) => (
                <div key={idx} className="space-y-4">
                    {renderMessage(msg)}
                </div>
            ))}

            {/* Pending Confirmation Card */}
            {pendingConfirmation && (
                <Confirmation
                    key={pendingConfirmation.request_id}
                    requestId={pendingConfirmation.request_id}
                    message={pendingConfirmation.message}
                    timeout={pendingConfirmation.timeout}
                    onDecision={handleConfirmationDecision}
                />
            )}

            {/* Pending Runtime Input Card */}
            {pendingInput && (
                <RuntimeInput
                    key={pendingInput.request_id}
                    requestId={pendingInput.request_id}
                    message={pendingInput.message}
                    timeout={pendingInput.timeout}
                    onDecision={handleInputDecision}
                />
            )}

            {/* Streaming Response */}
            {streamingContent && (
                <MessageBubble role="assistant" content={streamingContent + ' ▌'} isStreaming />
            )}

            {/* Thinking Indicator */}
            {isProcessing && !streamingContent && <ThinkingIndicator />}

            <div ref={bottomRef} className="h-4" />
        </div>
    );
}

// ============================================================================
// Message Rendering
// ============================================================================

function renderMessage(msg: Message) {
    switch (msg.type) {
        case 'confirmation':
            return (
                <Confirmation
                    requestId={msg.requestId}
                    message={msg.command}
                    initialStatus={msg.status}
                />
            );
        case 'user_input':
            return (
                <RuntimeInput
                    requestId={msg.requestId}
                    message={msg.prompt}
                    initialStatus={msg.status}
                    initialValue={msg.result}
                />
            );
        case 'status':
            return <StatusIndicator variant={msg.variant} />;
        case 'error':
            return <ErrorCard content={msg.content} />;
        case 'text':
        default:
            return <MessageBubble role={msg.role} content={msg.content} />;
    }
}

// ============================================================================
// Sub-components
// ============================================================================

interface MessageBubbleProps {
    role: MessageRole;
    content: string;
    isStreaming?: boolean;
}

function MessageBubble({ role, content, isStreaming }: MessageBubbleProps) {
    const isUser = role === 'user';

    return (
        <div className={cn(
            "flex gap-4 max-w-3xl mx-auto w-full animate-in slide-in-from-bottom-2 duration-300",
            isUser && "flex-row-reverse"
        )}>
            <Avatar role={role} />
            <div className={cn("flex-1 space-y-2", isUser ? "text-right" : "text-left")}>
                <div className="font-semibold text-sm text-foreground/80">
                    {isUser ? 'You' : 'HALLW'}
                </div>
                <div className={cn(
                    "inline-block rounded-lg px-4 py-2 max-w-[85%] text-sm shadow-sm",
                    "bg-muted/50 text-foreground border border-border/50"
                )}>
                    <div className={cn(
                        "prose prose-sm dark:prose-invert max-w-none break-words",
                        isStreaming && "leading-relaxed text-foreground/90"
                    )}>
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {content}
                        </ReactMarkdown>
                    </div>
                </div>
            </div>
        </div>
    );
}

function Avatar({ role }: { role: MessageRole }) {
    const isUser = role === 'user';

    return (
        <div className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border shadow-sm",
            isUser
                ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                : "bg-teal-500/10 border-teal-500/20 text-teal-400"
        )}>
            {isUser ? <User className="w-4 h-4" /> : <Bot className="w-5 h-5" />}
        </div>
    );
}

function ErrorCard({ content }: { content: string }) {
    return (
        <div className="max-w-3xl mx-auto w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 flex gap-3 items-start">
                <AlertTriangle className="w-5 h-5 text-destructive shrink-0 mt-0.5" />
                <div className="space-y-1 overflow-hidden min-w-0">
                    <h3 className="font-medium text-destructive text-sm">System Error</h3>
                    <div className="text-sm text-destructive/90 font-mono whitespace-pre-wrap break-words">
                        {content}
                    </div>
                </div>
            </div>
        </div>
    );
}

function ThinkingIndicator() {
    return (
        <div className="flex gap-4 max-w-3xl mx-auto w-full animate-pulse">
            <Avatar role="assistant" />
            <div className="flex-1 space-y-2 pt-1">
                <div className="h-4 w-24 bg-muted/50 rounded" />
                <div className="h-3 w-64 bg-muted/30 rounded" />
            </div>
        </div>
    );
}

function StatusIndicator({ variant }: { variant: 'completed' | 'cancelled' }) {
    const isCompleted = variant === 'completed';
    return (
        <div className="max-w-3xl mx-auto w-full text-center py-2">
            <span className={cn(
                "text-xs",
                isCompleted ? "text-muted-foreground" : "text-destructive/70"
            )}>
                {isCompleted ? '— Task completed —' : '— Task cancelled —'}
            </span>
        </div>
    );
}
