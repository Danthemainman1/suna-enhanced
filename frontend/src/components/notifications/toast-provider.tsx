"use client";

import { Toaster } from "sonner";

export function ToastProvider() {
  return (
    <Toaster
      position="bottom-right"
      expand={true}
      richColors
      closeButton
      toastOptions={{
        className: "group",
        duration: 4000,
      }}
    />
  );
}
