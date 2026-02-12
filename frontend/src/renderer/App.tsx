import { useAppStore } from './stores/appStore';
import { useEffect } from 'react';
import { Sidebar } from './components/Sidebar/Sidebar';
import { ChatArea } from './components/ChatArea/ChatArea';
import { InputArea } from './components/InputArea/InputArea';
import { WelcomeScreen } from './components/WelcomeScreen/WelcomeScreen';
import { Settings } from './components/Settings/Settings';

export default function App() {
  const initSocket = useAppStore(s => s.initSocket);
  const theme = useAppStore(s => s.theme);

  // Initialize socket on mount
  useEffect(() => {
    return initSocket();
  }, [initSocket]);

  // Apply theme on mount and when theme changes
  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);

  // Select only needed state to minimize re-renders
  const isChatting = useAppStore(s => s.isChatting);
  const isSettingsOpen = useAppStore(s => s.isSettingsOpen);
  const setIsSettingsOpen = useAppStore(s => s.setIsSettingsOpen);
  const startTask = useAppStore(s => s.startTask);
  const resetSession = useAppStore(s => s.resetSession);

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans antialiased selection:bg-primary/20">

      {/* Main Content Area (Center) */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        <div className="flex-1 flex flex-col overflow-hidden relative">
          <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
            <div className="max-w-[1200px] mx-auto w-full h-full flex flex-col relative">

              {/* Background Pattern */}
              <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px] pointer-events-none" />

              {isChatting ? <ChatArea /> : <WelcomeScreen onQuickStart={startTask} />}
            </div>
          </div>
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
