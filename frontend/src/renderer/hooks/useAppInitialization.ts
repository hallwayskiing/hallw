import { useEffect } from "react";

import { useAppStore } from "../store/store";

export function useAppInitialization() {
  const initSocket = useAppStore((s) => s.initSocket);
  const theme = useAppStore((s) => s.theme);

  // Initialize socket on mount
  useEffect(() => {
    return initSocket();
  }, [initSocket]);

  // Apply theme on mount and when theme changes
  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);
}
