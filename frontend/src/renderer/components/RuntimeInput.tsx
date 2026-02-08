import { MessageSquare, Send, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSocket } from '../contexts/SocketContext';

export type RuntimeInputStatus = 'pending' | 'submitted' | 'rejected' | 'timeout';

interface RuntimeInputProps {
    requestId: string;
    message: string;
    timeout?: number;
    initialStatus?: RuntimeInputStatus;
    initialValue?: string;
    onDecision?: (status: RuntimeInputStatus, value?: string) => void;
}

export function RuntimeInput({ requestId, message, timeout, initialStatus, initialValue, onDecision }: RuntimeInputProps) {
    const { socket } = useSocket();
    const [timeLeft, setTimeLeft] = useState(timeout || 0);
    const [status, setStatus] = useState<RuntimeInputStatus>(initialStatus || 'pending');
    const [inputValue, setInputValue] = useState(initialValue || '');

    useEffect(() => {
        if (status !== 'pending') return;

        const timer = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    setStatus('timeout');
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [timeLeft, status]);

    const handleSubmit = (e?: React.FormEvent) => {
        e?.preventDefault();
        if (!inputValue.trim()) return;

        setStatus('submitted');
        if (socket) {
            socket.emit('resolve_user_input', {
                request_id: requestId,
                status: 'submitted',
                value: inputValue
            });
        }
        onDecision?.('submitted', inputValue);
    };

    const handleReject = () => {
        setStatus('rejected');
        if (socket) {
            socket.emit('resolve_user_input', {
                request_id: requestId,
                status: 'rejected'
            });
        }
        onDecision?.('rejected');
    };

    const getStatusContent = () => {
        switch (status) {
            case 'submitted':
                return (
                    <div className="flex gap-3 w-full p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 items-center animate-in fade-in">
                        <MessageSquare className="w-5 h-5 shrink-0" />
                        <div className="flex flex-col">
                            <span className="text-sm font-medium">Input submitted.</span>
                            <span className="text-xs opacity-90 mt-1">"{inputValue}"</span>
                        </div>
                    </div>
                );
            case 'rejected':
                return (
                    <div className="flex gap-3 w-full p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 items-center animate-in fade-in">
                        <X className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-medium">Input request rejected.</span>
                    </div>
                );
            case 'timeout':
                return (
                    <div className="flex gap-3 w-full p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 items-center animate-in fade-in">
                        <X className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-medium">Input request timed out.</span>
                    </div>
                );
            default:
                return (
                    <form onSubmit={handleSubmit} className="flex gap-2 pt-1">
                        <input
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            placeholder="Type your response..."
                            className="flex-1 bg-background/50 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                            autoFocus
                        />
                        <button
                            type="submit"
                            disabled={!inputValue.trim()}
                            className="flex items-center justify-center gap-2 bg-blue-500 text-white font-semibold px-4 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
                        >
                            <Send className="w-4 h-4" />
                            Send
                        </button>
                        <button
                            type="button"
                            onClick={handleReject}
                            className="flex items-center justify-center gap-2 bg-muted hover:bg-muted/80 text-foreground font-medium px-4 py-2 rounded-lg transition-colors text-sm border border-border"
                        >
                            <X className="w-4 h-4" />
                            Reject
                        </button>
                    </form>
                );
        }
    };

    return (
        <div className="flex flex-col gap-4 max-w-3xl mx-auto w-full p-5 rounded-xl bg-blue-500/10 border border-blue-500/20 animate-in slide-in-from-bottom-2">
            <div className="flex items-center gap-3 text-blue-500">
                <MessageSquare className="w-5 h-5" />
                <span className="font-semibold text-sm tracking-wide uppercase">User Input Required</span>
                {timeLeft > 0 && (
                    <span className="ml-auto text-xs font-mono bg-blue-500/20 px-2 py-1 rounded">
                        Expires in {timeLeft}s
                    </span>
                )}
            </div>

            <div className="space-y-2">
                <p className="text-sm text-foreground/80">The agent is asking for your input:</p>
                <div className="bg-background/50 rounded-lg p-3 border border-border/50 font-mono text-xs overflow-x-auto whitespace-pre-wrap">
                    {message}
                </div>
            </div>

            {getStatusContent()}
        </div>
    );
}
