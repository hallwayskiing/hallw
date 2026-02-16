import { create } from "zustand";

import { type BottomSlice, createBottomSlice } from "../features/bottom/store/bottomSlice";
import { type ChatSlice, createChatSlice } from "../features/chat/store/chatSlice";
import { createSettingsSlice, type SettingsSlice } from "../features/settings/store/settingsSlice";
import { createSidebarSlice, type SidebarSlice } from "../features/sidebar/store/sidebarSlice";
import { createWelcomeSlice, type WelcomeSlice } from "../features/welcome/store/welcomeSlice";
import { createSocketSlice, type SocketSlice } from "./slices/socketSlice";
import { createUISlice, type UISlice } from "./slices/uiSlice";

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
