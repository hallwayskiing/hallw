import { cn } from '@lib/utils';
import { Bot, User } from 'lucide-react';
import { ReasoningAccordion } from './ReasoningAccordion';
import { MarkdownContent } from './MarkdownContent';
import { AvatarProps, MessageBubbleProps } from '../types';
import { useSmoothTyping } from '../hooks/useSmoothTyping';

export function Avatar({ role }: AvatarProps) {
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


export function MessageBubble({ role, content, reasoning, isStreaming }: MessageBubbleProps) {
    const isUser = role === 'user';
    const smoothContent = useSmoothTyping(content, isStreaming || false);

    return (
        <div className={cn("flex gap-4 max-w-3xl mx-auto w-full animate-in fade-in duration-300", isUser && "flex-row-reverse")}>
            <Avatar role={role} />
            <div className={cn("flex-1 space-y-2 min-w-0", isUser ? "text-right" : "text-left")}>
                <div className="font-semibold text-sm text-foreground/80">{isUser ? 'You' : 'HALLW'}</div>
                {reasoning && <ReasoningAccordion content={reasoning} isStreaming={isStreaming} />}
                {(isStreaming || content) && (
                    <div className={cn(
                        "inline-block rounded-lg px-4 py-2 max-w-[85%] text-sm shadow-sm text-left",
                        "bg-muted/50 text-foreground border border-border/50",
                        isStreaming && "min-h-[40px]"
                    )}>
                        <MarkdownContent content={isStreaming ? smoothContent : content} isStreaming={isStreaming} />
                    </div>
                )}
            </div>
        </div>
    );
}
