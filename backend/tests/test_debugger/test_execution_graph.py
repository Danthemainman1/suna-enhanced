"""
Tests for execution graph generator.
"""

import pytest
from debugger.execution_graph import ExecutionGraphGenerator
from debugger.models import GraphNodeType


@pytest.mark.asyncio
async def test_generate_graph():
    """Test generating an execution graph."""
    generator = ExecutionGraphGenerator()
    
    graph = await generator.generate("task-1")
    
    assert graph.task_id == "task-1"
    assert len(graph.nodes) >= 2  # At least start and end
    assert len(graph.edges) >= 1


@pytest.mark.asyncio
async def test_to_mermaid():
    """Test converting graph to Mermaid format."""
    generator = ExecutionGraphGenerator()
    
    graph = await generator.generate("task-1")
    mermaid = generator.to_mermaid(graph)
    
    assert "flowchart TD" in mermaid
    assert len(mermaid) > 0


@pytest.mark.asyncio
async def test_to_dot():
    """Test converting graph to DOT format."""
    generator = ExecutionGraphGenerator()
    
    graph = await generator.generate("task-1")
    dot = generator.to_dot(graph)
    
    assert "digraph ExecutionGraph" in dot
    assert len(dot) > 0


@pytest.mark.asyncio
async def test_to_json():
    """Test converting graph to JSON."""
    generator = ExecutionGraphGenerator()
    
    graph = await generator.generate("task-1")
    json_data = generator.to_json(graph)
    
    assert "task_id" in json_data
    assert "nodes" in json_data
    assert "edges" in json_data
    assert isinstance(json_data["nodes"], list)
    assert isinstance(json_data["edges"], list)
