"use client";

import { useEffect, useRef } from "react";

export function useKeyboardShortcuts(
  shortcuts: Record<string, () => void>
): void {
  const shortcutsRef = useRef(shortcuts);

  // Update the ref when shortcuts change
  useEffect(() => {
    shortcutsRef.current = shortcuts;
  }, [shortcuts]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const modifierKey = e.ctrlKey || e.metaKey ? "cmd+" : "";
      const shiftKey = e.shiftKey ? "shift+" : "";
      const key = `${modifierKey}${shiftKey}${e.key.toLowerCase()}`;

      if (shortcutsRef.current[key]) {
        e.preventDefault();
        shortcutsRef.current[key]();
      }
    };

    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []); // Empty dependency array since we use ref
}
