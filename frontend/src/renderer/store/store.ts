import { create } from "zustand";

import { BottomSlice, createBottomSlice } from "../features/bottom/store/bottomSlice";
import { ChatSlice, createChatSlice } from "../features/chat/store/chatSlice";
import { SettingsSlice, createSettingsSlice } from "../features/settings/store/settingsSlice";
import { SidebarSlice, createSidebarSlice } from "../features/sidebar/store/sidebarSlice";
import { WelcomeSlice, createWelcomeSlice } from "../features/welcome/store/welcomeSlice";
import { SocketSlice, createSocketSlice } from "./slices/socketSlice";
import { UISlice, createUISlice } from "./slices/uiSlice";

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
