import { useEffect, useRef, useState } from "react";

export function useCountdown(seconds: number | undefined, onTimeout: () => void, enabled: boolean = true) {
  const [timeLeft, setTimeLeft] = useState(seconds ?? 0);
  const onTimeoutRef = useRef(onTimeout);
  const timeoutTriggeredRef = useRef(false);

  useEffect(() => {
    onTimeoutRef.current = onTimeout;
  }, [onTimeout]);

  useEffect(() => {
    timeoutTriggeredRef.current = false;
    setTimeLeft(seconds ?? 0);
  }, [seconds]);

  useEffect(() => {
    if (!enabled || typeof seconds !== "number" || timeLeft > 0 || timeoutTriggeredRef.current) return;
    timeoutTriggeredRef.current = true;
    onTimeoutRef.current();
  }, [enabled, seconds, timeLeft]);

  useEffect(() => {
    if (!enabled || timeLeft <= 0) return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          timeoutTriggeredRef.current = true;
          onTimeoutRef.current();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [enabled, timeLeft]); // Re-run if seconds or enabled changes

  return timeLeft;
}
