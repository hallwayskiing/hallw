import { cn } from "@lib/utils";
import { forwardRef, useImperativeHandle } from "react";

import { useAutoResize } from "../hooks/useAutoResize";
import type { ChatInputProps } from "../types";

export const ChatInput = forwardRef<HTMLTextAreaElement, ChatInputProps>(
  ({ value, onChange, onKeyDown, disabled, isFocused, placeholder, onFocus, onBlur, className }, ref) => {
    const maxHeight = 320;
    const { textareaRef, height } = useAutoResize(value, maxHeight);
    useImperativeHandle(ref, () => textareaRef.current as HTMLTextAreaElement);

    return (
      <form
        className={cn(
          "absolute bottom-0 left-0 right-0 bg-muted/30 rounded-2xl border border-border flex items-center",
          "focus-within:ring-2 focus-within:ring-ring focus-within:border-transparent",
          "transition-all duration-200 ease-in-out overflow-hidden shadow-sm",
          isFocused || value.length > 0 ? "bg-background shadow-lg" : "",
          className
        )}
        style={{ height: `${height}px` }}
      >
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={onKeyDown}
          onFocus={onFocus}
          onBlur={onBlur}
          disabled={disabled}
          placeholder={placeholder}
          className={cn(
            "w-full h-full bg-transparent border-0 focus:ring-0 focus:outline-none flex items-center",
            "resize-none py-2 px-4 text-[15px] text-foreground",
            "placeholder:text-muted-foreground/50 leading-[24px]",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            height >= maxHeight ? "overflow-y-auto custom-scrollbar" : "overflow-y-hidden"
          )}
          rows={1}
        />
      </form>
    );
  }
);
