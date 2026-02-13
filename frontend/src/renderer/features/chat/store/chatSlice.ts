import { StateCreator } from 'zustand';
import { Message, ConfirmationRequest, UserInputRequest, ConfirmationStatus, RuntimeInputStatus } from '../types';
import { AppState } from '@store/store';

export interface ChatSlice {
    messages: Message[];
    isRunning: boolean;
    streamingContent: string;
    streamingReasoning: string;
    pendingConfirmation: ConfirmationRequest | null;
    pendingInput: UserInputRequest | null;
    _streamingContentRef: string;

    getProcessedMessages: (messages: Message[]) => Message[];

    startTask: (task: string) => void;
    stopTask: () => void;
    resetSession: () => void;
    handleConfirmationDecision: (status: ConfirmationStatus) => void;
    handleInputDecision: (status: RuntimeInputStatus, value?: string) => void;

    _onChatUserMessage: (msg: string) => void;
    _onChatNewReasoning: (reasoning: string) => void;
    _onChatNewText: (text: string) => void;
    _onChatTaskStarted: () => void;
    _onChatTaskFinished: () => void;
    _onChatTaskCancelled: () => void;
    _onChatFatalError: (data: unknown) => void;
    _onChatReset: () => void;
    _onChatHistoryLoaded: (data: { messages: Message[] }) => void;
    _onChatRequestConfirmation: (data: ConfirmationRequest) => void;
    _onChatRequestUserInput: (data: UserInputRequest) => void;
}

export const createChatSlice: StateCreator<AppState, [], [], ChatSlice> = (set, get) => ({
    messages: [],
    isRunning: false,
    streamingContent: '',
    streamingReasoning: '',
    pendingConfirmation: null,
    pendingInput: null,
    _streamingContentRef: '',

    getProcessedMessages: (messages: Message[]) => {
        const result: Message[] = [];
        let reasoningBuffer: string[] = [];

        for (const msg of messages) {
            const isReasoningOnly = msg.type === 'text' && !msg.content?.trim() && !!msg.reasoning;
            const isAssistantContentMsg = msg.type === 'text' && msg.role === 'assistant' && !!msg.content?.trim();

            if (isReasoningOnly) {
                if (msg.reasoning) reasoningBuffer.push(msg.reasoning);
            } else if (isAssistantContentMsg) {
                const combinedReasoning = [...reasoningBuffer, msg.reasoning].filter(Boolean).join('\n\n');
                result.push({ ...msg, reasoning: combinedReasoning || undefined });
                reasoningBuffer = [];
            } else {
                if (reasoningBuffer.length > 0) {
                    result.push({
                        type: 'text',
                        role: 'assistant',
                        content: '',
                        reasoning: reasoningBuffer.join('\n\n')
                    });
                    reasoningBuffer = [];
                }
                result.push(msg);
            }
        }

        if (reasoningBuffer.length > 0) {
            let merged = false;
            for (let i = result.length - 1; i >= 0; i--) {
                const msg = result[i];
                if (msg.type === 'text' && msg.role === 'assistant' && !!msg.content?.trim()) {
                    result[i] = { ...msg, reasoning: [msg.reasoning, ...reasoningBuffer].filter(Boolean).join('\n\n') || undefined };
                    merged = true;
                    break;
                }
            }
            if (!merged) {
                result.push({ type: 'text', role: 'assistant', content: '', reasoning: reasoningBuffer.join('\n\n') });
            }
        }
        return result;
    },


    startTask: (task) => {
        const { _socket } = get();
        if (!_socket) return;
        set({
            isRunning: true,
            streamingContent: '',
            streamingReasoning: '',
            pendingConfirmation: null,
            pendingInput: null,
            _streamingContentRef: '',
        });
        _socket.emit('start_task', { task });
    },

    stopTask: () => {
        const { _socket } = get();
        if (!_socket) return;
        _socket.emit('stop_task');
        set({ isRunning: false });
    },

    resetSession: () => {
        const { _socket } = get();
        if (!_socket) return;
        _socket.emit('reset_session');
        set({
            isRunning: false,
            messages: [],
            streamingContent: '',
            streamingReasoning: '',
            pendingConfirmation: null,
            pendingInput: null,
            _streamingContentRef: '',
        });
    },

    handleConfirmationDecision: (status) => {
        const { pendingConfirmation, _socket } = get();
        if (!pendingConfirmation) return;

        if (_socket) {
            _socket.emit('resolve_confirmation', {
                request_id: pendingConfirmation.requestId,
                status
            });
        }

        set((state: ChatSlice) => ({
            messages: [...state.messages, {
                type: 'confirmation',
                role: 'system',
                requestId: pendingConfirmation.requestId,
                command: pendingConfirmation.message,
                status
            }],
            pendingConfirmation: null
        }));
    },

    handleInputDecision: (status, value) => {
        const { pendingInput, _socket } = get();
        if (!pendingInput) return;

        if (_socket) {
            _socket.emit('resolve_user_input', {
                request_id: pendingInput.requestId,
                status,
                value: value || ''
            });
        }

        set((state: ChatSlice) => ({
            messages: [...state.messages, {
                type: 'user_input',
                role: 'system',
                requestId: pendingInput.requestId,
                prompt: pendingInput.message,
                result: value || '',
                status
            }],
            pendingInput: null
        }));
    },


    _onChatUserMessage: (msg) => {
        set((state: ChatSlice) => ({
            messages: [...state.messages, { type: 'text', role: 'user', content: msg }],
            streamingContent: '',
            streamingReasoning: '',
            _streamingContentRef: '',
            isRunning: true,
            pendingConfirmation: null,
            pendingInput: null,
        }));
    },

    _onChatNewReasoning: (reasoning) => {
        set((state: ChatSlice) => ({
            streamingReasoning: state.streamingReasoning + reasoning
        }));
    },

    _onChatNewText: (text) => {
        set((state: ChatSlice) => {
            const newContent = state.streamingContent + text;
            return {
                streamingContent: newContent,
                _streamingContentRef: newContent
            };
        });
    },

    _onChatTaskStarted: () => {
        set({
            isRunning: true,
        });
    },

    _onChatTaskFinished: () => {
        set((state: any) => {
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
            newMessages.push({ type: 'status', role: 'system', variant: 'completed' });
            return {
                messages: newMessages,
                streamingContent: '',
                streamingReasoning: '',
                _streamingContentRef: '',
                isRunning: false
            };
        });
    },

    _onChatTaskCancelled: () => {
        set((state: any) => {
            if (!state.isChatting) return {};

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

            return {
                messages: newMessages,
                streamingContent: '',
                streamingReasoning: '',
                _streamingContentRef: '',
                isRunning: false,
            };
        });
    },

    _onChatFatalError: (data: any) => {
        const content = typeof data === 'string'
            ? data
            : (data as { message?: string }).message || JSON.stringify(data);
        set((state: any) => {
            const newMessages = [...state.messages];

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

            return {
                messages: [...newMessages, { type: 'error', role: 'system', content }],
                streamingContent: '',
                streamingReasoning: '',
                _streamingContentRef: '',
                isRunning: false,
            };
        });
    },

    _onChatReset: () => {
        set({
            messages: [],
            streamingContent: '',
            _streamingContentRef: '',
            isRunning: false,
            pendingConfirmation: null,
            pendingInput: null,
        });
    },

    _onChatHistoryLoaded: (data) => {
        set({
            messages: data.messages,
            isRunning: false,
            streamingContent: '',
            streamingReasoning: '',
            _streamingContentRef: '',
        });
    },

    _onChatRequestConfirmation: (data) => {
        set((state: ChatSlice) => {
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
                pendingConfirmation: {
                    requestId: (data as any).request_id ?? data.requestId,
                    message: data.message,
                    timeout: data.timeout
                }
            };
        });
    },

    _onChatRequestUserInput: (data) => {
        set((state: ChatSlice) => {
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
                pendingInput: {
                    requestId: (data as any).request_id ?? data.requestId,
                    message: data.message,
                    timeout: data.timeout
                }
            };
        });
    },
});
