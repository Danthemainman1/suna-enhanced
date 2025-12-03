import { Suspense } from 'react';
import { TaskQueueBoard } from '@/components/dashboard/task-queue-board';
import { Skeleton } from '@/components/ui/skeleton';
import { BackgroundAALChecker } from '@/components/auth/background-aal-checker';

export default function TaskQueuePage() {
  return (
    <BackgroundAALChecker>
      <div className="flex flex-col h-full w-full p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Task Queue</h1>
          <p className="text-muted-foreground">
            Visualize and manage tasks across all agents in Kanban-style view
          </p>
        </div>
        
        <Suspense
          fallback={
            <div className="space-y-4">
              <Skeleton className="h-96 w-full" />
            </div>
          }
        >
          <TaskQueueBoard />
        </Suspense>
      </div>
    </BackgroundAALChecker>
  );
}
