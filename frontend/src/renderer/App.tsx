import { useState, useEffect } from 'react';
import { SocketProvider, useSocket } from './contexts/SocketContext';
import { Sidebar } from './components/Sidebar';
import { ChatArea } from './components/ChatArea';
import { InputArea } from './components/InputArea';
import { WelcomeScreen } from './components/WelcomeScreen';
import { SettingsModal } from './components/SettingsModal';

export default function App() {
  return (
    <SocketProvider>
      <AppContent />
    </SocketProvider>
  );
}

function AppContent() {
  const { socket } = useSocket();
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  useEffect(() => {
    const handleBeforeUnload = (event: BeforeUnloadEvent) => {
      if (socket) {
        socket.emit('window_closing');
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [socket]);

  // Auto-switch from Welcome to Chat when task starts
  socket?.on('user_message', () => setHasStarted(true));

  const handleQuickStart = (text: string) => {
    socket?.emit('start_task', { task: text });
    setHasStarted(true);
  };

  const handleBack = () => {
    setHasStarted(false);
    socket?.emit('reset_session');
  };

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans antialiased selection:bg-primary/20">

      {/* Main Content Area (Left/Center) */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        <div className="flex-1 flex flex-col overflow-hidden relative">
          {/* Background Pattern */}
          <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:20px_20px] pointer-events-none" />

          {hasStarted ? <ChatArea /> : <WelcomeScreen onQuickStart={handleQuickStart} />}
        </div>

        <InputArea
          onSettingsClick={() => setIsSettingsOpen(true)}
          onStartTask={() => setHasStarted(true)}
          hasStarted={hasStarted}
          onBack={handleBack}
        />
      </div>

      {/* Sidebar (Right) */}
      <Sidebar className="flex-shrink-0" />

      {/* Modals */}
      <SettingsModal isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />
    </div>
  );
}
