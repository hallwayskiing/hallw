import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { useEffect, useRef, useState, useLayoutEffect, useCallback } from 'react';
import { useAppStore, Message } from '../../stores/appStore';
import { cn } from '../../lib/utils';
import { Bot, User, AlertTriangle, ChevronDown, ChevronRight, Brain } from 'lucide-react';
import { Confirmation } from './Confirmation';
import { RuntimeInput } from './RuntimeInput';

// ============================================================================
// Types
// ============================================================================

type MessageRole = 'user' | 'assistant' | 'system';

// ============================================================================
// Hooks
// ============================================================================

/**
 * Hook to handle smooth typing effect.
 * Takes the raw stream string and returns a progressively displayed string.
 */
function useSmoothTyping(targetText: string, isStreaming: boolean, speed: number = 2) {
    const [displayedText, setDisplayedText] = useState('');

    useEffect(() => {
        if (!isStreaming) {
            setDisplayedText(targetText);
            return;
        }

        let animationFrameId: number;

        const animate = () => {
            setDisplayedText((current) => {
                if (current.length >= targetText.length) {
                    return targetText;
                }
                // Calculate how much to append.
                // If we are far behind, speed up slightly to catch up.
                const diff = targetText.length - current.length;
                const chunk = Math.min(diff, Math.max(1, Math.floor(diff / 10)) + speed);

                return targetText.slice(0, current.length + chunk);
            });
            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);

        return () => cancelAnimationFrame(animationFrameId);
    }, [targetText, isStreaming, speed]);

    return displayedText;
}

/**
 * Hook to handle Gemini-like sticky scrolling.
 * Stays at bottom only if user hasn't scrolled up.
 */
function useAutoScroll(dependencies: any[]) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);

    const handleScroll = useCallback(() => {
        const div = scrollRef.current;
        if (!div) return;

        // threshold to consider "at bottom" (e.g., 50px)
        const isAtBottom = div.scrollHeight - div.scrollTop - div.clientHeight <= 50;

        // If user is at bottom, reset the flag. If they scroll up, set the flag.
        if (isAtBottom) {
            setUserHasScrolledUp(false);
        } else {
            setUserHasScrolledUp(true);
        }
    }, []);

    // Effect to scroll to bottom when dependencies change, ONLY if user hasn't scrolled up
    useLayoutEffect(() => {
        const div = scrollRef.current;
        if (div && !userHasScrolledUp) {
            div.scrollTo({ top: div.scrollHeight, behavior: 'instant' }); // 'instant' is better for streaming than 'smooth' to prevent lag
        }
    }, [dependencies, userHasScrolledUp]);

    // Force scroll to bottom when a specific flag is passed (e.g. new message start)
    const scrollToBottom = useCallback(() => {
        const div = scrollRef.current;
        if (div) {
            div.scrollTo({ top: div.scrollHeight, behavior: 'smooth' });
            setUserHasScrolledUp(false);
        }
    }, []);

    return { scrollRef, handleScroll, scrollToBottom };
}

// ============================================================================
// Main Component
// ============================================================================

export function ChatArea() {
    const messages = useAppStore(s => s.messages);
    const streamingContent = useAppStore(s => s.streamingContent);
    const streamingReasoning = useAppStore(s => s.streamingReasoning);
    const isProcessing = useAppStore(s => s.isProcessing);
    const pendingConfirmation = useAppStore(s => s.pendingConfirmation);
    const pendingInput = useAppStore(s => s.pendingInput);
    const handleConfirmationDecision = useAppStore(s => s.handleConfirmationDecision);
    const handleInputDecision = useAppStore(s => s.handleInputDecision);

    // Grouping Logic (Preserved from original)
    const processedMessages = (() => {
        const result: Message[] = [];
        let reasoningBuffer: string[] = [];

        for (const msg of messages) {
            const isReasoningOnly = msg.type === 'text' && !msg.content?.trim() && !!msg.reasoning;
            const isAssistantContentMsg = msg.type === 'text' && msg.role === 'assistant' && !!msg.content?.trim();

            if (isReasoningOnly) {
                if (msg.reasoning) reasoningBuffer.push(msg.reasoning);
            } else if (isAssistantContentMsg) {
                const combinedReasoning = [...reasoningBuffer, msg.reasoning].filter(Boolean).join('\n\n');
                result.push({ ...msg, reasoning: combinedReasoning || undefined });
                reasoningBuffer = [];
            } else {
                if (reasoningBuffer.length > 0) {
                    result.push({
                        type: 'text',
                        role: 'assistant',
                        content: '',
                        reasoning: reasoningBuffer.join('\n\n')
                    });
                    reasoningBuffer = [];
                }
                result.push(msg);
            }
        }
        if (reasoningBuffer.length > 0) {
            let merged = false;
            for (let i = result.length - 1; i >= 0; i--) {
                const msg = result[i];
                if (msg.type === 'text' && msg.role === 'assistant' && !!msg.content?.trim()) {
                    result[i] = { ...msg, reasoning: [msg.reasoning, ...reasoningBuffer].filter(Boolean).join('\n\n') || undefined };
                    merged = true;
                    break;
                }
            }
            if (!merged) {
                result.push({ type: 'text', role: 'assistant', content: '', reasoning: reasoningBuffer.join('\n\n') });
            }
        }
        return result;
    })();

    // Use Custom Scroll Hook
    // We pass streamingContent to trigger the "sticky" check
    const { scrollRef, handleScroll, scrollToBottom } = useAutoScroll([processedMessages.length, streamingContent, streamingReasoning]);

    // When a NEW processing state begins, force scroll to bottom once
    useEffect(() => {
        if (isProcessing && !streamingContent && !streamingReasoning) {
            scrollToBottom();
        }
    }, [isProcessing, scrollToBottom]);

    if (processedMessages.length === 0 && !streamingContent && !isProcessing) {
        return null;
    }

    return (
        <div
            ref={scrollRef}
            onScroll={handleScroll}
            className="flex flex-col h-full overflow-y-auto p-4 space-y-6 scroll-smooth"
        >
            {/* Rendered Messages */}
            {processedMessages.map((msg, idx) => (
                <div key={idx} className="space-y-4">
                    {renderMessage(msg)}
                </div>
            ))}

            {/* Streaming Response (Special Component for Smoothness) */}
            {(streamingContent || streamingReasoning) && (
                <StreamingMessageBubble
                    role="assistant"
                    content={streamingContent}
                    reasoning={streamingReasoning}
                />
            )}

            {/* Pending Confirmation Card */}
            {pendingConfirmation && (
                <div className="animate-in slide-in-from-bottom-2 duration-300">
                    <Confirmation
                        key={pendingConfirmation.request_id}
                        requestId={pendingConfirmation.request_id}
                        message={pendingConfirmation.message}
                        timeout={pendingConfirmation.timeout}
                        onDecision={handleConfirmationDecision}
                    />
                </div>
            )}

            {/* Pending Runtime Input Card */}
            {pendingInput && (
                <div className="animate-in slide-in-from-bottom-2 duration-300">
                    <RuntimeInput
                        key={pendingInput.request_id}
                        requestId={pendingInput.request_id}
                        message={pendingInput.message}
                        timeout={pendingInput.timeout}
                        onDecision={handleInputDecision}
                    />
                </div>
            )}

            {/* Thinking Indicator */}
            {isProcessing && !streamingContent && !streamingReasoning && <ThinkingIndicator />}

            {/* Extra padding at bottom to give space */}
            <div className="h-4 w-full shrink-0" />
        </div>
    );
}

// ============================================================================
// Message Components
// ============================================================================

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

/**
 * Standard Bubble for completed messages (No typing effect)
 */
function MessageBubble({ role, content, reasoning }: { role: MessageRole; content: string; reasoning?: string }) {
    const isUser = role === 'user';
    return (
        <div className={cn("flex gap-4 max-w-3xl mx-auto w-full", isUser && "flex-row-reverse")}>
            <Avatar role={role} />
            <div className={cn("flex-1 space-y-2 min-w-0", isUser ? "text-right" : "text-left")}>
                <div className="font-semibold text-sm text-foreground/80">{isUser ? 'You' : 'HALLW'}</div>
                {reasoning && <ReasoningAccordion content={reasoning} />}
                {content && (
                    <div className={cn(
                        "inline-block rounded-lg px-4 py-2 max-w-[85%] text-sm shadow-sm text-left",
                        "bg-muted/50 text-foreground border border-border/50"
                    )}>
                        <MarkdownContent content={content} />
                    </div>
                )}
            </div>
        </div>
    );
}

/**
 * Special Bubble for Streaming - Handles Smooth Typing
 */
function StreamingMessageBubble({ role, content, reasoning }: { role: MessageRole; content: string; reasoning?: string }) {
    // Apply smooth typing to the content
    const smoothContent = useSmoothTyping(content, true);
    // Note: We don't smooth-type reasoning usually as it's collapsible, but you can if desired.

    return (
        <div className="flex gap-4 max-w-3xl mx-auto w-full animate-in fade-in duration-300">
            <Avatar role={role} />
            <div className="flex-1 space-y-2 min-w-0 text-left">
                <div className="font-semibold text-sm text-foreground/80">HALLW</div>

                {reasoning && <ReasoningAccordion content={reasoning} isStreaming />}

                <div className={cn(
                    "inline-block rounded-lg px-4 py-2 max-w-[85%] text-sm shadow-sm text-left",
                    "bg-muted/50 text-foreground border border-border/50 min-h-[40px]"
                )}>
                    <MarkdownContent content={smoothContent} isStreaming />
                </div>
            </div>
        </div>
    );
}

function MarkdownContent({ content, isStreaming }: { content: string, isStreaming?: boolean }) {
    return (
        <div className={cn(
            "prose prose-sm dark:prose-invert max-w-none break-words",
            isStreaming && "leading-relaxed text-foreground/90"
        )}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
            >
                {/* Append cursor if streaming */}
                {content.replace(/\n/g, '  \n') + (isStreaming ? ' ●' : '')}
            </ReactMarkdown>
        </div>
    );
}

// ============================================================================
// UI Helper Components
// ============================================================================

function Avatar({ role }: { role: MessageRole }) {
    const isUser = role === 'user';
    return (
        <div className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border shadow-sm",
            isUser ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400" : "bg-teal-500/10 border-teal-500/20 text-teal-400"
        )}>
            {isUser ? <User className="w-4 h-4" /> : <Bot className="w-5 h-5" />}
        </div>
    );
}

function ErrorCard({ content }: { content: string }) {
    return (
        <div className="max-w-3xl mx-auto w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="bg-destructive/10 border border-destructive/80 rounded-lg p-4 flex gap-3 items-start">
                <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
                <div className="space-y-1 overflow-hidden min-w-0">
                    <h3 className="font-bold text-red-600 dark:text-red-400 text-sm">System Error</h3>
                    <div className="text-sm text-red-600 dark:text-red-400 font-mono whitespace-pre-wrap break-words">{content}</div>
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
            <span className={cn("text-xs", isCompleted ? "text-muted-foreground" : "text-destructive/70")}>
                {isCompleted ? '— Task completed —' : '— Task cancelled —'}
            </span>
        </div>
    );
}

function ReasoningAccordion({ content, isStreaming }: { content: string, isStreaming?: boolean }) {
    const [isOpen, setIsOpen] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (isOpen && isStreaming) {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }, [isOpen, content, isStreaming]);

    const lastLine = content.split('\n').filter(line => line.trim() !== '').pop() || '';

    return (
        <div className="border border-border/50 rounded-lg overflow-hidden bg-background/50 max-w-[85%]">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={cn(
                    "flex items-center gap-2 px-3 py-2 w-full hover:bg-muted/30 transition-all text-left group",
                    !isOpen && isStreaming && "bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 animate-gradient-wave"
                )}
            >
                {isOpen ? <ChevronDown className="w-4 h-4 text-muted-foreground shrink-0" /> : <ChevronRight className="w-4 h-4 text-muted-foreground shrink-0" />}
                <Brain className={cn("w-4 h-4 text-purple-400 shrink-0", isStreaming && "animate-pulse")} />
                <div className="flex-1 min-w-0">
                    {!isOpen && isStreaming && lastLine ? (
                        <span className="text-xs text-muted-foreground/80 truncate block font-mono">{lastLine.slice(0, 100)}</span>
                    ) : (
                        <span className="text-xs font-medium text-muted-foreground">{isStreaming ? "Thinking..." : "Thought Process"}</span>
                    )}
                </div>
            </button>
            {isOpen && (
                <div className="px-4 py-3 bg-muted/20 border-t border-border/30 text-xs text-foreground/80 animate-in slide-in-from-top-1 max-h-80 overflow-y-auto custom-scrollbar">
                    <MarkdownContent content={content} />
                    <div ref={bottomRef} className="h-0 w-0" />
                </div>
            )}
        </div>
    );
}
