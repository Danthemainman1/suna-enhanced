"""
Execution graph generator for debugging visualization.

This module generates visual execution graphs from task history,
supporting multiple output formats (Mermaid, Graphviz DOT, JSON).
"""

import json
from typing import Optional
from datetime import datetime
from .models import ExecutionGraph, GraphNode, GraphEdge, GraphNodeType


class ExecutionGraphGenerator:
    """
    Generates execution graphs from task history.
    
    Converts task execution history into visual graphs that can be
    rendered in various formats for debugging and analysis.
    """
    
    def __init__(self):
        """Initialize the execution graph generator."""
        self._graphs: dict[str, ExecutionGraph] = {}
    
    async def generate(self, task_id: str) -> ExecutionGraph:
        """
        Generate execution graph from task history.
        
        Args:
            task_id: ID of the task
            
        Returns:
            ExecutionGraph: The generated graph
        """
        # In a real implementation, this would fetch actual task history
        # For now, we create a sample graph structure
        
        nodes = []
        edges = []
        
        # Create start node
        start_node = GraphNode(
            id=f"{task_id}_start",
            type=GraphNodeType.START,
            label="Start",
            data={"task_id": task_id},
            timestamp=datetime.utcnow()
        )
        nodes.append(start_node)
        
        # Create end node placeholder
        end_node = GraphNode(
            id=f"{task_id}_end",
            type=GraphNodeType.END,
            label="End",
            data={"task_id": task_id},
            timestamp=datetime.utcnow()
        )
        nodes.append(end_node)
        
        # Add edge from start to end (placeholder)
        edges.append(GraphEdge(
            source=start_node.id,
            target=end_node.id,
            label=None
        ))
        
        graph = ExecutionGraph(
            task_id=task_id,
            nodes=nodes,
            edges=edges,
            metadata={"generated_at": datetime.utcnow().isoformat()}
        )
        
        self._graphs[task_id] = graph
        
        return graph
    
    def to_mermaid(self, graph: ExecutionGraph) -> str:
        """
        Convert to Mermaid diagram format.
        
        Args:
            graph: The execution graph
            
        Returns:
            str: Mermaid diagram syntax
        """
        lines = ["flowchart TD"]
        
        # Add nodes with appropriate shapes
        for node in graph.nodes:
            node_id = self._sanitize_id(node.id)
            label = node.label
            
            # Choose shape based on node type
            if node.type == GraphNodeType.START:
                lines.append(f"    {node_id}([{label}])")
            elif node.type == GraphNodeType.END:
                lines.append(f"    {node_id}([{label}])")
            elif node.type == GraphNodeType.DECISION:
                lines.append(f"    {node_id}{{{label}}}")
            elif node.type == GraphNodeType.ERROR:
                lines.append(f"    {node_id}[/{label}/]")
            else:
                lines.append(f"    {node_id}[{label}]")
        
        # Add edges
        for edge in graph.edges:
            source_id = self._sanitize_id(edge.source)
            target_id = self._sanitize_id(edge.target)
            
            if edge.label:
                lines.append(f"    {source_id} -->|{edge.label}| {target_id}")
            else:
                lines.append(f"    {source_id} --> {target_id}")
        
        return "\n".join(lines)
    
    def to_dot(self, graph: ExecutionGraph) -> str:
        """
        Convert to Graphviz DOT format.
        
        Args:
            graph: The execution graph
            
        Returns:
            str: DOT format syntax
        """
        lines = ["digraph ExecutionGraph {"]
        lines.append("    rankdir=TD;")
        lines.append("    node [shape=box];")
        lines.append("")
        
        # Add nodes with attributes
        for node in graph.nodes:
            node_id = self._sanitize_id(node.id)
            label = node.label.replace('"', '\\"')
            
            # Set shape based on node type
            shape = "box"
            if node.type == GraphNodeType.START or node.type == GraphNodeType.END:
                shape = "ellipse"
            elif node.type == GraphNodeType.DECISION:
                shape = "diamond"
            elif node.type == GraphNodeType.ERROR:
                shape = "octagon"
            
            lines.append(f'    {node_id} [label="{label}", shape={shape}];')
        
        lines.append("")
        
        # Add edges
        for edge in graph.edges:
            source_id = self._sanitize_id(edge.source)
            target_id = self._sanitize_id(edge.target)
            
            if edge.label:
                label = edge.label.replace('"', '\\"')
                lines.append(f'    {source_id} -> {target_id} [label="{label}"];')
            else:
                lines.append(f'    {source_id} -> {target_id};')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def to_json(self, graph: ExecutionGraph) -> dict:
        """
        Convert to JSON for frontend visualization.
        
        Args:
            graph: The execution graph
            
        Returns:
            dict: JSON-serializable dictionary
        """
        return {
            "task_id": graph.task_id,
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type.value,
                    "label": node.label,
                    "data": node.data,
                    "timestamp": node.timestamp.isoformat()
                }
                for node in graph.nodes
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "label": edge.label
                }
                for edge in graph.edges
            ],
            "metadata": graph.metadata
        }
    
    def _sanitize_id(self, node_id: str) -> str:
        """
        Sanitize node ID for use in graph formats.
        
        Args:
            node_id: Original node ID
            
        Returns:
            str: Sanitized ID
        """
        # Replace invalid characters with underscores
        sanitized = node_id.replace("-", "_").replace(".", "_")
        
        # Ensure it starts with a letter
        if sanitized and not sanitized[0].isalpha():
            sanitized = "n_" + sanitized
        
        return sanitized
    
    def add_node(self, task_id: str, node: GraphNode) -> None:
        """
        Add a node to an existing graph.
        
        Args:
            task_id: ID of the task
            node: Node to add
        """
        if task_id in self._graphs:
            self._graphs[task_id].nodes.append(node)
    
    def add_edge(self, task_id: str, edge: GraphEdge) -> None:
        """
        Add an edge to an existing graph.
        
        Args:
            task_id: ID of the task
            edge: Edge to add
        """
        if task_id in self._graphs:
            self._graphs[task_id].edges.append(edge)
    
    def get_graph(self, task_id: str) -> Optional[ExecutionGraph]:
        """
        Get a previously generated graph.
        
        Args:
            task_id: ID of the task
            
        Returns:
            ExecutionGraph or None: The graph if it exists
        """
        return self._graphs.get(task_id)
