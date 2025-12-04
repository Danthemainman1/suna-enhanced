"""
FastAPI router for debugger endpoints.

This module provides REST API endpoints for agent debugging,
including step debugging, time travel, execution graphs, and AI explanations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .step_debugger import AgentDebugger
from .time_travel import TimeTravelDebugger
from .execution_graph import ExecutionGraphGenerator
from .explainer import AgentExplainer
from .breakpoints import BreakpointManager
from .inspector import StateInspector
from .models import (
    DebugSession,
    DebugState,
    ReplaySession,
    ExecutionSnapshot,
    ExecutionGraph,
    Explanation,
    FailureExplanation,
    Suggestion,
    Breakpoint,
    BreakpointType
)


# Initialize components
router = APIRouter(prefix="/debug", tags=["debugger"])
agent_debugger = AgentDebugger()
time_travel_debugger = TimeTravelDebugger()
execution_graph_generator = ExecutionGraphGenerator()
agent_explainer = AgentExplainer()
breakpoint_manager = BreakpointManager()
state_inspector = StateInspector()


# Debugger Endpoints
@router.post("/attach", response_model=DebugSession)
async def attach_debugger(agent_id: str, task_id: str):
    """
    Attach debugger to a running task.
    
    Args:
        agent_id: ID of the agent to debug
        task_id: ID of the task to debug
        
    Returns:
        DebugSession: The created debug session
    """
    try:
        session = await agent_debugger.attach(agent_id, task_id)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/detach")
async def detach_debugger(session_id: str):
    """
    Detach debugger from a task.
    
    Args:
        session_id: ID of the debug session
        
    Returns:
        dict: Success status
    """
    try:
        success = await agent_debugger.detach(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Debug session not found")
        return {"success": True, "message": "Debugger detached"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/step", response_model=DebugState)
async def step_debugger(session_id: str):
    """
    Execute one step and pause.
    
    Args:
        session_id: ID of the debug session
        
    Returns:
        DebugState: State after executing the step
    """
    try:
        state = await agent_debugger.step(session_id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/pause", response_model=DebugState)
async def pause_debugger(session_id: str):
    """
    Pause execution at current step.
    
    Args:
        session_id: ID of the debug session
        
    Returns:
        DebugState: Current execution state
    """
    try:
        state = await agent_debugger.pause(session_id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/continue")
async def continue_debugger(session_id: str):
    """
    Continue execution until next breakpoint or end.
    
    Args:
        session_id: ID of the debug session
        
    Returns:
        dict: Success status
    """
    try:
        await agent_debugger.continue_run(session_id)
        return {"success": True, "message": "Execution continued"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/state", response_model=DebugState)
async def get_debug_state(session_id: str):
    """
    Get current execution state.
    
    Args:
        session_id: ID of the debug session
        
    Returns:
        DebugState: Current state
    """
    try:
        state = await agent_debugger.get_state(session_id)
        return state
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/variables")
async def get_debug_variables(session_id: str):
    """
    Get all variables in current scope.
    
    Args:
        session_id: ID of the debug session
        
    Returns:
        dict: Variables in current scope
    """
    try:
        variables = await agent_debugger.get_variables(session_id)
        return {"variables": variables}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/evaluate")
async def evaluate_expression(session_id: str, expression: str):
    """
    Evaluate expression in current context.
    
    Args:
        session_id: ID of the debug session
        expression: Expression to evaluate
        
    Returns:
        dict: Evaluation result
    """
    try:
        result = await agent_debugger.evaluate(session_id, expression)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Time Travel Endpoints
@router.get("/tasks/{task_id}/history", response_model=list[ExecutionSnapshot])
async def get_execution_history(task_id: str):
    """
    Get execution history for a task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        list[ExecutionSnapshot]: All execution snapshots
    """
    try:
        history = await time_travel_debugger.get_execution_history(task_id)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tasks/{task_id}/replay", response_model=ReplaySession)
async def create_replay_session(task_id: str):
    """
    Create a replay session for a task.
    
    Args:
        task_id: ID of the task to replay
        
    Returns:
        ReplaySession: The created replay session
    """
    try:
        session = await time_travel_debugger.create_replay(task_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay/{session_id}/step-forward", response_model=ExecutionSnapshot)
async def replay_step_forward(session_id: str):
    """
    Move to next snapshot in replay.
    
    Args:
        session_id: ID of the replay session
        
    Returns:
        ExecutionSnapshot: The next snapshot
    """
    try:
        snapshot = await time_travel_debugger.step_forward(session_id)
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay/{session_id}/step-backward", response_model=ExecutionSnapshot)
async def replay_step_backward(session_id: str):
    """
    Move to previous snapshot in replay.
    
    Args:
        session_id: ID of the replay session
        
    Returns:
        ExecutionSnapshot: The previous snapshot
    """
    try:
        snapshot = await time_travel_debugger.step_backward(session_id)
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/replay/{session_id}/jump-to/{step_number}", response_model=ExecutionSnapshot)
async def replay_jump_to(session_id: str, step_number: int):
    """
    Jump to specific step in replay.
    
    Args:
        session_id: ID of the replay session
        step_number: Step number to jump to
        
    Returns:
        ExecutionSnapshot: The snapshot at the specified step
    """
    try:
        snapshot = await time_travel_debugger.jump_to(session_id, step_number)
        return snapshot
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Execution Graph Endpoints
@router.get("/tasks/{task_id}/graph", response_model=ExecutionGraph)
async def get_execution_graph(task_id: str):
    """
    Get execution graph for a task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        ExecutionGraph: The execution graph
    """
    try:
        graph = await execution_graph_generator.generate(task_id)
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/graph/mermaid")
async def get_graph_mermaid(task_id: str):
    """
    Get execution graph as Mermaid diagram.
    
    Args:
        task_id: ID of the task
        
    Returns:
        dict: Mermaid diagram syntax
    """
    try:
        graph = await execution_graph_generator.generate(task_id)
        mermaid = execution_graph_generator.to_mermaid(graph)
        return {"mermaid": mermaid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/graph/dot")
async def get_graph_dot(task_id: str):
    """
    Get execution graph as Graphviz DOT format.
    
    Args:
        task_id: ID of the task
        
    Returns:
        dict: DOT format syntax
    """
    try:
        graph = await execution_graph_generator.generate(task_id)
        dot = execution_graph_generator.to_dot(graph)
        return {"dot": dot}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Explainer Endpoints
@router.get("/tasks/{task_id}/explain", response_model=list[Suggestion])
async def explain_task(task_id: str):
    """
    Get improvement suggestions for a task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        list[Suggestion]: Improvement suggestions
    """
    try:
        suggestions = await agent_explainer.suggest_improvements(task_id)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/steps/{step_id}/explain", response_model=Explanation)
async def explain_step(task_id: str, step_id: str):
    """
    Explain a specific step in task execution.
    
    Args:
        task_id: ID of the task
        step_id: ID of the step to explain
        
    Returns:
        Explanation: Detailed explanation of the step
    """
    try:
        explanation = await agent_explainer.explain_decision(task_id, step_id)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/failure", response_model=FailureExplanation)
async def explain_failure(task_id: str):
    """
    Explain why a task failed.
    
    Args:
        task_id: ID of the failed task
        
    Returns:
        FailureExplanation: Detailed failure explanation
    """
    try:
        explanation = await agent_explainer.explain_failure(task_id)
        return explanation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks/{task_id}/suggestions", response_model=list[Suggestion])
async def get_suggestions(task_id: str):
    """
    Get improvement suggestions for a task.
    
    Args:
        task_id: ID of the task
        
    Returns:
        list[Suggestion]: Improvement suggestions
    """
    try:
        suggestions = await agent_explainer.suggest_improvements(task_id)
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Breakpoint Endpoints
@router.post("/{session_id}/breakpoints", response_model=Breakpoint)
async def add_breakpoint(
    session_id: str,
    breakpoint_type: BreakpointType,
    condition: Optional[str] = None,
    step_number: Optional[int] = None,
    tool_name: Optional[str] = None
):
    """
    Add a breakpoint to a debug session.
    
    Args:
        session_id: Debug session ID
        breakpoint_type: Type of breakpoint
        condition: Condition expression (for conditional breakpoints)
        step_number: Step number (for step breakpoints)
        tool_name: Tool name (for tool breakpoints)
        
    Returns:
        Breakpoint: The created breakpoint
    """
    try:
        breakpoint = await breakpoint_manager.add_breakpoint(
            session_id,
            breakpoint_type,
            condition,
            step_number,
            tool_name
        )
        return breakpoint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/breakpoints", response_model=list[Breakpoint])
async def list_breakpoints(session_id: str):
    """
    List all breakpoints for a debug session.
    
    Args:
        session_id: Debug session ID
        
    Returns:
        list[Breakpoint]: All breakpoints
    """
    try:
        breakpoints = await breakpoint_manager.list_breakpoints(session_id)
        return breakpoints
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/breakpoints/{breakpoint_id}")
async def remove_breakpoint(breakpoint_id: str):
    """
    Remove a breakpoint.
    
    Args:
        breakpoint_id: ID of the breakpoint to remove
        
    Returns:
        dict: Success status
    """
    try:
        success = await breakpoint_manager.remove_breakpoint(breakpoint_id)
        if not success:
            raise HTTPException(status_code=404, detail="Breakpoint not found")
        return {"success": True, "message": "Breakpoint removed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Initialize function for app startup
async def initialize():
    """Initialize the debugger API components."""
    pass


# Cleanup function for app shutdown
async def cleanup():
    """Cleanup debugger API components."""
    pass
