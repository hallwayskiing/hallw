import { X, CheckCircle2, XCircle, Copy, Check, Loader2 } from 'lucide-react';
import { useState } from 'react';
import { cn } from '../../lib/utils';
import { ToolState } from '../../stores/appStore';

interface ToolPreviewProps {
    toolState: ToolState;
    isOpen: boolean;
    onClose: () => void;
}

export function ToolPreview({ toolState, isOpen, onClose }: ToolPreviewProps) {
    const [activeTab, setActiveTab] = useState<'result' | 'args'>('result');
    const [copied, setCopied] = useState(false);

    if (!isOpen) return null;

    // Parse result JSON safely
    let parsedResult: any = null;
    let resultMessage = toolState.result;
    let resultData = null;
    let isSuccess = toolState.status === 'success';
    let isRunning = toolState.status === 'running';

    try {
        const parsed = JSON.parse(toolState.result);
        if (parsed && typeof parsed === 'object') {
            parsedResult = parsed;
            // If it follows the standard {success, message, data} format
            if ('message' in parsed) resultMessage = parsed.message;
            if ('data' in parsed) resultData = parsed.data;
            if ('success' in parsed) isSuccess = parsed.success;
        }
    } catch (e) {
        // Not JSON, treat as raw string
    }

    const copyToClipboard = async (text: string) => {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const contentToDisplay = activeTab === 'result'
        ? (resultData ? JSON.stringify(resultData, null, 2) : resultMessage)
        : toolState.args;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm animate-in fade-in-0">
            <div className="w-full max-w-2xl bg-card border border-border rounded-lg shadow-lg flex flex-col max-h-[80vh] animate-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-border">
                    <div className="flex items-center gap-3">
                        <div className={cn(
                            "p-2 rounded-full",
                            isRunning ? "bg-blue-500/10 text-blue-500" :
                                isSuccess ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
                        )}>
                            {isRunning ? <Loader2 className="w-5 h-5 animate-spin" /> :
                                isSuccess ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                        </div>
                        <div>
                            <h3 className="font-semibold text-lg">{toolState.tool_name}</h3>
                            <p className="text-xs text-muted-foreground font-mono">{toolState.run_id}</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-muted rounded-full transition-colors"
                    >
                        <X className="w-5 h-5 text-muted-foreground" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-border px-4">
                    <button
                        onClick={() => setActiveTab('result')}
                        className={cn(
                            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
                            activeTab === 'result'
                                ? "border-primary text-primary"
                                : "border-transparent text-muted-foreground hover:text-foreground"
                        )}
                    >
                        Result
                    </button>
                    <button
                        onClick={() => setActiveTab('args')}
                        className={cn(
                            "px-4 py-2 text-sm font-medium border-b-2 transition-colors",
                            activeTab === 'args'
                                ? "border-primary text-primary"
                                : "border-transparent text-muted-foreground hover:text-foreground"
                        )}
                    >
                        Arguments
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-hidden flex flex-col">
                    {activeTab === 'result' && (
                        <div className="p-4 space-y-4 overflow-y-auto">
                            {/* Message Section */}
                            <div className="space-y-1">
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Message</span>
                                <p className="text-sm p-3 bg-muted/30 rounded-md border border-border/50">
                                    {resultMessage}
                                </p>
                            </div>

                            {/* Data Section */}
                            {resultData && (
                                <div className="space-y-1 flex-1">
                                    <div className="flex items-center justify-between">
                                        <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Data</span>
                                        <button
                                            onClick={() => copyToClipboard(JSON.stringify(resultData, null, 2))}
                                            className="text-xs flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors"
                                        >
                                            {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                            {copied ? "Copied" : "Copy"}
                                        </button>
                                    </div>
                                    <pre className="text-xs font-mono p-4 bg-muted/50 rounded-md border border-border overflow-x-auto">
                                        {JSON.stringify(resultData, null, 2)}
                                    </pre>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'args' && (
                        <div className="p-4 flex-1 flex flex-col overflow-hidden">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Input Arguments</span>
                                <button
                                    onClick={() => copyToClipboard(toolState.args)}
                                    className="text-xs flex items-center gap-1 text-muted-foreground hover:text-primary transition-colors"
                                >
                                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                                    {copied ? "Copied" : "Copy"}
                                </button>
                            </div>
                            <pre className="flex-1 text-xs font-mono p-4 bg-muted/50 rounded-md border border-border overflow-auto whitespace-pre-wrap break-all">
                                {tryFormatJson(toolState.args)}
                            </pre>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-border bg-muted/10 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-md transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}

function tryFormatJson(str: string): string {
    try {
        const parsed = JSON.parse(str);
        return JSON.stringify(parsed, null, 2);
    } catch {
        return str;
    }
}
