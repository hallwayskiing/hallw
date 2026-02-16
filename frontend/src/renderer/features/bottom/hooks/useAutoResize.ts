import { useLayoutEffect, useRef, useState } from "react";

export function useAutoResize(text: string, maxHeight: number = 128) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [height, setHeight] = useState(42);

  useLayoutEffect(() => {
    const node = textareaRef.current;
    if (!node) return;

    node.style.height = "0";

    const scrollHeight = node.scrollHeight;
    const nextHeight = Math.min(Math.max(scrollHeight, 42), maxHeight);

    setHeight(nextHeight);

    node.style.height = "";

    // for muting biome warning
    console.log(text?.[0]);
  }, [maxHeight, text]);

  return { textareaRef, height };
}
