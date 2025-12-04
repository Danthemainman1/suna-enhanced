"""
Chain-of-Thought (CoT) reasoning implementation.

This module provides step-by-step reasoning capabilities that break down
complex problems into manageable steps, similar to how humans think through problems.
"""

import time
from typing import Optional
from .models import ReasoningStep, ReasoningResult
from llm.provider import LLMProvider


class ChainOfThoughtReasoner:
    """
    Implements Chain-of-Thought reasoning for complex problem solving.
    
    Chain-of-Thought prompts the LLM to break down its reasoning into explicit
    steps, improving accuracy and interpretability for complex tasks.
    """
    
    def __init__(self, llm_provider: LLMProvider, max_steps: int = 10):
        """
        Initialize the CoT reasoner.
        
        Args:
            llm_provider: LLM provider to use for reasoning
            max_steps: Maximum number of reasoning steps allowed
        """
        self.llm_provider = llm_provider
        self.max_steps = max_steps
        self._reasoning_trace: list[ReasoningStep] = []
    
    async def reason(
        self,
        problem: str,
        context: Optional[dict] = None,
        use_few_shot: bool = False
    ) -> ReasoningResult:
        """
        Perform chain-of-thought reasoning on a problem.
        
        Args:
            problem: The problem to reason about
            context: Optional additional context information
            use_few_shot: Whether to use few-shot examples
            
        Returns:
            ReasoningResult with steps and conclusion
        """
        start_time = time.time()
        self._reasoning_trace = []
        context = context or {}
        
        # Build the reasoning prompt
        prompt = self._build_cot_prompt(problem, context, use_few_shot)
        
        # Get reasoning from LLM
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse the response into steps
        steps = self._parse_reasoning_steps(response.content)
        self._reasoning_trace = steps
        
        # Extract conclusion from final step
        conclusion = steps[-1].thought if steps else "No conclusion reached"
        
        # Calculate overall confidence
        total_confidence = sum(s.confidence for s in steps) / len(steps) if steps else 0.0
        
        duration = time.time() - start_time
        
        return ReasoningResult(
            problem=problem,
            steps=steps,
            conclusion=conclusion,
            total_confidence=total_confidence,
            reasoning_type="chain_of_thought",
            duration_seconds=duration,
            metadata={
                "context_provided": bool(context),
                "few_shot_used": use_few_shot,
                "model": response.model
            }
        )
    
    def _build_cot_prompt(
        self,
        problem: str,
        context: dict,
        use_few_shot: bool
    ) -> str:
        """Build the chain-of-thought prompt."""
        prompt_parts = []
        
        if use_few_shot:
            # Add few-shot examples
            prompt_parts.append(self._get_few_shot_examples())
        
        prompt_parts.append(
            "Let's solve this problem step by step:\n\n"
            f"Problem: {problem}\n\n"
        )
        
        if context:
            prompt_parts.append(f"Context: {context}\n\n")
        
        prompt_parts.append(
            "Please think through this carefully, showing your reasoning at each step. "
            "Format your response as:\n"
            "Step 1: [your first thought]\n"
            "Step 2: [your second thought]\n"
            "...\n"
            "Conclusion: [final answer]\n"
        )
        
        return "".join(prompt_parts)
    
    def _get_few_shot_examples(self) -> str:
        """Get few-shot examples for CoT prompting."""
        return """Here are some examples of step-by-step reasoning:

Example 1:
Problem: If a train travels 60 miles in 1 hour, how far will it travel in 2.5 hours?
Step 1: The train travels 60 miles per hour
Step 2: We need to find distance for 2.5 hours
Step 3: Distance = Speed × Time = 60 × 2.5
Step 4: 60 × 2.5 = 150 miles
Conclusion: The train will travel 150 miles in 2.5 hours

Example 2:
Problem: Is it better to invest in stocks or bonds during high inflation?
Step 1: High inflation erodes the purchasing power of fixed returns
Step 2: Bonds typically provide fixed interest payments
Step 3: Stocks represent ownership in companies that can raise prices
Step 4: During inflation, companies can increase prices to maintain margins
Step 5: Stock prices often rise with inflation, while bond returns are fixed
Conclusion: Stocks are generally better during high inflation as they can appreciate with rising prices

Now let's solve your problem:

"""
    
    def _parse_reasoning_steps(self, response: str) -> list[ReasoningStep]:
        """Parse the LLM response into reasoning steps."""
        steps = []
        lines = response.strip().split('\n')
        step_number = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with "Step X:"
            if line.lower().startswith('step'):
                # Extract the thought
                if ':' in line:
                    thought = line.split(':', 1)[1].strip()
                else:
                    thought = line
                
                # Estimate confidence based on language used
                confidence = self._estimate_confidence(thought)
                
                steps.append(ReasoningStep(
                    step_number=step_number,
                    thought=thought,
                    confidence=confidence
                ))
                step_number += 1
            
            elif line.lower().startswith('conclusion'):
                # Extract conclusion as final step
                if ':' in line:
                    thought = line.split(':', 1)[1].strip()
                else:
                    thought = line
                
                steps.append(ReasoningStep(
                    step_number=step_number,
                    thought=thought,
                    confidence=0.9  # High confidence for conclusion
                ))
        
        return steps
    
    def _estimate_confidence(self, thought: str) -> float:
        """Estimate confidence based on language used in thought."""
        # Simple heuristic based on certainty markers
        thought_lower = thought.lower()
        
        # High confidence markers
        if any(word in thought_lower for word in ['definitely', 'certainly', 'clearly', 'obvious']):
            return 0.9
        
        # Low confidence markers
        if any(word in thought_lower for word in ['maybe', 'perhaps', 'might', 'possibly', 'uncertain']):
            return 0.5
        
        # Medium confidence markers
        if any(word in thought_lower for word in ['probably', 'likely', 'seems']):
            return 0.7
        
        # Default confidence
        return 0.8
    
    def get_reasoning_trace(self) -> list[ReasoningStep]:
        """
        Get the trace of reasoning steps from last execution.
        
        Returns:
            List of reasoning steps
        """
        return self._reasoning_trace
    
    def visualize_steps(self) -> str:
        """
        Generate a text visualization of reasoning steps.
        
        Returns:
            Formatted string showing the reasoning chain
        """
        if not self._reasoning_trace:
            return "No reasoning trace available"
        
        lines = ["Chain of Thought Reasoning:", "=" * 50, ""]
        
        for step in self._reasoning_trace:
            lines.append(f"Step {step.step_number} (confidence: {step.confidence:.2f}):")
            lines.append(f"  {step.thought}")
            if step.observation:
                lines.append(f"  Observation: {step.observation}")
            lines.append("")
        
        return "\n".join(lines)
