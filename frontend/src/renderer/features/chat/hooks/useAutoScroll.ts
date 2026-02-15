import { useCallback, useLayoutEffect, useRef, useState } from "react";

/**
 * Hook to handle auto-scrolling in a container.
 * It stays at the bottom unless the user has manually scrolled up.
 */
export function useAutoScroll(dependencies: any[]) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);

  const handleScroll = useCallback(() => {
    const div = scrollRef.current;
    if (!div) return;

    // threshold to consider "at bottom"
    const threshold = 80;
    const isAtBottom = div.scrollHeight - div.scrollTop - div.clientHeight <= threshold;

    // If user is at bottom, reset the flag. If they scroll up, set the flag.
    if (isAtBottom) {
      setUserHasScrolledUp(false);
    } else {
      setUserHasScrolledUp(true);
    }
  }, []);

  // Effect to scroll to bottom when dependencies change, ONLY if user hasn't scrolled up
  useLayoutEffect(() => {
    const div = scrollRef.current;
    if (div && !userHasScrolledUp) {
      div.scrollTo({ top: div.scrollHeight, behavior: "instant" }); // 'instant' is better for streaming than 'smooth'
    }
  }, [dependencies, userHasScrolledUp]);

  // Force scroll to bottom when requested
  const scrollToBottom = useCallback(() => {
    const div = scrollRef.current;
    if (div) {
      div.scrollTo({ top: div.scrollHeight, behavior: "smooth" });
      setUserHasScrolledUp(false);
    }
  }, []);

  return { scrollRef, handleScroll, scrollToBottom };
}
