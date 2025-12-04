"""
Ensemble collaboration mode.

Multiple agents work in parallel, and results are merged using various strategies.
"""

import asyncio
from typing import Optional, Any
from datetime import datetime
from collections import Counter
from .collaboration_modes import CollaborationModeBase
from .models import (
    CollaborationResult,
    CollaborationTask,
    CollaborationAgent,
    EnsembleConfig,
    EnsembleVote,
    MergeStrategy
)


class EnsembleMode(CollaborationModeBase):
    """
    Ensemble collaboration mode.
    
    Multiple agents work on the same task in parallel. Their results
    are merged using various strategies (voting, averaging, LLM synthesis).
    """
    
    name = "ensemble"
    description = "Multiple agents work in parallel, results merged"
    
    async def execute(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent],
        config: Optional[dict] = None
    ) -> CollaborationResult:
        """
        Execute ensemble mode.
        
        Args:
            task: The task to execute
            agents: Agents in the ensemble
            config: Ensemble configuration
            
        Returns:
            CollaborationResult: Ensemble results
        """
        start_time = datetime.utcnow()
        
        # Validate at least 2 agents for ensemble
        await self.validate_agents(agents, min_agents=2)
        
        # Parse config
        ensemble_config = EnsembleConfig(**(config or {}))
        
        # Execute agents in parallel or sequentially
        if ensemble_config.parallel_execution:
            votes = await self._execute_parallel(task, agents)
        else:
            votes = await self._execute_sequential(task, agents)
        
        # Merge results based on strategy
        final_output = await self._merge_results(
            votes,
            ensemble_config
        )
        
        # Collect individual outputs
        individual_outputs = [
            {
                "agent_id": vote.agent_id,
                "output": vote.output,
                "confidence": vote.confidence,
                "reasoning": vote.reasoning
            }
            for vote in votes
        ]
        
        # Calculate agreement metrics
        agreement = self._calculate_agreement(votes, ensemble_config)
        
        # Create result
        return self._create_result(
            mode=self.name,
            agents=agents,
            final_output=final_output,
            individual_outputs=individual_outputs,
            start_time=start_time,
            metadata={
                "merge_strategy": ensemble_config.merge_strategy.value,
                "agreement": agreement,
                "total_votes": len(votes)
            }
        )
    
    async def _execute_parallel(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent]
    ) -> list[EnsembleVote]:
        """
        Execute agents in parallel.
        
        Args:
            task: Task to execute
            agents: Agents to execute
            
        Returns:
            list[EnsembleVote]: Votes from all agents
        """
        # Execute all agents concurrently
        tasks = [
            self._execute_agent(agent, task)
            for agent in agents
        ]
        
        votes = await asyncio.gather(*tasks)
        
        return votes
    
    async def _execute_sequential(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent]
    ) -> list[EnsembleVote]:
        """
        Execute agents sequentially.
        
        Args:
            task: Task to execute
            agents: Agents to execute
            
        Returns:
            list[EnsembleVote]: Votes from all agents
        """
        votes = []
        
        for agent in agents:
            vote = await self._execute_agent(agent, task)
            votes.append(vote)
        
        return votes
    
    async def _execute_agent(
        self,
        agent: CollaborationAgent,
        task: CollaborationTask
    ) -> EnsembleVote:
        """
        Execute a single agent.
        
        Args:
            agent: Agent to execute
            task: Task to execute
            
        Returns:
            EnsembleVote: Agent's vote
        """
        # In a real implementation, this would call the actual agent
        # For now, return a placeholder vote
        
        return EnsembleVote(
            agent_id=agent.id,
            output=f"Output from {agent.name} for task: {task.description}",
            confidence=0.8,
            reasoning=f"Agent {agent.name} analyzed the task and generated this output"
        )
    
    async def _merge_results(
        self,
        votes: list[EnsembleVote],
        config: EnsembleConfig
    ) -> Any:
        """
        Merge results using configured strategy.
        
        Args:
            votes: Votes from all agents
            config: Ensemble configuration
            
        Returns:
            Any: Merged result
        """
        if config.merge_strategy == MergeStrategy.VOTE:
            return self._merge_by_vote(votes)
        elif config.merge_strategy == MergeStrategy.AVERAGE:
            return self._merge_by_average(votes)
        elif config.merge_strategy == MergeStrategy.LLM_SYNTHESIS:
            return await self._merge_by_llm_synthesis(votes)
        else:
            return self._merge_by_vote(votes)
    
    def _merge_by_vote(self, votes: list[EnsembleVote]) -> Any:
        """
        Merge by majority vote.
        
        Args:
            votes: Votes to merge
            
        Returns:
            Any: Winning output
        """
        # Count occurrences of each output
        output_counter = Counter(
            str(vote.output) for vote in votes
        )
        
        # Return most common output
        most_common = output_counter.most_common(1)
        if most_common:
            winning_output_str = most_common[0][0]
            # Find original vote with this output
            for vote in votes:
                if str(vote.output) == winning_output_str:
                    return vote.output
        
        # Fallback: return first vote
        return votes[0].output if votes else None
    
    def _merge_by_average(self, votes: list[EnsembleVote]) -> Any:
        """
        Merge by averaging numeric outputs.
        
        Args:
            votes: Votes to merge
            
        Returns:
            Any: Average output
        """
        # Try to average numeric outputs
        numeric_outputs = []
        
        for vote in votes:
            try:
                if isinstance(vote.output, (int, float)):
                    numeric_outputs.append(vote.output)
                elif isinstance(vote.output, str):
                    numeric_outputs.append(float(vote.output))
            except (ValueError, TypeError):
                pass
        
        if numeric_outputs:
            return sum(numeric_outputs) / len(numeric_outputs)
        
        # Fallback to vote-based merging for non-numeric outputs
        return self._merge_by_vote(votes)
    
    async def _merge_by_llm_synthesis(
        self,
        votes: list[EnsembleVote]
    ) -> Any:
        """
        Merge using LLM to synthesize best answer.
        
        Args:
            votes: Votes to merge
            
        Returns:
            Any: Synthesized output
        """
        # In a real implementation, this would use Claude to:
        # 1. Analyze all outputs
        # 2. Identify common themes
        # 3. Synthesize the best answer
        
        # Placeholder: return highest confidence vote
        if votes:
            best_vote = max(votes, key=lambda v: v.confidence)
            return best_vote.output
        
        return None
    
    def _calculate_agreement(
        self,
        votes: list[EnsembleVote],
        config: EnsembleConfig
    ) -> float:
        """
        Calculate agreement level among agents.
        
        Args:
            votes: Votes from agents
            config: Ensemble configuration
            
        Returns:
            float: Agreement level (0.0 to 1.0)
        """
        if len(votes) < 2:
            return 1.0
        
        # Count most common output
        output_counter = Counter(
            str(vote.output) for vote in votes
        )
        
        if output_counter:
            most_common_count = output_counter.most_common(1)[0][1]
            return most_common_count / len(votes)
        
        return 0.0
