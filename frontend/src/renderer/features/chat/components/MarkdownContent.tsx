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
    <div
      className={cn(
        "md-content max-w-none wrap-break-word text-[15px]",
        isStreaming && "leading-relaxed [&>p:last-of-type]:inline"
      )}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
        rehypePlugins={[rehypeKatex, rehypeHighlight]}
        components={mdComponents}
      >
        {content}
      </ReactMarkdown>
      {isStreaming && (
        <span className="inline-flex gap-1.5 items-center ml-2 align-middle opacity-60 h-4 overflow-hidden">
          <span
            className="rounded-full bg-current animate-[bounce-dot_1s_ease-in-out_infinite_-0.3s]"
            style={{ width: 4, height: 4, minWidth: 4, minHeight: 4 }}
          />
          <span
            className="rounded-full bg-current animate-[bounce-dot_1s_ease-in-out_infinite_-0.15s]"
            style={{ width: 4, height: 4, minWidth: 4, minHeight: 4 }}
          />
          <span
            className="rounded-full bg-current animate-[bounce-dot_1s_ease-in-out_infinite]"
            style={{ width: 4, height: 4, minWidth: 4, minHeight: 4 }}
          />
        </span>
      )}
    </div>
  );
});
