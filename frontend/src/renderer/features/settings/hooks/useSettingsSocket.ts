import { useEffect, useCallback, useMemo } from 'react';
import { useAppStore } from '@store/store';

function debounce<T extends (...args: any[]) => void>(fn: T, ms: number): T & { cancel: () => void } {
    let timer: ReturnType<typeof setTimeout> | null = null;
    const debounced = (...args: any[]) => {
        if (timer) clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
    debounced.cancel = () => { if (timer) clearTimeout(timer); };
    return debounced as T & { cancel: () => void };
}

export function useSettingsSocket(isOpen: boolean) {
    const {
        config,
        isLoading,
        updateConfigLocal,
        _socket
    } = useAppStore();

    // Fetch config when settings opens
    useEffect(() => {
        if (isOpen && _socket) {
            _socket.emit('get_config');
        }
    }, [isOpen, _socket]);

    // Debounced save — emits the latest config from the store
    const debouncedSave = useMemo(
        () => debounce(() => {
            const state = useAppStore.getState();
            if (state._socket) {
                state.setSaveStatus('saving');
                state._socket.emit('update_config', state.config);
            }
        }, 500),
        []
    );

    // Cancel pending save when settings closes or unmounts
    useEffect(() => {
        if (!isOpen) debouncedSave.cancel();
        return () => debouncedSave.cancel();
    }, [isOpen, debouncedSave]);

    // Wrap handleChange: update local state then trigger debounced save
    const handleChange = useCallback((key: string, value: any) => {
        updateConfigLocal(key, value);
        debouncedSave();
    }, [updateConfigLocal, debouncedSave]);

    return {
        config,
        isLoading,
        handleChange
    };
}
