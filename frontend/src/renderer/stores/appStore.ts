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
    reasoning?: string;
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

export interface HistoryItem {
    id: string;
    title?: string;
    created_at?: string;
    metadata?: Record<string, any>;
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
    theme: 'dark' | 'light';

    // Chat State
    messages: Message[];
    streamingContent: string;
    streamingReasoning: string;
    pendingConfirmation: ConfirmationRequest | null;
    pendingInput: UserInputRequest | null;

    // Sidebar State
    toolStates: ToolState[];
    stages: string[];
    currentStageIndex: number;
    completedStages: number[];
    errorStageIndex: number;


    // History State
    history: HistoryItem[];
    isHistoryOpen: boolean;
    currentHistoryId: string | null;

    // Internal
    _socket: Socket | null;
    _streamingContentRef: string;
}

interface AppActions {
    // Setters
    setIsSettingsOpen: (open: boolean) => void;
    toggleTheme: () => void;

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
    _onNewReasoning: (reasoning: string) => void;
    _onNewText: (text: string) => void;
    _onTaskStarted: () => void;
    _onTaskFinished: () => void;
    _onTaskCancelled: () => void;
    _onFatalError: (data: unknown) => void;
    _onReset: () => void;
    _onRequestConfirmation: (data: ConfirmationRequest) => void;
    _onRequestUserInput: (data: UserInputRequest) => void;
    _onToolStateUpdate: (state: ToolState) => void;
    _onStagesBuilt: (data: string[] | { stages?: string[] }) => void;
    _onStageStarted: (data: { stage_index: number }) => void;
    _onStagesCompleted: (data: { stage_indices: number[] }) => void;

    // History Actions/Events
    toggleHistory: () => void;
    fetchHistory: () => void;
    loadHistory: (id: string) => void;
    deleteHistory: (id: string) => void;
    _onHistoryList: (list: HistoryItem[]) => void;
    _onHistoryLoaded: (data: { messages: any[], thread_id: string, toolStates?: ToolState[] }) => void;
    _onHistoryDeleted: (data: { thread_id: string }) => void;
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
    theme: (localStorage.getItem('theme') as 'dark' | 'light') || 'dark',
    messages: [],
    streamingContent: '',
    streamingReasoning: '',
    pendingConfirmation: null,
    pendingInput: null,
    toolStates: [],
    stages: [],
    currentStageIndex: -1,
    completedStages: [],
    errorStageIndex: -1,
    history: [],
    isHistoryOpen: false,
    currentHistoryId: null,
    _socket: null,
    _streamingContentRef: '',

    // Setters
    setIsSettingsOpen: (open) => set({ isSettingsOpen: open }),

    toggleTheme: () => {
        set(state => {
            const newTheme = state.theme === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', newTheme);
            document.documentElement.classList.toggle('dark', newTheme === 'dark');
            return { theme: newTheme };
        });
    },

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
        socket.on('llm_new_reasoning', actions._onNewReasoning);
        socket.on('llm_new_text', actions._onNewText);
        socket.on('task_started', actions._onTaskStarted);
        socket.on('task_finished', actions._onTaskFinished);
        socket.on('task_cancelled', actions._onTaskCancelled);
        socket.on('fatal_error', actions._onFatalError);
        socket.on('tool_error', actions._onFatalError);
        socket.on('reset', actions._onReset);
        socket.on('request_confirmation', actions._onRequestConfirmation);
        socket.on('request_user_input', actions._onRequestUserInput);
        socket.on('tool_state_update', actions._onToolStateUpdate);
        socket.on('stages_built', actions._onStagesBuilt);
        socket.on('stage_started', actions._onStageStarted);
        socket.on('stages_completed', actions._onStagesCompleted);
        socket.on('history_list', actions._onHistoryList);
        socket.on('history_loaded', actions._onHistoryLoaded);
        socket.on('history_deleted', actions._onHistoryDeleted);

        set({ _socket: socket });

        // Return cleanup function
        return () => {
            socket.off('user_message', actions._onUserMessage);
            socket.off('llm_new_reasoning', actions._onNewReasoning);
            socket.off('llm_new_text', actions._onNewText);
            socket.off('task_started', actions._onTaskStarted);
            socket.off('task_finished', actions._onTaskFinished);
            socket.off('task_cancelled', actions._onTaskCancelled);
            socket.off('fatal_error', actions._onFatalError);
            socket.off('tool_error', actions._onFatalError);
            socket.off('reset', actions._onReset);
            socket.off('request_confirmation', actions._onRequestConfirmation);
            socket.off('request_user_input', actions._onRequestUserInput);
            socket.off('tool_state_update', actions._onToolStateUpdate);
            socket.off('stages_built', actions._onStagesBuilt);
            socket.off('stage_started', actions._onStageStarted);
            socket.off('stages_completed', actions._onStagesCompleted);
            socket.off('history_list', actions._onHistoryList);
            socket.off('history_loaded', actions._onHistoryLoaded);
            socket.off('history_deleted', actions._onHistoryDeleted);
            socket.close();
            set({ _socket: null, isConnected: false });
        };
    },

    // Actions
    startTask: (task) => {
        const { _socket } = get();
        if (!_socket) return;
        set({
            isChatting: true,
            isProcessing: true,
            streamingContent: '',
            streamingReasoning: '',
            pendingConfirmation: null,
            pendingInput: null,
            stages: [],
            currentStageIndex: -1,
            completedStages: [],
            errorStageIndex: -1,
            _streamingContentRef: '',
        });
        _socket.emit('start_task', { task });
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
        set({
            isChatting: false,
            isProcessing: false,
            // Force Clear State
            messages: [],
            streamingContent: '',
            streamingReasoning: '',
            pendingConfirmation: null,
            pendingInput: null,
            toolStates: [],
            stages: [],
            currentStageIndex: -1,
            completedStages: [],
            errorStageIndex: -1,
            _streamingContentRef: '',
        });
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

    _onNewReasoning: (reasoning) => {
        set(state => ({
            streamingReasoning: state.streamingReasoning + reasoning
        }));
    },

    _onNewText: (text) => {
        set(state => {
            const newContent = state.streamingContent + text;
            return {
                streamingContent: newContent,
                _streamingContentRef: newContent
            };
        });
    },

    _onTaskStarted: () => {
        set({
            isProcessing: true,
            // Reset sidebar state for new task
            stages: [],
            currentStageIndex: -1,
            completedStages: [],
            errorStageIndex: -1
        });
    },

    _onTaskFinished: () => {
        set(state => {
            const content = state._streamingContentRef;
            const newMessages = [...state.messages];
            const reasoning = state.streamingReasoning;

            if (content || reasoning) {
                const last = state.messages[state.messages.length - 1];
                // Avoid duplicating the message if it's already the last one
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content && last.reasoning === reasoning)) {
                    newMessages.push({
                        type: 'text',
                        role: 'assistant',
                        content,
                        reasoning
                    });
                }
            }
            newMessages.push({ type: 'status', role: 'system', variant: 'completed' });
            return {
                messages: newMessages,
                streamingContent: '',
                streamingReasoning: '',
                _streamingContentRef: '',
                isProcessing: false
            };
        });
    },

    _onTaskCancelled: () => {
        set(state => {
            if (!state.isChatting) return {}; // Ignore if user already left

            const content = state._streamingContentRef;
            const newMessages = [...state.messages];
            const reasoning = state.streamingReasoning;

            if (content || reasoning) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content && last.reasoning === reasoning)) {
                    newMessages.push({
                        type: 'text',
                        role: 'assistant',
                        content,
                        reasoning
                    });
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
                streamingReasoning: '',
                _streamingContentRef: '',
                isProcessing: false,
                toolStates: updatedToolStates,
                errorStageIndex: state.currentStageIndex
            };
        });
    },

    _onFatalError: (data) => {
        const content = typeof data === 'string'
            ? data
            : (data as { message?: string }).message || JSON.stringify(data);
        set(state => {
            const newMessages = [...state.messages];

            // Flush any pending streaming content
            const pendingContent = state._streamingContentRef;
            const pendingReasoning = state.streamingReasoning;

            if (pendingContent || pendingReasoning) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === pendingContent && last.reasoning === pendingReasoning)) {
                    newMessages.push({
                        type: 'text',
                        role: 'assistant',
                        content: pendingContent,
                        reasoning: pendingReasoning
                    });
                }
            }

            // Mark last running tool as error
            const updatedToolStates = [...state.toolStates];
            if (updatedToolStates.length > 0) {
                const lastIdx = updatedToolStates.length - 1;
                if (updatedToolStates[lastIdx].status === 'running') {
                    updatedToolStates[lastIdx] = { ...updatedToolStates[lastIdx], status: 'error' };
                }
            }

            return {
                messages: [...newMessages, { type: 'error', role: 'system', content }],
                streamingContent: '',
                streamingReasoning: '',
                _streamingContentRef: '',
                isProcessing: false,
                toolStates: updatedToolStates,
                errorStageIndex: state.currentStageIndex
            };
        });
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
            stages: [],
            currentStageIndex: -1,
            completedStages: [],
            errorStageIndex: -1,
            isChatting: false
        });
    },

    _onRequestConfirmation: (data) => {
        set(state => {
            const content = state._streamingContentRef;
            const reasoning = state.streamingReasoning;
            const newMessages = [...state.messages];
            if (content || reasoning) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content && last.reasoning === reasoning)) {
                    newMessages.push({
                        type: 'text',
                        role: 'assistant',
                        content,
                        reasoning
                    });
                }
            }
            return {
                messages: newMessages,
                streamingContent: '',
                streamingReasoning: '',
                _streamingContentRef: '',
                pendingConfirmation: data
            };
        });
    },

    _onRequestUserInput: (data) => {
        set(state => {
            const content = state._streamingContentRef;
            const reasoning = state.streamingReasoning;
            const newMessages = [...state.messages];
            if (content || reasoning) {
                const last = state.messages[state.messages.length - 1];
                if (!(last?.type === 'text' && last.role === 'assistant' && last.content === content && last.reasoning === reasoning)) {
                    newMessages.push({
                        type: 'text',
                        role: 'assistant',
                        content,
                        reasoning
                    });
                }
            }
            return {
                messages: newMessages,
                streamingContent: '',
                streamingReasoning: '',
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

    _onStagesBuilt: (data) => {
        const stages = Array.isArray(data) ? data : (data?.stages || []);
        set({ stages: stages });
    },

    _onStageStarted: (data) => {
        set({ currentStageIndex: data.stage_index });
    },

    _onStagesCompleted: (data: { stage_indices: number[] }) => {
        set(state => ({
            completedStages: [...new Set([...state.completedStages, ...data.stage_indices])]
        }));
    },

    // History Implementation
    toggleHistory: () => {
        set(state => {
            const newState = !state.isHistoryOpen;
            if (newState) {
                get().fetchHistory();
            }
            return { isHistoryOpen: newState };
        });
    },

    fetchHistory: () => {
        const { _socket } = get();
        if (!_socket) return;
        _socket.emit('get_history');
    },

    loadHistory: (id) => {
        const { _socket } = get();
        if (!_socket) return;
        // set({ isProcessing: true }); // Optional: show loading state
        _socket.emit('load_history', { thread_id: id });
    },

    deleteHistory: (id) => {
        // Optimistic update
        set(state => ({
            history: state.history.filter(h => h.id !== id),
            currentHistoryId: state.currentHistoryId === id ? null : state.currentHistoryId
        }));

        const { _socket } = get();
        if (!_socket) return;
        _socket.emit('delete_history', { thread_id: id });
    },

    _onHistoryList: (list) => {
        set({ history: list });
    },

    _onHistoryLoaded: (data) => {
        // Need to cast the raw messages to our Message type if strictly typed,
        // but for now we assume the backend sends compatible structure.
        // Backend sends: {role: 'user'|'assistant'|'system', type: 'text', content, reasoning}
        // Our store expects Message[] which includes type='text' etc.
        // We should map them to ensure type safety if needed, but backend output looks compatible.

        // We also need to set chat active
        set({
            messages: data.messages as Message[],
            currentHistoryId: data.thread_id,
            isChatting: true,
            isProcessing: false,
            // Keep isHistoryOpen as true, we only toggle it manually
            // Clear other transient states
            streamingContent: '',
            streamingReasoning: '',
            _streamingContentRef: '',
            toolStates: data.toolStates || [], // Restore tool states
            stages: [],
            currentStageIndex: -1,
            completedStages: [],
            errorStageIndex: -1
        });
    },

    _onHistoryDeleted: (data) => {
        set(state => ({
            history: state.history.filter(h => h.id !== data.thread_id),
            // If current loaded history is deleted, maybe reset?
            currentHistoryId: state.currentHistoryId === data.thread_id ? null : state.currentHistoryId
        }));
    }
}));
