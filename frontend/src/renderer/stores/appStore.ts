import { create } from 'zustand';
import { io, Socket } from 'socket.io-client';

// ============================================================================
// Types
// ============================================================================

type MessageRole = 'user' | 'assistant' | 'system';
type ConfirmationStatus = 'pending' | 'approved' | 'rejected' | 'timeout';
type RuntimeInputStatus = 'pending' | 'submitted' | 'rejected' | 'timeout';
type ToolStatus = 'running' | 'success' | 'error';

interface BaseMessage {
    role: MessageRole;
}

interface TextMessage extends BaseMessage {
    type: 'text';
    content: string;
}

interface ErrorMessage extends BaseMessage {
    type: 'error';
    content: string;
}

interface ConfirmationMessage extends BaseMessage {
    type: 'confirmation';
    requestId: string;
    command: string;
    status: ConfirmationStatus;
}

interface UserInputMessage extends BaseMessage {
    type: 'user_input';
    requestId: string;
    prompt: string;
    result: string;
    status: RuntimeInputStatus;
}

interface StatusMessage extends BaseMessage {
    type: 'status';
    variant: 'completed' | 'cancelled';
}

export type Message = TextMessage | ErrorMessage | ConfirmationMessage | UserInputMessage | StatusMessage;

export interface ConfirmationRequest {
    request_id: string;
    message: string;
    timeout?: number;
}

export interface UserInputRequest {
    request_id: string;
    message: string;
    timeout?: number;
}

export interface ToolState {
    run_id: string;
    tool_name: string;
    status: ToolStatus;
    args: string;
    result: string;
}

// ============================================================================
// Store Interface
// ============================================================================

interface AppState {
    // UI Control
    isChatting: boolean;
    isProcessing: boolean;
    isSettingsOpen: boolean;
    isConnected: boolean;

    // Chat State
    messages: Message[];
    streamingContent: string;
    pendingConfirmation: ConfirmationRequest | null;
    pendingInput: UserInputRequest | null;

    // Sidebar State
    toolStates: ToolState[];
    toolPlan: string[];
    currentStageIndex: number;
    completedStages: number[];

    // Internal
    _socket: Socket | null;
    _streamingContentRef: string;
}

interface AppActions {
    // Setters
    setIsSettingsOpen: (open: boolean) => void;

    // Socket
    initSocket: () => () => void;
    getSocket: () => Socket | null;

    // Actions
    startTask: (task: string) => void;
    stopTask: () => void;
    resetSession: () => void;
    handleConfirmationDecision: (status: ConfirmationStatus) => void;
    handleInputDecision: (status: RuntimeInputStatus, value?: string) => void;

    // Internal actions for socket events
    _onUserMessage: (msg: string) => void;
    _onNewToken: (token: string) => void;
    _onTaskStarted: () => void;
    _onTaskFinished: () => void;
    _onTaskCancelled: () => void;
    _onFatalError: (data: unknown) => void;
    _onReset: () => void;
    _onRequestConfirmation: (data: ConfirmationRequest) => void;
    _onRequestUserInput: (data: UserInputRequest) => void;
    _onToolStateUpdate: (state: ToolState) => void;
    _onToolPlanUpdated: (data: string[] | { plan?: string[] }) => void;
    _onStageStarted: (data: { stage_index: number }) => void;
    _onStageCompleted: (data: { stage_index: number }) => void;
}

// ============================================================================
// Store
// ============================================================================

export const useAppStore = create<AppState & AppActions>((set, get) => ({
    // Initial State
    isChatting: false,
    isProcessing: false,
    isSettingsOpen: false,
    isConnected: false,
    messages: [],
    streamingContent: '',
    pendingConfirmation: null,
    pendingInput: null,
    toolStates: [],
    toolPlan: [],
    currentStageIndex: -1,
    completedStages: [],
    _socket: null,
    _streamingContentRef: '',

    // Setters
    setIsSettingsOpen: (open) => set({ isSettingsOpen: open }),

    // Socket
    getSocket: () => get()._socket,

    initSocket: () => {
        const socket = io('http://localhost:8000', {
            transports: ['websocket'],
            reconnection: true,
        });

        socket.on('connect', () => {
            console.log('Connected to backend');
            set({ isConnected: true });
        });

        socket.on('connect_error', (err) => {
            console.error('Connection failed:', err);
            set({ isConnected: false });
        });

        socket.on('disconnect', (reason) => {
            console.log('Disconnected from backend:', reason);
            set({ isConnected: false });
        });

        // Bind all event handlers
        const actions = get();
        socket.on('user_message', actions._onUserMessage);
        socket.on('llm_new_token', actions._onNewToken);
        socket.on('task_started', actions._onTaskStarted);
        socket.on('task_finished', actions._onTaskFinished);
        socket.on('task_cancelled', actions._onTaskCancelled);
        socket.on('fatal_error', actions._onFatalError);
        socket.on('tool_error', actions._onFatalError);
        socket.on('reset', actions._onReset);
        socket.on('request_confirmation', actions._onRequestConfirmation);
        socket.on('request_user_input', actions._onRequestUserInput);
        socket.on('tool_state_update', actions._onToolStateUpdate);
        socket.on('tool_plan_updated', actions._onToolPlanUpdated);
        socket.on('stage_started', actions._onStageStarted);
        socket.on('stage_completed', actions._onStageCompleted);

        // Window closing
        const handleBeforeUnload = () => socket.emit('window_closing');
        window.addEventListener('beforeunload', handleBeforeUnload);

        set({ _socket: socket });

        // Return cleanup function
        return () => {
            window.removeEventListener('beforeunload', handleBeforeUnload);
            socket.off('user_message', actions._onUserMessage);
            socket.off('llm_new_token', actions._onNewToken);
            socket.off('task_started', actions._onTaskStarted);
            socket.off('task_finished', actions._onTaskFinished);
            socket.off('task_cancelled', actions._onTaskCancelled);
            socket.off('fatal_error', actions._onFatalError);
            socket.off('tool_error', actions._onFatalError);
            socket.off('reset', actions._onReset);
            socket.off('request_confirmation', actions._onRequestConfirmation);
            socket.off('request_user_input', actions._onRequestUserInput);
            socket.off('tool_state_update', actions._onToolStateUpdate);
            socket.off('tool_plan_updated', actions._onToolPlanUpdated);
            socket.off('stage_started', actions._onStageStarted);
            socket.off('stage_completed', actions._onStageCompleted);
            socket.close();
            set({ _socket: null, isConnected: false });
        };
    },

    // Actions
    startTask: (task) => {
        const { _socket } = get();
        if (!_socket) return;
        _socket.emit('start_task', { task });
        set({ isChatting: true, isProcessing: true });
    },

    stopTask: () => {
        const { _socket } = get();
        if (!_socket) return;
        _socket.emit('stop_task');
        set({ isProcessing: false });
    },

    resetSession: () => {
        const { _socket } = get();
        if (!_socket) return;
        _socket.emit('reset_session');
        set({ isChatting: false });
    },

    handleConfirmationDecision: (status) => {
        const { pendingConfirmation } = get();
        if (!pendingConfirmation) return;
        set(state => ({
            messages: [...state.messages, {
                type: 'confirmation',
                role: 'system',
                requestId: pendingConfirmation.request_id,
                command: pendingConfirmation.message,
                status
            }],
            pendingConfirmation: null
        }));
    },

    handleInputDecision: (status, value) => {
        const { pendingInput } = get();
        if (!pendingInput) return;
        set(state => ({
            messages: [...state.messages, {
                type: 'user_input',
                role: 'system',
                requestId: pendingInput.request_id,
                prompt: pendingInput.message,
                result: value || '',
                status
            }],
            pendingInput: null
        }));
    },

    // Socket Event Handlers
    _onUserMessage: (msg) => {
        set(state => ({
            messages: [...state.messages, { type: 'text', role: 'user', content: msg }],
            streamingContent: '',
            _streamingContentRef: '',
            isProcessing: true
        }));
    },

    _onNewToken: (token) => {
        set(state => {
            const newContent = state.streamingContent + token;
            return {
                streamingContent: newContent,
                _streamingContentRef: newContent
            };
        });
    },

    _onTaskStarted: () => {
        set({ isProcessing: true });
    },

    _onTaskFinished: () => {
        set(state => {
            const content = state._streamingContentRef;
            const newMessages = [...state.messages];
            if (content) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content)) {
                    newMessages.push({ type: 'text', role: 'assistant', content });
                }
            }
            newMessages.push({ type: 'status', role: 'system', variant: 'completed' });
            return {
                messages: newMessages,
                streamingContent: '',
                _streamingContentRef: '',
                isProcessing: false
            };
        });
    },

    _onTaskCancelled: () => {
        set(state => {
            const content = state._streamingContentRef;
            const newMessages = [...state.messages];
            if (content) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content)) {
                    newMessages.push({ type: 'text', role: 'assistant', content });
                }
            }
            newMessages.push({ type: 'status', role: 'system', variant: 'cancelled' });

            // Mark last running tool as error
            const updatedToolStates = [...state.toolStates];
            if (updatedToolStates.length > 0) {
                const lastIdx = updatedToolStates.length - 1;
                if (updatedToolStates[lastIdx].status === 'running') {
                    updatedToolStates[lastIdx] = { ...updatedToolStates[lastIdx], status: 'error' };
                }
            }

            return {
                messages: newMessages,
                streamingContent: '',
                _streamingContentRef: '',
                isProcessing: false,
                toolStates: updatedToolStates
            };
        });
    },

    _onFatalError: (data) => {
        const content = typeof data === 'string'
            ? data
            : (data as { message?: string }).message || JSON.stringify(data);
        set(state => ({
            messages: [...state.messages, { type: 'error', role: 'system', content }],
            isProcessing: false
        }));
    },

    _onReset: () => {
        set({
            messages: [],
            streamingContent: '',
            _streamingContentRef: '',
            isProcessing: false,
            pendingConfirmation: null,
            pendingInput: null,
            toolStates: [],
            toolPlan: [],
            currentStageIndex: -1,
            completedStages: [],
            isChatting: false
        });
    },

    _onRequestConfirmation: (data) => {
        set(state => {
            const content = state._streamingContentRef;
            const newMessages = [...state.messages];
            if (content) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content)) {
                    newMessages.push({ type: 'text', role: 'assistant', content });
                }
            }
            return {
                messages: newMessages,
                streamingContent: '',
                _streamingContentRef: '',
                pendingConfirmation: data
            };
        });
    },

    _onRequestUserInput: (data) => {
        set(state => {
            const content = state._streamingContentRef;
            const newMessages = [...state.messages];
            if (content) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content)) {
                    newMessages.push({ type: 'text', role: 'assistant', content });
                }
            }
            return {
                messages: newMessages,
                streamingContent: '',
                _streamingContentRef: '',
                pendingInput: data
            };
        });
    },

    _onToolStateUpdate: (state) => {
        if (!state) return;
        set(prev => {
            const { run_id } = state;
            if (!run_id) return { toolStates: [...prev.toolStates, state] };
            const idx = prev.toolStates.findIndex(t => t.run_id === run_id);
            if (idx >= 0) {
                const updated = [...prev.toolStates];
                updated[idx] = { ...updated[idx], ...state };
                return { toolStates: updated };
            }
            return { toolStates: [...prev.toolStates, state] };
        });
    },

    _onToolPlanUpdated: (data) => {
        const plan = Array.isArray(data) ? data : (data?.plan || []);
        set({ toolPlan: plan });
    },

    _onStageStarted: (data) => {
        set({ currentStageIndex: data.stage_index });
    },

    _onStageCompleted: (data) => {
        set(state => ({
            completedStages: [...new Set([...state.completedStages, data.stage_index])]
        }));
    }
}));
