"use client";

import { useEffect, useState, useRef, useCallback } from "react";

export interface WebSocketMessage<T = any> {
  type: string;
  data: T;
  timestamp: string;
}

export interface UseWebSocketOptions {
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
}

export interface UseWebSocketReturn<T = any> {
  messages: WebSocketMessage<T>[];
  lastMessage: WebSocketMessage<T> | null;
  send: (message: any) => void;
  status: "connecting" | "connected" | "disconnected" | "error";
  reconnect: () => void;
}

export function useWebSocket<T = any>(
  endpoint: string,
  options: UseWebSocketOptions = {}
): UseWebSocketReturn<T> {
  const {
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    onOpen,
    onClose,
    onError,
  } = options;

  const [messages, setMessages] = useState<WebSocketMessage<T>[]>([]);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage<T> | null>(
    null
  );
  const [status, setStatus] = useState<
    "connecting" | "connected" | "disconnected" | "error"
  >("connecting");

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    try {
      const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
      const wsUrl = `${protocol}//${window.location.host}${endpoint}`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus("connected");
        reconnectAttemptsRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage<T> = JSON.parse(event.data);
          setMessages((prev) => [...prev, message]);
          setLastMessage(message);
        } catch (error) {
          console.error("Failed to parse WebSocket message:", error);
        }
      };

      ws.onerror = (error) => {
        setStatus("error");
        onError?.(error);
      };

      ws.onclose = () => {
        setStatus("disconnected");
        onClose?.();

        // Attempt to reconnect
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++;
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };
    } catch (error) {
      console.error("Failed to connect to WebSocket:", error);
      setStatus("error");
    }
  }, [endpoint, maxReconnectAttempts, reconnectInterval, onOpen, onClose, onError]);

  const send = useCallback((message: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn("WebSocket is not connected");
    }
  }, []);

  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    reconnectAttemptsRef.current = 0;
    connect();
  }, [connect]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return {
    messages,
    lastMessage,
    send,
    status,
    reconnect,
  };
}
