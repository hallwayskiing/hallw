import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useEffect, useRef, useState } from 'react';
import { useSocket } from '../contexts/SocketContext';
import { cn } from '../lib/utils';
import { Bot, User } from 'lucide-react';
import { SafetyConfirmation } from './SafetyConfirmation';

export function ChatArea() {
    const { socket } = useSocket();
    const [messages, setMessages] = useState([]);
    const [streamingContent, setStreamingContent] = useState('');
    const [isThinking, setIsThinking] = useState(false);
    const [scriptRequest, setScriptRequest] = useState(null);
    const bottomRef = useRef(null);

    useEffect(() => {
        if (!socket) return;

        const handleUserMessage = (msg) => {
            console.log("ChatArea received user_message:", msg);
            setMessages(prev => [...prev, { role: 'user', content: msg }]);
            setStreamingContent('');
            setIsThinking(true);
        };

        const handleNewToken = (token) => {
            setIsThinking(false);
            setStreamingContent(prev => prev + token);
        };

        const handleTaskFinished = () => {
            setStreamingContent(current => {
                if (current) {
                    setMessages(prev => {
                        const lastMsg = prev[prev.length - 1];
                        if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content === current) {
                            return prev;
                        }
                        return [...prev, { role: 'assistant', content: current }];
                    });
                }
                return '';
            });
            setIsThinking(false);
        };

        const handleReset = () => {
            setMessages([]);
            setStreamingContent('');
            setIsThinking(false);
            setScriptRequest(null);
        }

        const handleScriptConfirm = (data) => {
            // Flush current streaming content to messages so the card appears AFTER the text
            setStreamingContent(current => {
                if (current) {
                    setMessages(prev => {
                        // Prevent duplicates: check if the last message is identical
                        const lastMsg = prev[prev.length - 1];
                        if (lastMsg && lastMsg.role === 'assistant' && lastMsg.content === current) {
                            return prev;
                        }
                        return [...prev, { role: 'assistant', content: current }];
                    });
                }
                return '';
            });

            setScriptRequest(data);
            setIsThinking(false);
        };

        socket.on('user_message', handleUserMessage);
        socket.on('llm_new_token', handleNewToken);
        socket.on('task_finished', handleTaskFinished);
        socket.on('reset', handleReset);
        socket.on('script_confirm_requested', handleScriptConfirm);

        return () => {
            socket.off('user_message', handleUserMessage);
            socket.off('llm_new_token', handleNewToken);
            socket.off('task_finished', handleTaskFinished);
            socket.off('reset', handleReset);
            socket.off('script_confirm_requested', handleScriptConfirm);
        };
    }, [socket]);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, streamingContent, isThinking]);

    if (messages.length === 0 && !streamingContent && !isThinking) {
        return null; // Show Welcome Screen instead
    }

    return (
        <div className="flex flex-col h-full overflow-y-auto p-4 space-y-6 scroll-smooth">
            {messages.map((msg, idx) => (
                <div key={idx} className="space-y-4">
                    {msg.type === 'confirmation' ? (
                        <SafetyConfirmation
                            requestId={msg.request_id}
                            command={msg.command}
                            initialStatus={msg.status}
                        />
                    ) : (
                        <MessageBubble role={msg.role} content={msg.content} />
                    )}
                </div>
            ))}

            {scriptRequest && (
                <SafetyConfirmation
                    key={scriptRequest.request_id}
                    requestId={scriptRequest.request_id}
                    command={scriptRequest.command}
                    timeout={scriptRequest.timeout}
                    onDecision={(status) => {
                        setMessages(prev => [...prev, {
                            type: 'confirmation',
                            request_id: scriptRequest.request_id,
                            command: scriptRequest.command,
                            status: status,
                            role: 'system'
                        }]);
                        setScriptRequest(null);
                    }}
                />
            )}

            {streamingContent && (
                <div className="flex gap-4 max-w-3xl mx-auto w-full animate-in fade-in duration-300">
                    <Avatar role="assistant" />
                    <div className="flex-1 space-y-2">
                        <div className="font-semibold text-sm text-foreground/80">HALLW</div>
                        <div className="prose prose-sm dark:prose-invert max-w-none break-words leading-relaxed text-foreground/90">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                {streamingContent + ' ▌'}
                            </ReactMarkdown>
                        </div>
                    </div>
                </div>
            )}

            {isThinking && !streamingContent && (
                <div className="flex gap-4 max-w-3xl mx-auto w-full animate-pulse">
                    <Avatar role="assistant" />
                    <div className="flex-1 space-y-2 pt-1">
                        <div className="h-4 w-24 bg-muted/50 rounded" />
                        <div className="h-3 w-64 bg-muted/30 rounded" />
                    </div>
                </div>
            )}

            <div ref={bottomRef} className="h-4" />
        </div>
    );
}

function MessageBubble({ role, content }) {
    return (
        <div className={cn(
            "flex gap-4 max-w-3xl mx-auto w-full animate-in slide-in-from-bottom-2 duration-300",
            role === 'user' ? "flex-row-reverse" : ""
        )}>
            <Avatar role={role} />
            <div className={cn(
                "flex-1 space-y-2",
                role === 'user' ? "text-right" : "text-left"
            )}>
                <div className="font-semibold text-sm text-foreground/80">
                    {role === 'user' ? 'You' : 'HALLW'}
                </div>
                <div className={cn(
                    "inline-block rounded-lg px-4 py-2 max-w-[85%] text-sm shadow-sm",
                    "bg-muted/50 text-foreground border border-border/50"
                )}>
                    <div className="prose prose-sm dark:prose-invert max-w-none break-words">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {content}
                        </ReactMarkdown>
                    </div>
                </div>
            </div>
        </div>
    )
}

function Avatar({ role }) {
    return (
        <div className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border shadow-sm",
            role === 'user' ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400" : "bg-teal-500/10 border-teal-500/20 text-teal-400"
        )}>
            {role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-5 h-5" />}
        </div>
    )
}
