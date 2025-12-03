import { Suspense } from 'react';
import { WorkflowBuilder } from '@/components/dashboard/workflow-builder';
import { Skeleton } from '@/components/ui/skeleton';
import { BackgroundAALChecker } from '@/components/auth/background-aal-checker';

export default function WorkflowsPage() {
  return (
    <BackgroundAALChecker>
      <div className="flex flex-col h-full w-full p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Workflow Builder</h1>
          <p className="text-muted-foreground">
            Create and manage complex multi-agent workflows with drag-and-drop
          </p>
        </div>
        
        <Suspense
          fallback={
            <div className="space-y-4">
              <Skeleton className="h-96 w-full" />
            </div>
          }
        >
          <WorkflowBuilder />
        </Suspense>
      </div>
    </BackgroundAALChecker>
  );
}
