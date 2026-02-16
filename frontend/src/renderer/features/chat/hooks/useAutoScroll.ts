import { useCallback, useLayoutEffect, useRef, useState } from "react";

export function useAutoScroll<T extends unknown[]>(dependencies: T) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);
  const isSmoothScrolling = useRef(false);

  const handleScroll = useCallback(() => {
    if (isSmoothScrolling.current) return;

    const div = scrollRef.current;
    if (!div) return;

    const threshold = 80;
    const isAtBottom = div.scrollHeight - div.scrollTop - div.clientHeight <= threshold;

    setUserHasScrolledUp(!isAtBottom);
  }, []);

  useLayoutEffect(() => {
    if (isSmoothScrolling.current) return;

    const div = scrollRef.current;
    if (div && !userHasScrolledUp) {
      div.scrollTo({ top: div.scrollHeight, behavior: "instant" });
    }
  }, [...dependencies, userHasScrolledUp]);

  const scrollToBottom = useCallback(() => {
    const div = scrollRef.current;
    if (div) {
      isSmoothScrolling.current = true;
      setUserHasScrolledUp(false);

      setTimeout(() => {
        div.scrollTo({ top: div.scrollHeight, behavior: "smooth" });
        setTimeout(() => {
          isSmoothScrolling.current = false;
        }, 1000);
      }, 0);
    }
  }, []);

  return {
    scrollRef,
    handleScroll,
    scrollToBottom,
    showScrollButton: userHasScrolledUp,
  };
}
