"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";
import { ExecutionGraph } from "@/components/debugger/execution-graph";
import { DebugPanel } from "@/components/debugger/debug-panel";
import { TimeTravelControls } from "@/components/debugger/time-travel-controls";
import { LiveAgentStream } from "@/components/dashboard/live-agent-stream";

export default function DebuggerPage() {
  const [taskId, setTaskId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const handleLoadTask = () => {
    if (taskId.trim()) {
      setActiveTaskId(taskId.trim());
    }
  };

  const handleLoadSession = () => {
    if (sessionId.trim()) {
      setActiveSessionId(sessionId.trim());
    }
  };

  return (
    <div className="container mx-auto px-6 py-6 max-w-7xl">
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Debugger</h1>
          <p className="text-muted-foreground mt-1">
            Debug and inspect task executions
          </p>
        </div>

        <Tabs defaultValue="graph" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="graph">Execution Graph</TabsTrigger>
            <TabsTrigger value="debug">Debug Panel</TabsTrigger>
            <TabsTrigger value="time-travel">Time Travel</TabsTrigger>
            <TabsTrigger value="stream">Live Stream</TabsTrigger>
          </TabsList>

          <TabsContent value="graph" className="space-y-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Enter task ID..."
                    value={taskId}
                    onChange={(e) => setTaskId(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleLoadTask();
                      }
                    }}
                  />
                  <Button onClick={handleLoadTask}>
                    <Search className="w-4 h-4 mr-2" />
                    Load Task
                  </Button>
                </div>
              </CardContent>
            </Card>

            {activeTaskId ? (
              <ExecutionGraph taskId={activeTaskId} />
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <p className="text-muted-foreground">
                    Enter a task ID to view its execution graph
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="debug" className="space-y-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Enter debug session ID..."
                    value={sessionId}
                    onChange={(e) => setSessionId(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleLoadSession();
                      }
                    }}
                  />
                  <Button onClick={handleLoadSession}>
                    <Search className="w-4 h-4 mr-2" />
                    Load Session
                  </Button>
                </div>
              </CardContent>
            </Card>

            {activeSessionId ? (
              <DebugPanel sessionId={activeSessionId} />
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <p className="text-muted-foreground">
                    Enter a debug session ID to start debugging
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="time-travel" className="space-y-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Enter task ID..."
                    value={taskId}
                    onChange={(e) => setTaskId(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleLoadTask();
                      }
                    }}
                  />
                  <Button onClick={handleLoadTask}>
                    <Search className="w-4 h-4 mr-2" />
                    Load Task
                  </Button>
                </div>
              </CardContent>
            </Card>

            {activeTaskId ? (
              <TimeTravelControls taskId={activeTaskId} />
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <p className="text-muted-foreground">
                    Enter a task ID to view its execution history
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="stream" className="space-y-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Enter task ID..."
                    value={taskId}
                    onChange={(e) => setTaskId(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleLoadTask();
                      }
                    }}
                  />
                  <Button onClick={handleLoadTask}>
                    <Search className="w-4 h-4 mr-2" />
                    Load Stream
                  </Button>
                </div>
              </CardContent>
            </Card>

            {activeTaskId ? (
              <div className="h-[600px]">
                <LiveAgentStream taskId={activeTaskId} />
              </div>
            ) : (
              <Card>
                <CardContent className="p-12 text-center">
                  <p className="text-muted-foreground">
                    Enter a task ID to view its live stream
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
