"""
Automatic prompt optimization.

This module tracks prompt performance and generates optimized variations
to improve task outcomes over time.
"""

import uuid
from typing import Callable, Optional, Awaitable
from datetime import datetime
from .models import PromptStats, PromptVariation


class PromptOptimizer:
    """
    Automatically optimizes prompts based on performance.
    
    The prompt optimizer tracks how different prompts perform,
    generates variations, and selects the best-performing ones.
    """
    
    def __init__(self):
        """Initialize the prompt optimizer."""
        self._prompts: dict[str, PromptStats] = {}
        self._variations: dict[str, list[PromptVariation]] = {}
    
    async def optimize(
        self,
        base_prompt: str,
        evaluation_fn: Callable[[str], Awaitable[float]],
        num_variations: int = 5,
        num_iterations: int = 3
    ) -> str:
        """
        Optimize a prompt through iterative variation and evaluation.
        
        Args:
            base_prompt: The initial prompt to optimize
            evaluation_fn: Async function that evaluates prompt quality (returns 0-1 score)
            num_variations: Number of variations to generate per iteration
            num_iterations: Number of optimization iterations
            
        Returns:
            The best performing prompt
        """
        # Create initial prompt stats
        prompt_id = str(uuid.uuid4())
        base_stats = PromptStats(
            prompt_id=prompt_id,
            prompt_text=base_prompt,
            usage_count=0,
            success_count=0
        )
        self._prompts[prompt_id] = base_stats
        
        # Evaluate base prompt
        base_score = await evaluation_fn(base_prompt)
        base_stats.average_score = base_score
        base_stats.usage_count = 1
        
        best_prompt = base_prompt
        best_score = base_score
        best_prompt_id = prompt_id
        
        for iteration in range(num_iterations):
            # Generate variations of current best
            variations = self._generate_variations(
                best_prompt,
                best_prompt_id,
                num_variations
            )
            
            # Evaluate each variation
            for variation in variations:
                score = await evaluation_fn(variation.prompt_text)
                
                # Update stats
                if variation.stats:
                    variation.stats.usage_count += 1
                    variation.stats.average_score = score
                else:
                    variation.stats = PromptStats(
                        prompt_id=variation.variation_id,
                        prompt_text=variation.prompt_text,
                        usage_count=1,
                        average_score=score
                    )
                
                # Track if this is the new best
                if score > best_score:
                    best_score = score
                    best_prompt = variation.prompt_text
                    best_prompt_id = variation.variation_id
            
            # Store variations
            if best_prompt_id not in self._variations:
                self._variations[best_prompt_id] = []
            self._variations[best_prompt_id].extend(variations)
        
        return best_prompt
    
    def _generate_variations(
        self,
        base_prompt: str,
        base_prompt_id: str,
        count: int
    ) -> list[PromptVariation]:
        """Generate variations of a prompt."""
        variations = []
        
        variation_strategies = [
            self._add_clarity_instructions,
            self._add_step_by_step,
            self._add_examples,
            self._make_more_specific,
            self._simplify_language,
            self._add_constraints,
            self._change_tone,
            self._add_context_hints
        ]
        
        for i in range(min(count, len(variation_strategies))):
            strategy = variation_strategies[i]
            varied_prompt = strategy(base_prompt)
            
            variation = PromptVariation(
                variation_id=str(uuid.uuid4()),
                base_prompt_id=base_prompt_id,
                prompt_text=varied_prompt,
                variation_type=strategy.__name__
            )
            variations.append(variation)
        
        return variations
    
    def _add_clarity_instructions(self, prompt: str) -> str:
        """Add clarity instructions to prompt."""
        return f"{prompt}\n\nPlease provide a clear and detailed response."
    
    def _add_step_by_step(self, prompt: str) -> str:
        """Add step-by-step instruction."""
        return f"{prompt}\n\nLet's approach this step by step:\n1. First, analyze the problem\n2. Then, break it down into components\n3. Finally, provide a comprehensive solution"
    
    def _add_examples(self, prompt: str) -> str:
        """Add example request."""
        return f"{prompt}\n\nPlease provide concrete examples in your response."
    
    def _make_more_specific(self, prompt: str) -> str:
        """Make prompt more specific."""
        return f"Task: {prompt}\n\nBe as specific and precise as possible in your response. Focus on actionable details."
    
    def _simplify_language(self, prompt: str) -> str:
        """Simplify the prompt language."""
        # In a real implementation, this would use NLP to simplify
        # For now, just add a simplification instruction
        return f"{prompt}\n\nExplain your response in simple, easy-to-understand terms."
    
    def _add_constraints(self, prompt: str) -> str:
        """Add constraints to the prompt."""
        return f"{prompt}\n\nConstraints:\n- Keep your response concise\n- Focus on the most important points\n- Use bullet points where appropriate"
    
    def _change_tone(self, prompt: str) -> str:
        """Change the tone of the prompt."""
        return f"{prompt}\n\nUse a professional and analytical tone in your response."
    
    def _add_context_hints(self, prompt: str) -> str:
        """Add context hints."""
        return f"Context: This is an important task that requires careful thought.\n\n{prompt}\n\nConsider all relevant factors in your analysis."
    
    async def record_usage(
        self,
        prompt_id: str,
        success: bool,
        score: Optional[float] = None,
        duration: Optional[float] = None
    ):
        """
        Record usage of a prompt.
        
        Args:
            prompt_id: Prompt identifier
            success: Whether the prompt led to success
            score: Optional quality score
            duration: Optional execution duration
        """
        if prompt_id not in self._prompts:
            return
        
        stats = self._prompts[prompt_id]
        stats.usage_count += 1
        stats.last_used = datetime.utcnow()
        
        if success:
            stats.success_count += 1
        
        # Update success rate
        stats.success_rate = stats.success_count / stats.usage_count
        
        # Update average score if provided
        if score is not None:
            # Running average
            n = stats.usage_count
            stats.average_score = (
                (stats.average_score * (n - 1) + score) / n
            )
        
        # Update average duration if provided
        if duration is not None:
            n = stats.usage_count
            stats.average_duration = (
                (stats.average_duration * (n - 1) + duration) / n
            )
    
    def get_prompt_stats(self, prompt_id: str) -> Optional[PromptStats]:
        """
        Get statistics for a prompt.
        
        Args:
            prompt_id: Prompt identifier
            
        Returns:
            PromptStats if found, None otherwise
        """
        return self._prompts.get(prompt_id)
    
    def get_best_prompts(self, limit: int = 10) -> list[PromptStats]:
        """
        Get the best performing prompts.
        
        Args:
            limit: Maximum number of prompts to return
            
        Returns:
            List of top performing prompts
        """
        # Sort by average score descending
        sorted_prompts = sorted(
            self._prompts.values(),
            key=lambda p: (p.average_score, p.success_rate),
            reverse=True
        )
        return sorted_prompts[:limit]
    
    def get_variations(self, base_prompt_id: str) -> list[PromptVariation]:
        """
        Get variations of a prompt.
        
        Args:
            base_prompt_id: Base prompt identifier
            
        Returns:
            List of variations
        """
        return self._variations.get(base_prompt_id, [])
    
    async def compare_prompts(
        self,
        prompt_ids: list[str],
        evaluation_fn: Callable[[str], Awaitable[float]]
    ) -> dict[str, float]:
        """
        Compare multiple prompts using an evaluation function.
        
        Args:
            prompt_ids: List of prompt IDs to compare
            evaluation_fn: Function to evaluate prompts
            
        Returns:
            Dictionary mapping prompt_id to score
        """
        results = {}
        
        for prompt_id in prompt_ids:
            if prompt_id not in self._prompts:
                continue
            
            prompt = self._prompts[prompt_id].prompt_text
            score = await evaluation_fn(prompt)
            results[prompt_id] = score
            
            # Update stats
            await self.record_usage(prompt_id, success=True, score=score)
        
        return results
