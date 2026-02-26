export {};

declare global {
  interface Window {
    electron: import("@electron-toolkit/preload").ElectronAPI;
    api: {
      openCdpPage: () => Promise<void>;
      resizeCdpWindow: (expand: boolean, headless?: boolean, userDataDir?: string) => Promise<boolean>;
      windowMinimize: () => void;
      windowMaximize: () => void;
      windowClose: () => void;
    };
  }
}
