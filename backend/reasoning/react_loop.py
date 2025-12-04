"""
ReAct (Reasoning + Acting) loop implementation.

This module implements the ReAct paradigm which interleaves reasoning
and action execution, allowing agents to reason about what to do and
then act on those decisions iteratively.
"""

import time
from typing import Optional, Callable, Any
from .models import ReActStep, ReActResult, Action, Observation
from llm.provider import LLMProvider


class ReActLoop:
    """
    Implements the ReAct (Reasoning + Acting) paradigm.
    
    ReAct interleaves reasoning steps with action execution, allowing the
    agent to observe the results of its actions and adapt its reasoning accordingly.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize the ReAct loop.
        
        Args:
            llm_provider: LLM provider for reasoning
        """
        self.llm_provider = llm_provider
        self._trajectory: list[ReActStep] = []
    
    async def run(
        self,
        goal: str,
        available_actions: list[Action],
        max_iterations: int = 10,
        action_executor: Optional[Callable[[Action], Any]] = None
    ) -> ReActResult:
        """
        Run the ReAct loop to achieve a goal.
        
        Args:
            goal: The goal to achieve
            available_actions: List of actions the agent can take
            max_iterations: Maximum number of iterations
            action_executor: Optional function to execute actions (for testing, pass None)
            
        Returns:
            ReActResult with trajectory and outcome
        """
        start_time = time.time()
        self._trajectory = []
        
        context = self._build_initial_context(goal, available_actions)
        goal_achieved = False
        final_answer = None
        
        for iteration in range(max_iterations):
            # Reasoning step: Think about what to do next
            thought = await self._reason_next_step(goal, context, available_actions)
            
            # Check if we've reached the goal
            if self._is_goal_achieved(thought, goal):
                goal_achieved = True
                final_answer = self._extract_answer(thought)
                
                # Add final step
                self._trajectory.append(ReActStep(
                    step_number=iteration + 1,
                    thought=thought
                ))
                break
            
            # Action step: Select and execute an action
            action = await self._select_action(thought, available_actions)
            
            if action is None:
                # No action needed, just reasoning
                self._trajectory.append(ReActStep(
                    step_number=iteration + 1,
                    thought=thought
                ))
                continue
            
            # Execute the action
            observation = await self._execute_action(action, action_executor)
            
            # Add step to trajectory
            self._trajectory.append(ReActStep(
                step_number=iteration + 1,
                thought=thought,
                action=action,
                observation=observation
            ))
            
            # Update context with observation
            context = self._update_context(context, thought, action, observation)
        
        duration = time.time() - start_time
        
        return ReActResult(
            goal=goal,
            steps=self._trajectory,
            goal_achieved=goal_achieved,
            final_answer=final_answer,
            iterations_used=len(self._trajectory),
            duration_seconds=duration,
            metadata={
                "max_iterations": max_iterations,
                "actions_available": len(available_actions)
            }
        )
    
    def _build_initial_context(
        self,
        goal: str,
        available_actions: list[Action]
    ) -> str:
        """Build the initial context for reasoning."""
        actions_desc = "\n".join([
            f"- {action.name}: {action.description}"
            for action in available_actions
        ])
        
        return f"""Goal: {goal}

Available actions:
{actions_desc}

You can take actions to work towards the goal. After each action, you'll observe the result.
Think step by step about what to do next.
"""
    
    async def _reason_next_step(
        self,
        goal: str,
        context: str,
        available_actions: list[Action]
    ) -> str:
        """Reason about what to do next."""
        prompt = f"""{context}

Based on the goal and previous observations, what should we do next?

Think through:
1. What have we learned so far?
2. What do we still need to know or do?
3. What's the best next action?

If you've achieved the goal, state "Goal achieved:" followed by your final answer.
Otherwise, describe your reasoning and what action to take next.
"""
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=300
        )
        
        return response.content.strip()
    
    def _is_goal_achieved(self, thought: str, goal: str) -> bool:
        """Check if the goal has been achieved based on the thought."""
        thought_lower = thought.lower()
        return any(phrase in thought_lower for phrase in [
            "goal achieved",
            "task completed",
            "finished",
            "done",
            "final answer"
        ])
    
    def _extract_answer(self, thought: str) -> str:
        """Extract the final answer from a thought."""
        # Look for "Goal achieved:" or similar markers
        markers = ["goal achieved:", "final answer:", "answer:", "result:"]
        
        for marker in markers:
            if marker in thought.lower():
                idx = thought.lower().index(marker)
                return thought[idx + len(marker):].strip()
        
        return thought
    
    async def _select_action(
        self,
        thought: str,
        available_actions: list[Action]
    ) -> Optional[Action]:
        """Select an action based on the reasoning."""
        # Check if the thought mentions any action
        thought_lower = thought.lower()
        
        for action in available_actions:
            if action.name.lower() in thought_lower:
                return action
        
        # If no specific action mentioned, ask LLM to choose
        actions_list = "\n".join([
            f"{i+1}. {action.name}: {action.description}"
            for i, action in enumerate(available_actions)
        ])
        
        prompt = f"""Thought: {thought}

Available actions:
{actions_list}

Which action should be taken? Respond with just the action name, or "none" if no action is needed.
"""
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=50
        )
        
        action_name = response.content.strip().lower()
        
        # Find matching action
        for action in available_actions:
            if action.name.lower() in action_name:
                return action
        
        return None
    
    async def _execute_action(
        self,
        action: Action,
        action_executor: Optional[Callable[[Action], Any]]
    ) -> Observation:
        """Execute an action and return observation."""
        if action_executor:
            # Use provided executor
            try:
                result = action_executor(action)
                # Handle async executors
                if hasattr(result, '__await__'):
                    result = await result
                
                return Observation(
                    action_id=action.action_id,
                    success=True,
                    result=result
                )
            except Exception as e:
                return Observation(
                    action_id=action.action_id,
                    success=False,
                    error=str(e)
                )
        else:
            # Simulate action execution with LLM
            return await self._simulate_action(action)
    
    async def _simulate_action(self, action: Action) -> Observation:
        """Simulate action execution using LLM."""
        prompt = f"""Simulate the result of executing this action:

Action: {action.name}
Description: {action.description}
Parameters: {action.parameters}

What would be the likely result or observation from executing this action?
Provide a realistic simulation of what would happen.
"""
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=200
        )
        
        return Observation(
            action_id=action.action_id,
            success=True,
            result=response.content.strip(),
            metadata={"simulated": True}
        )
    
    def _update_context(
        self,
        context: str,
        thought: str,
        action: Optional[Action],
        observation: Optional[Observation]
    ) -> str:
        """Update context with new information."""
        context += f"\n\nThought: {thought}"
        
        if action:
            context += f"\nAction taken: {action.name}"
        
        if observation:
            if observation.success:
                context += f"\nObservation: {observation.result}"
            else:
                context += f"\nObservation: Action failed - {observation.error}"
        
        return context
    
    def get_trajectory(self) -> list[ReActStep]:
        """
        Get the trajectory of ReAct steps from last execution.
        
        Returns:
            List of ReActStep objects
        """
        return self._trajectory
