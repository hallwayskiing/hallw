import { Activity, CheckCircle2, Clock, Loader2, XCircle } from 'lucide-react';
import { useSocket } from '../contexts/SocketContext';
import { useEffect, useState } from 'react';
import { cn } from '../lib/utils';

// ============================================================================
// Types
// ============================================================================

type ToolStatus = 'running' | 'success' | 'error';

interface ToolState {
    run_id: string;
    tool_name: string;
    status: ToolStatus;
    args: string;
    result: string;
}

interface StageEvent {
    stage_index: number;
}

interface ToolPlanEvent {
    plan?: string[];
}

interface SidebarProps {
    className?: string;
}

// ============================================================================
// Main Component
// ============================================================================

export function Sidebar({ className }: SidebarProps) {
    const { socket } = useSocket();
    const [toolStates, setToolStates] = useState<ToolState[]>([]);
    const [toolPlan, setToolPlan] = useState<string[]>([]);
    const [currentStageIndex, setCurrentStageIndex] = useState<number>(-1);
    const [completedStages, setCompletedStages] = useState<number[]>([]);

    useEffect(() => {
        if (!socket) return;

        // Incremental tool state update from backend
        const onToolStateUpdate = (state: ToolState) => {
            if (!state) return;
            setToolStates(prev => {
                const { run_id } = state;
                if (!run_id) return [...prev, state];

                const idx = prev.findIndex(t => t.run_id === run_id);
                if (idx >= 0) {
                    const updated = [...prev];
                    updated[idx] = { ...updated[idx], ...state };
                    return updated;
                }
                return [...prev, state];
            });
        };

        // Tool plan updates
        const onToolPlanUpdated = (data: string[] | ToolPlanEvent) => {
            const plan = Array.isArray(data) ? data : (data?.plan || []);
            setToolPlan(plan);
        };

        // Stage lifecycle
        const onStageStarted = (data: StageEvent) => {
            setCurrentStageIndex(data.stage_index);
        };

        const onStageCompleted = (data: StageEvent) => {
            setCompletedStages(prev => [...new Set([...prev, data.stage_index])]);
        };

        // Reset all state
        const onReset = () => {
            setToolStates([]);
            setToolPlan([]);
            setCurrentStageIndex(-1);
            setCompletedStages([]);
        };

        // Register events
        socket.on('tool_state_update', onToolStateUpdate);
        socket.on('tool_plan_updated', onToolPlanUpdated);
        socket.on('stage_started', onStageStarted);
        socket.on('stage_completed', onStageCompleted);
        socket.on('reset', onReset);

        return () => {
            socket.off('tool_state_update', onToolStateUpdate);
            socket.off('tool_plan_updated', onToolPlanUpdated);
            socket.off('stage_started', onStageStarted);
            socket.off('stage_completed', onStageCompleted);
            socket.off('reset', onReset);
        };
    }, [socket]);

    return (
        <div className={cn("flex flex-col h-full bg-secondary/30 border-l border-border w-64", className)}>
            {/* Stages Section */}
            <StagesPanel
                stages={toolPlan}
                currentIndex={currentStageIndex}
                completedIndices={completedStages}
            />

            {/* Execution Section */}
            <ExecutionPanel toolStates={toolStates} />
        </div>
    );
}

// ============================================================================
// Sub-components
// ============================================================================

interface StagesPanelProps {
    stages: string[];
    currentIndex: number;
    completedIndices: number[];
}

function StagesPanel({ stages, currentIndex, completedIndices }: StagesPanelProps) {
    return (
        <div className="flex-1 overflow-y-auto p-4 border-b border-border">
            <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                <Clock className="w-3 h-3" /> Stages
            </h2>
            <div className="space-y-4">
                {stages.length === 0 ? (
                    <p className="text-sm text-muted-foreground italic">No active stages.</p>
                ) : (
                    stages.map((step, idx) => (
                        <StageItem
                            key={idx}
                            index={idx}
                            label={step}
                            isCurrent={idx === currentIndex}
                            isCompleted={completedIndices.includes(idx)}
                        />
                    ))
                )}
            </div>
        </div>
    );
}

interface StageItemProps {
    index: number;
    label: string;
    isCurrent: boolean;
    isCompleted: boolean;
}

function StageItem({ index, label, isCurrent, isCompleted }: StageItemProps) {
    return (
        <div className={cn(
            "text-sm flex justify-between items-start gap-2",
            isCurrent ? "text-foreground font-medium" : "text-foreground/70"
        )}>
            <div className="flex gap-2">
                <span className="text-muted-foreground">{index + 1}.</span>
                <span>{label}</span>
            </div>
            {isCompleted ? (
                <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0 mt-0.5" />
            ) : isCurrent ? (
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin shrink-0 mt-0.5" />
            ) : null}
        </div>
    );
}

interface ExecutionPanelProps {
    toolStates: ToolState[];
}

function ExecutionPanel({ toolStates }: ExecutionPanelProps) {
    return (
        <div className="flex-1 overflow-y-auto p-4 bg-background/50">
            <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                <Activity className="w-3 h-3" /> Execution
            </h2>
            <div className="space-y-3">
                {toolStates.length === 0 ? (
                    <p className="text-sm text-muted-foreground italic">Ready to execute.</p>
                ) : (
                    // Show newest first
                    [...toolStates].reverse().map(state => (
                        <ToolItem key={state.run_id} state={state} />
                    ))
                )}
            </div>
        </div>
    );
}

interface ToolItemProps {
    state: ToolState;
}

function ToolItem({ state }: ToolItemProps) {
    const { tool_name, status, args } = state;

    const borderColor = {
        running: 'border-blue-500',
        success: 'border-green-500',
        error: 'border-red-500'
    }[status];

    const StatusIcon = {
        running: <Loader2 className="w-3 h-3 animate-spin text-blue-500" />,
        success: '',
        error: ''
    }[status];

    return (
        <div className={cn("group relative pl-4 border-l-2 transition-colors", borderColor)}>
            <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-sm text-foreground">{tool_name}</span>
                {StatusIcon}
            </div>
            <p className="text-xs text-muted-foreground truncate" title={formatArgs(args)}>
                {status === 'running' ? 'Running...' : formatArgs(args)}
            </p>
        </div>
    );
}

// ============================================================================
// Helpers
// ============================================================================

function formatArgs(args: string): string {
    try {
        return args.replace(/[{}']/g, '');
    } catch {
        return args;
    }
}
