"""
Tests for reasoning engines.

This module tests Chain-of-Thought, Tree-of-Thoughts, ReAct,
self-reflection, feedback loops, and prompt optimization.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from reasoning import (
    ChainOfThoughtReasoner,
    TreeOfThoughts,
    ReActLoop,
    SelfReflection,
    FeedbackLoop,
    PromptOptimizer,
    Action,
    Critique,
    Strategy,
)


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    provider = AsyncMock()
    
    # Mock generate method
    async def mock_generate(prompt, **kwargs):
        response = MagicMock()
        response.content = "Step 1: Think about the problem\nStep 2: Break it down\nConclusion: Solution found"
        response.model = "test-model"
        return response
    
    provider.generate = mock_generate
    return provider


# Chain-of-Thought Tests
@pytest.mark.asyncio
async def test_chain_of_thought_basic(mock_llm_provider):
    """Test basic Chain-of-Thought reasoning."""
    reasoner = ChainOfThoughtReasoner(mock_llm_provider, max_steps=5)
    
    result = await reasoner.reason(
        problem="What is 2+2?",
        context={"difficulty": "easy"}
    )
    
    assert result.problem == "What is 2+2?"
    assert len(result.steps) > 0
    assert result.conclusion is not None
    assert result.reasoning_type == "chain_of_thought"
    assert result.duration_seconds >= 0


@pytest.mark.asyncio
async def test_chain_of_thought_with_few_shot(mock_llm_provider):
    """Test CoT with few-shot examples."""
    reasoner = ChainOfThoughtReasoner(mock_llm_provider)
    
    result = await reasoner.reason(
        problem="Solve a complex problem",
        use_few_shot=True
    )
    
    assert result.steps is not None
    assert result.metadata.get('few_shot_used') is True


@pytest.mark.asyncio
async def test_get_reasoning_trace(mock_llm_provider):
    """Test getting reasoning trace."""
    reasoner = ChainOfThoughtReasoner(mock_llm_provider)
    
    await reasoner.reason(problem="Test problem")
    trace = reasoner.get_reasoning_trace()
    
    assert isinstance(trace, list)
    assert len(trace) > 0


@pytest.mark.asyncio
async def test_visualize_steps(mock_llm_provider):
    """Test visualization of reasoning steps."""
    reasoner = ChainOfThoughtReasoner(mock_llm_provider)
    
    await reasoner.reason(problem="Test problem")
    visualization = reasoner.visualize_steps()
    
    assert isinstance(visualization, str)
    assert "Chain of Thought" in visualization


# Tree-of-Thoughts Tests
@pytest.mark.asyncio
async def test_tree_of_thoughts_breadth_first(mock_llm_provider):
    """Test ToT with breadth-first exploration."""
    tot = TreeOfThoughts(mock_llm_provider, evaluation_threshold=0.5)
    
    result = await tot.explore(
        problem="Test problem",
        max_depth=2,
        branching_factor=2,
        strategy="breadth_first"
    )
    
    assert result.problem == "Test problem"
    assert result.exploration_strategy == "breadth_first"
    assert result.nodes_explored > 0
    assert len(result.nodes) > 0


@pytest.mark.asyncio
async def test_tree_of_thoughts_depth_first(mock_llm_provider):
    """Test ToT with depth-first exploration."""
    tot = TreeOfThoughts(mock_llm_provider)
    
    result = await tot.explore(
        problem="Test problem",
        max_depth=2,
        branching_factor=2,
        strategy="depth_first"
    )
    
    assert result.exploration_strategy == "depth_first"
    assert result.max_depth_reached <= 2


@pytest.mark.asyncio
async def test_get_best_path(mock_llm_provider):
    """Test getting best path from ToT."""
    tot = TreeOfThoughts(mock_llm_provider)
    
    await tot.explore(problem="Test", max_depth=2, branching_factor=2)
    best_path = tot.get_best_path()
    
    assert isinstance(best_path, list)


@pytest.mark.asyncio
async def test_to_graph(mock_llm_provider):
    """Test converting ToT to graph representation."""
    tot = TreeOfThoughts(mock_llm_provider)
    
    await tot.explore(problem="Test", max_depth=2, branching_factor=2)
    graph = tot.to_graph()
    
    assert 'nodes' in graph
    assert 'edges' in graph
    assert isinstance(graph['nodes'], list)


# ReAct Loop Tests
@pytest.mark.asyncio
async def test_react_loop_basic(mock_llm_provider):
    """Test basic ReAct loop execution."""
    react = ReActLoop(mock_llm_provider)
    
    # Create test actions
    actions = [
        Action(
            action_id="action_1",
            name="search",
            description="Search for information"
        ),
        Action(
            action_id="action_2",
            name="analyze",
            description="Analyze results"
        )
    ]
    
    result = await react.run(
        goal="Find information about AI",
        available_actions=actions,
        max_iterations=3
    )
    
    assert result.goal == "Find information about AI"
    assert result.iterations_used <= 3
    assert len(result.steps) > 0


@pytest.mark.asyncio
async def test_react_trajectory(mock_llm_provider):
    """Test getting ReAct trajectory."""
    react = ReActLoop(mock_llm_provider)
    
    actions = [Action(action_id="1", name="test", description="Test action")]
    await react.run(goal="Test", available_actions=actions, max_iterations=2)
    
    trajectory = react.get_trajectory()
    assert isinstance(trajectory, list)


# Self-Reflection Tests
@pytest.mark.asyncio
async def test_self_reflection_basic(mock_llm_provider):
    """Test basic self-reflection."""
    reflection = SelfReflection(mock_llm_provider, max_iterations=2)
    
    result = await reflection.reflect(
        output="This is a test output",
        context={"task": "test"}
    )
    
    assert result.original_output == "This is a test output"
    assert result.critique is not None
    assert result.reflection_iterations >= 1


@pytest.mark.asyncio
async def test_critique_generation(mock_llm_provider):
    """Test critique generation."""
    reflection = SelfReflection(mock_llm_provider)
    
    critique = await reflection.critique(
        output="Test output",
        context={"task": "test"}
    )
    
    assert isinstance(critique, Critique)
    assert critique.output == "Test output"
    assert hasattr(critique, 'issues')
    assert hasattr(critique, 'strengths')


@pytest.mark.asyncio
async def test_improve_output(mock_llm_provider):
    """Test output improvement."""
    reflection = SelfReflection(mock_llm_provider)
    
    critique = Critique(
        critique_id="test_critique",
        output="Original",
        issues=["Issue 1"],
        strengths=["Strength 1"],
        suggestions=["Suggestion 1"],
        overall_quality=0.5
    )
    
    improved = await reflection.improve("Original output", critique)
    assert isinstance(improved, str)


# Feedback Loop Tests
@pytest.mark.asyncio
async def test_record_outcome():
    """Test recording task outcomes."""
    feedback = FeedbackLoop()
    
    await feedback.record_outcome(
        task_id="task_1",
        agent_id="agent_1",
        success=True,
        metrics={"duration": 10.5}
    )
    
    success_rate = await feedback.get_success_rate("agent_1")
    assert success_rate == 1.0


@pytest.mark.asyncio
async def test_get_agent_metrics():
    """Test getting agent metrics."""
    feedback = FeedbackLoop()
    
    await feedback.record_outcome("task_1", "agent_1", True, {"duration": 10})
    await feedback.record_outcome("task_2", "agent_1", False, {"duration": 5})
    
    metrics = await feedback.get_agent_metrics("agent_1")
    
    assert metrics['total_tasks'] == 2
    assert metrics['success_rate'] == 0.5
    assert 'recent_trend' in metrics


@pytest.mark.asyncio
async def test_optimize_strategy():
    """Test strategy optimization."""
    feedback = FeedbackLoop()
    
    # Record some outcomes
    await feedback.record_outcome("t1", "agent_1", True, {"duration": 10})
    await feedback.record_outcome("t2", "agent_1", True, {"duration": 12})
    
    strategy = await feedback.optimize_strategy("agent_1")
    
    assert isinstance(strategy, Strategy)
    assert strategy.agent_id == "agent_1"
    assert strategy.success_rate > 0


# Prompt Optimizer Tests
@pytest.mark.asyncio
async def test_prompt_optimization():
    """Test prompt optimization."""
    optimizer = PromptOptimizer()
    
    # Mock evaluation function
    async def evaluate(prompt: str) -> float:
        return 0.8 if "detailed" in prompt else 0.5
    
    best_prompt = await optimizer.optimize(
        base_prompt="Solve this problem",
        evaluation_fn=evaluate,
        num_variations=3,
        num_iterations=2
    )
    
    assert isinstance(best_prompt, str)


@pytest.mark.asyncio
async def test_record_prompt_usage():
    """Test recording prompt usage."""
    optimizer = PromptOptimizer()
    
    # First optimize to create a prompt
    async def evaluate(prompt: str) -> float:
        return 0.7
    
    best = await optimizer.optimize(
        base_prompt="Test",
        evaluation_fn=evaluate,
        num_variations=2,
        num_iterations=1
    )
    
    # Get best prompts
    prompts = optimizer.get_best_prompts(limit=5)
    assert len(prompts) > 0


@pytest.mark.asyncio
async def test_compare_prompts():
    """Test comparing multiple prompts."""
    optimizer = PromptOptimizer()
    
    # Create some prompts first
    async def evaluate(prompt: str) -> float:
        return 0.6
    
    await optimizer.optimize(
        base_prompt="Prompt A",
        evaluation_fn=evaluate,
        num_variations=2,
        num_iterations=1
    )
    
    # Get prompts to compare
    all_prompts = optimizer.get_best_prompts(limit=10)
    if all_prompts:
        prompt_ids = [p.prompt_id for p in all_prompts[:2]]
        results = await optimizer.compare_prompts(prompt_ids, evaluate)
        assert isinstance(results, dict)
