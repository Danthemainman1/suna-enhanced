"use client";

import { useState } from "react";
import { Calendar, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AnalyticsCharts } from "@/components/dashboard/analytics-charts";
import { useAnalytics } from "@/hooks/use-analytics";
import { DatePickerWithRange } from "@/components/ui/date-range-picker";
import { DateRange } from "react-day-picker";
import { addDays } from "date-fns";

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: addDays(new Date(), -30),
    to: new Date(),
  });

  // TODO: Get workspace ID from context or auth
  const workspaceId = "default";

  const { data, isLoading, error } = useAnalytics({
    workspaceId,
    startDate: dateRange?.from || addDays(new Date(), -30),
    endDate: dateRange?.to || new Date(),
  });

  const handleExport = () => {
    // Export analytics data as CSV
    if (!data) return;

    const csv = [
      ["Metric", "Value"],
      ["Total Tasks", data.tasks.total],
      ["Completed Tasks", data.tasks.completed],
      ["Failed Tasks", data.tasks.failed],
      ["Running Tasks", data.tasks.running],
      ["Success Rate", `${data.successRate.rate}%`],
      ["Average Duration", `${data.averageDuration.duration}s`],
      ["Total Token Usage", data.tokenUsage.total],
      ["Total Cost", `$${data.costEstimation.total}`],
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `analytics-${new Date().toISOString()}.csv`;
    a.click();
  };

  return (
    <div className="container mx-auto px-6 py-6 max-w-7xl">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-muted-foreground mt-1">
              Monitor your workspace performance and usage
            </p>
          </div>
          <div className="flex items-center gap-2">
            <DatePickerWithRange
              date={dateRange}
              onDateChange={setDateRange}
            />
            <Button variant="outline" onClick={handleExport} disabled={!data}>
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-2">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-muted rounded"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : error ? (
          <Card>
            <CardContent className="p-6 text-center">
              <p className="text-muted-foreground">
                Failed to load analytics data. Please try again.
              </p>
            </CardContent>
          </Card>
        ) : data ? (
          <AnalyticsCharts data={data} />
        ) : null}
      </div>
    </div>
  );
}
