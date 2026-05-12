import { cn } from "@lib/utils";
import { useAppStore } from "@store/store";
import {
  Atom,
  Bot,
  BrainCircuit,
  Cat,
  Check,
  CircuitBoard,
  Cpu,
  Crown,
  Dog,
  Gem,
  Ghost,
  Heart,
  type LucideIcon,
  Orbit,
  Rabbit,
  Rocket,
  RotateCcw,
  Smile,
  Sparkles,
  SquarePen,
  Squirrel,
  User,
  UserCircle,
  X,
  Zap,
} from "lucide-react";
import { memo, useEffect, useRef, useState } from "react";

import { useEditableTextarea } from "../hooks/useEditableTextarea";
import { useSmoothTyping } from "../hooks/useSmoothTyping";
import { splitAttachmentPreviews } from "../lib/utils";
import type { AvatarProps, MessageBubbleProps } from "../types";
import { MarkdownContent } from "./MarkdownContent";
import { ReasoningAccordion } from "./ReasoningAccordion";

export const AVATAR_ICON_MAP: Record<string, LucideIcon> = {
  // User avatars
  User,
  UserCircle,
  Smile,
  Ghost,
  Cat,
  Dog,
  Heart,
  Squirrel,
  Rabbit,
  Crown,
  // AI avatars
  Bot,
  BrainCircuit,
  Cpu,
  Sparkles,
  Zap,
  CircuitBoard,
  Atom,
  Orbit,
  Gem,
  Rocket,
};

export function Avatar({ msgRole: role }: AvatarProps) {
  const isUser = role === "user";
  const userAvatarIcon = useAppStore((s) => s.userAvatarIcon);
  const aiAvatarIcon = useAppStore((s) => s.aiAvatarIcon);

  const iconName = isUser ? userAvatarIcon : aiAvatarIcon;
  const IconComponent = AVATAR_ICON_MAP[iconName] || (isUser ? User : Bot);

  return (
    <div
      className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border shadow-md transition-all duration-300",
        isUser
          ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400 shadow-indigo-500/10"
          : "bg-teal-500/10 border-teal-500/20 text-teal-400 shadow-teal-500/10"
      )}
    >
      <IconComponent className={cn("transition-all", "w-5 h-5")} />
    </div>
  );
}

export const MessageBubble = memo(
  ({
    messageId,
    msgRole,
    content,
    reasoning,
    isStreamingReasoning,
    isStreamingContent,
    canEdit,
    onEdit,
    onRetry,
    actionLabel,
    className,
  }: MessageBubbleProps) => {
    const isUser = msgRole === "user";
    const smoothContent = useSmoothTyping(content, isStreamingContent || false);
    const { messageContent } = splitAttachmentPreviews(content);
    const [isEditing, setIsEditing] = useState(false);
    const [draft, setDraft] = useState(messageContent);
    const bubbleRef = useRef<HTMLDivElement | null>(null);
    const { textareaRef, mirrorRef, handleTextareaChange } = useEditableTextarea(isEditing);

    useEffect(() => {
      if (isEditing) return;
      setDraft(messageContent);
    }, [messageContent, isEditing]);

    const handleStartEdit = () => {
      if (!canEdit) return;
      setDraft(messageContent);
      setIsEditing(true);
    };

    const handleCancelEdit = () => {
      setDraft(messageContent);
      setIsEditing(false);
    };

    const handleSaveEdit = () => {
      if (!canEdit || !onEdit) return;
      const nextContent = draft.trim();
      if (!nextContent || nextContent === messageContent) {
        setIsEditing(false);
        setDraft(messageContent);
        return;
      }
      onEdit(messageId, nextContent);
      setIsEditing(false);
    };

    const handleRetry = () => {
      if (!canEdit || !onRetry) return;
      onRetry(messageId, messageContent);
    };

    return (
      <div
        className={cn(
          "flex gap-4 max-w-4xl mx-auto w-full animate-in fade-in duration-300",
          isUser && "flex-row-reverse"
        )}
      >
        <Avatar msgRole={msgRole} />
        <div className={cn("flex-1 space-y-2 min-w-0", isUser ? "text-right" : "text-left")}>
          <div className={cn("flex items-center gap-2 leading-none", isUser ? "justify-end" : "justify-start")}>
            {isUser && (
              <div className="flex items-center gap-1">
                {actionLabel ? (
                  <span className="font-semibold text-xs uppercase tracking-wider leading-none text-sky-400/80">
                    {actionLabel}
                  </span>
                ) : isEditing ? (
                  <>
                    <button
                      type="button"
                      onClick={handleSaveEdit}
                      className="inline-flex h-5 w-5 items-center justify-center rounded-md text-emerald-500/80 hover:text-emerald-400 hover:bg-emerald-500/10 transition-colors"
                      aria-label="Save edit"
                      title="Save edit"
                    >
                      <Check className="w-3.5 h-3.5 translate-y-px" />
                    </button>
                    <button
                      type="button"
                      onClick={handleCancelEdit}
                      className="inline-flex h-5 w-5 items-center justify-center rounded-md text-muted-foreground/60 hover:text-foreground hover:bg-foreground/10 transition-colors"
                      aria-label="Cancel edit"
                      title="Cancel edit"
                    >
                      <X className="w-3.5 h-3.5 translate-y-px" />
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      type="button"
                      onClick={handleRetry}
                      disabled={!canEdit}
                      className={cn(
                        "inline-flex h-5 w-5 items-center justify-center rounded-md transition-colors",
                        canEdit
                          ? "text-muted-foreground/70 hover:text-foreground hover:bg-foreground/10"
                          : "text-muted-foreground/35 cursor-not-allowed"
                      )}
                      aria-label="Retry"
                      title="Retry"
                    >
                      <RotateCcw className="w-3.5 h-3.5 translate-y-px" />
                    </button>
                    <button
                      type="button"
                      onClick={handleStartEdit}
                      disabled={!canEdit}
                      className={cn(
                        "inline-flex h-5 w-5 items-center justify-center rounded-md transition-colors",
                        canEdit
                          ? "text-muted-foreground/70 hover:text-foreground hover:bg-foreground/10"
                          : "text-muted-foreground/35 cursor-not-allowed"
                      )}
                      aria-label="Edit"
                      title="Edit"
                    >
                      <SquarePen className="w-3.5 h-3.5 translate-y-px" />
                    </button>
                  </>
                )}
              </div>
            )}
            <div className="font-semibold text-xs uppercase tracking-wider leading-none text-muted-foreground/60">
              {isUser ? "You" : "HALLW"}
            </div>
          </div>
          {reasoning && <ReasoningAccordion content={reasoning} isStreaming={isStreamingReasoning} />}
          {(isStreamingContent || content) && (
            <div
              ref={bubbleRef}
              className={cn(
                "rounded-2xl text-left",
                isUser
                  ? "inline-block bg-linear-to-br from-indigo-500/10 to-indigo-600/3 border border-indigo-500/10 text-foreground/90 px-4 py-2.5 shadow-sm shadow-indigo-500/5"
                  : "block max-w-[85%] bg-linear-to-br from-teal-500/10 to-teal-600/3 border border-teal-500/12 text-foreground/85 px-5 py-3 shadow-sm shadow-teal-500/8",
                isUser && !isEditing && "max-w-[90%]",
                isUser &&
                  isEditing &&
                  "w-[90%] max-w-[90%] bg-muted/60 from-transparent to-transparent border-border/70 shadow-none",
                isStreamingContent && "min-h-10",
                className
              )}
            >
              {isEditing ? (
                <div className="relative">
                  <div
                    ref={mirrorRef}
                    aria-hidden="true"
                    className="invisible pointer-events-none whitespace-pre-wrap wrap-break-word px-0 py-0 text-[15px] font-[450] tracking-[-0.005em] leading-[1.75] text-foreground/80"
                    style={{ fontFamily: "inherit" }}
                  >
                    {`${draft || " "}\n`}
                  </div>
                  <textarea
                    ref={textareaRef}
                    value={draft}
                    onChange={(e) => {
                      setDraft(e.target.value);
                      handleTextareaChange();
                    }}
                    rows={1}
                    className="absolute inset-0 block h-full w-full resize-none overflow-hidden whitespace-pre-wrap wrap-break-word bg-transparent px-0 py-0 text-[15px] font-[450] tracking-[-0.005em] leading-[1.75] text-foreground/80 outline-hidden border-0 shadow-none"
                    style={{ fontFamily: "inherit" }}
                  />
                </div>
              ) : (
                <MarkdownContent
                  content={isStreamingContent ? smoothContent : content}
                  isStreaming={isStreamingContent}
                />
              )}
            </div>
          )}
        </div>
      </div>
    );
  }
);
