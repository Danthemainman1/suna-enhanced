import { Suspense } from 'react';
import { AgentControlCenter } from '@/components/dashboard/agent-control-center';
import { Skeleton } from '@/components/ui/skeleton';
import { BackgroundAALChecker } from '@/components/auth/background-aal-checker';

export default function AgentControlCenterPage() {
  return (
    <BackgroundAALChecker>
      <div className="flex flex-col h-full w-full p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Agent Control Center</h1>
          <p className="text-muted-foreground">
            Monitor and manage all your running agents in real-time
          </p>
        </div>
        
        <Suspense
          fallback={
            <div className="space-y-4">
              <Skeleton className="h-24 w-full" />
              <Skeleton className="h-64 w-full" />
            </div>
          }
        >
          <AgentControlCenter />
        </Suspense>
      </div>
    </BackgroundAALChecker>
  );
}
