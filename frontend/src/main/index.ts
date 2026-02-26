import { join, resolve } from "node:path";
import { electronApp, is, optimizer } from "@electron-toolkit/utils";
import { app, BrowserWindow, ipcMain, session, shell, WebContentsView } from "electron";

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 960,
    height: 720,
    icon: join(__dirname, "../../resources/hallw.png"),
    show: false,
    frame: false,
    autoHideMenuBar: true,
    webPreferences: {
      preload: join(__dirname, "../preload/index.js"),
      sandbox: false,
      webviewTag: true,
    },
  });

  mainWindow.on("ready-to-show", () => mainWindow.show());

  // Intercept external links and open them in the default system browser
  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url);
    return { action: "deny" };
  });

  // Load the dev server URL or local static file based on the environment
  if (is.dev && process.env.ELECTRON_RENDERER_URL) {
    mainWindow.loadURL(process.env.ELECTRON_RENDERER_URL);
  } else {
    mainWindow.loadFile(join(__dirname, "../renderer/index.html"));
  }
}

// Enable remote debugging protocol
app.commandLine.appendSwitch("remote-debugging-port", "9222");

app.whenReady().then(() => {
  electronApp.setAppUserModelId("com.electron");

  // Default open/close DevTools by F12 in development
  app.on("browser-window-created", (_, window) => {
    optimizer.watchWindowShortcuts(window);
  });

  ipcMain.on("ping", () => console.log("pong"));

  // Window control IPC handlers for custom title bar
  ipcMain.on("window-minimize", (event) => {
    BrowserWindow.fromWebContents(event.sender)?.minimize();
  });
  ipcMain.on("window-maximize", (event) => {
    const win = BrowserWindow.fromWebContents(event.sender);
    if (win) win.isMaximized() ? win.unmaximize() : win.maximize();
  });
  ipcMain.on("window-close", (event) => {
    BrowserWindow.fromWebContents(event.sender)?.close();
  });

  let cdpView: WebContentsView | null = null;
  let unexpandedBounds: Electron.Rectangle | null = null;

  // Handle expanding, collapsing, and destroying the CDP view
  ipcMain.handle(
    "resize-cdp-window",
    async (event, expand: boolean, headless: boolean = false, userDataDir: string = "") => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (!window) return false;

      const bounds = window.getBounds();

      if (expand) {
        if (!cdpView) {
          const ses = userDataDir
            ? session.fromPath(resolve(app.getPath("userData"), userDataDir))
            : session.defaultSession;

          cdpView = new WebContentsView({
            webPreferences: { session: ses, devTools: !headless },
          });

          if (!headless) {
            unexpandedBounds = window.getBounds();
            const widthPerPane = unexpandedBounds.width;
            const expandedWidth = widthPerPane * 2;

            // Expand the main window
            window.setBounds(
              {
                x: unexpandedBounds.x - Math.floor(widthPerPane / 2),
                y: unexpandedBounds.y,
                width: expandedWidth,
                height: unexpandedBounds.height,
              },
              true
            );

            window.contentView.addChildView(cdpView);
            const titleBarHeight = 32;
            cdpView.setBounds({
              x: 0,
              y: titleBarHeight,
              width: widthPerPane,
              height: unexpandedBounds.height - titleBarHeight,
            });

            // Ensure the CDP view height and width adjusts with the main window
            window.on("resize", () => {
              if (cdpView && !window.isDestroyed()) {
                const curBounds = window.getBounds();
                const tbH = 32;
                cdpView.setBounds({
                  x: 0,
                  y: tbH,
                  width: Math.floor(curBounds.width / 2),
                  height: curBounds.height - tbH,
                });
              }
            });
          }

          // Initialize the CDP page and inject the Playwright marker
          await cdpView.webContents.loadURL("about:blank");
          await cdpView.webContents.executeJavaScript("window.__IS_AGENT_VIEW__ = true;");

          window.on("closed", () => {
            cdpView = null;
            unexpandedBounds = null;
          });
        }
      } else {
        // Remove and destroy the CDP view
        if (cdpView) {
          try {
            window.contentView.removeChildView(cdpView);
            // Destroy the WebContents to ensure the page is actually closed, not just hidden
            if (cdpView.webContents && !cdpView.webContents.isDestroyed()) {
              cdpView.webContents.close();
            }
          } catch {}
          cdpView = null;
        }

        // Restore the main window bounds
        if (!headless) {
          if (unexpandedBounds) {
            window.setBounds(unexpandedBounds, true);
            unexpandedBounds = null;
          } else if (bounds.width > 1080) {
            window.setBounds(
              { x: bounds.x + Math.floor(bounds.width / 4), y: bounds.y, width: 1080, height: bounds.height },
              true
            );
          }
        }
      }
      return true;
    }
  );

  createWindow();

  // Recreate the window on macOS activate if no windows exist
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit when all windows are closed, except on macOS
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
