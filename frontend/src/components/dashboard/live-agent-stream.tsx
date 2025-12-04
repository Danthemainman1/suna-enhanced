"use client";

import { useEffect, useRef, useState } from "react";
import { Copy, Pause, Play, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useWebSocket } from "@/hooks/use-realtime";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface LogEntry {
  id: string;
  timestamp: string;
  level: "info" | "debug" | "warning" | "error";
  type: "thinking" | "tool_call" | "output" | "error";
  content: string;
}

interface LiveAgentStreamProps {
  taskId: string;
}

export function LiveAgentStream({ taskId }: LiveAgentStreamProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [logLevelFilter, setLogLevelFilter] = useState<Set<string>>(
    new Set(["info", "debug", "warning", "error"])
  );

  const { messages, status } = useWebSocket<LogEntry>(
    `/ws/tasks/${taskId}/stream`
  );

  const filteredMessages = messages.filter((msg) =>
    logLevelFilter.has(msg.data.level)
  );

  useEffect(() => {
    if (autoScroll && scrollRef.current && !isPaused) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, autoScroll, isPaused]);

  const handleCopyOutput = async () => {
    const output = filteredMessages
      .map(
        (msg) =>
          `[${new Date(msg.data.timestamp).toLocaleTimeString()}] [${msg.data.level.toUpperCase()}] ${msg.data.content}`
      )
      .join("\n");

    try {
      await navigator.clipboard.writeText(output);
      toast.success("Output copied to clipboard");
    } catch (error) {
      toast.error("Failed to copy output");
    }
  };

  const toggleLogLevel = (level: string) => {
    const newFilter = new Set(logLevelFilter);
    if (newFilter.has(level)) {
      newFilter.delete(level);
    } else {
      newFilter.add(level);
    }
    setLogLevelFilter(newFilter);
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case "error":
        return "text-red-500";
      case "warning":
        return "text-yellow-500";
      case "debug":
        return "text-blue-500";
      default:
        return "text-gray-500";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "error":
        return "bg-red-100 text-red-800 border-red-200";
      case "tool_call":
        return "bg-blue-100 text-blue-800 border-blue-200";
      case "thinking":
        return "bg-purple-100 text-purple-800 border-purple-200";
      case "output":
        return "bg-green-100 text-green-800 border-green-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="flex flex-col h-full border rounded-lg">
      <div className="flex items-center justify-between border-b px-4 py-2">
        <div className="flex items-center gap-2">
          <h3 className="font-semibold">Live Stream</h3>
          <Badge
            variant={status === "connected" ? "default" : "secondary"}
            className="text-xs"
          >
            {status}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Log Levels</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuCheckboxItem
                checked={logLevelFilter.has("info")}
                onCheckedChange={() => toggleLogLevel("info")}
              >
                Info
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={logLevelFilter.has("debug")}
                onCheckedChange={() => toggleLogLevel("debug")}
              >
                Debug
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={logLevelFilter.has("warning")}
                onCheckedChange={() => toggleLogLevel("warning")}
              >
                Warning
              </DropdownMenuCheckboxItem>
              <DropdownMenuCheckboxItem
                checked={logLevelFilter.has("error")}
                onCheckedChange={() => toggleLogLevel("error")}
              >
                Error
              </DropdownMenuCheckboxItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsPaused(!isPaused)}
          >
            {isPaused ? (
              <Play className="w-4 h-4" />
            ) : (
              <Pause className="w-4 h-4" />
            )}
          </Button>
          <Button variant="outline" size="sm" onClick={handleCopyOutput}>
            <Copy className="w-4 h-4" />
          </Button>
        </div>
      </div>
      <ScrollArea
        ref={scrollRef}
        className="flex-1 p-4"
        onMouseEnter={() => setAutoScroll(false)}
        onMouseLeave={() => setAutoScroll(true)}
      >
        <div className="space-y-2 font-mono text-sm">
          {filteredMessages.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No logs to display
            </div>
          ) : (
            filteredMessages.map((msg) => (
              <div
                key={msg.data.id}
                className="flex items-start gap-2 hover:bg-muted/50 p-2 rounded"
              >
                <span className="text-xs text-muted-foreground whitespace-nowrap">
                  {new Date(msg.data.timestamp).toLocaleTimeString()}
                </span>
                <Badge variant="outline" className={`text-xs ${getTypeColor(msg.data.type)}`}>
                  {msg.data.type}
                </Badge>
                <span className={`text-xs ${getLevelColor(msg.data.level)}`}>
                  [{msg.data.level.toUpperCase()}]
                </span>
                <span className="flex-1 whitespace-pre-wrap break-words">
                  {msg.data.content}
                </span>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
