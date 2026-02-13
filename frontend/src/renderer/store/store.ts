import { create } from 'zustand';
import { createBottomSlice, BottomSlice } from '../features/bottom/store/bottomSlice';
import { createChatSlice, ChatSlice } from '../features/chat/store/chatSlice';
import { createSettingsSlice, SettingsSlice } from '../features/settings/store/settingsSlice';
import { createSidebarSlice, SidebarSlice } from '../features/sidebar/store/sidebarSlice';
import { createWelcomeSlice, WelcomeSlice } from '../features/welcome/store/welcomeSlice';
import { createSocketSlice, SocketSlice } from './slices/socketSlice';
import { createUISlice, UISlice } from './slices/uiSlice';

export type AppState = BottomSlice & ChatSlice & SettingsSlice & SidebarSlice & WelcomeSlice & SocketSlice & UISlice;

export const useAppStore = create<AppState>((...a) => ({
    ...createBottomSlice(...a),
    ...createChatSlice(...a),
    ...createSettingsSlice(...a),
    ...createSidebarSlice(...a),
    ...createWelcomeSlice(...a),
    ...createSocketSlice(...a),
    ...createUISlice(...a),
}));
