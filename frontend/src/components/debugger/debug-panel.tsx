"use client";

import { useState, useEffect } from "react";
import {
  Play,
  Pause,
  StepForward,
  SkipForward,
  RotateCcw,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { StateInspector } from "./state-inspector";

interface DebugPanelProps {
  sessionId: string;
}

interface DebugSession {
  id: string;
  status: "running" | "paused" | "completed" | "error";
  currentStep: number;
  totalSteps: number;
  callStack: Array<{
    function: string;
    file: string;
    line: number;
  }>;
}

export function DebugPanel({ sessionId }: DebugPanelProps) {
  const [session, setSession] = useState<DebugSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const response = await fetch(`/api/debug/sessions/${sessionId}`);
        if (response.ok) {
          const data = await response.json();
          setSession(data);
        }
      } catch (error) {
        console.error("Failed to fetch debug session:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSession();
    const interval = setInterval(fetchSession, 1000);

    return () => clearInterval(interval);
  }, [sessionId]);

  const handleControl = async (action: string) => {
    try {
      const response = await fetch(`/api/debug/sessions/${sessionId}/control`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action }),
      });

      if (response.ok) {
        const data = await response.json();
        setSession(data);
      }
    } catch (error) {
      console.error("Failed to control debug session:", error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading debug session...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center text-muted-foreground py-8">
        Debug session not found
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Debugger Controls</CardTitle>
            <Badge
              variant={
                session.status === "running"
                  ? "default"
                  : session.status === "paused"
                    ? "secondary"
                    : session.status === "error"
                      ? "destructive"
                      : "outline"
              }
            >
              {session.status}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  handleControl(
                    session.status === "running" ? "pause" : "play"
                  )
                }
                disabled={session.status === "completed"}
              >
                {session.status === "running" ? (
                  <>
                    <Pause className="w-4 h-4 mr-2" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Play
                  </>
                )}
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleControl("step")}
                disabled={session.status !== "paused"}
              >
                <StepForward className="w-4 h-4 mr-2" />
                Step
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleControl("continue")}
                disabled={session.status !== "paused"}
              >
                <SkipForward className="w-4 h-4 mr-2" />
                Continue
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleControl("restart")}
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Restart
              </Button>
            </div>

            <div className="border-t pt-4">
              <div className="text-sm text-muted-foreground mb-2">
                Current Step
              </div>
              <div className="text-2xl font-bold">
                {session.currentStep} / {session.totalSteps}
              </div>
              <div className="w-full bg-secondary rounded-full h-2 mt-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{
                    width: `${(session.currentStep / session.totalSteps) * 100}%`,
                  }}
                />
              </div>
            </div>

            {session.callStack && session.callStack.length > 0 && (
              <div className="border-t pt-4">
                <div className="text-sm font-medium mb-2">Call Stack</div>
                <div className="space-y-1">
                  {session.callStack.map((frame, index) => (
                    <div
                      key={index}
                      className="text-sm font-mono bg-muted p-2 rounded"
                    >
                      <div className="font-medium">{frame.function}</div>
                      <div className="text-xs text-muted-foreground">
                        {frame.file}:{frame.line}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      <StateInspector sessionId={sessionId} currentStep={session.currentStep} />
    </div>
  );
}
