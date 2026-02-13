import { AlertTriangle } from 'lucide-react';

export function ErrorCard({ content }: { content: string }) {
    return (
        <div className="max-w-3xl mx-auto w-full animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="bg-destructive/10 border border-destructive/80 rounded-lg p-4 flex gap-3 items-start">
                <AlertTriangle className="w-5 h-5 text-red-600 dark:text-red-400 shrink-0 mt-0.5" />
                <div className="space-y-1 overflow-hidden min-w-0">
                    <h3 className="font-bold text-red-600 dark:text-red-400 text-sm">System Error</h3>
                    <div className="text-sm text-red-600 dark:text-red-400 font-mono whitespace-pre-wrap break-words">{content}</div>
                </div>
            </div>
        </div>
    );
}
