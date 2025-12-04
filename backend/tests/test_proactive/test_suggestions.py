"""
Tests for proactive suggestions.
"""

import pytest
from proactive.suggestions import SuggestionEngine


@pytest.mark.asyncio
async def test_analyze_patterns():
    """Test analyzing user patterns."""
    engine = SuggestionEngine()
    
    analysis = await engine.analyze_patterns("ws-123", "user-123")
    
    assert analysis is not None
    assert "patterns" in analysis
    assert "insights" in analysis


@pytest.mark.asyncio
async def test_get_suggestions():
    """Test getting task suggestions."""
    engine = SuggestionEngine()
    
    suggestions = await engine.get_suggestions("ws-123", "user-123", limit=3)
    
    assert suggestions is not None
    assert len(suggestions) <= 3
    
    if len(suggestions) > 0:
        suggestion = suggestions[0]
        assert suggestion.workspace_id == "ws-123"
        assert suggestion.user_id == "user-123"
        assert 0.0 <= suggestion.confidence <= 1.0


@pytest.mark.asyncio
async def test_accept_suggestion():
    """Test accepting a suggestion."""
    engine = SuggestionEngine()
    
    suggestions = await engine.get_suggestions("ws-123", "user-123", limit=1)
    assert len(suggestions) > 0
    
    suggestion = suggestions[0]
    task_id = await engine.accept(suggestion.id)
    
    assert task_id is not None
    assert suggestion.accepted is True


@pytest.mark.asyncio
async def test_dismiss_suggestion():
    """Test dismissing a suggestion."""
    engine = SuggestionEngine()
    
    suggestions = await engine.get_suggestions("ws-123", "user-123", limit=1)
    assert len(suggestions) > 0
    
    suggestion = suggestions[0]
    success = await engine.dismiss(suggestion.id)
    
    assert success is True
    assert suggestion.dismissed is True


@pytest.mark.asyncio
async def test_accept_nonexistent_suggestion():
    """Test accepting a non-existent suggestion."""
    engine = SuggestionEngine()
    
    with pytest.raises(ValueError, match="not found"):
        await engine.accept("non-existent")
