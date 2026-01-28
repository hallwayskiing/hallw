import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

interface SocketContextType {
    socket: Socket | null;
    isConnected: boolean;
}

const SocketContext = createContext<SocketContextType | null>(null);

export function SocketProvider({ children }: { children: ReactNode }) {
    const [socket, setSocket] = useState<Socket | null>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // Connect to Python backend (default port 8000)
        const newSocket = io('http://localhost:8000', {
            transports: ['websocket'],
            reconnection: true,
        });

        newSocket.on('connect', () => {
            console.log('Connected to backend');
            setIsConnected(true);
        });

        newSocket.on('connect_error', (err) => {
            console.error('Connection failed:', err);
            setIsConnected(false);
        });

        newSocket.on('disconnect', (reason) => {
            console.log('Disconnected from backend:', reason);
            setIsConnected(false);
        });

        setSocket(newSocket);

        return () => {
            newSocket.close();
        };
    }, []);

    return (
        <SocketContext.Provider value={{ socket, isConnected }}>
            {children}
        </SocketContext.Provider>
    );
}

export function useSocket() {
    return useContext(SocketContext) as SocketContextType;
}
