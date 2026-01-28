import { Activity, CheckCircle2, CircleX, Clock, Loader2, Play } from 'lucide-react';
import { useSocket } from '../contexts/SocketContext';
import { useEffect, useState } from 'react';
import { cn } from '../lib/utils';

interface ToolState {
    name: string;
    status: 'running' | 'success' | 'error';
    args: string;
}

interface SidebarProps {
    className?: string;
}

export function Sidebar({ className }: SidebarProps) {
    const { socket } = useSocket();
    const [toolStates, setToolStates] = useState<ToolState[]>([]);
    const [toolPlan, setToolPlan] = useState<string[]>([]);

    useEffect(() => {
        if (!socket) return;

        const handleToolStates = (states: ToolState[]) => setToolStates(states || []);
        const handleToolPlan = (data: string[] | { plan: string[] }) => {
            // Handle both raw list and {plan: []} formats
            const plan = Array.isArray(data) ? data : (data?.plan || []);
            setToolPlan(plan);
        };
        const handleReset = () => {
            setToolStates([]);
            setToolPlan([]);
        };

        socket.on('tool_states_updated', handleToolStates);
        socket.on('tool_plan_updated', handleToolPlan);
        socket.on('reset', handleReset);

        return () => {
            socket.off('tool_states_updated', handleToolStates);
            socket.off('tool_plan_updated', handleToolPlan);
            socket.off('reset', handleReset);
        };
    }, [socket]);

    const parseToolArgs = (args: string) => {
        try {
            const cleanStr = args.replace(/[{}']/g, '');
            return cleanStr;
        } catch (e) {
            return args;
        }
    };

    return (
        <div className={cn("flex flex-col h-full bg-secondary/30 border-l border-border w-64", className)}>
            {/* Stages Section */}
            <div className="flex-1 overflow-y-auto p-4 border-b border-border">
                <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Clock className="w-3 h-3" /> Stages
                </h2>
                <div className="space-y-4">
                    {(toolPlan || []).length === 0 && (
                        <p className="text-sm text-muted-foreground italic">No active stages.</p>
                    )}
                    {(toolPlan || []).map((step, idx) => (
                        <div key={idx} className="text-sm text-foreground/80 flex gap-2">
                            <span className="text-muted-foreground">{idx + 1}.</span>
                            <span>{step}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Execution Section */}
            <div className="flex-1 overflow-y-auto p-4 bg-background/50">
                <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Activity className="w-3 h-3" /> Execution
                </h2>
                <div className="space-y-3">
                    {(toolStates || []).length === 0 && (
                        <p className="text-sm text-muted-foreground italic">Ready to execute.</p>
                    )}
                    {(toolStates || []).slice().reverse().map((state, idx) => (
                        <div key={idx} className={cn(
                            "group relative pl-4 border-l-2 transition-colors",
                            state.status === 'running' ? "border-blue-500" :
                                state.status === 'error' ? "border-red-500" :
                                    "border-green-500"
                        )}  >
                            <div className="flex items-center justify-between mb-1">
                                <span className="font-medium text-sm text-foreground">{state.name}</span>
                                {state.status === 'running' && <Loader2 className="w-3 h-3 animate-spin text-blue-500" />}
                            </div>
                            <p className="text-xs text-muted-foreground truncate" title={parseToolArgs(state.args)}>
                                {state.status === 'running' ? 'Running...' : parseToolArgs(state.args)}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
