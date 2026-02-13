import { StateCreator } from 'zustand';
import { AppState } from '@store/store';

export interface BottomSlice {
    input: string;
    setInput: (input: string) => void;
    submitInput: () => void;
}

export const createBottomSlice: StateCreator<AppState, [], [], BottomSlice> = (set, get) => ({
    input: '',
    setInput: (input) => set({ input }),
    submitInput: () => {
        const { input, _socket } = get();
        if (!input.trim() || !_socket) return;
        _socket.emit('start_task', { task: input });
        set({ input: '' });
    },
});
