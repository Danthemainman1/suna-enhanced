"use client";

import { toast as sonnerToast } from "sonner";

export interface ToastOptions {
  title: string;
  description?: string;
  duration?: number;
}

export function useToast() {
  const toast = {
    success: (options: ToastOptions | string) => {
      if (typeof options === "string") {
        sonnerToast.success(options);
      } else {
        sonnerToast.success(options.title, {
          description: options.description,
          duration: options.duration,
        });
      }
    },
    error: (options: ToastOptions | string) => {
      if (typeof options === "string") {
        sonnerToast.error(options);
      } else {
        sonnerToast.error(options.title, {
          description: options.description,
          duration: options.duration,
        });
      }
    },
    info: (options: ToastOptions | string) => {
      if (typeof options === "string") {
        sonnerToast.info(options);
      } else {
        sonnerToast.info(options.title, {
          description: options.description,
          duration: options.duration,
        });
      }
    },
    warning: (options: ToastOptions | string) => {
      if (typeof options === "string") {
        sonnerToast.warning(options);
      } else {
        sonnerToast.warning(options.title, {
          description: options.description,
          duration: options.duration,
        });
      }
    },
  };

  return { toast };
}
