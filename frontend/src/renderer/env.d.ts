export {};

declare global {
  interface Window {
    electron: import("@electron-toolkit/preload").ElectronAPI;
    api: {
      openCdpPage: () => Promise<void>;
      pickFiles: () => Promise<string[]>;
      cdpCreateOrShow: (sessionId: string, headless?: boolean, userDataDir?: string) => Promise<boolean>;
      cdpHide: () => Promise<boolean>;
      cdpDestroy: (sessionId: string) => Promise<boolean>;
      saveTempFile: (fileName: string, buffer: ArrayBuffer) => Promise<string>;
      windowMinimize: () => void;
      windowMaximize: () => void;
      windowClose: () => void;
    };
  }
}
