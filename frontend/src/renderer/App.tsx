import { BottomBar } from "@features/bottom";
import { ChatArea } from "@features/chat";
import { Settings } from "@features/settings";
import { Sidebar } from "@features/sidebar";
import { Welcome } from "@features/welcome";
import { useAppStore } from "@store/store";
import { X } from "lucide-react";
import "katex/dist/katex.min.css";

import { useAppInitialization } from "./hooks/useAppInitialization";

export default function App() {
  useAppInitialization();

  const isChatting = useAppStore((s) => s.isChatting);
  const isSettingsOpen = useAppStore((s) => s.isSettingsOpen);
  const showCdpView = useAppStore((s) => s.showCdpView);
  const toggleCdpView = useAppStore((s) => s.toggleCdpView);

  return (
    // Root container: global font, background, overflow control
    <div className="flex h-screen w-full bg-background text-foreground overflow-auto font-sans antialiased selection:bg-primary/20">
      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        {/* Content Container: scroll and max-width */}
        <section className="flex-1 overflow-hidden relative">
          <div className="w-full h-full flex flex-col">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-grid-white/[0.02] bg-size-[20px_20px] pointer-events-none" />

            {/* Core View Switching */}
            {!isChatting ? (
              <Welcome />
            ) : (
              <div className="flex w-full h-full relative z-10">
                {/* CDP Webview Split Pane (Left Side) */}
                {showCdpView && (
                  <div className="w-1/2 shrink-0 flex flex-col border-r border-border/10 bg-background/50 shadow-2xl relative animate-in slide-in-from-left duration-300">
                    <div className="h-10 border-b border-border/10 flex items-center justify-between px-4 bg-muted/20 backdrop-blur-md shrink-0">
                      <span className="text-xs font-medium text-muted-foreground flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        Live Task Execution
                      </span>
                      <button
                        type="button"
                        onClick={() => toggleCdpView(false)}
                        className="p-1 hover:bg-muted text-muted-foreground rounded transition-colors"
                        title="Close View"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    {/* The actual web content is drawn here natively by Electron's WebContentsView via IPC */}
                    <div className="w-full h-full flex-1" />
                  </div>
                )}

                {/* Main Chat Area (Right Side if Split) */}
                <div
                  id="chat-viewport"
                  className={`flex-1 h-full flex flex-row relative ${showCdpView ? "max-w-[$var(--center-col)]" : ""}`}
                >
                  <div className="flex-1 min-w-0 h-full">
                    <ChatArea />
                  </div>

                  {/* Sidebar: App controls visibility, Logic internal */}
                  <Sidebar className="h-full shrink-0 border-l border-border/10 shadow-2xl bg-secondary/30" />
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Input Area: Fixed at bottom */}
        <div className={`transition-all duration-300 ${showCdpView ? "pl-[50%]" : ""}`}>
          <BottomBar />
        </div>
      </main>

      {/* Global Modals */}
      <Settings isOpen={isSettingsOpen} />
    </div>
  );
}
