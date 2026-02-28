export type ToolStatus = "running" | "success" | "error";

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

export interface ToolPreviewProps {
  toolState: ToolState;
  isOpen: boolean;
  onClose: () => void;
}

// ---------------------------------------------------------------------------
// Session state
// ---------------------------------------------------------------------------

export interface SidebarSessionState {
  toolStates: ToolState[];
  stages: string[];
  currentStageIndex: number;
  completedStages: number[];
  errorStageIndex: number;
}

// ---------------------------------------------------------------------------
// Slice interface
// ---------------------------------------------------------------------------

export interface SidebarSlice {
  sidebarSessions: Record<string, SidebarSessionState>;

  getVisibleTools: () => ToolState[];

  _onToolStateUpdate: (sessionId: string, state: ToolState) => void;
  _onStagesBuilt: (sessionId: string, data: string[] | { stages?: string[] }) => void;
  _onStageStarted: (sessionId: string, data: { stage_index: number }) => void;
  _onStagesCompleted: (sessionId: string, data: { stage_indices: number[] }) => void;
  _onStagesEdited: (sessionId: string, data: { stages: string[]; current_index: number }) => void;

  _onSidebarTaskStarted: (sessionId: string) => void;
  _onSidebarTaskCancelled: (sessionId: string) => void;
  _onSidebarFatalError: (sessionId: string, data: unknown) => void;
  _onSidebarReset: (sessionId: string) => void;
  _onSidebarHistoryLoaded: (sessionId: string, data: { toolStates?: ToolState[] }) => void;
}
