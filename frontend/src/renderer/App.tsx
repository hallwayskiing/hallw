import { BottomBar } from "@features/bottom";
import { TitleBar } from "@features/titlebar";
import { Welcome } from "@features/welcome";
import { useAppStore } from "@store/store";
import { lazy, Suspense } from "react";

import { useAppInitialization } from "./hooks/useAppInitialization";

// Lazy load heavy components
const ChatArea = lazy(() => import("@features/chat").then((m) => ({ default: m.ChatArea })));
const Settings = lazy(() => import("@features/settings").then((m) => ({ default: m.Settings })));
const Sidebar = lazy(() => import("@features/sidebar").then((m) => ({ default: m.Sidebar })));

export default function App() {
  useAppInitialization();

  const isChatting = useAppStore((s) => s.isChatting);
  const isSettingsOpen = useAppStore((s) => s.isSettingsOpen);
  const showCdpView = useAppStore((s) => s.showCdpView);

  return (
    // Root container: global font, background, overflow control
    <div className="relative h-screen w-full bg-background text-foreground overflow-hidden font-sans antialiased selection:bg-primary/20">
      <TitleBar />
      {/* Main Content Area */}
      <main className="h-full flex flex-col min-w-0 relative">
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
                {/* CDP Webview Split Pane */}
                {showCdpView && (
                  <div className="w-1/2 shrink-0 border-r border-border/10 bg-background/50 shadow-2xl" />
                )}

                {/* Main Chat Area */}
                <div
                  id="chat-viewport"
                  className={`flex-1 min-w-0 h-full flex flex-row relative ${showCdpView ? "max-w-[$var(--center-col)]" : ""}`}
                >
                  <div className="flex-1 min-w-0 h-full overflow-hidden">
                    <Suspense fallback={<div className="flex-1 animate-pulse bg-muted/20" />}>
                      <ChatArea />
                    </Suspense>
                  </div>

                  {/* Sidebar: Collapsable at Right Side */}
                  <div className="w-12 shrink-0 border-l border-transparent" />
                  <Suspense fallback={null}>
                    <Sidebar className="absolute top-0 right-0 h-full pt-8 shrink-0 border-l border-border shadow-2xl bg-background z-50" />
                  </Suspense>
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
      <Suspense fallback={null}>
        <Settings isOpen={isSettingsOpen} />
      </Suspense>
    </div>
  );
}
