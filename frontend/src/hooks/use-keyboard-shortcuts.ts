"use client";

import { useEffect } from "react";

export function useKeyboardShortcuts(
  shortcuts: Record<string, () => void>
): void {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const modifierKey = e.ctrlKey || e.metaKey ? "cmd+" : "";
      const shiftKey = e.shiftKey ? "shift+" : "";
      const key = `${modifierKey}${shiftKey}${e.key.toLowerCase()}`;

      if (shortcuts[key]) {
        e.preventDefault();
        shortcuts[key]();
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [shortcuts]);
}
