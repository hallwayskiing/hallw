import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { cn } from '@lib/utils';

export function MarkdownContent({ content, isStreaming }: { content: string, isStreaming?: boolean }) {
    return (
        <div className={cn(
            "prose prose-sm dark:prose-invert max-w-none break-words",
            isStreaming && "leading-relaxed text-foreground/90"
        )}>
            <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath]}
                rehypePlugins={[rehypeKatex]}
                components={{
                    p: ({ children }) => <p className="mb-4 last:mb-0 inline">{children}</p>
                }}
            >
                {content.replace(/\n/g, '  \n')}
            </ReactMarkdown>
            {isStreaming && (
                <span className="inline-flex ml-1 gap-1 items-baseline">
                    <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce"></span>
                </span>
            )}
        </div>
    );
}
