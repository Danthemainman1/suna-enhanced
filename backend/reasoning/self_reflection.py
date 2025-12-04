"""
Self-reflection and error correction implementation.

This module provides capabilities for agents to evaluate their own outputs,
identify errors, generate critiques, and propose improvements.
"""

import uuid
from typing import Optional
from .models import ReflectionResult, Critique
from llm.provider import LLMProvider


class SelfReflection:
    """
    Implements self-reflection and error correction for agent outputs.
    
    Self-reflection allows agents to critically evaluate their own work,
    identify mistakes, and iteratively improve their outputs.
    """
    
    def __init__(self, llm_provider: LLMProvider, max_iterations: int = 3):
        """
        Initialize the self-reflection system.
        
        Args:
            llm_provider: LLM provider for reflection
            max_iterations: Maximum reflection iterations
        """
        self.llm_provider = llm_provider
        self.max_iterations = max_iterations
    
    async def reflect(
        self,
        output: str,
        context: Optional[dict] = None
    ) -> ReflectionResult:
        """
        Reflect on an output and optionally improve it.
        
        Args:
            output: The output to reflect on
            context: Optional context about the task/goal
            
        Returns:
            ReflectionResult with critique and improved output
        """
        context = context or {}
        
        # Generate initial critique
        critique = await self.critique(output, context)
        
        # If quality is already high, no need to improve
        if critique.overall_quality >= 0.9:
            return ReflectionResult(
                original_output=output,
                critique=critique,
                improved_output=output,
                reflection_iterations=1,
                improvement_score=0.0
            )
        
        # Iteratively improve based on critique
        current_output = output
        iterations = 1
        
        for _ in range(self.max_iterations - 1):
            improved = await self.improve(current_output, critique)
            
            # Critique the improvement
            new_critique = await self.critique(improved, context)
            
            # Check if we've improved enough
            if new_critique.overall_quality >= 0.9:
                return ReflectionResult(
                    original_output=output,
                    critique=new_critique,
                    improved_output=improved,
                    reflection_iterations=iterations + 1,
                    improvement_score=new_critique.overall_quality - critique.overall_quality
                )
            
            # If quality decreased, stop
            if new_critique.overall_quality < critique.overall_quality:
                break
            
            current_output = improved
            critique = new_critique
            iterations += 1
        
        improvement_score = critique.overall_quality - (
            await self.critique(output, context)
        ).overall_quality
        
        return ReflectionResult(
            original_output=output,
            critique=critique,
            improved_output=current_output,
            reflection_iterations=iterations,
            improvement_score=improvement_score
        )
    
    async def critique(
        self,
        output: str,
        context: Optional[dict] = None
    ) -> Critique:
        """
        Generate a critique of an output.
        
        Args:
            output: The output to critique
            context: Optional context information
            
        Returns:
            Critique with identified issues and suggestions
        """
        context = context or {}
        
        prompt = self._build_critique_prompt(output, context)
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.5,
            max_tokens=1000
        )
        
        # Parse the critique from response
        parsed = self._parse_critique(response.content)
        
        return Critique(
            critique_id=str(uuid.uuid4()),
            output=output,
            issues=parsed['issues'],
            strengths=parsed['strengths'],
            suggestions=parsed['suggestions'],
            overall_quality=parsed['quality_score']
        )
    
    def _build_critique_prompt(self, output: str, context: dict) -> str:
        """Build the critique prompt."""
        context_text = ""
        if context:
            context_text = f"\nContext: {context}\n"
        
        return f"""Please critically evaluate the following output:{context_text}

Output to evaluate:
{output}

Provide a detailed critique with the following:

STRENGTHS:
- List what's good about this output
- What does it do well?

ISSUES:
- What problems or errors do you see?
- What's unclear or incorrect?
- What's missing?

SUGGESTIONS:
- How could this be improved?
- What specific changes would help?

QUALITY SCORE (0.0-1.0):
- Overall quality rating

Format your response exactly as shown above with these section headers.
"""
    
    def _parse_critique(self, response: str) -> dict:
        """Parse critique from LLM response."""
        sections = {
            'strengths': [],
            'issues': [],
            'suggestions': [],
            'quality_score': 0.7
        }
        
        current_section = None
        lines = response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for section headers
            line_lower = line.lower()
            if 'strength' in line_lower:
                current_section = 'strengths'
            elif 'issue' in line_lower or 'problem' in line_lower:
                current_section = 'issues'
            elif 'suggestion' in line_lower or 'improvement' in line_lower:
                current_section = 'suggestions'
            elif 'quality' in line_lower or 'score' in line_lower:
                # Try to extract quality score
                try:
                    # Look for numbers in the line
                    words = line.split()
                    for word in words:
                        try:
                            score = float(word.strip('():'))
                            if 0.0 <= score <= 1.0:
                                sections['quality_score'] = score
                                break
                        except ValueError:
                            continue
                except Exception:
                    pass
                current_section = None
            elif current_section and line.startswith('-'):
                # This is a list item
                item = line[1:].strip()
                if item:
                    sections[current_section].append(item)
        
        return sections
    
    async def improve(self, output: str, critique: Critique) -> str:
        """
        Generate an improved version based on critique.
        
        Args:
            output: The original output
            critique: Critique with suggestions
            
        Returns:
            Improved version of the output
        """
        prompt = self._build_improvement_prompt(output, critique)
        
        response = await self.llm_provider.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.content.strip()
    
    def _build_improvement_prompt(self, output: str, critique: Critique) -> str:
        """Build the improvement prompt."""
        issues_text = "\n".join([f"- {issue}" for issue in critique.issues])
        suggestions_text = "\n".join([f"- {suggestion}" for suggestion in critique.suggestions])
        
        return f"""Please improve the following output based on the critique provided.

Original output:
{output}

Issues identified:
{issues_text}

Suggestions for improvement:
{suggestions_text}

Please provide an improved version that addresses these issues and incorporates the suggestions.
Keep the strengths but fix the problems.
"""
