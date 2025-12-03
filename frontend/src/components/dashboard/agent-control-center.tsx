'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity,
  Cpu,
  Database,
  Circle,
  Pause,
  Play,
  Square,
  MoreVertical,
  TrendingUp,
  AlertCircle,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Progress } from '@/components/ui/progress';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'running' | 'idle' | 'paused' | 'error';
  uptime: string;
  tasksCompleted: number;
  currentTask?: string;
  cpu: number;
  memory: number;
  apiCalls: number;
}

// Mock data - replace with actual API call
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Research Agent Alpha',
    type: 'ResearchAgent',
    status: 'running',
    uptime: '2h 34m',
    tasksCompleted: 12,
    currentTask: 'Analyzing market trends for Q4 2025',
    cpu: 45,
    memory: 62,
    apiCalls: 234,
  },
  {
    id: '2',
    name: 'Code Agent Beta',
    type: 'CodeAgent',
    status: 'running',
    uptime: '5h 12m',
    tasksCompleted: 8,
    currentTask: 'Refactoring authentication module',
    cpu: 78,
    memory: 84,
    apiCalls: 156,
  },
  {
    id: '3',
    name: 'Data Agent Gamma',
    type: 'DataAgent',
    status: 'idle',
    uptime: '1h 05m',
    tasksCompleted: 23,
    cpu: 12,
    memory: 28,
    apiCalls: 89,
  },
  {
    id: '4',
    name: 'Writer Agent Delta',
    type: 'WriterAgent',
    status: 'paused',
    uptime: '45m',
    tasksCompleted: 5,
    cpu: 5,
    memory: 15,
    apiCalls: 67,
  },
  {
    id: '5',
    name: 'Executor Agent Epsilon',
    type: 'ExecutorAgent',
    status: 'error',
    uptime: '10m',
    tasksCompleted: 2,
    currentTask: 'Failed to connect to API endpoint',
    cpu: 0,
    memory: 10,
    apiCalls: 12,
  },
];

const statusConfig = {
  running: {
    color: 'bg-green-500',
    label: 'Running',
    icon: Activity,
  },
  idle: {
    color: 'bg-blue-500',
    label: 'Idle',
    icon: Circle,
  },
  paused: {
    color: 'bg-yellow-500',
    label: 'Paused',
    icon: Pause,
  },
  error: {
    color: 'bg-red-500',
    label: 'Error',
    icon: AlertCircle,
  },
};

function AgentCard({ agent }: { agent: Agent }) {
  const status = statusConfig[agent.status];
  const StatusIcon = status.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-3 h-3 rounded-full ${status.color} animate-pulse`} />
              <div>
                <CardTitle className="text-lg">{agent.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{agent.type}</p>
              </div>
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm">
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>
                  <Play className="w-4 h-4 mr-2" />
                  Start
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Pause className="w-4 h-4 mr-2" />
                  Pause
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Square className="w-4 h-4 mr-2" />
                  Stop
                </DropdownMenuItem>
                <DropdownMenuItem className="text-destructive">
                  <AlertCircle className="w-4 h-4 mr-2" />
                  Restart
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-2">
            <Badge variant={agent.status === 'error' ? 'destructive' : 'secondary'}>
              <StatusIcon className="w-3 h-3 mr-1" />
              {status.label}
            </Badge>
            <span className="text-xs text-muted-foreground">Uptime: {agent.uptime}</span>
          </div>

          {agent.currentTask && (
            <div className="text-sm">
              <p className="text-muted-foreground mb-1">Current Task:</p>
              <p className="font-medium line-clamp-2">{agent.currentTask}</p>
            </div>
          )}

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-muted-foreground" />
                <span>CPU</span>
              </div>
              <span className="font-medium">{agent.cpu}%</span>
            </div>
            <Progress value={agent.cpu} className="h-1" />

            <div className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-muted-foreground" />
                <span>Memory</span>
              </div>
              <span className="font-medium">{agent.memory}%</span>
            </div>
            <Progress value={agent.memory} className="h-1" />
          </div>

          <div className="flex items-center justify-between pt-2 border-t">
            <div className="text-center">
              <p className="text-2xl font-bold">{agent.tasksCompleted}</p>
              <p className="text-xs text-muted-foreground">Tasks</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold">{agent.apiCalls}</p>
              <p className="text-xs text-muted-foreground">API Calls</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export function AgentControlCenter() {
  const [agents] = useState<Agent[]>(mockAgents);

  const stats = {
    total: agents.length,
    running: agents.filter((a) => a.status === 'running').length,
    idle: agents.filter((a) => a.status === 'idle').length,
    error: agents.filter((a) => a.status === 'error').length,
  };

  return (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Agents</p>
                <p className="text-3xl font-bold">{stats.total}</p>
              </div>
              <Activity className="w-8 h-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Running</p>
                <p className="text-3xl font-bold text-green-500">{stats.running}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Idle</p>
                <p className="text-3xl font-bold text-blue-500">{stats.idle}</p>
              </div>
              <Circle className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Errors</p>
                <p className="text-3xl font-bold text-red-500">{stats.error}</p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
}
