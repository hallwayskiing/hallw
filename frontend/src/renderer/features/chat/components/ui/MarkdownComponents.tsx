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

    const lineCount = rawText.split("\n").length;

    return (
      <div className="md-code-block group relative my-1 text-left">
        {/* Sticky Copy Button Area */}
        <div className="sticky top-[10px] z-20 w-full h-0 flex justify-end pointer-events-none">
          <div className="pointer-events-auto mt-px mr-[6px]">
            <CopyButton text={rawText} />
          </div>
        </div>

        {/* Header bar */}
        <div className="flex items-center justify-between px-1 pb-1 bg-transparent">
          <span className="text-[13px] font-semibold lowercase pl-1 bg-stone-500 dark:bg-stone-300 bg-clip-text text-transparent">
            {lang || "PLAINTEXT"}
          </span>
          <div className="opacity-0 pointer-events-none select-none">
            <CopyButton text="" />
          </div>
        </div>
        {/* Code content with line numbers */}
        <div className="code-body flex overflow-x-auto overflow-y-hidden rounded-xl border border-foreground/8 dark:border-white/6 bg-[#f5f0e4] dark:bg-[#0d1117]">
          {/* Line number gutter */}
          <div
            className="code-line-numbers shrink-0 select-none text-right text-[13px] leading-6 font-mono py-2 pl-2 pr-1 text-foreground/20 dark:text-white/20 sticky left-0 z-10 bg-[#f5f0e4] dark:bg-[#0d1117]"
            aria-hidden="true"
          >
            {Array.from({ length: lineCount }, (_, i) => (
              <div key={`ln-${i + 1}`}>{i + 1}</div>
            ))}
          </div>
          {/* Code */}
          <pre className="m-0! bg-transparent! py-2! pl-2! pr-1! text-[13px] leading-6 font-mono whitespace-pre flex-1 min-w-0">
            {children}
          </pre>
        </div>
      </div>
    );
  },

  // Inline code
  code: ({ className, children, ...props }) => {
    const text = typeof children === "string" ? children : Array.isArray(children) ? children.join("") : "";
    const isBlock = className?.includes("language-") || className?.includes("hljs") || text.includes("\n");
    if (isBlock) {
      return (
        <code className={cn(className, "block m-0! bg-transparent! p-0!")} {...props}>
          {children}
        </code>
      );
    }
    return (
      <code
        className="px-1.5 py-0.5 rounded-md bg-foreground/6 dark:bg-white/6 border border-foreground/10 dark:border-white/8 text-[13px] font-mono text-emerald-700/90 dark:text-emerald-300/90"
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
          "relative pl-6 text-[15px] text-foreground/80 font-[450] tracking-[-0.005em] leading-[1.75] mb-2 last:mb-0",
          "before:absolute before:left-0 before:top-2.75",
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
      className="text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300 underline decoration-blue-600/30 dark:decoration-blue-400/30 underline-offset-2 hover:decoration-blue-500/50 dark:hover:decoration-blue-300/50 transition-colors duration-200"
    >
      {children}
    </a>
  ),

  // Tables
  table: ({ children }) => (
    <div className="my-4 overflow-x-auto rounded-lg border border-foreground/8 dark:border-white/6">
      <table className="w-full text-sm">{children}</table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-foreground/3 dark:bg-white/3 border-b border-foreground/8 dark:border-white/8">
      {children}
    </thead>
  ),
  th: ({ children }) => (
    <th className="px-4 py-2.5 text-left text-xs font-semibold text-foreground/70 uppercase tracking-wider">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-4 py-2.5 text-foreground/80 border-t border-foreground/4 dark:border-white/4">{children}</td>
  ),
  tr: ({ children }) => (
    <tr className="hover:bg-foreground/2 dark:hover:bg-white/2 transition-colors duration-150">{children}</tr>
  ),

  // Horizontal rule
  hr: () => <hr className="my-8 border-0 h-px bg-linear-to-r from-transparent via-foreground/10 to-transparent" />,

  // Strong & emphasis
  strong: ({ children }) => <strong className="font-semibold text-foreground/90">{children}</strong>,
  em: ({ children }) => <em className="font-medium italic text-foreground/85">{children}</em>,

  // Images
  img: ({ src, alt }) => (
    <img
      src={src}
      alt={alt}
      className="my-4 rounded-xl border border-foreground/8 dark:border-white/6 max-w-full shadow-lg"
    />
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
      title={copied ? "Copied!" : "Copy code"}
      className={cn(
        "flex items-center justify-center p-1 rounded-md transition-all duration-200",
        copied
          ? "text-emerald-400 bg-emerald-500/10"
          : "text-stone-500 dark:text-stone-300 hover:text-stone-600 dark:hover:text-stone-200 hover:bg-foreground/5 dark:hover:bg-white/5"
      )}
    >
      {copied ? <Check className="w-[14px] h-[14px]" /> : <Copy className="w-[14px] h-[14px]" />}
    </button>
  );
}
