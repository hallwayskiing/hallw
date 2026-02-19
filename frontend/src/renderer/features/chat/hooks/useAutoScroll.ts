import { useCallback, useEffect, useLayoutEffect, useRef, useState } from "react";

export function useAutoScroll<T extends unknown[]>(dependencies: T) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);
  const userHasScrolledUpRef = useRef(false);
  const isSmoothScrolling = useRef(false);

  const handleScroll = useCallback(() => {
    if (isSmoothScrolling.current) return;

    const div = scrollRef.current;
    if (!div) return;

    const threshold = 80;
    const isAtBottom = div.scrollHeight - div.scrollTop - div.clientHeight <= threshold;

    userHasScrolledUpRef.current = !isAtBottom;
    setUserHasScrolledUp(!isAtBottom);
  }, []);

  useLayoutEffect(() => {
    if (isSmoothScrolling.current) return;

    const div = scrollRef.current;
    if (div && !userHasScrolledUp) {
      div.scrollTo({ top: div.scrollHeight, behavior: "instant" });
    }
  }, [...dependencies, userHasScrolledUp]);

  // Handle local DOM expansion which doesn't trigger parent re-renders
  useEffect(() => {
    const div = scrollRef.current;
    if (!div) return;

    const observer = new ResizeObserver(() => {
      // If smooth scrolling or user has scrolled up, don't interrupt
      if (isSmoothScrolling.current || userHasScrolledUpRef.current) return;
      div.scrollTo({ top: div.scrollHeight, behavior: "instant" });
    });

    // Observe both the container and its content wrapper for height changes
    observer.observe(div);
    if (div.firstElementChild) {
      observer.observe(div.firstElementChild);
    }

    return () => observer.disconnect();
  }, []);

  const scrollToBottom = useCallback(() => {
    const div = scrollRef.current;
    if (div) {
      isSmoothScrolling.current = true;
      userHasScrolledUpRef.current = false;
      setUserHasScrolledUp(false);

      setTimeout(() => {
        div.scrollTo({ top: div.scrollHeight, behavior: "smooth" });
        setTimeout(() => {
          isSmoothScrolling.current = false;
        }, 1500);
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
