"""
Advanced reasoning engines for Suna Ultra.

This module provides sophisticated reasoning capabilities including:
- Chain-of-Thought (CoT) reasoning
- Tree-of-Thoughts (ToT) exploration
- ReAct (Reasoning + Acting) loops
- Self-reflection and error correction
- Feedback-based learning
- Automatic prompt optimization
"""

from .models import (
    ReasoningStep,
    ReasoningResult,
    ThoughtNode,
    ToTResult,
    Action,
    Observation,
    ReActStep,
    ReActResult,
    Critique,
    ReflectionResult,
    Strategy,
    TaskOutcome,
    PromptStats,
    PromptVariation,
)

from .chain_of_thought import ChainOfThoughtReasoner
from .tree_of_thoughts import TreeOfThoughts
from .react_loop import ReActLoop
from .self_reflection import SelfReflection
from .feedback_loop import FeedbackLoop
from .prompt_optimizer import PromptOptimizer


__all__ = [
    # Models
    "ReasoningStep",
    "ReasoningResult",
    "ThoughtNode",
    "ToTResult",
    "Action",
    "Observation",
    "ReActStep",
    "ReActResult",
    "Critique",
    "ReflectionResult",
    "Strategy",
    "TaskOutcome",
    "PromptStats",
    "PromptVariation",
    
    # Reasoning engines
    "ChainOfThoughtReasoner",
    "TreeOfThoughts",
    "ReActLoop",
    "SelfReflection",
    "FeedbackLoop",
    "PromptOptimizer",
]

__version__ = "1.0.0"
