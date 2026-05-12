import type { AppState } from "@store/store";
import type { StateCreator } from "zustand";

export interface AttachedFile {
  /** Unique ID for UI rendering */
  id: string;
  /** Display name */
  name: string;
  /** Absolute path (local) or null if pending save */
  path: string | null;
  /** File size in bytes */
  size: number;
  /** MIME type if available */
  type: string;
  /** True while saving a dragged/pasted/web-selected file to temp */
  isSaving: boolean;
}

export interface BottomSlice {
  input: string;
  attachedFiles: AttachedFile[];
  setInput: (input: string) => void;
  addFiles: (files: FileList | File[]) => Promise<void>;
  addLocalPaths: (paths: string[]) => void;
  removeFile: (id: string) => void;
  clearFiles: () => void;
  submitInput: () => void;
}

const getDisplayNames = (files: Pick<AttachedFile, "id" | "name" | "path">[]) => {
  const counts = new Map<string, number>();
  const totals = new Map<string, Set<string>>();

  for (const file of files) {
    const paths = totals.get(file.name) ?? new Set<string>();
    paths.add(file.path ?? file.id);
    totals.set(file.name, paths);
  }

  return new Map(
    files.map((file) => {
      const distinctPathCount = totals.get(file.name)?.size ?? 0;
      if (distinctPathCount <= 1) {
        return [file.id, file.name] as const;
      }

      const next = (counts.get(file.name) ?? 0) + 1;
      counts.set(file.name, next);
      return [file.id, `${file.name}(${next})`] as const;
    })
  );
};

export const createBottomSlice: StateCreator<AppState, [], [], BottomSlice> = (set, get) => ({
  input: "",
  attachedFiles: [],

  setInput: (input) => set({ input }),

  /**
   * Handle File objects that must be persisted to a temp path first.
   * Saves them to temp via Electron IPC and stores the resulting path.
   */
  addFiles: async (fileList) => {
    const files = Array.from(fileList);
    if (files.length === 0) return;

    // Create placeholders
    const placeholders: AttachedFile[] = files.map((f) => ({
      id: crypto.randomUUID(),
      name: f.name,
      path: null,
      size: f.size,
      type: f.type,
      isSaving: true,
    }));

    set((state) => ({ attachedFiles: [...state.attachedFiles, ...placeholders] }));

    // Save each file to temp via IPC
    const saveTempFile = window.api?.saveTempFile;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const placeholder = placeholders[i];

      try {
        let savedPath: string;

        if (saveTempFile) {
          // Electron environment: save via main process IPC
          const buffer = await file.arrayBuffer();
          savedPath = await saveTempFile(file.name, buffer);
        } else {
          // Fallback: shouldn't happen in Electron context
          console.warn("saveTempFile IPC not available");
          set((state) => ({
            attachedFiles: state.attachedFiles.filter((f) => f.id !== placeholder.id),
          }));
          continue;
        }

        // Preserve the original display name; only the backing path changes.
        set((state) => ({
          attachedFiles: state.attachedFiles.map((f) =>
            f.id === placeholder.id
              ? { ...f, name: savedPath.split(/[\\/]/).pop() || savedPath, path: savedPath, isSaving: false }
              : f
          ),
        }));
      } catch (err) {
        console.error("Failed to save temp file:", err);
        set((state) => ({
          attachedFiles: state.attachedFiles.filter((f) => f.id !== placeholder.id),
        }));
      }
    }
  },

  /**
   * Handle directly-selected local file paths.
   */
  addLocalPaths: (paths) => {
    const newFiles: AttachedFile[] = paths.map((p) => {
      const name = p.split(/[\\/]/).pop() || p;
      return {
        id: crypto.randomUUID(),
        name,
        path: p,
        size: 0,
        type: "",
        isSaving: false,
      };
    });
    set((state) => ({ attachedFiles: [...state.attachedFiles, ...newFiles] }));
  },

  removeFile: (id) => {
    set((state) => ({ attachedFiles: state.attachedFiles.filter((f) => f.id !== id) }));
  },

  clearFiles: () => set({ attachedFiles: [] }),

  submitInput: () => {
    const { input, attachedFiles, startTask, addRecentModelLocal, config } = get();
    const hasSavingFiles = attachedFiles.some((f) => f.isSaving);
    if (hasSavingFiles) return; // Wait for files to finish saving
    if (!input.trim() && attachedFiles.length === 0) return;

    const readyFiles = attachedFiles.filter((f) => f.path !== null);
    const displayNames = getDisplayNames(readyFiles);
    const filePaths = readyFiles.map((f) => f.path as string);
    const fileDisplayNames = readyFiles.map((f) => displayNames.get(f.id) ?? f.name);
    const modelName = typeof config.model_name === "string" ? config.model_name : "";

    addRecentModelLocal(modelName);
    startTask(input, filePaths, fileDisplayNames);
    set({ input: "", attachedFiles: [] });
  },
});
