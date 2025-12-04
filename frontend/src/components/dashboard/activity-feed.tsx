"use client";

import { useEffect, useState, useRef, useCallback, useMemo } from "react";
import { useWebSocket } from "@/hooks/use-realtime";
import { useInfiniteQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  CheckCircle2,
  XCircle,
  Clock,
  User,
  Bot,
  Webhook,
} from "lucide-react";
import { useRouter } from "next/navigation";

interface ActivityItem {
  id: string;
  type:
    | "task_started"
    | "task_completed"
    | "task_failed"
    | "agent_created"
    | "agent_updated"
    | "member_joined"
    | "webhook_fired";
  title: string;
  description: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface ActivityFeedProps {
  workspaceId: string;
}

async function fetchActivities(
  workspaceId: string,
  pageParam: number = 0
): Promise<{ activities: ActivityItem[]; nextPage: number | null }> {
  const response = await fetch(
    `/api/activity?workspace_id=${workspaceId}&page=${pageParam}&limit=20`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch activities");
  }

  return response.json();
}

export function ActivityFeed({ workspaceId }: ActivityFeedProps) {
  const router = useRouter();
  const scrollRef = useRef<HTMLDivElement>(null);
  const [realtimeActivities, setRealtimeActivities] = useState<ActivityItem[]>(
    []
  );

  const { lastMessage } = useWebSocket<ActivityItem>(
    `/ws/workspaces/${workspaceId}/activity`
  );

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteQuery({
    queryKey: ["activity", workspaceId],
    queryFn: ({ pageParam = 0 }) => fetchActivities(workspaceId, pageParam),
    getNextPageParam: (lastPage) => lastPage.nextPage,
    initialPageParam: 0,
  });

  // Add real-time activities
  useEffect(() => {
    if (lastMessage?.data) {
      setRealtimeActivities((prev) => [lastMessage.data, ...prev]);
    }
  }, [lastMessage]);

  const handleScroll = useCallback(() => {
    if (!scrollRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;

    if (isNearBottom && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  const allActivities = useMemo(() => {
    const paginatedActivities = data?.pages.flatMap((page) => page.activities) || [];
    const combined = [...realtimeActivities, ...paginatedActivities];
    
    // Deduplicate activities by id
    const seen = new Set<string>();
    return combined.filter((activity) => {
      if (seen.has(activity.id)) {
        return false;
      }
      seen.add(activity.id);
      return true;
    });
  }, [realtimeActivities, data]);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "task_completed":
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case "task_failed":
        return <XCircle className="w-5 h-5 text-red-600" />;
      case "task_started":
        return <Clock className="w-5 h-5 text-blue-600" />;
      case "agent_created":
      case "agent_updated":
        return <Bot className="w-5 h-5 text-purple-600" />;
      case "member_joined":
        return <User className="w-5 h-5 text-indigo-600" />;
      case "webhook_fired":
        return <Webhook className="w-5 h-5 text-orange-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getActivityBadge = (type: string) => {
    switch (type) {
      case "task_completed":
        return (
          <Badge className="bg-green-100 text-green-800 border-green-200">
            Completed
          </Badge>
        );
      case "task_failed":
        return (
          <Badge className="bg-red-100 text-red-800 border-red-200">
            Failed
          </Badge>
        );
      case "task_started":
        return (
          <Badge className="bg-blue-100 text-blue-800 border-blue-200">
            Started
          </Badge>
        );
      default:
        return <Badge variant="secondary">{type.replace("_", " ")}</Badge>;
    }
  };

  const handleActivityClick = (activity: ActivityItem) => {
    if (activity.metadata?.url) {
      router.push(activity.metadata.url);
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  if (isLoading) {
    return (
      <div className="space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-muted rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-3/4"></div>
                  <div className="h-3 bg-muted rounded w-1/2"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <ScrollArea
      ref={scrollRef}
      className="h-[600px]"
      onScrollCapture={handleScroll}
    >
      <div className="space-y-2">
        {allActivities.length === 0 ? (
          <Card>
            <CardContent className="p-6 text-center text-muted-foreground">
              No activities yet
            </CardContent>
          </Card>
        ) : (
          allActivities.map((activity) => (
            <Card
              key={activity.id}
              className="cursor-pointer hover:bg-muted/50 transition-colors"
              onClick={() => handleActivityClick(activity)}
            >
              <CardContent className="p-4">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                    {getActivityIcon(activity.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium truncate">
                        {activity.title}
                      </h4>
                      {getActivityBadge(activity.type)}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {activity.description}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatTimestamp(activity.timestamp)}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
        {isFetchingNextPage && (
          <Card className="animate-pulse">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-muted rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-muted rounded w-3/4"></div>
                  <div className="h-3 bg-muted rounded w-1/2"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </ScrollArea>
  );
}
