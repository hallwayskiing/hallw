import { useState } from 'react';
import { Activity, CheckCircle2, Clock, Loader2, ChevronLeft, ChevronRight, XCircle } from 'lucide-react';
import { useAppStore, ToolState } from '../../stores/appStore';
import { cn } from '../../lib/utils';

// ============================================================================
// Types
// ============================================================================

interface SidebarProps {
    className?: string;
}

// ============================================================================
// Main Component
// ============================================================================

export function Sidebar({ className }: SidebarProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const toolStates = useAppStore(s => s.toolStates);
    const toolPlan = useAppStore(s => s.stages);
    const currentStageIndex = useAppStore(s => s.currentStageIndex);
    const completedStages = useAppStore(s => s.completedStages);
    const errorStageIndex = useAppStore(s => s.errorStageIndex);

    return (
        <div
            className={cn(
                "flex flex-col h-full bg-secondary/30 border-l border-border transition-all duration-300 ease-in-out",
                isExpanded ? "w-64" : "w-12",
                className
            )}
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => setIsExpanded(false)}
        >
            {/* Collapse/Expand Indicator */}
            <div className="flex items-center justify-center h-10 border-b border-border shrink-0">
                {isExpanded ? (
                    <ChevronRight className="w-4 h-4 text-muted-foreground" />
                ) : (
                    <ChevronLeft className="w-4 h-4 text-muted-foreground" />
                )}
            </div>

            {/* Stages Section */}
            <StagesPanel
                stages={toolPlan}
                currentIndex={currentStageIndex}
                completedIndices={completedStages}
                errorStageIndex={errorStageIndex}
                isExpanded={isExpanded}
            />

            {/* Execution Section */}
            <ExecutionPanel toolStates={toolStates} isExpanded={isExpanded} />
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
    errorStageIndex: number;
    isExpanded: boolean;
}

function StagesPanel({ stages, currentIndex, completedIndices, errorStageIndex, isExpanded }: StagesPanelProps) {
    return (
        <div className={cn(
            "flex-1 overflow-y-auto border-b border-border transition-all duration-300",
            isExpanded ? "p-4" : "p-2"
        )}>
            <h2 className={cn(
                "text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2",
                !isExpanded && "justify-center"
            )}>
                <Clock className="w-3 h-3 shrink-0" />
                {isExpanded && <span>Stages</span>}
            </h2>
            <div className="space-y-4">
                {stages.length === 0 ? (
                    isExpanded && <p className="text-sm text-muted-foreground italic">No active stages.</p>
                ) : (
                    stages.map((step, idx) => (
                        <StageItem
                            key={idx}
                            index={idx}
                            label={step}
                            isCurrent={idx === currentIndex}
                            isCompleted={completedIndices.includes(idx)}
                            isError={errorStageIndex === idx}
                            isExpanded={isExpanded}
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
    isError: boolean;
    isExpanded: boolean;
}

function StageItem({ index, label, isCurrent, isCompleted, isError, isExpanded }: StageItemProps) {
    const StatusIcon = isCompleted ? (
        <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />
    ) : isError ? (
        <XCircle className="w-4 h-4 text-red-500 shrink-0" />
    ) : isCurrent ? (
        <Loader2 className="w-4 h-4 text-blue-500 animate-spin shrink-0" />
    ) : (
        <div className="w-4 h-4 rounded-full border border-muted-foreground/30 shrink-0" />
    );

    if (!isExpanded) {
        return (
            <div className="flex justify-center">
                {StatusIcon}
            </div>
        );
    }

    return (
        <div className={cn(
            "text-sm flex justify-between items-start gap-2",
            isError ? "text-red-500" : isCurrent ? "text-foreground font-medium" : "text-foreground/70"
        )}>
            <div className="flex gap-2">
                <span className="text-muted-foreground">{index + 1}.</span>
                <span>{label}</span>
            </div>
            {StatusIcon}
        </div>
    );
}

interface ExecutionPanelProps {
    toolStates: ToolState[];
    isExpanded: boolean;
}

const HIDDEN_TOOLS = ['build_stages', 'end_current_stage'];

function ExecutionPanel({ toolStates, isExpanded }: ExecutionPanelProps) {
    // Filter out internal tools
    const visibleTools = toolStates.filter(t => !HIDDEN_TOOLS.includes(t.tool_name));

    return (
        <div className={cn(
            "flex-1 overflow-y-auto bg-background/50 transition-all duration-300",
            isExpanded ? "p-4" : "p-2"
        )}>
            <h2 className={cn(
                "text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 flex items-center gap-2",
                !isExpanded && "justify-center"
            )}>
                <Activity className="w-3 h-3 shrink-0" />
                {isExpanded && <span>Execution</span>}
            </h2>
            <div className="space-y-3">
                {visibleTools.length === 0 ? (
                    isExpanded && <p className="text-sm text-muted-foreground italic">Ready to execute.</p>
                ) : (
                    // Show newest first
                    [...visibleTools].reverse().map(state => (
                        <ToolItem key={state.run_id} state={state} isExpanded={isExpanded} />
                    ))
                )}
            </div>
        </div>
    );
}

interface ToolItemProps {
    state: ToolState;
    isExpanded: boolean;
}

function ToolItem({ state, isExpanded }: ToolItemProps) {
    const { tool_name, status, args } = state;

    const statusColor = {
        running: 'bg-blue-500',
        success: 'bg-green-500',
        error: 'bg-red-500'
    }[status];

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

    // Collapsed: show only status dot
    if (!isExpanded) {
        return (
            <div className="flex justify-center">
                <div className={cn("w-2 h-2 rounded-full", statusColor)} />
            </div>
        );
    }

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
