"""
Tree-of-Thoughts (ToT) reasoning implementation.

This module provides tree-based exploration of multiple reasoning paths,
evaluating and pruning branches to find the optimal solution path.
"""

import time
import uuid
from typing import Optional
from collections import deque
from .models import ThoughtNode, ToTResult
from llm.provider import LLMProvider


class TreeOfThoughts:
    """
    Implements Tree-of-Thoughts reasoning for complex problem solving.
    
    ToT explores multiple reasoning branches, evaluates each branch's quality,
    and prunes low-scoring branches to find the best solution path.
    """
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        evaluation_threshold: float = 0.5
    ):
        """
        Initialize the ToT explorer.
        
        Args:
            llm_provider: LLM provider for generating and evaluating thoughts
            evaluation_threshold: Minimum score to continue exploring a branch
        """
        self.llm_provider = llm_provider
        self.evaluation_threshold = evaluation_threshold
        self._nodes: dict[str, ThoughtNode] = {}
        self._root_id: Optional[str] = None
    
    async def explore(
        self,
        problem: str,
        max_depth: int = 3,
        branching_factor: int = 3,
        strategy: str = "breadth_first"
    ) -> ToTResult:
        """
        Explore the problem space using tree-of-thoughts.
        
        Args:
            problem: The problem to explore
            max_depth: Maximum depth to explore
            branching_factor: Number of branches per node
            strategy: Exploration strategy ("breadth_first" or "depth_first")
            
        Returns:
            ToTResult with exploration results and best path
        """
        start_time = time.time()
        self._nodes = {}
        
        # Create root node
        root_id = self._create_node(
            thought=f"Problem: {problem}",
            depth=0,
            parent_id=None
        )
        self._root_id = root_id
        
        # Explore based on strategy
        if strategy == "breadth_first":
            await self._explore_breadth_first(problem, max_depth, branching_factor)
        elif strategy == "depth_first":
            await self._explore_depth_first(problem, max_depth, branching_factor)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Find best path
        best_path, best_score = self._find_best_path()
        
        duration = time.time() - start_time
        
        return ToTResult(
            problem=problem,
            nodes=self._nodes,
            best_path=best_path,
            best_score=best_score,
            exploration_strategy=strategy,
            nodes_explored=len(self._nodes),
            max_depth_reached=max(n.depth for n in self._nodes.values()),
            duration_seconds=duration,
            metadata={
                "branching_factor": branching_factor,
                "max_depth": max_depth
            }
        )
    
    async def _explore_breadth_first(
        self,
        problem: str,
        max_depth: int,
        branching_factor: int
    ):
        """Explore the tree breadth-first."""
        queue = deque([self._root_id])
        
        while queue:
            node_id = queue.popleft()
            node = self._nodes[node_id]
            
            # Stop if we've reached max depth
            if node.depth >= max_depth:
                node.is_terminal = True
                continue
            
            # Generate child thoughts
            children = await self._generate_children(
                node_id,
                problem,
                branching_factor
            )
            
            # Evaluate and prune
            for child_id in children:
                child = self._nodes[child_id]
                score = await self._evaluate_thought(child.thought, problem)
                child.score = score
                
                # Only explore promising branches
                if score >= self.evaluation_threshold:
                    queue.append(child_id)
                else:
                    child.is_terminal = True
    
    async def _explore_depth_first(
        self,
        problem: str,
        max_depth: int,
        branching_factor: int
    ):
        """Explore the tree depth-first."""
        stack = [self._root_id]
        
        while stack:
            node_id = stack.pop()
            node = self._nodes[node_id]
            
            # Stop if we've reached max depth
            if node.depth >= max_depth:
                node.is_terminal = True
                continue
            
            # Generate child thoughts
            children = await self._generate_children(
                node_id,
                problem,
                branching_factor
            )
            
            # Evaluate and add promising children to stack
            for child_id in reversed(children):  # Reverse to maintain left-to-right order
                child = self._nodes[child_id]
                score = await self._evaluate_thought(child.thought, problem)
                child.score = score
                
                if score >= self.evaluation_threshold:
                    stack.append(child_id)
                else:
                    child.is_terminal = True
    
    async def _generate_children(
        self,
        parent_id: str,
        problem: str,
        count: int
    ) -> list[str]:
        """Generate child thoughts for a node."""
        parent = self._nodes[parent_id]
        
        # Build prompt for generating next thoughts
        prompt = self._build_generation_prompt(parent, problem, count)
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.8,  # Higher temperature for diversity
            max_tokens=500
        )
        
        # Parse response into multiple thoughts
        thoughts = self._parse_thoughts(response.content, count)
        
        # Create child nodes
        child_ids = []
        for thought in thoughts:
            child_id = self._create_node(
                thought=thought,
                depth=parent.depth + 1,
                parent_id=parent_id
            )
            child_ids.append(child_id)
            parent.children.append(child_id)
        
        return child_ids
    
    def _build_generation_prompt(
        self,
        parent: ThoughtNode,
        problem: str,
        count: int
    ) -> str:
        """Build prompt for generating next thoughts."""
        # Get path to this node
        path = self._get_path_to_node(parent.node_id)
        path_text = " → ".join([self._nodes[nid].thought for nid in path])
        
        return f"""Problem: {problem}

Current reasoning path: {path_text}

Generate {count} different possible next steps or thoughts to solve this problem.
Each thought should explore a different approach or angle.
Format your response as:
1. [first thought]
2. [second thought]
3. [third thought]
"""
    
    async def _evaluate_thought(self, thought: str, problem: str) -> float:
        """Evaluate the quality/promise of a thought."""
        prompt = f"""Problem: {problem}

Thought to evaluate: {thought}

On a scale of 0.0 to 1.0, how promising is this thought for solving the problem?
Consider:
- Relevance to the problem
- Logical soundness
- Likelihood of leading to a solution

Provide only a number between 0.0 and 1.0.
"""
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.3,  # Low temperature for consistent evaluation
            max_tokens=10
        )
        
        # Parse score from response
        try:
            score = float(response.content.strip())
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except ValueError:
            # If parsing fails, use a default score
            return 0.5
    
    def _parse_thoughts(self, response: str, expected_count: int) -> list[str]:
        """Parse multiple thoughts from response."""
        thoughts = []
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove numbering if present
            if line and line[0].isdigit() and '.' in line:
                thought = line.split('.', 1)[1].strip()
            else:
                thought = line
            
            if thought:
                thoughts.append(thought)
        
        # Ensure we have the expected count
        while len(thoughts) < expected_count:
            thoughts.append(f"Alternative approach {len(thoughts) + 1}")
        
        return thoughts[:expected_count]
    
    def _create_node(
        self,
        thought: str,
        depth: int,
        parent_id: Optional[str]
    ) -> str:
        """Create a new thought node."""
        node_id = str(uuid.uuid4())
        node = ThoughtNode(
            node_id=node_id,
            parent_id=parent_id,
            depth=depth,
            thought=thought,
            score=0.0,
            is_terminal=False,
            children=[]
        )
        self._nodes[node_id] = node
        return node_id
    
    def _get_path_to_node(self, node_id: str) -> list[str]:
        """Get the path from root to a node."""
        path = []
        current_id = node_id
        
        while current_id is not None:
            path.insert(0, current_id)
            current_id = self._nodes[current_id].parent_id
        
        return path
    
    def _find_best_path(self) -> tuple[list[str], float]:
        """Find the best path through the tree."""
        if not self._nodes:
            return [], 0.0
        
        best_path = []
        best_score = 0.0
        
        # Find all terminal nodes
        terminal_nodes = [
            node_id for node_id, node in self._nodes.items()
            if node.is_terminal
        ]
        
        # Evaluate each path to a terminal node
        for node_id in terminal_nodes:
            path = self._get_path_to_node(node_id)
            # Calculate path score as average of node scores
            scores = [self._nodes[nid].score for nid in path[1:]]  # Skip root
            path_score = sum(scores) / len(scores) if scores else 0.0
            
            if path_score > best_score:
                best_score = path_score
                best_path = path
        
        return best_path, best_score
    
    def get_best_path(self) -> list[ThoughtNode]:
        """
        Get the best path as a list of thought nodes.
        
        Returns:
            List of ThoughtNode objects in the best path
        """
        best_path_ids, _ = self._find_best_path()
        return [self._nodes[nid] for nid in best_path_ids]
    
    def to_graph(self) -> dict:
        """
        Convert the tree to a graph representation for visualization.
        
        Returns:
            Dictionary with nodes and edges
        """
        nodes = []
        edges = []
        
        for node_id, node in self._nodes.items():
            nodes.append({
                "id": node_id,
                "thought": node.thought,
                "depth": node.depth,
                "score": node.score,
                "is_terminal": node.is_terminal
            })
            
            for child_id in node.children:
                edges.append({
                    "source": node_id,
                    "target": child_id
                })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
