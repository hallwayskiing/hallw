import { useAppStore } from './stores/appStore';
import { useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { InputArea } from './components/InputArea';
import { WelcomeScreen } from './components/WelcomeScreen';
import { Settings } from './components/Settings';

export default function App() {
  const initSocket = useAppStore(s => s.initSocket);

  // Initialize socket on mount
  useEffect(() => {
    return initSocket();
  }, [initSocket]);

  // Select only needed state to minimize re-renders
  const isChatting = useAppStore(s => s.isChatting);
  const isSettingsOpen = useAppStore(s => s.isSettingsOpen);
  const setIsSettingsOpen = useAppStore(s => s.setIsSettingsOpen);
  const startTask = useAppStore(s => s.startTask);
  const resetSession = useAppStore(s => s.resetSession);

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans antialiased selection:bg-primary/20">

      {/* Main Content Area (Left/Center) */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {/* Background Pattern */}
          <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px] pointer-events-none" />

          {isChatting ? <ChatArea /> : <WelcomeScreen onQuickStart={startTask} />}
        </div>

        <InputArea
          onSettingsClick={() => setIsSettingsOpen(true)}
          onBack={resetSession}
        />
      </div>

      {/* Sidebar (Right) - Only show when chatting */}
      {isChatting && <Sidebar className="flex-shrink-0" />}

      {/* Modals */}
      <Settings isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  );
}
