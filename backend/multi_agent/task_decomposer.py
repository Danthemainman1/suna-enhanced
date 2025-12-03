"""
Task Decomposer - Break complex tasks into subtasks

Analyzes complex tasks and decomposes them into smaller, manageable subtasks
that can be distributed across multiple specialized agents.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class SubTask:
    """Represents a subtask"""
    id: str
    description: str
    agent_type: str
    priority: int = 0
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: Optional[int] = None  # in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskPlan:
    """Represents a decomposed task plan"""
    task_id: str
    original_task: str
    subtasks: List[SubTask]
    execution_strategy: str = "sequential"  # sequential, parallel, or mixed
    total_estimated_duration: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class TaskDecomposer:
    """
    Decompose complex tasks into smaller subtasks.
    
    Features:
    - Analyze task complexity
    - Generate subtask dependencies
    - Optimize execution order
    - Estimate task duration
    """

    def __init__(self):
        self.task_patterns: Dict[str, Any] = {}
        self._initialize_patterns()

    def _initialize_patterns(self):
        """Initialize common task patterns"""
        self.task_patterns = {
            "research_and_report": {
                "subtasks": [
                    {"type": "research_agent", "action": "gather_information"},
                    {"type": "data_agent", "action": "analyze_data"},
                    {"type": "writer_agent", "action": "write_report"},
                    {"type": "critic_agent", "action": "review_quality"},
                ],
                "strategy": "sequential",
            },
            "code_development": {
                "subtasks": [
                    {"type": "planner_agent", "action": "design_architecture"},
                    {"type": "code_agent", "action": "implement_code"},
                    {"type": "code_agent", "action": "write_tests"},
                    {"type": "critic_agent", "action": "review_code"},
                ],
                "strategy": "sequential",
            },
            "data_pipeline": {
                "subtasks": [
                    {"type": "data_agent", "action": "extract_data"},
                    {"type": "data_agent", "action": "transform_data"},
                    {"type": "data_agent", "action": "load_data"},
                    {"type": "data_agent", "action": "validate_results"},
                ],
                "strategy": "sequential",
            },
        }

    async def decompose(
        self,
        task_id: str,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskPlan:
        """
        Decompose a complex task into subtasks.
        
        Args:
            task_id: Unique identifier for the task
            task_description: Description of the task to decompose
            context: Additional context for decomposition
            
        Returns:
            TaskPlan with subtasks and execution strategy
        """
        logger.info(f"Decomposing task: {task_id}")

        # Detect task pattern
        pattern = self._detect_pattern(task_description)

        if pattern:
            # Use pattern-based decomposition
            subtasks = self._decompose_by_pattern(task_id, task_description, pattern)
            strategy = self.task_patterns[pattern]["strategy"]
        else:
            # Use generic decomposition
            subtasks = await self._generic_decompose(task_id, task_description, context)
            strategy = "sequential"

        # Calculate dependencies
        subtasks = self._calculate_dependencies(subtasks, strategy)

        # Estimate duration
        total_duration = sum(st.estimated_duration or 60 for st in subtasks)

        plan = TaskPlan(
            task_id=task_id,
            original_task=task_description,
            subtasks=subtasks,
            execution_strategy=strategy,
            total_estimated_duration=total_duration,
        )

        logger.info(
            f"Task decomposed into {len(subtasks)} subtasks "
            f"(strategy: {strategy}, estimated: {total_duration}s)"
        )
        return plan

    def _detect_pattern(self, task_description: str) -> Optional[str]:
        """Detect task pattern from description"""
        task_lower = task_description.lower()

        if any(
            keyword in task_lower
            for keyword in ["research", "report", "analyze", "study"]
        ):
            return "research_and_report"
        elif any(
            keyword in task_lower for keyword in ["code", "develop", "implement", "build"]
        ):
            return "code_development"
        elif any(
            keyword in task_lower for keyword in ["data", "pipeline", "etl", "process"]
        ):
            return "data_pipeline"

        return None

    def _decompose_by_pattern(
        self, task_id: str, task_description: str, pattern: str
    ) -> List[SubTask]:
        """Decompose task using a known pattern"""
        pattern_data = self.task_patterns[pattern]
        subtasks = []

        for i, subtask_def in enumerate(pattern_data["subtasks"]):
            subtask = SubTask(
                id=f"{task_id}_subtask_{i}",
                description=f"{subtask_def['action']} for: {task_description}",
                agent_type=subtask_def["type"],
                priority=i,
                estimated_duration=60,
            )
            subtasks.append(subtask)

        return subtasks

    async def _generic_decompose(
        self,
        task_id: str,
        task_description: str,
        context: Optional[Dict[str, Any]],
    ) -> List[SubTask]:
        """Generic task decomposition when no pattern matches"""
        # Simple decomposition: plan -> execute -> review
        subtasks = [
            SubTask(
                id=f"{task_id}_plan",
                description=f"Plan approach for: {task_description}",
                agent_type="planner_agent",
                priority=0,
                estimated_duration=30,
            ),
            SubTask(
                id=f"{task_id}_execute",
                description=f"Execute: {task_description}",
                agent_type="executor_agent",
                priority=1,
                estimated_duration=120,
            ),
            SubTask(
                id=f"{task_id}_review",
                description=f"Review results of: {task_description}",
                agent_type="critic_agent",
                priority=2,
                estimated_duration=30,
            ),
        ]

        return subtasks

    def _calculate_dependencies(
        self, subtasks: List[SubTask], strategy: str
    ) -> List[SubTask]:
        """Calculate dependencies between subtasks based on execution strategy"""
        if strategy == "sequential":
            # Each task depends on the previous one
            for i in range(1, len(subtasks)):
                subtasks[i].dependencies = [subtasks[i - 1].id]
        elif strategy == "parallel":
            # No dependencies, all can run in parallel
            pass
        elif strategy == "mixed":
            # Custom dependency logic
            pass

        return subtasks

    async def optimize_plan(self, plan: TaskPlan) -> TaskPlan:
        """Optimize task execution plan"""
        # Sort subtasks by priority and dependencies
        # This is a simple implementation; could be enhanced with topological sort
        plan.subtasks.sort(key=lambda x: (len(x.dependencies), x.priority))
        return plan
