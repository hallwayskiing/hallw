export type ToolStatus = 'running' | 'success' | 'error';

export interface SidebarProps {
    className?: string;
}

export interface ToolState {
    run_id: string;
    tool_name: string;
    status: ToolStatus;
    args: string;
    result: string;
}

export interface ToolItemProps {
    state: ToolState;
    isExpanded: boolean;
    onClick: () => void;
}

export interface ToolsPanelProps {
    toolStates: ToolState[];
    isExpanded: boolean;
    onToolClick: (tool: ToolState) => void;
}

export interface StageItemProps {
    index: number;
    label: string;
    isCurrent: boolean;
    isCompleted: boolean;
    isError: boolean;
    isExpanded: boolean;
}

export interface StagesPanelProps {
    stages: string[];
    currentIndex: number;
    completedIndices: number[];
    errorStageIndex: number | null;
    isExpanded: boolean;
}
