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

  // Per-session CDP view pool: Map<sessionId, WebContentsView>
  const cdpViews = new Map<string, WebContentsView>();
  let attachedSessionId: string | null = null;
  let unexpandedBounds: Electron.Rectangle | null = null;
  let resizeHandler: (() => void) | null = null;

  /** Detach the currently-attached CDP view from the window (without destroying it). */
  function detachCurrentView(win: BrowserWindow) {
    if (!attachedSessionId) return;
    const view = cdpViews.get(attachedSessionId);
    if (view) {
      try {
        win.contentView.removeChildView(view);
      } catch {}
    }
    // Remove resize listener
    if (resizeHandler) {
      win.removeListener("resize", resizeHandler);
      resizeHandler = null;
    }
    attachedSessionId = null;
  }

  /** Restore the main window to its pre-expansion size. */
  function restoreWindowBounds(win: BrowserWindow) {
    if (unexpandedBounds) {
      win.setBounds(unexpandedBounds, true);
      unexpandedBounds = null;
    } else {
      const bounds = win.getBounds();
      if (bounds.width > 1080) {
        win.setBounds(
          { x: bounds.x + Math.floor(bounds.width / 4), y: bounds.y, width: 1080, height: bounds.height },
          true
        );
      }
    }
  }

  /** Attach a view to the window and expand the window for split-pane layout. */
  function attachView(win: BrowserWindow, sessionId: string, view: WebContentsView) {
    // Detach any currently-attached view first
    detachCurrentView(win);

    unexpandedBounds = unexpandedBounds || win.getBounds();
    const widthPerPane = unexpandedBounds.width;
    const expandedWidth = widthPerPane * 2;

    win.setBounds(
      {
        x: unexpandedBounds.x - Math.floor(widthPerPane / 2),
        y: unexpandedBounds.y,
        width: expandedWidth,
        height: unexpandedBounds.height,
      },
      true
    );

    win.contentView.addChildView(view);
    const topOffset = 32;
    view.setBounds({
      x: 0,
      y: topOffset,
      width: widthPerPane,
      height: unexpandedBounds.height - topOffset,
    });

    // Keep CDP view sized when window resizes
    resizeHandler = () => {
      if (!win.isDestroyed() && view && !view.webContents.isDestroyed()) {
        const curBounds = win.getBounds();
        view.setBounds({
          x: 0,
          y: topOffset,
          width: Math.floor(curBounds.width / 2),
          height: curBounds.height - topOffset,
        });
      }
    };
    win.on("resize", resizeHandler);

    attachedSessionId = sessionId;
  }

  // --- IPC: Create or show a CDP view for a session ---
  ipcMain.handle(
    "cdp-create-or-show",
    async (event, sessionId: string, headless: boolean = false, userDataDir: string = "") => {
      const window = BrowserWindow.fromWebContents(event.sender);
      if (!window) return false;

      let view = cdpViews.get(sessionId);
      const isNew = !view;

      if (!view) {
        // Create a brand-new view for this session
        const ses = userDataDir
          ? session.fromPath(resolve(app.getPath("userData"), userDataDir))
          : session.defaultSession;

        view = new WebContentsView({
          webPreferences: { session: ses, devTools: !headless },
        });

        cdpViews.set(sessionId, view);
      }

      // Attach BEFORE loading so the view is discoverable via CDP
      if (!headless) {
        attachView(window, sessionId, view);
      }

      // Initialize page only on first creation
      if (isNew) {
        await view.webContents.loadURL("about:blank");
        await view.webContents.executeJavaScript("window.__IS_AGENT_VIEW__ = true;");
      }

      return true;
    }
  );

  // --- IPC: Hide the currently-attached CDP view (no destruction) ---
  ipcMain.handle("cdp-hide", async (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (!window) return false;

    detachCurrentView(window);
    restoreWindowBounds(window);

    return true;
  });

  // --- IPC: Destroy a specific session's CDP view ---
  ipcMain.handle("cdp-destroy", async (event, sessionId: string) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    if (!window) return false;

    // If this session's view is currently attached, detach first
    if (attachedSessionId === sessionId) {
      detachCurrentView(window);
      restoreWindowBounds(window);
    }

    const view = cdpViews.get(sessionId);
    if (view) {
      try {
        if (!view.webContents.isDestroyed()) {
          view.webContents.close();
        }
      } catch {}
      cdpViews.delete(sessionId);
    }

    return true;
  });

  // Clean up all views when the window is closed
  app.on("browser-window-created", (_, win) => {
    win.on("closed", () => {
      for (const view of cdpViews.values()) {
        try {
          if (!view.webContents.isDestroyed()) view.webContents.close();
        } catch {}
      }
      cdpViews.clear();
      attachedSessionId = null;
      unexpandedBounds = null;
      resizeHandler = null;
    });
  });

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
