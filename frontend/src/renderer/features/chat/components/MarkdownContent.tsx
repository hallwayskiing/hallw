import { cn } from "@lib/utils";
import { memo } from "react";
import ReactMarkdown from "react-markdown";
import rehypeHighlight from "rehype-highlight";
import rehypeKatex from "rehype-katex";
import remarkBreaks from "remark-breaks";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import "highlight.js/styles/github-dark.css";

import { mdComponents } from "./ui/MarkdownComponents";

export const MarkdownContent = memo(({ content, isStreaming }: { content: string; isStreaming?: boolean }) => {
  return (
    <div className={cn("md-content max-w-none wrap-break-word text-[15px]", isStreaming && "leading-relaxed")}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
        rehypePlugins={[rehypeKatex, [rehypeHighlight, { detect: true, ignoreMissing: true }]]}
        components={mdComponents}
      >
        {content}
      </ReactMarkdown>
      {isStreaming && (
        <span className="inline-flex gap-1 items-baseline">
          <span className="w-1 h-1 rounded-full bg-current animate-bounce [animation-delay:-0.3s]" />
          <span className="w-1 h-1 rounded-full bg-current animate-bounce [animation-delay:-0.15s]" />
          <span className="w-1 h-1 rounded-full bg-current animate-bounce" />
        </span>
      )}
    </div>
  );
});
