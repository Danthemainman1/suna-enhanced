"""
Pipeline collaboration mode.

Sequential handoff between specialist agents, each processing in turn.
"""

from typing import Optional, Any
from datetime import datetime
from .collaboration_modes import CollaborationModeBase
from .models import (
    CollaborationResult,
    CollaborationTask,
    CollaborationAgent,
    PipelineConfig,
    PipelineStage,
    HandoffFormat
)


class PipelineMode(CollaborationModeBase):
    """
    Pipeline collaboration mode.
    
    Agents work sequentially, each processing the output of the previous
    agent. Useful for multi-stage tasks where specialists handle different
    phases.
    """
    
    name = "pipeline"
    description = "Sequential handoff between specialist agents"
    
    async def execute(
        self,
        task: CollaborationTask,
        agents: list[CollaborationAgent],
        config: Optional[dict] = None
    ) -> CollaborationResult:
        """
        Execute pipeline mode.
        
        Args:
            task: The task to execute
            agents: Agents in pipeline order
            config: Pipeline configuration
            
        Returns:
            CollaborationResult: Pipeline results
        """
        start_time = datetime.utcnow()
        
        # Validate at least 2 agents for pipeline
        await self.validate_agents(agents, min_agents=2)
        
        # Parse config
        pipeline_config = PipelineConfig(**(config or {}))
        
        # Execute pipeline stages
        stages = []
        current_input = {
            "task_description": task.description,
            "requirements": task.requirements,
            "context": task.context
        }
        
        for stage_num, agent in enumerate(agents, start=1):
            stage = await self._execute_stage(
                stage_num,
                agent,
                current_input,
                pipeline_config
            )
            
            stages.append(stage)
            
            # Use output as input for next stage
            if stage.output_data:
                current_input = stage.output_data
            elif pipeline_config.allow_backtrack:
                # Backtrack if stage failed and backtracking is allowed
                if stage_num > 1:
                    # Use input from previous stage
                    current_input = stages[stage_num - 2].output_data or current_input
        
        # Final output is from last stage
        final_output = stages[-1].output_data if stages else None
        
        # Collect individual outputs
        individual_outputs = [
            {
                "agent_id": stage.agent_id,
                "stage": stage.stage_number,
                "input": stage.input_data,
                "output": stage.output_data,
                "status": stage.status
            }
            for stage in stages
        ]
        
        # Create result
        return self._create_result(
            mode=self.name,
            agents=agents,
            final_output=final_output,
            individual_outputs=individual_outputs,
            start_time=start_time,
            metadata={
                "total_stages": len(stages),
                "successful_stages": sum(1 for s in stages if s.status == "completed"),
                "handoff_format": pipeline_config.handoff_format.value
            }
        )
    
    async def _execute_stage(
        self,
        stage_number: int,
        agent: CollaborationAgent,
        input_data: dict,
        config: PipelineConfig
    ) -> PipelineStage:
        """
        Execute one pipeline stage.
        
        Args:
            stage_number: Stage sequence number
            agent: Agent handling this stage
            input_data: Input for this stage
            config: Pipeline configuration
            
        Returns:
            PipelineStage: Stage results
        """
        stage = PipelineStage(
            stage_number=stage_number,
            agent_id=agent.id,
            input_data=input_data,
            status="running",
            started_at=datetime.utcnow()
        )
        
        try:
            # In a real implementation, this would call the actual agent
            # For now, transform the input based on handoff format
            
            if config.handoff_format == HandoffFormat.STRUCTURED:
                output = self._process_structured(agent, input_data)
            else:
                output = self._process_natural(agent, input_data)
            
            stage.output_data = output
            stage.status = "completed"
            stage.completed_at = datetime.utcnow()
            
        except Exception as e:
            stage.status = "failed"
            stage.output_data = {"error": str(e)}
            stage.completed_at = datetime.utcnow()
        
        return stage
    
    def _process_structured(
        self,
        agent: CollaborationAgent,
        input_data: dict
    ) -> dict:
        """
        Process with structured handoff format.
        
        Args:
            agent: Agent processing the stage
            input_data: Structured input data
            
        Returns:
            dict: Structured output data
        """
        # In a real implementation, this would invoke the agent
        # For now, create a structured transformation
        
        return {
            "processed_by": agent.id,
            "agent_name": agent.name,
            "input_summary": str(input_data)[:100],
            "result": f"Processed by {agent.name}",
            "next_steps": []
        }
    
    def _process_natural(
        self,
        agent: CollaborationAgent,
        input_data: dict
    ) -> dict:
        """
        Process with natural language handoff format.
        
        Args:
            agent: Agent processing the stage
            input_data: Input data
            
        Returns:
            dict: Output with natural language description
        """
        # In a real implementation, this would invoke the agent
        # For now, create a natural language transformation
        
        return {
            "processed_by": agent.id,
            "narrative": f"{agent.name} received the input and processed it accordingly.",
            "output": f"Natural language output from {agent.name}",
            "handoff_note": "Ready for next agent in pipeline"
        }
