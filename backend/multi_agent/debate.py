"""
Debate collaboration mode.

Agents argue different perspectives, and a judge decides the winner.
"""

import uuid
from typing import Optional
from datetime import datetime
from .collaboration_modes import CollaborationModeBase
from .models import (
    CollaborationResult,
    CollaborationTask,
    CollaborationAgent,
    DebateConfig,
    DebateArgument,
    DebateResult,
    AgentRole
)


class DebateMode(CollaborationModeBase):
    """
    Debate collaboration mode.
    
    Multiple agents argue different perspectives on a task, presenting
    arguments over multiple rounds. A judge agent (or Claude) evaluates
    all arguments and selects the winning position.
    """
    
    name = "debate"
    description = "Agents argue different perspectives, judge decides winner"
    
    async def execute(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent],
        config: Optional[dict] = None
    ) -> CollaborationResult:
        """
        Execute debate mode.
        
        Args:
            task: The task to debate
            agents: Agents participating in debate
            config: Debate configuration
            
        Returns:
            CollaborationResult: Debate results
        """
        start_time = datetime.utcnow()
        
        # Validate at least 2 agents for debate
        await self.validate_agents(agents, min_agents=2)
        
        # Parse config
        debate_config = DebateConfig(**(config or {}))
        
        # Assign positions to agents
        debaters = self._assign_positions(agents, debate_config)
        
        # Conduct debate rounds
        arguments = []
        individual_outputs = []
        
        for round_num in range(1, debate_config.rounds + 1):
            round_args = await self._conduct_round(
                task,
                debaters,
                round_num,
                arguments
            )
            arguments.extend(round_args)
        
        # Judge the debate
        debate_result = await self._judge_debate(
            task,
            arguments,
            debate_config
        )
        
        # Collect individual outputs
        for agent in debaters:
            agent_args = [arg for arg in arguments if arg.agent_id == agent.id]
            individual_outputs.append({
                "agent_id": agent.id,
                "position": agent.position,
                "arguments": [arg.argument for arg in agent_args]
            })
        
        # Create result
        return self._create_result(
            mode=self.name,
            agents=agents,
            final_output={
                "winner": debate_result.winner,
                "winning_agent": debate_result.winning_agent_id,
                "judge_reasoning": debate_result.judge_reasoning,
                "confidence": debate_result.confidence
            },
            individual_outputs=individual_outputs,
            start_time=start_time,
            metadata={
                "rounds": debate_config.rounds,
                "total_arguments": len(arguments),
                "debate_result": debate_result.model_dump()
            }
        )
    
    def _assign_positions(
        self,
        agents: list[CollaborationAgent],
        config: DebateConfig
    ) -> list[CollaborationAgent]:
        """
        Assign debate positions to agents.
        
        Args:
            agents: Agents to assign positions
            config: Debate configuration
            
        Returns:
            list[CollaborationAgent]: Agents with positions assigned
        """
        # Simple alternating assignment
        positions = ["pro", "con"]
        
        for i, agent in enumerate(agents):
            agent.position = positions[i % len(positions)]
            agent.role = AgentRole.SPECIALIST
        
        return agents
    
    async def _conduct_round(
        self,
        task: CollaborationTask,
        debaters: list[CollaborationAgent],
        round_num: int,
        previous_arguments: list[DebateArgument]
    ) -> list[DebateArgument]:
        """
        Conduct one round of debate.
        
        Args:
            task: The task being debated
            debaters: Debating agents
            round_num: Current round number
            previous_arguments: Arguments from previous rounds
            
        Returns:
            list[DebateArgument]: Arguments from this round
        """
        round_args = []
        
        for agent in debaters:
            # In a real implementation, this would call the actual agent
            # to generate an argument based on task and previous arguments
            
            argument_text = self._generate_argument(
                agent,
                task,
                round_num,
                previous_arguments
            )
            
            argument = DebateArgument(
                agent_id=agent.id,
                round=round_num,
                position=agent.position or "neutral",
                argument=argument_text,
                timestamp=datetime.utcnow()
            )
            
            round_args.append(argument)
        
        return round_args
    
    def _generate_argument(
        self,
        agent: CollaborationAgent,
        task: CollaborationTask,
        round_num: int,
        previous_arguments: list[DebateArgument]
    ) -> str:
        """
        Generate an argument for an agent.
        
        Args:
            agent: The agent making the argument
            task: The task being debated
            round_num: Current round number
            previous_arguments: Previous arguments
            
        Returns:
            str: The argument text
        """
        # Placeholder implementation
        # In a real system, this would invoke the agent's LLM
        
        position = agent.position or "neutral"
        
        if round_num == 1:
            return f"Opening argument from {agent.name} ({position}): Supporting the {position} position on {task.description}"
        else:
            opposing_args = [
                arg for arg in previous_arguments
                if arg.position != position and arg.round == round_num - 1
            ]
            return f"Round {round_num} argument from {agent.name} ({position}): Responding to {len(opposing_args)} opposing arguments"
    
    async def _judge_debate(
        self,
        task: CollaborationTask,
        arguments: list[DebateArgument],
        config: DebateConfig
    ) -> DebateResult:
        """
        Judge the debate and select winner.
        
        Args:
            task: The task that was debated
            arguments: All arguments from the debate
            config: Debate configuration
            
        Returns:
            DebateResult: Judgment results
        """
        # In a real implementation, this would:
        # 1. Use the judge agent if specified
        # 2. Otherwise use Claude to evaluate arguments
        # 3. Provide detailed reasoning
        
        # Placeholder: count arguments per position
        position_counts = {}
        for arg in arguments:
            position_counts[arg.position] = position_counts.get(arg.position, 0) + 1
        
        # Simple majority wins
        winner = max(position_counts.items(), key=lambda x: x[1])[0]
        
        # Find winning agent (first agent with winning position)
        winning_agent = next(
            (arg.agent_id for arg in arguments if arg.position == winner),
            ""
        )
        
        return DebateResult(
            winner=winner,
            winning_agent_id=winning_agent,
            arguments=arguments,
            judge_reasoning=f"The {winner} position presented more comprehensive arguments across {len(arguments)} total arguments.",
            confidence=0.75
        )
