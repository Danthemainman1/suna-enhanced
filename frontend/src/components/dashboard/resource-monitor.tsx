"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Activity, Zap, Users, AlertCircle, DollarSign } from "lucide-react";

interface ResourceMetrics {
  apiCallsPerMinute: Array<{ time: string; calls: number }>;
  tokenUsage: Array<{ time: string; input: number; output: number }>;
  activeAgents: number;
  taskQueueDepth: Array<{ status: string; count: number }>;
  errorRate: number;
  costEstimation: number;
}

interface ResourceMonitorProps {
  workspaceId: string;
}

export function ResourceMonitor({ workspaceId }: ResourceMonitorProps) {
  const [metrics, setMetrics] = useState<ResourceMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`/api/metrics?workspace_id=${workspaceId}`);
        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
        }
      } catch (error) {
        console.error("Failed to fetch metrics:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Fetch every 5 seconds

    return () => clearInterval(interval);
  }, [workspaceId]);

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-muted rounded w-1/2"></div>
            </CardHeader>
            <CardContent>
              <div className="h-24 bg-muted rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className="text-center text-muted-foreground">
        Failed to load metrics
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {/* API Calls Per Minute */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            API Calls Per Minute
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={metrics.apiCallsPerMinute}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="calls"
                stroke="#8884d8"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Active Agents */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Active Agents
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold">{metrics.activeAgents}</div>
          <p className="text-sm text-muted-foreground mt-2">
            Currently running
          </p>
        </CardContent>
      </Card>

      {/* Token Usage */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Token Usage
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={metrics.tokenUsage}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area
                type="monotone"
                dataKey="input"
                stackId="1"
                stroke="#82ca9d"
                fill="#82ca9d"
                name="Input Tokens"
              />
              <Area
                type="monotone"
                dataKey="output"
                stackId="1"
                stroke="#8884d8"
                fill="#8884d8"
                name="Output Tokens"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Error Rate */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            Error Rate
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold">
            {metrics.errorRate.toFixed(2)}%
          </div>
          <p className="text-sm text-muted-foreground mt-2">Last hour</p>
        </CardContent>
      </Card>

      {/* Task Queue Depth */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle>Task Queue</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={metrics.taskQueueDepth}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Cost Estimation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="w-5 h-5" />
            Cost Estimation
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold">
            ${metrics.costEstimation.toFixed(2)}
          </div>
          <p className="text-sm text-muted-foreground mt-2">This month</p>
        </CardContent>
      </Card>
    </div>
  );
}
