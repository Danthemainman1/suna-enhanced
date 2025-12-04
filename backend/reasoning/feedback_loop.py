"""
Agent learning from task outcomes.

This module tracks agent performance, learns from successes and failures,
and optimizes strategies based on historical outcomes.
"""

from typing import Optional
from collections import defaultdict
from datetime import datetime
from .models import TaskOutcome, Strategy


class FeedbackLoop:
    """
    Implements learning from task outcomes.
    
    The feedback loop tracks task successes and failures, analyzes patterns,
    and helps agents improve their strategies over time.
    """
    
    def __init__(self):
        """Initialize the feedback loop."""
        self._outcomes: dict[str, list[TaskOutcome]] = defaultdict(list)
        self._strategies: dict[str, Strategy] = {}
        self._agent_stats: dict[str, dict] = defaultdict(lambda: {
            'total_tasks': 0,
            'successful_tasks': 0,
            'total_duration': 0.0
        })
    
    async def record_outcome(
        self,
        task_id: str,
        agent_id: str,
        success: bool,
        metrics: Optional[dict] = None,
        strategy_id: Optional[str] = None,
        error: Optional[str] = None
    ):
        """
        Record the outcome of a task.
        
        Args:
            task_id: Unique task identifier
            agent_id: Agent that executed the task
            success: Whether the task succeeded
            metrics: Performance metrics (e.g., duration, quality score)
            strategy_id: Strategy used (if any)
            error: Error message if failed
        """
        metrics = metrics or {}
        
        outcome = TaskOutcome(
            task_id=task_id,
            agent_id=agent_id,
            strategy_id=strategy_id,
            success=success,
            metrics=metrics,
            error=error
        )
        
        self._outcomes[agent_id].append(outcome)
        
        # Update agent statistics
        stats = self._agent_stats[agent_id]
        stats['total_tasks'] += 1
        if success:
            stats['successful_tasks'] += 1
        if 'duration' in metrics:
            stats['total_duration'] += metrics['duration']
        
        # Update strategy statistics if applicable
        if strategy_id and strategy_id in self._strategies:
            strategy = self._strategies[strategy_id]
            strategy.usage_count += 1
            strategy.last_used = datetime.utcnow()
            
            # Update success rate
            if strategy.usage_count > 0:
                # Get all outcomes for this strategy
                strategy_outcomes = [
                    o for o in self._outcomes[agent_id]
                    if o.strategy_id == strategy_id
                ]
                successful = sum(1 for o in strategy_outcomes if o.success)
                strategy.success_rate = successful / len(strategy_outcomes)
    
    async def get_success_rate(self, agent_id: str) -> float:
        """
        Get the success rate for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Success rate (0.0 to 1.0)
        """
        stats = self._agent_stats[agent_id]
        if stats['total_tasks'] == 0:
            return 0.0
        return stats['successful_tasks'] / stats['total_tasks']
    
    async def get_agent_metrics(self, agent_id: str) -> dict:
        """
        Get comprehensive metrics for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Dictionary with performance metrics
        """
        stats = self._agent_stats[agent_id]
        outcomes = self._outcomes[agent_id]
        
        if not outcomes:
            return {
                'success_rate': 0.0,
                'total_tasks': 0,
                'average_duration': 0.0,
                'recent_trend': 'no_data'
            }
        
        # Calculate average duration
        durations = [
            o.metrics.get('duration', 0.0) for o in outcomes
            if 'duration' in o.metrics
        ]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        # Calculate recent trend (last 10 tasks)
        recent = outcomes[-10:]
        recent_success_rate = sum(1 for o in recent if o.success) / len(recent)
        overall_success_rate = await self.get_success_rate(agent_id)
        
        if recent_success_rate > overall_success_rate + 0.1:
            trend = 'improving'
        elif recent_success_rate < overall_success_rate - 0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'success_rate': overall_success_rate,
            'total_tasks': stats['total_tasks'],
            'average_duration': avg_duration,
            'recent_trend': trend,
            'recent_success_rate': recent_success_rate
        }
    
    async def optimize_strategy(self, agent_id: str) -> Strategy:
        """
        Optimize strategy for an agent based on historical performance.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Optimized strategy
        """
        outcomes = self._outcomes[agent_id]
        
        if not outcomes:
            # Return default strategy
            return Strategy(
                strategy_id=f"default_{agent_id}",
                agent_id=agent_id,
                name="Default Strategy",
                description="Default strategy with no optimization",
                parameters={},
                success_rate=0.0,
                usage_count=0
            )
        
        # Analyze patterns in successful tasks
        successful = [o for o in outcomes if o.success]
        failed = [o for o in outcomes if not o.success]
        
        # Extract common patterns from successful tasks
        parameters = self._extract_success_patterns(successful, failed)
        
        # Calculate expected success rate
        success_rate = len(successful) / len(outcomes)
        
        # Create optimized strategy
        strategy = Strategy(
            strategy_id=f"optimized_{agent_id}_{datetime.utcnow().timestamp()}",
            agent_id=agent_id,
            name="Optimized Strategy",
            description="Strategy optimized based on historical performance",
            parameters=parameters,
            success_rate=success_rate,
            usage_count=0,
            metadata={
                'based_on_tasks': len(outcomes),
                'optimization_date': datetime.utcnow().isoformat()
            }
        )
        
        # Store the strategy
        self._strategies[strategy.strategy_id] = strategy
        
        return strategy
    
    def _extract_success_patterns(
        self,
        successful: list[TaskOutcome],
        failed: list[TaskOutcome]
    ) -> dict:
        """Extract patterns from successful vs failed outcomes."""
        parameters = {}
        
        # Analyze metrics to find patterns
        if successful:
            # Calculate average metrics for successful tasks
            all_metrics = {}
            for outcome in successful:
                for key, value in outcome.metrics.items():
                    if isinstance(value, (int, float)):
                        if key not in all_metrics:
                            all_metrics[key] = []
                        all_metrics[key].append(value)
            
            # Calculate averages
            for key, values in all_metrics.items():
                if values:
                    parameters[f'avg_{key}'] = sum(values) / len(values)
        
        # Add heuristics based on patterns
        if len(successful) > len(failed):
            parameters['approach'] = 'aggressive'
        else:
            parameters['approach'] = 'conservative'
        
        return parameters
    
    async def get_strategy(self, strategy_id: str) -> Optional[Strategy]:
        """
        Get a strategy by ID.
        
        Args:
            strategy_id: Strategy identifier
            
        Returns:
            Strategy if found, None otherwise
        """
        return self._strategies.get(strategy_id)
    
    async def list_strategies(self, agent_id: str) -> list[Strategy]:
        """
        List all strategies for an agent.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            List of strategies
        """
        return [
            strategy for strategy in self._strategies.values()
            if strategy.agent_id == agent_id
        ]
    
    def get_recent_outcomes(
        self,
        agent_id: str,
        limit: int = 10
    ) -> list[TaskOutcome]:
        """
        Get recent outcomes for an agent.
        
        Args:
            agent_id: Agent identifier
            limit: Maximum number of outcomes to return
            
        Returns:
            List of recent outcomes
        """
        outcomes = self._outcomes[agent_id]
        return outcomes[-limit:] if outcomes else []
