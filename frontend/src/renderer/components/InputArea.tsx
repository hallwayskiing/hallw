import { Send, Settings, Square, ArrowLeft } from 'lucide-react';
import { useState, FormEvent, KeyboardEvent } from 'react';
import { useAppStore } from '../stores/appStore';
import { cn } from '../lib/utils';

interface InputAreaProps {
    onSettingsClick: () => void;
    onBack: () => void;
}

export function InputArea({ onSettingsClick, onBack }: InputAreaProps) {
    const isChatting = useAppStore(s => s.isChatting);
    const isProcessing = useAppStore(s => s.isProcessing);
    const startTask = useAppStore(s => s.startTask);
    const stopTask = useAppStore(s => s.stopTask);

    const [input, setInput] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;
        startTask(input);
        setInput('');
    };

    const handleStop = () => {
        stopTask();
    };

    const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e as unknown as FormEvent);
        }
    }

    return (
        <div className="p-4 border-t border-border bg-background">
            <div className="max-w-full mx-auto flex items-stretch gap-3">

                {/* Back / Settings Button */}
                <button
                    onClick={isChatting ? onBack : onSettingsClick}
                    className="flex items-center justify-center px-3 rounded-xl hover:bg-muted text-muted-foreground transition-colors border border-transparent"
                >
                    {isChatting ? <ArrowLeft className="w-5 h-5" /> : <Settings className="w-5 h-5" />}
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
                    onClick={isProcessing ? handleStop : (e) => handleSubmit(e as unknown as FormEvent)}
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
