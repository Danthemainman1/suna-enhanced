"""
Tests for AI explainer.
"""

import pytest
from debugger.explainer import AgentExplainer


@pytest.mark.asyncio
async def test_explain_decision():
    """Test explaining an agent decision."""
    explainer = AgentExplainer()
    
    explanation = await explainer.explain_decision("task-1", "step-1")
    
    assert explanation.summary is not None
    assert len(explanation.reasoning_chain) > 0
    assert len(explanation.key_factors) > 0
    assert 0.0 <= explanation.confidence <= 1.0


@pytest.mark.asyncio
async def test_explain_failure():
    """Test explaining a task failure."""
    explainer = AgentExplainer()
    
    explanation = await explainer.explain_failure("task-1")
    
    assert explanation.error_type is not None
    assert explanation.root_cause is not None
    assert len(explanation.suggestions) > 0


@pytest.mark.asyncio
async def test_suggest_improvements():
    """Test getting improvement suggestions."""
    explainer = AgentExplainer()
    
    suggestions = await explainer.suggest_improvements("task-1")
    
    assert len(suggestions) > 0
    assert all(s.title is not None for s in suggestions)
    assert all(s.description is not None for s in suggestions)


@pytest.mark.asyncio
async def test_compare_approaches():
    """Test comparing approaches."""
    explainer = AgentExplainer()
    
    comparison = await explainer.compare_approaches(
        "task-1",
        "Alternative approach: Use a different strategy"
    )
    
    assert "actual_approach" in comparison
    assert "alternative_approach" in comparison
    assert "recommendation" in comparison
