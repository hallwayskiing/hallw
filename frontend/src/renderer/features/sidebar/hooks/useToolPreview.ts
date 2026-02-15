import { useState, useMemo, useCallback } from 'react';
import { ToolState } from '../types';

export function useToolPreview(toolState: ToolState | null | undefined) {
    const [activeTab, setActiveTab] = useState<'result' | 'args'>('result');
    const [copied, setCopied] = useState(false);

    const parsedResult = useMemo(() => {
        if (!toolState) return { resultMessage: '', resultData: null, isSuccess: false };

        let resultMessage = toolState.result || '';
        let resultData = null;
        let isSuccess = toolState.status === 'success';

        try {
            if (toolState.result && typeof toolState.result === 'string') {
                // Try parsing JSON result
                const parsed = JSON.parse(toolState.result);
                if (parsed && typeof parsed === 'object') {
                    if ('message' in parsed) resultMessage = parsed.message;
                    if ('data' in parsed) resultData = parsed.data;
                    if ('success' in parsed) isSuccess = parsed.success;
                }
            } else if (toolState.result && typeof toolState.result === 'object') {
                // If result is already an object
                const res = toolState.result as any;
                if ('message' in res) resultMessage = res.message;
                if ('data' in res) resultData = res.data;
                if ('success' in res) isSuccess = res.success;
            }
        } catch (e) {
            // Treat as raw it failed
        }

        return { resultMessage, resultData, isSuccess };
    }, [toolState?.result, toolState?.status]);

    const parsedArgs = useMemo(() => {
        if (!toolState?.args) return null;

        // If it's already an object, return it
        if (typeof toolState.args === 'object') {
            return Object.entries(toolState.args);
        }

        if (typeof toolState.args !== 'string') return null;

        let str = toolState.args.trim();
        if (!str) return null;

        try {
            // Standard JSON parse
            const parsed = JSON.parse(str);
            if (typeof parsed === 'object' && parsed !== null) {
                return Object.entries(parsed);
            }
        } catch (e) {
            // Try handling Python style dicts (single quotes)
            try {
                // Replace single quotes with double quotes, but be careful with nested quotes
                // This is a naive attempt, but often enough for simple tool args
                const jsonFixed = str.replace(/'/g, '"');
                const parsed = JSON.parse(jsonFixed);
                if (typeof parsed === 'object' && parsed !== null) {
                    return Object.entries(parsed);
                }
            } catch (e2) {
                // Still failed
            }
        }
        return null;
    }, [toolState?.args]);

    const copyToClipboard = useCallback(async (text: string) => {
        if (!text) return;
        try {
            await navigator.clipboard.writeText(text);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    }, []);

    const isRunning = toolState?.status === 'running';

    return {
        activeTab,
        setActiveTab,
        copied,
        copyToClipboard,
        isRunning,
        ...parsedResult,
        parsedArgs
    };
}
