'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  DndContext,
  DragOverlay,
  closestCorners,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragStartEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, User, AlertCircle, CheckCircle2, PlayCircle } from 'lucide-react';
import { SortableTaskCard } from './sortable-task-card';

interface Task {
  id: string;
  title: string;
  description: string;
  agent: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimatedTime: string;
  assignedTo?: string;
  tags: string[];
}

interface Column {
  id: string;
  title: string;
  tasks: Task[];
  icon: any;
  color: string;
}

// Mock data
const initialColumns: Column[] = [
  {
    id: 'pending',
    title: 'Pending',
    icon: Clock,
    color: 'text-blue-500',
    tasks: [
      {
        id: '1',
        title: 'Market Research Analysis',
        description: 'Analyze Q4 2025 market trends for SaaS industry',
        agent: 'ResearchAgent',
        priority: 'high',
        estimatedTime: '2h',
        tags: ['research', 'analysis'],
      },
      {
        id: '2',
        title: 'Code Review PR #1234',
        description: 'Review authentication refactoring changes',
        agent: 'CodeAgent',
        priority: 'medium',
        estimatedTime: '45m',
        tags: ['code', 'review'],
      },
      {
        id: '3',
        title: 'Generate Monthly Report',
        description: 'Create PDF report for November 2025 metrics',
        agent: 'DataAgent',
        priority: 'urgent',
        estimatedTime: '30m',
        tags: ['data', 'reporting'],
      },
    ],
  },
  {
    id: 'in-progress',
    title: 'In Progress',
    icon: PlayCircle,
    color: 'text-yellow-500',
    tasks: [
      {
        id: '4',
        title: 'Write Blog Post',
        description: 'Draft article about AI agent orchestration',
        agent: 'WriterAgent',
        priority: 'medium',
        estimatedTime: '3h',
        assignedTo: 'Writer Agent Delta',
        tags: ['content', 'writing'],
      },
      {
        id: '5',
        title: 'Deploy to Production',
        description: 'Deploy version 2.1.0 to production environment',
        agent: 'ExecutorAgent',
        priority: 'high',
        estimatedTime: '1h',
        assignedTo: 'Executor Agent Epsilon',
        tags: ['deployment', 'devops'],
      },
    ],
  },
  {
    id: 'completed',
    title: 'Completed',
    icon: CheckCircle2,
    color: 'text-green-500',
    tasks: [
      {
        id: '6',
        title: 'Database Optimization',
        description: 'Optimize query performance for user table',
        agent: 'DataAgent',
        priority: 'high',
        estimatedTime: '2h',
        tags: ['database', 'optimization'],
      },
      {
        id: '7',
        title: 'Customer Support Tickets',
        description: 'Respond to 15 support tickets',
        agent: 'ExecutorAgent',
        priority: 'medium',
        estimatedTime: '1h 30m',
        tags: ['support', 'customer'],
      },
    ],
  },
];

const priorityColors = {
  low: 'bg-gray-500/10 text-gray-500',
  medium: 'bg-blue-500/10 text-blue-500',
  high: 'bg-orange-500/10 text-orange-500',
  urgent: 'bg-red-500/10 text-red-500',
};

function TaskCard({ task }: { task: Task }) {
  return (
    <Card className="mb-3 hover:shadow-md transition-shadow cursor-move">
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-sm">{task.title}</h3>
          <Badge className={priorityColors[task.priority]} variant="secondary">
            {task.priority}
          </Badge>
        </div>
        
        <p className="text-xs text-muted-foreground mb-3 line-clamp-2">
          {task.description}
        </p>
        
        <div className="flex flex-wrap gap-1 mb-3">
          {task.tags.map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
        
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-1 text-muted-foreground">
            <User className="w-3 h-3" />
            <span>{task.agent}</span>
          </div>
          <div className="flex items-center gap-1 text-muted-foreground">
            <Clock className="w-3 h-3" />
            <span>{task.estimatedTime}</span>
          </div>
        </div>
        
        {task.assignedTo && (
          <div className="mt-2 pt-2 border-t">
            <div className="flex items-center gap-2 text-xs">
              <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center">
                <User className="w-3 h-3 text-primary" />
              </div>
              <span className="text-muted-foreground">{task.assignedTo}</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function TaskQueueBoard() {
  const [columns, setColumns] = useState<Column[]>(initialColumns);
  const [activeId, setActiveId] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (!over) {
      setActiveId(null);
      return;
    }

    // Find which column the task is being moved to
    const overColumnId = over.id as string;
    
    // Find the task and its current column
    let taskToMove: Task | undefined;
    let sourceColumnId: string | undefined;

    columns.forEach((col) => {
      const task = col.tasks.find((t) => t.id === active.id);
      if (task) {
        taskToMove = task;
        sourceColumnId = col.id;
      }
    });

    if (!taskToMove || !sourceColumnId) {
      setActiveId(null);
      return;
    }

    // If dropped on a task, find its column
    let targetColumnId = overColumnId;
    const isOverTask = columns.some((col) =>
      col.tasks.some((task) => task.id === overColumnId)
    );

    if (isOverTask) {
      const targetColumn = columns.find((col) =>
        col.tasks.some((task) => task.id === overColumnId)
      );
      if (targetColumn) {
        targetColumnId = targetColumn.id;
      }
    }

    // Move the task
    setColumns((prevColumns) => {
      const newColumns = prevColumns.map((col) => ({
        ...col,
        tasks: col.tasks.filter((t) => t.id !== taskToMove!.id),
      }));

      const targetCol = newColumns.find((col) => col.id === targetColumnId);
      if (targetCol) {
        targetCol.tasks.push(taskToMove!);
      }

      return newColumns;
    });

    setActiveId(null);
  };

  const activeTask = activeId
    ? columns.flatMap((col) => col.tasks).find((task) => task.id === activeId)
    : null;

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCorners}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
    >
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => {
          const Icon = column.icon;
          return (
            <motion.div
              key={column.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex-shrink-0 w-80"
            >
              <Card className="h-full">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-5 h-5 ${column.color}`} />
                      <CardTitle className="text-lg">{column.title}</CardTitle>
                    </div>
                    <Badge variant="secondary">{column.tasks.length}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <SortableContext
                    items={column.tasks.map((t) => t.id)}
                    strategy={verticalListSortingStrategy}
                  >
                    <div className="space-y-2 min-h-[400px]">
                      {column.tasks.map((task) => (
                        <SortableTaskCard key={task.id} id={task.id}>
                          <TaskCard task={task} />
                        </SortableTaskCard>
                      ))}
                    </div>
                  </SortableContext>
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      <DragOverlay>
        {activeTask ? (
          <div className="w-80 opacity-80">
            <TaskCard task={activeTask} />
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
}
