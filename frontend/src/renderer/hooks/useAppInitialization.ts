import { useAppStore } from "@store/store";
import { useEffect } from "react";

export function useAppInitialization() {
  const initSocket = useAppStore((s) => s.initSocket);
  const theme = useAppStore((s) => s.theme);

  // Initialize socket on mount
  useEffect(() => {
    return initSocket();
  }, [initSocket]);

  const hideCdpView = useAppStore((s) => s.hideCdpView);
  // Reset CDP view on mount to ensure Electron window is at default size
  useEffect(() => {
    hideCdpView();
  }, [hideCdpView]);

  // Apply theme on mount and when theme changes
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);
}
