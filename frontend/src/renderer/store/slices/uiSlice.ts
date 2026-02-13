import { StateCreator } from 'zustand';
import { AppState } from '@store/store';

export interface UISlice {
    theme: 'light' | 'dark';
    isSettingsOpen: boolean;
    isChatting: boolean;
    setTheme: (theme: 'light' | 'dark') => void;
    toggleTheme: () => void;
    toggleSettings: () => void;
    setIsChatting: (isChatting: boolean) => void;
}

export const createUISlice: StateCreator<AppState, [], [], UISlice> = (set) => ({
    theme: 'dark',
    isSettingsOpen: false,
    isChatting: false,
    setTheme: (theme) => set({ theme }),
    toggleTheme: () => set((state) => {
        const newTheme = state.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        document.documentElement.classList.toggle('dark', newTheme === 'dark');
        return { theme: newTheme };
    }),
    toggleSettings: () => set((state) => ({ isSettingsOpen: !state.isSettingsOpen })),
    setIsChatting: (isChatting) => set({ isChatting }),
});
