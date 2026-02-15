import { useEffect, useRef, useState } from "react";

export function useCountdown(seconds: number | undefined, onTimeout: () => void, enabled: boolean = true) {
  const [timeLeft, setTimeLeft] = useState(seconds || 0);
  const onTimeoutRef = useRef(onTimeout);

  useEffect(() => {
    onTimeoutRef.current = onTimeout;
  }, [onTimeout]);

  useEffect(() => {
    if (!enabled || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onTimeoutRef.current();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [enabled, seconds]); // Re-run if seconds or enabled changes

  return timeLeft;
}
