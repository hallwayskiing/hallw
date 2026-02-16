import { useCallback, useLayoutEffect, useRef, useState } from "react";

export function useAutoScroll<T extends unknown[]>(dependencies: T) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);

  const handleScroll = useCallback(() => {
    const div = scrollRef.current;
    if (!div) return;

    const threshold = 80;
    const isAtBottom = div.scrollHeight - div.scrollTop - div.clientHeight <= threshold;

    setUserHasScrolledUp(!isAtBottom);
  }, []);

  useLayoutEffect(() => {
    const div = scrollRef.current;
    if (div && !userHasScrolledUp) {
      div.scrollTo({ top: div.scrollHeight, behavior: "instant" });
    }
  }, [...dependencies, userHasScrolledUp]);

  const scrollToBottom = useCallback(() => {
    const div = scrollRef.current;
    if (div) {
      div.scrollTo({ top: div.scrollHeight, behavior: "smooth" });
      setUserHasScrolledUp(false);
    }
  }, []);

  return {
    scrollRef,
    handleScroll,
    scrollToBottom,
    showScrollButton: userHasScrolledUp,
  };
}
