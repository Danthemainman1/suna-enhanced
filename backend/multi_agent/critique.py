"""
Critique collaboration mode.

One agent works while others review and provide feedback for improvement.
"""

import asyncio
from typing import Optional
from datetime import datetime
from .collaboration_modes import CollaborationModeBase
from .models import (
    CollaborationResult,
    CollaborationTask,
    CollaborationAgent,
    CritiqueConfig,
    CritiqueReview,
    CritiqueIteration,
    AgentRole
)


class CritiqueMode(CollaborationModeBase):
    """
    Critique collaboration mode.
    
    A primary agent produces output, which is then reviewed by critic agents.
    The primary agent iteratively improves based on feedback until the output
    meets the approval threshold or maximum iterations are reached.
    """
    
    name = "critique"
    description = "One agent works, others critique and improve"
    
    async def execute(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent],
        config: Optional[dict] = None
    ) -> CollaborationResult:
        """
        Execute critique mode.
        
        Args:
            task: The task to execute
            agents: Agents (first is primary, rest are critics)
            config: Critique configuration
            
        Returns:
            CollaborationResult: Critique results
        """
        start_time = datetime.utcnow()
        
        # Validate at least 2 agents (1 primary + 1 critic)
        await self.validate_agents(agents, min_agents=2)
        
        # Parse config
        critique_config = CritiqueConfig(**(config or {}))
        
        # Assign roles
        primary_agent = agents[0]
        primary_agent.role = AgentRole.PRIMARY
        
        critic_agents = agents[1:]
        for critic in critic_agents:
            critic.role = AgentRole.CRITIC
        
        # Iterative improvement loop
        iterations = []
        current_output = None
        approved = False
        
        for iteration_num in range(1, critique_config.max_iterations + 1):
            # Primary agent produces/improves output
            current_output = await self._produce_output(
                primary_agent,
                task,
                current_output,
                iterations
            )
            
            # Critics review the output
            reviews = await self._get_reviews(
                critic_agents,
                task,
                current_output,
                iteration_num,
                critique_config
            )
            
            # Calculate average score
            avg_score = sum(r.score for r in reviews) / len(reviews) if reviews else 0.0
            
            # Check if approved
            approved = avg_score >= critique_config.approval_threshold
            
            # Record iteration
            iteration = CritiqueIteration(
                iteration_number=iteration_num,
                primary_output=current_output,
                reviews=reviews,
                average_score=avg_score,
                approved=approved
            )
            iterations.append(iteration)
            
            # Break if approved
            if approved:
                break
        
        # Collect individual outputs
        individual_outputs = [
            {
                "agent_id": primary_agent.id,
                "role": "primary",
                "final_output": current_output,
                "iterations": len(iterations)
            }
        ]
        
        for critic in critic_agents:
            critic_reviews = [
                r for it in iterations for r in it.reviews if r.critic_id == critic.id
            ]
            individual_outputs.append({
                "agent_id": critic.id,
                "role": "critic",
                "total_reviews": len(critic_reviews),
                "average_score": (
                    sum(r.score for r in critic_reviews) / len(critic_reviews)
                    if critic_reviews else 0.0
                )
            })
        
        # Create result
        return self._create_result(
            mode=self.name,
            agents=agents,
            final_output={
                "output": current_output,
                "approved": approved,
                "iterations": len(iterations),
                "final_score": iterations[-1].average_score if iterations else 0.0
            },
            individual_outputs=individual_outputs,
            start_time=start_time,
            metadata={
                "total_iterations": len(iterations),
                "approved": approved,
                "approval_threshold": critique_config.approval_threshold,
                "max_iterations_reached": len(iterations) >= critique_config.max_iterations
            }
        )
    
    async def _produce_output(
        self,
        primary_agent: CollaborationAgent,
        task: CollaborationTask,
        previous_output: Optional[any],
        iterations: list[CritiqueIteration]
    ) -> any:
        """
        Primary agent produces or improves output.
        
        Args:
            primary_agent: The primary agent
            task: The task
            previous_output: Previous output (if any)
            iterations: Previous iterations with feedback
            
        Returns:
            any: New or improved output
        """
        # In a real implementation, this would invoke the actual agent
        # with the task and previous feedback
        
        if previous_output is None:
            # First iteration - produce initial output
            return f"Initial output from {primary_agent.name} for: {task.description}"
        else:
            # Improvement iteration - incorporate feedback
            latest_iteration = iterations[-1] if iterations else None
            if latest_iteration:
                feedback_summary = "; ".join([
                    r.feedback for r in latest_iteration.reviews
                ])
                return f"Improved output from {primary_agent.name} addressing: {feedback_summary}"
            else:
                return previous_output
    
    async def _get_reviews(
        self,
        critics: list[CollaborationAgent],
        task: CollaborationTask,
        output: any,
        iteration_num: int,
        config: CritiqueConfig
    ) -> list[CritiqueReview]:
        """
        Get reviews from critic agents.
        
        Args:
            critics: Critic agents
            task: The task
            output: Output to review
            iteration_num: Current iteration number
            config: Critique configuration
            
        Returns:
            list[CritiqueReview]: Reviews from all critics
        """
        if config.parallel_review:
            # Execute reviews in parallel
            review_tasks = [
                self._get_single_review(critic, task, output, iteration_num)
                for critic in critics
            ]
            reviews = await asyncio.gather(*review_tasks)
        else:
            # Execute reviews sequentially
            reviews = []
            for critic in critics:
                review = await self._get_single_review(
                    critic,
                    task,
                    output,
                    iteration_num
                )
                reviews.append(review)
        
        return reviews
    
    async def _get_single_review(
        self,
        critic: CollaborationAgent,
        task: CollaborationTask,
        output: any,
        iteration_num: int
    ) -> CritiqueReview:
        """
        Get review from a single critic.
        
        Args:
            critic: Critic agent
            task: The task
            output: Output to review
            iteration_num: Current iteration number
            
        Returns:
            CritiqueReview: The review
        """
        # In a real implementation, this would invoke the actual agent
        # to review the output and provide scored feedback
        
        # Placeholder: simulate improving scores over iterations
        base_score = 0.5 + (iteration_num * 0.15)
        score = min(base_score, 1.0)
        
        return CritiqueReview(
            critic_id=critic.id,
            iteration=iteration_num,
            score=score,
            feedback=f"Review from {critic.name}: {'Looks good!' if score >= 0.8 else 'Needs improvement.'}",
            suggestions=[
                "Consider improving clarity",
                "Add more detail",
                "Verify accuracy"
            ] if score < 0.8 else [],
            timestamp=datetime.utcnow()
        )
