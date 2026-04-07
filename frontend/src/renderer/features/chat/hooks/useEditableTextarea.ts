import { useCallback, useLayoutEffect, useRef } from "react";

function resizeTextarea(el: HTMLTextAreaElement) {
  el.style.height = "0px";
  el.style.height = `${el.scrollHeight}px`;
}

export function useEditableTextarea(isEditing: boolean) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const mirrorRef = useRef<HTMLDivElement | null>(null);

  const syncTextareaHeight = useCallback(() => {
    const el = textareaRef.current;
    const mirror = mirrorRef.current;
    if (!el) return;
    if (mirror) {
      const nextHeight = mirror.getBoundingClientRect().height;
      el.style.height = `${nextHeight}px`;
      return;
    }
    resizeTextarea(el);
  }, []);

  useLayoutEffect(() => {
    if (!isEditing || !textareaRef.current) return;
    const el = textareaRef.current;
    syncTextareaHeight();
    el.focus();
    const end = el.value.length;
    el.setSelectionRange(end, end);
  }, [isEditing, syncTextareaHeight]);

  useLayoutEffect(() => {
    if (!isEditing) return;
    syncTextareaHeight();
  }, [isEditing, syncTextareaHeight]);

  const handleTextareaChange = useCallback(
    () => {
      requestAnimationFrame(() => {
        syncTextareaHeight();
      });
    },
    [syncTextareaHeight]
  );

  return {
    textareaRef,
    mirrorRef,
    handleTextareaChange,
  };
}
