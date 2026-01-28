import { AlertTriangle, Check, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useSocket } from '../contexts/SocketContext';

export function SafetyConfirmation({ requestId, command, timeout, initialStatus = 'pending', onDecision }) {
    const { socket } = useSocket();
    const [timeLeft, setTimeLeft] = useState(timeout || 0);
    const [status, setStatus] = useState(initialStatus); // pending, approved, rejected, timeout

    useEffect(() => {
        if (initialStatus !== 'pending') return;
        if (timeLeft <= 0 || status !== 'pending') return;

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
    }, [timeLeft, status, initialStatus]);

    const handleDecision = (_status) => {
        setStatus(_status);
        socket.emit('script_response', {
            request_id: requestId,
            status: _status
        });
        if (onDecision) {
            // Small delay to let the UI update before moving to history
            setTimeout(() => onDecision(_status), 500);
        }
    };

    // If initialStatus is set (history mode), we might want to skip the socket emit?
    // Actually handleDecision is only called on button click.
    // For timeout, we need to handle onDecision too.

    useEffect(() => {
        if (status === 'timeout' && onDecision && initialStatus === 'pending') {
            onDecision('timeout');
        }
    }, [status, onDecision, initialStatus]);

    if (status === 'approved') {
        return (
            <div className="flex gap-3 max-w-3xl mx-auto w-full p-4 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 items-center animate-in fade-in">
                <Check className="w-5 h-5 shrink-0" />
                <span className="text-sm font-medium">Command execution approved.</span>
            </div>
        );
    }

    if (status === 'rejected') {
        return (
            <div className="flex gap-3 max-w-3xl mx-auto w-full p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 items-center animate-in fade-in">
                <X className="w-5 h-5 shrink-0" />
                <span className="text-sm font-medium">Command execution rejected.</span>
            </div>
        );
    }

    if (status === 'timeout') {
        return (
            <div className="flex gap-3 max-w-3xl mx-auto w-full p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 items-center animate-in fade-in">
                <X className="w-5 h-5 shrink-0" />
                <span className="text-sm font-medium">Command execution timed out.</span>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-4 max-w-3xl mx-auto w-full p-5 rounded-xl bg-amber-500/10 border border-amber-500/20 animate-in slide-in-from-bottom-2">
            <div className="flex items-center gap-3 text-amber-500">
                <AlertTriangle className="w-5 h-5" />
                <span className="font-semibold text-sm tracking-wide uppercase">Safety Confirmation</span>
                {timeLeft > 0 && (
                    <span className="ml-auto text-xs font-mono bg-amber-500/20 px-2 py-1 rounded">
                        Expires in {timeLeft}s
                    </span>
                )}
            </div>

            <div className="space-y-2">
                <p className="text-sm text-foreground/80">The agent wants to execute a system command:</p>
                <div className="bg-background/50 rounded-lg p-3 border border-border/50 font-mono text-xs overflow-x-auto">
                    {command}
                </div>
            </div>

            <div className="flex gap-3 pt-1">
                <button
                    onClick={() => handleDecision("approved")}
                    className="flex-1 flex items-center justify-center gap-2 bg-amber-500 text-black font-semibold py-2 rounded-lg hover:bg-amber-400 transition-colors text-sm"
                >
                    <Check className="w-4 h-4" />
                    Approve
                </button>
                <button
                    onClick={() => handleDecision("rejected")}
                    className="flex-1 flex items-center justify-center gap-2 bg-muted hover:bg-muted/80 text-foreground font-medium py-2 rounded-lg transition-colors text-sm border border-border"
                >
                    <X className="w-4 h-4" />
                    Reject
                </button>
            </div>
        </div>
    );
}
