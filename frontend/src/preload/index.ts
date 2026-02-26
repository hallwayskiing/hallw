import { electronAPI } from "@electron-toolkit/preload";

import { contextBridge, ipcRenderer } from "electron";

// Custom APIs for renderer
const api = {
  openCdpPage: () => ipcRenderer.invoke("open-cdp-page"),
  resizeCdpWindow: (expand: boolean, headless: boolean = false, userDataDir: string = "") =>
    ipcRenderer.invoke("resize-cdp-window", expand, headless, userDataDir),
  windowMinimize: () => ipcRenderer.send("window-minimize"),
  windowMaximize: () => ipcRenderer.send("window-maximize"),
  windowClose: () => ipcRenderer.send("window-close"),
};

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld("electron", electronAPI);
    contextBridge.exposeInMainWorld("api", api);
  } catch (error) {
    console.error(error);
  }
} else {
  // @ts-expect-error
  window.electron = electronAPI;
  // @ts-expect-error
  window.api = api;
}
