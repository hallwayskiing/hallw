import { useLayoutEffect, useRef, useState } from "react";

export function useAutoResize(text: string, maxHeight: number = 320) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [height, setHeight] = useState(38);

  useLayoutEffect(() => {
    const node = textareaRef.current;
    if (!node) return;

    node.style.height = "0";

    const scrollHeight = node.scrollHeight;
    const nextHeight = Math.min(Math.max(scrollHeight, 38), maxHeight);

    setHeight(nextHeight);

    node.style.height = "";

    // for muting biome warning
    text = text.trim();
  }, [maxHeight, text]);

  return { textareaRef, height };
}
