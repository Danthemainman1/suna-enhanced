import { Suspense } from 'react';
import { AgentMarketplace } from '@/components/dashboard/agent-marketplace';
import { Skeleton } from '@/components/ui/skeleton';
import { BackgroundAALChecker } from '@/components/auth/background-aal-checker';

export default function MarketplacePage() {
  return (
    <BackgroundAALChecker>
      <div className="flex flex-col h-full w-full p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Agent Marketplace</h1>
          <p className="text-muted-foreground">
            Browse, install, and manage pre-built agent templates
          </p>
        </div>
        
        <Suspense
          fallback={
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <Skeleton key={i} className="h-64 w-full" />
                ))}
              </div>
            </div>
          }
        >
          <AgentMarketplace />
        </Suspense>
      </div>
    </BackgroundAALChecker>
  );
}
