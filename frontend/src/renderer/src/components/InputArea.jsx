import { Send, Settings, Square, ArrowLeft } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useSocket } from '../contexts/SocketContext';
import { cn } from '../lib/utils';

export function InputArea({ onSettingsClick, onStartTask, hasStarted, onBack }) {
    const { socket, isConnected } = useSocket();
    const [input, setInput] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);

    useEffect(() => {
        if (!socket) return;

        const handleTaskFinished = () => {
            setIsProcessing(false);
        };

        socket.on('task_finished', handleTaskFinished);
        socket.on('tool_error', handleTaskFinished);
        socket.on('fatal_error', handleTaskFinished);

        return () => {
            socket.off('task_finished', handleTaskFinished);
            socket.off('tool_error', handleTaskFinished);
            socket.off('fatal_error', handleTaskFinished);
        };
    }, [socket]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        // Switch to chat view immediately
        if (onStartTask) onStartTask();

        if (isConnected) {
            console.log("Emitting start_task:", input, "is_reply:", hasStarted);
            socket.emit('start_task', { task: input, is_reply: hasStarted });
        } else {
            console.log("Task submitted while disconnected:", input);
        }

        setInput('');
        setIsProcessing(true);
    };

    const handleStop = () => {
        if (isConnected) socket.emit('stop_task');
        setIsProcessing(false);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    }

    return (
        <div className="p-4 border-t border-border bg-background">
            <div className="max-w-full mx-auto flex items-stretch gap-3">

                {/* Back / Settings Button */}
                <button
                    onClick={hasStarted ? onBack : onSettingsClick}
                    className="flex items-center justify-center px-3 rounded-xl hover:bg-muted text-muted-foreground transition-colors border border-transparent"
                >
                    {hasStarted ? <ArrowLeft className="w-5 h-5" /> : <Settings className="w-5 h-5" />}
                </button>

                {/* Input Form */}
                <form onSubmit={handleSubmit} className="flex-1 relative bg-muted/30 rounded-2xl border border-border focus-within:ring-2 focus-within:ring-ring focus-within:border-transparent transition-all">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Tell me what to do..."
                        className="w-full bg-transparent border-0 focus:ring-0 focus:outline-none resize-none max-h-32 min-h-[40px] py-2.5 leading-5 px-4 text-sm text-foreground placeholder:text-muted-foreground/50 scrollbar-hide"
                        rows={1}
                    />

                </form>

                {/* Action Button (Send/Stop) */}
                <button
                    type="button"
                    onClick={isProcessing ? handleStop : handleSubmit}
                    disabled={!isProcessing && !input.trim()}
                    className={cn(
                        "flex items-center justify-center px-4 rounded-2xl transition-all shadow-lg",
                        isProcessing
                            ? "bg-destructive text-destructive-foreground"
                            : (input.trim() ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground")
                    )}
                >
                    {isProcessing ? <Square className="w-5 h-5 fill-current" /> : <Send className="w-5 h-5" />}
                </button>
            </div>
        </div>
    );
}
