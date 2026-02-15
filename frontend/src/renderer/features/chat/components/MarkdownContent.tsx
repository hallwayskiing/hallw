import ReactMarkdown from "react-markdown";

import rehypeHighlight from "rehype-highlight";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";

import { cn } from "@lib/utils";

import { mdComponents } from "./ui/MarkdownComponents";

export function MarkdownContent({ content, isStreaming }: { content: string; isStreaming?: boolean }) {
  return (
    <div className={cn("md-content max-w-none break-words text-[14px]", isStreaming && "leading-relaxed")}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeHighlight]}
        components={mdComponents}
      >
        {content.replace(/\n/g, "  \n")}
      </ReactMarkdown>
      {isStreaming && (
        <span className="inline-flex ml-1 gap-1 items-baseline">
          <span className="w-1 h-1 rounded-full bg-current animate-bounce [animation-delay:-0.3s]" />
          <span className="w-1 h-1 rounded-full bg-current animate-bounce [animation-delay:-0.15s]" />
          <span className="w-1 h-1 rounded-full bg-current animate-bounce" />
        </span>
      )}
    </div>
  );
}
