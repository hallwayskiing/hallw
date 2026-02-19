import { cn } from "@lib/utils";
import { Check, Copy } from "lucide-react";
import type React from "react";
import type { ComponentPropsWithoutRef } from "react";
import { useCallback, useState } from "react";
import type ReactMarkdown from "react-markdown";

interface MarkdownLiProps extends React.LiHTMLAttributes<HTMLLIElement> {
  ordered?: boolean;
}

export const mdComponents: ComponentPropsWithoutRef<typeof ReactMarkdown>["components"] = {
  // Paragraphs
  p: ({ children }) => (
    <p className="mb-4 last:mb-0 leading-[1.75] text-[15px] text-foreground/80 font-[450] tracking-[-0.005em]">
      {children}
    </p>
  ),

  // Headings
  h1: ({ children }) => (
    <h1 className="text-2xl font-bold mb-6 mt-8 first:mt-0 text-foreground tracking-tight">{children}</h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-xl font-bold mb-4 mt-7 first:mt-0 text-foreground tracking-tight">{children}</h2>
  ),
  h3: ({ children }) => <h3 className="text-lg font-semibold mb-3 mt-6 first:mt-0 text-foreground/90">{children}</h3>,
  h4: ({ children }) => <h4 className="text-base font-semibold mb-2 mt-5 first:mt-0 text-foreground/85">{children}</h4>,

  // Code blocks
  pre: ({ children }) => {
    // Extract language and text from the code child
    const codeChild = children as React.ReactElement<{
      className?: string;
      children?: React.ReactNode;
    }>;
    const className = codeChild?.props?.className || "";
    const lang = className
      .replace(/language-/, "")
      .replace(/hljs/, "")
      .trim();

    // Extract raw text for copy
    const extractText = (node: React.ReactNode): string => {
      if (typeof node === "string") return node;
      if (Array.isArray(node)) return node.map(extractText).join("");
      if (node && typeof node === "object" && "props" in node) {
        return extractText((node as React.ReactElement<{ children?: React.ReactNode }>).props.children);
      }
      return "";
    };
    const rawText = extractText(codeChild?.props?.children).replace(/\n$/, "");

    return (
      <div className="md-code-block group relative my-4 rounded-xl overflow-hidden border border-white/6 bg-[#0d1117]">
        {/* Header bar */}
        <div className="flex items-center justify-between px-3 py-1 bg-white/3 border-b border-white/6">
          <span className="text-[12px] font-mono font-medium text-muted-foreground/40 uppercase tracking-wider pl-1">
            {lang || "code"}
          </span>
          <CopyButton text={rawText} />
        </div>
        {/* Code content */}
        <pre className="bg-transparent! m-0! p-4! text-[13px] leading-6 font-mono whitespace-pre-wrap wrap-break-word overflow-y-hidden">
          {children}
        </pre>
      </div>
    );
  },

  // Inline code
  code: ({ className, children, ...props }) => {
    const isBlock = className?.includes("language-") || className?.includes("hljs");
    if (isBlock) {
      return (
        <code className={cn(className, "bg-transparent!")} {...props}>
          {children}
        </code>
      );
    }
    return (
      <code
        className="px-1.5 py-0.5 rounded-md bg-white/6 border border-white/8 text-[14px] font-mono text-emerald-300/90"
        {...props}
      >
        {children}
      </code>
    );
  },

  // Blockquote
  blockquote: ({ children }) => (
    <blockquote className="my-6 pl-4 border-l-[3px] border-foreground/10 py-1 text-foreground/75 italic">
      {children}
    </blockquote>
  ),

  // Lists
  ul: ({ children }) => <ul className="my-3 ml-1 space-y-1.5 list-none">{children}</ul>,
  ol: ({ children }) => <ol className="my-3 ml-1 space-y-1.5 list-none [counter-reset:list-item]">{children}</ol>,
  li: ({ children, ...props }: MarkdownLiProps) => {
    const isOrdered = props.ordered;
    return (
      <li
        className={cn(
          "relative pl-6 text-foreground/90 leading-7 mb-2 last:mb-0",
          "before:absolute before:left-0 before:top-[11px]",
          isOrdered
            ? "before:content-[counter(list-item)'.'] before:text-foreground before:text-[12px] before:font-bold before:opacity-90 [counter-increment:list-item]"
            : "before:content-[''] before:w-1.5 before:h-1.5 before:rounded-full before:bg-foreground before:opacity-85"
        )}
      >
        {children}
      </li>
    );
  },

  // Links
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-400 hover:text-blue-300 underline decoration-blue-400/30 underline-offset-2 hover:decoration-blue-300/50 transition-colors duration-200"
    >
      {children}
    </a>
  ),

  // Tables
  table: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-lg border border-white/6">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-white/3 border-b border-white/8">{children}</thead>,
  th: ({ children }) => (
    <th className="px-4 py-2.5 text-left text-xs font-semibold text-foreground/70 uppercase tracking-wider">
      {children}
    </th>
  ),
  td: ({ children }) => <td className="px-4 py-2.5 text-foreground/80 border-t border-white/4">{children}</td>,
  tr: ({ children }) => <tr className="hover:bg-white/2 transition-colors duration-150">{children}</tr>,

  // Horizontal rule
  hr: () => <hr className="my-8 border-0 h-px bg-linear-to-r from-transparent via-foreground/10 to-transparent" />,

  // Strong & emphasis
  strong: ({ children }) => <strong className="font-semibold text-foreground/90">{children}</strong>,
  em: ({ children }) => <em className="font-medium italic text-foreground/85">{children}</em>,

  // Images
  img: ({ src, alt }) => (
    <img src={src} alt={alt} className="my-4 rounded-xl border border-white/6 max-w-full shadow-lg" />
  ),
};

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }, [text]);

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={cn(
        "flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[12px] font-medium transition-all duration-200",
        copied
          ? "text-emerald-400 bg-emerald-500/10"
          : "text-muted-foreground/60 hover:text-foreground/80 hover:bg-white/5"
      )}
    >
      {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}
