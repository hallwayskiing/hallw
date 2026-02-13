import { useAppStore } from '@store/store';
import { useAppInitialization } from './hooks/useAppInitialization';
import 'katex/dist/katex.min.css';

// Import Feature Modules
import { Sidebar } from '@features/sidebar';
import { ChatArea } from '@features/chat';
import { BottomBar } from '@features/bottom';
import { Welcome } from '@features/welcome';
import { Settings } from '@features/settings';

export default function App() {
  useAppInitialization();

  const { isChatting, isSettingsOpen } = useAppStore();

  return (
    // Root container: global font, background, overflow control
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans antialiased selection:bg-primary/20">

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 relative">

        {/* Content Container: scroll and max-width */}
        <section className="flex-1 overflow-y-auto relative scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          <div className="max-w-[1200px] mx-auto w-full h-full flex flex-col">

            {/* Background Pattern */}
            <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px] pointer-events-none" />

            {/* Core View Switching */}
            {isChatting ? <ChatArea /> : <Welcome />}
          </div>
        </section>

        {/* Input Area: Fixed at bottom */}
        <BottomBar />
      </main>

      {/* Sidebar: App controls visibility, Logic internal */}
      {isChatting && <Sidebar className="flex-shrink-0 border-l border-white/5" />}

      {/* Global Modals */}
      <Settings isOpen={isSettingsOpen} />
    </div>
  );
}
