import { useRef, useState, useLayoutEffect } from 'react';

export function useAutoResize(value: string, maxHeight: number = 128) {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const [height, setHeight] = useState(42);

    useLayoutEffect(() => {
        const node = textareaRef.current;
        if (!node) return;

        node.style.height = '0';

        const scrollHeight = node.scrollHeight;
        const nextHeight = Math.min(Math.max(scrollHeight, 42), maxHeight);

        setHeight(nextHeight);

        node.style.height = '';
    }, [value, maxHeight]);

    return { textareaRef, height };
}
