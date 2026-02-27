import { useEffect, useRef, useState } from "react";

/**
 * useSmoothTyping - Smoothly animates text content as it streams in.
 *
 * @param targetText The full text received so far from the stream.
 * @param isStreaming Whether the stream is still active.
 * @param baseSpeed Characters per second to drip (default 60).
 */
export function useSmoothTyping(targetText: string, isStreaming: boolean, baseSpeed: number = 60) {
  const [displayedText, setDisplayedText] = useState(isStreaming ? "" : targetText);
  const currentTextRef = useRef(isStreaming ? "" : targetText);
  const targetTextRef = useRef(targetText);
  const lastUpdateRef = useRef<number>(0);
  const animationFrameRef = useRef<number>(0);

  // Sync target ref whenever targetText changes
  useEffect(() => {
    targetTextRef.current = targetText;

    if (!isStreaming) {
      setDisplayedText(targetText);
      currentTextRef.current = targetText;
    }
  }, [targetText, isStreaming]);

  useEffect(() => {
    if (!isStreaming) {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      return;
    }

    const tick = (now: number) => {
      if (!lastUpdateRef.current) {
        lastUpdateRef.current = now;
      }

      const deltaTime = now - lastUpdateRef.current;
      const currentLen = currentTextRef.current.length;
      const targetLen = targetTextRef.current.length;
      const backlog = targetLen - currentLen;

      if (backlog > 0) {
        // Base rate: chars per millisecond
        let rate = baseSpeed / 1000;

        // Adaptive speed: Accelerate if we are falling behind
        if (backlog > 50) {
          rate += (backlog - 50) * 0.002;
        }

        const charsToAddFloat = deltaTime * rate;

        if (charsToAddFloat >= 1) {
          const charsToAdd = Math.floor(charsToAddFloat);
          const nextLen = Math.min(currentLen + charsToAdd, targetLen);
          const nextText = targetTextRef.current.slice(0, nextLen);

          currentTextRef.current = nextText;
          setDisplayedText(nextText);
          lastUpdateRef.current = now;
        }
      } else {
        lastUpdateRef.current = now;
      }

      animationFrameRef.current = requestAnimationFrame(tick);
    };

    animationFrameRef.current = requestAnimationFrame(tick);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isStreaming, baseSpeed]);

  return displayedText;
}
