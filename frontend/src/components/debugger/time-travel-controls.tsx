"use client";

import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, SkipBack } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";

interface TimeTravelControlsProps {
  taskId: string;
}

interface ExecutionStep {
  step: number;
  timestamp: string;
  type: string;
  description: string;
  state: Record<string, any>;
}

interface ExecutionHistory {
  steps: ExecutionStep[];
  currentStep: number;
}

export function TimeTravelControls({ taskId }: TimeTravelControlsProps) {
  const [history, setHistory] = useState<ExecutionHistory | null>(null);
  const [selectedStep, setSelectedStep] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`/api/tasks/${taskId}/history`);
        if (response.ok) {
          const data = await response.json();
          setHistory(data);
          setSelectedStep(data.currentStep);
        }
      } catch (error) {
        console.error("Failed to fetch execution history:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, [taskId]);

  const handleStepChange = (step: number) => {
    if (history && step >= 0 && step < history.steps.length) {
      setSelectedStep(step);
    }
  };

  const handleSliderChange = (value: number[]) => {
    handleStepChange(value[0]);
  };

  const goToPreviousStep = () => {
    handleStepChange(selectedStep - 1);
  };

  const goToNextStep = () => {
    handleStepChange(selectedStep + 1);
  };

  const goToFirstStep = () => {
    handleStepChange(0);
  };

  const calculateDiff = (step: number): string => {
    if (!history || step === 0) return "No changes";

    const currentState = history.steps[step].state;
    const previousState = history.steps[step - 1].state;

    const changes: string[] = [];

    // Check for added/modified keys
    for (const key in currentState) {
      if (!(key in previousState)) {
        const value = String(currentState[key]);
        changes.push(`+ ${key}: ${value.length > 100 ? value.substring(0, 100) + "..." : value}`);
      } else {
        // Simple string comparison for primitives, indicate change for objects
        const currentValue = currentState[key];
        const previousValue = previousState[key];
        
        if (typeof currentValue === "object" || typeof previousValue === "object") {
          // For objects, just indicate they changed
          changes.push(`~ ${key}: [Object changed]`);
        } else if (currentValue !== previousValue) {
          changes.push(`~ ${key}: ${previousValue} → ${currentValue}`);
        }
      }
    }

    // Check for deleted keys
    for (const key in previousState) {
      if (!(key in currentState)) {
        const value = String(previousState[key]);
        changes.push(`- ${key}: ${value.length > 100 ? value.substring(0, 100) + "..." : value}`);
      }
    }

    return changes.length > 0 ? changes.join("\n") : "No changes";
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[400px]">
        <div className="text-center">
          <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading execution history...</p>
        </div>
      </div>
    );
  }

  if (!history) {
    return (
      <div className="text-center text-muted-foreground py-8">
        No execution history available
      </div>
    );
  }

  const currentStep = history.steps[selectedStep];

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Time Travel Controls</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={goToFirstStep}
                disabled={selectedStep === 0}
              >
                <SkipBack className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={goToPreviousStep}
                disabled={selectedStep === 0}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <div className="flex-1 text-center">
                <div className="text-sm font-medium">
                  Step {selectedStep + 1} of {history.steps.length}
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={goToNextStep}
                disabled={selectedStep === history.steps.length - 1}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>

            <Slider
              value={[selectedStep]}
              onValueChange={handleSliderChange}
              max={history.steps.length - 1}
              step={1}
              className="w-full"
            />

            {currentStep && (
              <div className="border rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <Badge>{currentStep.type}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {new Date(currentStep.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="font-medium">{currentStep.description}</div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {currentStep && (
        <Card>
          <CardHeader>
            <CardTitle>State Diff</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              <pre className="text-xs font-mono whitespace-pre-wrap">
                {calculateDiff(selectedStep)}
              </pre>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Current State</CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[300px]">
            <pre className="text-xs font-mono">
              {JSON.stringify(currentStep?.state, null, 2)}
            </pre>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}
