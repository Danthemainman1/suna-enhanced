"use client";

import { useQuery, UseQueryResult } from "@tanstack/react-query";

export interface AnalyticsData {
  tasks: {
    total: number;
    completed: number;
    failed: number;
    running: number;
    trend: number; // percentage change
  };
  successRate: {
    rate: number;
    trend: number;
  };
  averageDuration: {
    duration: number; // in seconds
    byAgent: Array<{ agentId: string; agentName: string; duration: number }>;
  };
  tokenUsage: {
    input: number;
    output: number;
    total: number;
  };
  costEstimation: {
    daily: Array<{ date: string; cost: number }>;
    total: number;
  };
  topAgents: Array<{
    agentId: string;
    agentName: string;
    usageCount: number;
    successRate: number;
  }>;
  errors: Array<{
    type: string;
    count: number;
    percentage: number;
  }>;
}

export interface UseAnalyticsOptions {
  workspaceId: string;
  startDate: Date;
  endDate: Date;
  enabled?: boolean;
}

async function fetchAnalytics(
  workspaceId: string,
  startDate: Date,
  endDate: Date
): Promise<AnalyticsData> {
  const params = new URLSearchParams({
    workspace_id: workspaceId,
    start_date: startDate.toISOString(),
    end_date: endDate.toISOString(),
  });

  const response = await fetch(`/api/analytics?${params}`);

  if (!response.ok) {
    throw new Error("Failed to fetch analytics data");
  }

  return response.json();
}

export function useAnalytics(
  options: UseAnalyticsOptions
): UseQueryResult<AnalyticsData, Error> {
  const { workspaceId, startDate, endDate, enabled = true } = options;

  return useQuery({
    queryKey: ["analytics", workspaceId, startDate, endDate],
    queryFn: () => fetchAnalytics(workspaceId, startDate, endDate),
    enabled: enabled && !!workspaceId,
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // refetch every minute
  });
}
