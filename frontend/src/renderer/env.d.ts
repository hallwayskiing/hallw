export {};

declare global {
  interface Window {
    electron: import("@electron-toolkit/preload").ElectronAPI;
    api: {
      openCdpPage: () => Promise<void>;
      cdpCreateOrShow: (sessionId: string, headless?: boolean, userDataDir?: string) => Promise<boolean>;
      cdpHide: () => Promise<boolean>;
      cdpDestroy: (sessionId: string) => Promise<boolean>;
      windowMinimize: () => void;
      windowMaximize: () => void;
      windowClose: () => void;
    };
  }
}
