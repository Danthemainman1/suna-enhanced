"use client";

import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AnalyticsData } from "@/hooks/use-analytics";

interface AnalyticsChartsProps {
  data: AnalyticsData;
}

const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"];

export function AnalyticsCharts({ data }: AnalyticsChartsProps) {
  const tokenUsageData = [
    { name: "Input Tokens", value: data.tokenUsage.input },
    { name: "Output Tokens", value: data.tokenUsage.output },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {/* Tasks Over Time */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle>Task Success Rate</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {data.tasks.completed}
              </div>
              <div className="text-sm text-muted-foreground">Completed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {data.tasks.failed}
              </div>
              <div className="text-sm text-muted-foreground">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {data.tasks.running}
              </div>
              <div className="text-sm text-muted-foreground">Running</div>
            </div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold">
              {data.successRate.rate.toFixed(1)}%
            </div>
            <div className="text-sm text-muted-foreground">
              Success Rate{" "}
              <span
                className={
                  data.successRate.trend >= 0
                    ? "text-green-600"
                    : "text-red-600"
                }
              >
                ({data.successRate.trend >= 0 ? "+" : ""}
                {data.successRate.trend.toFixed(1)}%)
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Average Duration by Agent */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle>Average Duration by Agent</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.averageDuration.byAgent}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="agentName" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="duration" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Token Usage Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle>Token Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={tokenUsageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {tokenUsageData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="text-center mt-4">
            <div className="text-xl font-bold">
              {data.tokenUsage.total.toLocaleString()}
            </div>
            <div className="text-sm text-muted-foreground">Total Tokens</div>
          </div>
        </CardContent>
      </Card>

      {/* Cost Over Time */}
      <Card>
        <CardHeader>
          <CardTitle>Daily Cost</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data.costEstimation.daily}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="cost"
                stroke="#82ca9d"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="text-center mt-4">
            <div className="text-xl font-bold">
              ${data.costEstimation.total.toFixed(2)}
            </div>
            <div className="text-sm text-muted-foreground">Total Cost</div>
          </div>
        </CardContent>
      </Card>

      {/* Top Agents */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle>Top Agents by Usage</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {data.topAgents.map((agent, index) => (
              <div key={agent.agentId} className="flex items-center gap-4">
                <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="font-medium">{agent.agentName}</div>
                  <div className="text-sm text-muted-foreground">
                    {agent.usageCount} tasks • {agent.successRate.toFixed(1)}%
                    success rate
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Error Breakdown */}
      <Card className="col-span-2">
        <CardHeader>
          <CardTitle>Error Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.errors.map((error) => (
              <div key={error.type} className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium">{error.type}</span>
                    <span className="text-sm text-muted-foreground">
                      {error.count} ({error.percentage.toFixed(1)}%)
                    </span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-destructive h-2 rounded-full"
                      style={{ width: `${error.percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
