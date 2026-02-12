import { Send, Settings, Square, ArrowLeft, Clock, Zap } from 'lucide-react';
import { useState, FormEvent, KeyboardEvent, useRef, useEffect } from 'react';
import { useAppStore } from '../../stores/appStore';
import { cn } from '../../lib/utils';

interface InputAreaProps {
    onSettingsClick: () => void;
    onBack: () => void;
}

export function InputArea({ onSettingsClick, onBack }: InputAreaProps) {
    const isChatting = useAppStore(s => s.isChatting);
    const isProcessing = useAppStore(s => s.isProcessing);
    const startTask = useAppStore(s => s.startTask);
    const stopTask = useAppStore(s => s.stopTask);
    const toggleHistory = useAppStore(s => s.toggleHistory);
    const isHistoryOpen = useAppStore(s => s.isHistoryOpen);

    const [input, setInput] = useState('');
    const [height, setHeight] = useState(42);
    const [isFocused, setIsFocused] = useState(false);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const adjustHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            const newHeight = Math.min(textarea.scrollHeight, 128);
            setHeight(Math.max(newHeight, 42));
            textarea.style.height = '100%';
        }
    };

    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
        adjustHeight();
    };

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;
        startTask(input);
        setInput('');
        setHeight(42);
        if (textareaRef.current) {
            textareaRef.current.style.height = '100%';
        }
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
                    className="flex items-center justify-center px-3 rounded-xl text-muted-foreground hover:text-foreground transition-colors border border-transparent"
                    title={isChatting ? "Back to Home" : "Settings"}
                >
                    {isChatting ? <ArrowLeft className="w-5 h-5" /> : <Settings className="w-5 h-5" />}
                </button>

                {/* History/QuickStart Toggle */}
                <button
                    onClick={() => toggleHistory()}
                    className={cn(
                        "flex items-center justify-center px-3 rounded-xl transition-all duration-200 border border-transparent text-muted-foreground hover:text-foreground"
                    )}
                    title={isHistoryOpen ? "Back to Quick Start" : "View History"}
                >
                    {isHistoryOpen ? <Zap className="w-5 h-5" /> : <Clock className="w-5 h-5" />}
                </button>

                {/* Input Form Container */}
                <div className="flex-1 relative h-[42px] z-20">
                    <form
                        onSubmit={handleSubmit}
                        className={cn(
                            "absolute bottom-0 left-0 right-0 bg-muted/30 rounded-2xl border border-border focus-within:ring-2 focus-within:ring-ring focus-within:border-transparent transition-all duration-200 ease-in-out overflow-hidden shadow-sm",
                            isFocused || input.length > 0 ? "bg-background shadow-lg" : ""
                        )}
                        style={{ height: `${height}px` }}
                    >
                        <textarea
                            ref={textareaRef}
                            value={input}
                            onChange={handleInput}
                            onKeyDown={handleKeyDown}
                            onFocus={() => setIsFocused(true)}
                            onBlur={() => setIsFocused(false)}
                            disabled={isProcessing}
                            placeholder={isProcessing ? "Running..." : "Tell me what to do..."}
                            className={cn(
                                "w-full h-full bg-transparent border-0 focus:ring-0 focus:outline-none resize-none py-2.5 leading-5 px-4 text-sm text-foreground placeholder:text-muted-foreground/50",
                                "disabled:opacity-50 disabled:cursor-not-allowed",
                                height >= 128 ? "overflow-y-auto custom-scrollbar" : "overflow-y-hidden"
                            )}
                            rows={1}
                        />
                    </form>
                </div>

                {/* Action Button (Send/Stop) */}
                <button
                    type="button"
                    onClick={isProcessing ? handleStop : (e) => handleSubmit(e as unknown as FormEvent)}
                    disabled={!isProcessing && !input.trim()}
                    className={cn(
                        "flex items-center justify-center px-3 rounded-xl transition-all duration-200 relative overflow-hidden",
                        isProcessing
                            ? "bg-destructive text-destructive-foreground hover:bg-destructive/90"
                            : (input.trim()
                                ? "bg-[hsl(199,65%,50%)] text-white shadow-sm hover:bg-[hsl(199,65%,45%)]"
                                : "bg-transparent text-muted-foreground")
                    )}
                >
                    {/* Shimmer Overlay */}
                    {!isProcessing && input.trim() && (
                        <div className="absolute inset-[-100%] rotate-[25deg] pointer-events-none">
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full animate-shimmer-slide" />
                        </div>
                    )}

                    {isProcessing ? <Square className="w-5 h-5 fill-current relative z-10" /> : <Send className="w-5 h-5 relative z-10" />}
                </button>
            </div>
        </div>
    );
}
