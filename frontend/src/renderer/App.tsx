import { BottomBar } from "@features/bottom";
import { ChatArea } from "@features/chat";
import { Settings } from "@features/settings";
import { Sidebar } from "@features/sidebar";
import { Welcome } from "@features/welcome";
import { useAppStore } from "@store/store";
import "katex/dist/katex.min.css";

import { useAppInitialization } from "./hooks/useAppInitialization";

export default function App() {
  useAppInitialization();

  const { isChatting, isSettingsOpen } = useAppStore();

  return (
    // Root container: global font, background, overflow control
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans antialiased selection:bg-primary/20">
      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        {/* Content Container: scroll and max-width */}
        <section className="flex-1 overflow-hidden relative">
          <div className="w-full h-full flex flex-col">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-grid-white/[0.02] bg-size-[20px_20px] pointer-events-none" />

            {/* Core View Switching */}
            {isChatting ? <ChatArea /> : <Welcome />}
          </div>
        </section>

        {/* Input Area: Fixed at bottom */}
        <BottomBar />
      </main>

      {/* Sidebar: App controls visibility, Logic internal */}
      {isChatting && (
        <div className="absolute right-0 top-0 bottom-0 z-40 bg-background/95 backdrop-blur supports-backdrop-filter:bg-background/60">
          <Sidebar className="h-full shrink-0 border-l border-border/10 shadow-2xl" />
        </div>
      )}

      {/* Global Modals */}
      <Settings isOpen={isSettingsOpen} />
    </div>
  );
}
