"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChevronRight, ChevronDown } from "lucide-react";

interface StateInspectorProps {
  sessionId: string;
  currentStep?: number;
}

interface StateNode {
  key: string;
  value: any;
  type: string;
  expanded?: boolean;
}

export function StateInspector({ sessionId, currentStep }: StateInspectorProps) {
  const [state, setState] = useState<Record<string, any>>({});
  const [expandedKeys, setExpandedKeys] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchState = async () => {
      try {
        const params = new URLSearchParams({ session_id: sessionId });
        if (currentStep !== undefined) {
          params.append("step", currentStep.toString());
        }
        
        const response = await fetch(`/api/debug/state?${params}`);
        if (response.ok) {
          const data = await response.json();
          setState(data);
        }
      } catch (error) {
        console.error("Failed to fetch state:", error);
      }
    };

    fetchState();
  }, [sessionId, currentStep]);

  const toggleExpanded = (key: string) => {
    const newExpanded = new Set(expandedKeys);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedKeys(newExpanded);
  };

  const renderValue = (value: any, key: string, depth: number = 0): JSX.Element => {
    const paddingLeft = depth * 16;
    
    if (value === null) {
      return (
        <div style={{ paddingLeft }} className="text-muted-foreground">
          null
        </div>
      );
    }

    if (value === undefined) {
      return (
        <div style={{ paddingLeft }} className="text-muted-foreground">
          undefined
        </div>
      );
    }

    if (typeof value === "boolean") {
      return (
        <div style={{ paddingLeft }} className="text-purple-600">
          {value.toString()}
        </div>
      );
    }

    if (typeof value === "number") {
      return (
        <div style={{ paddingLeft }} className="text-blue-600">
          {value}
        </div>
      );
    }

    if (typeof value === "string") {
      return (
        <div style={{ paddingLeft }} className="text-green-600">
          "{value}"
        </div>
      );
    }

    if (Array.isArray(value)) {
      const isExpanded = expandedKeys.has(key);
      return (
        <div style={{ paddingLeft }}>
          <button
            onClick={() => toggleExpanded(key)}
            className="flex items-center gap-1 hover:bg-muted rounded px-1"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <span className="font-medium">Array({value.length})</span>
          </button>
          {isExpanded && (
            <div className="ml-4 border-l-2 border-muted pl-2 mt-1">
              {value.map((item, index) => (
                <div key={index} className="mb-1">
                  <span className="text-muted-foreground">[{index}]: </span>
                  {renderValue(item, `${key}.${index}`, depth + 1)}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    if (typeof value === "object") {
      const isExpanded = expandedKeys.has(key);
      const keys = Object.keys(value);
      return (
        <div style={{ paddingLeft }}>
          <button
            onClick={() => toggleExpanded(key)}
            className="flex items-center gap-1 hover:bg-muted rounded px-1"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <span className="font-medium">Object({keys.length})</span>
          </button>
          {isExpanded && (
            <div className="ml-4 border-l-2 border-muted pl-2 mt-1">
              {keys.map((k) => (
                <div key={k} className="mb-1">
                  <span className="font-medium">{k}: </span>
                  {renderValue(value[k], `${key}.${k}`, depth + 1)}
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div style={{ paddingLeft }} className="text-muted-foreground">
        {String(value)}
      </div>
    );
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>State Inspector</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px]">
          {Object.keys(state).length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No state data available
            </div>
          ) : (
            <div className="space-y-2 font-mono text-sm">
              {Object.entries(state).map(([key, value]) => (
                <div key={key} className="mb-2">
                  <span className="font-bold text-primary">{key}: </span>
                  {renderValue(value, key)}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
