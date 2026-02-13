import { useState, useEffect } from 'react';

export function useSmoothTyping(targetText: string, isStreaming: boolean, speed: number = 1) {
    const [displayedText, setDisplayedText] = useState('');

    useEffect(() => {
        if (!isStreaming) {
            setDisplayedText(targetText);
            return;
        }

        if (displayedText.length >= targetText.length) {
            return;
        }

        let animationFrameId: number;

        const animate = () => {
            setDisplayedText((current) => {
                if (current.length >= targetText.length) {
                    cancelAnimationFrame(animationFrameId);
                    return targetText;
                }

                const diff = targetText.length - current.length;
                const step = Math.ceil(diff / 50) + speed;

                const nextText = targetText.slice(0, current.length + step);
                return nextText;
            });
            animationFrameId = requestAnimationFrame(animate);
        };

        animationFrameId = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrameId);
    }, [targetText, isStreaming, speed]);

    return displayedText;
}
