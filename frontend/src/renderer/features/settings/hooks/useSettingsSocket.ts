import type { AppState } from "@store/store";
import { useAppStore } from "@store/store";
import { useCallback, useEffect, useMemo } from "react";

function debounce<T extends (...args: never[]) => void>(fn: T, ms: number) {
  let timer: ReturnType<typeof setTimeout> | null = null;

  const debounced = (...args: Parameters<T>) => {
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => fn(...args), ms);
  };

  debounced.cancel = () => {
    if (timer) clearTimeout(timer);
  };

  return debounced;
}

export function useSettingsSocket(isOpen: boolean) {
  const config = useAppStore((state) => state.config);
  const isLoading = useAppStore((state) => state.isLoading);
  const updateConfigLocal = useAppStore((state) => state.updateConfigLocal);
  const _socket = useAppStore((state) => state._socket);

  useEffect(() => {
    if (isOpen && _socket) {
      _socket.emit("get_config");
    }
  }, [isOpen, _socket]);

  const debouncedSave = useMemo(
    () =>
      debounce(() => {
        const state: AppState = useAppStore.getState();
        if (state._socket) {
          state.setSaveStatus("saving");
          state._socket.emit("update_config", state.config);
        }
      }, 500),
    []
  );

  useEffect(() => {
    if (!isOpen) debouncedSave.cancel();
    return () => debouncedSave.cancel();
  }, [isOpen, debouncedSave]);

  const handleChange = useCallback(
    (key: string, value: unknown) => {
      updateConfigLocal(key, value);
      debouncedSave();
    },
    [updateConfigLocal, debouncedSave]
  );

  return { config, isLoading, handleChange };
}
