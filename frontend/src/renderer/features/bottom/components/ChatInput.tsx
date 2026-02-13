import { forwardRef, useImperativeHandle, useEffect } from 'react';
import { cn } from '@lib/utils';
import { useAutoResize } from '../hooks/useAutoResize';
import { ChatInputProps } from '../types';

export const ChatInput = forwardRef<HTMLTextAreaElement, ChatInputProps>(({
    value,
    onChange,
    onKeyDown,
    disabled,
    isFocused,
    placeholder,
    onFocus,
    onBlur,
    className
}, ref) => {
    const { textareaRef, height } = useAutoResize(value);
    useImperativeHandle(ref, () => textareaRef.current!);

    return (
        <form
            className={cn(
                "absolute bottom-0 left-0 right-0 bg-muted/30 rounded-2xl border border-border",
                "focus-within:ring-2 focus-within:ring-ring focus-within:border-transparent",
                "transition-[all] duration-200 ease-in-out overflow-hidden shadow-sm",
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
                    "w-full h-full bg-transparent border-0 focus:ring-0 focus:outline-none",
                    "resize-none py-2.5 leading-5 px-4 text-sm text-foreground",
                    "placeholder:text-muted-foreground/50",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    height >= 128 ? "overflow-y-auto custom-scrollbar" : "overflow-y-hidden"
                )}
                rows={1}
            />
        </form>
    );
});
