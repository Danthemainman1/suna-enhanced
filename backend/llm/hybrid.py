"""
Hybrid LLM router for intelligent provider selection.

This module routes requests between local and cloud LLMs based on
task complexity, cost optimization, and availability.
"""

import time
from typing import AsyncGenerator, Optional, Dict, Any
import logging

from .provider import LLMProvider, LLMResponse, ModelInfo


logger = logging.getLogger(__name__)


class TaskComplexity:
    """Task complexity levels for routing decisions."""
    SIMPLE = "simple"      # Simple queries, summaries (< 1K tokens)
    MEDIUM = "medium"      # Standard tasks, analysis (1K-5K tokens)
    COMPLEX = "complex"    # Complex reasoning, code (5K-10K tokens)
    VERY_COMPLEX = "very_complex"  # Advanced reasoning, large context (> 10K tokens)


class HybridRouter(LLMProvider):
    """
    Intelligent router between local and cloud LLM providers.
    
    Features:
    - Route based on task complexity
    - Fallback from local to cloud on failure
    - Cost optimization (prefer local when possible)
    - Latency-based routing
    - Load balancing across providers
    """
    
    def __init__(
        self,
        local_provider: Optional[LLMProvider] = None,
        cloud_provider: Optional[LLMProvider] = None,
        fallback_provider: Optional[LLMProvider] = None,
        prefer_local: bool = True,
        max_local_tokens: int = 8000,
        complexity_threshold: str = TaskComplexity.MEDIUM,
        enable_fallback: bool = True,
        **config
    ):
        """
        Initialize hybrid router.
        
        Args:
            local_provider: Local LLM provider (e.g., Ollama)
            cloud_provider: Primary cloud provider (e.g., Anthropic, OpenAI)
            fallback_provider: Fallback cloud provider
            prefer_local: Prefer local over cloud when possible
            max_local_tokens: Max tokens for local provider before switching to cloud
            complexity_threshold: Complexity level at which to prefer cloud
            enable_fallback: Enable fallback on provider failure
            **config: Additional configuration
        """
        super().__init__(**config)
        self.local_provider = local_provider
        self.cloud_provider = cloud_provider
        self.fallback_provider = fallback_provider
        self.prefer_local = prefer_local
        self.max_local_tokens = max_local_tokens
        self.complexity_threshold = complexity_threshold
        self.enable_fallback = enable_fallback
        
        # Stats tracking
        self.stats = {
            "local_calls": 0,
            "cloud_calls": 0,
            "fallback_calls": 0,
            "total_latency": 0.0,
            "cost_saved": 0.0
        }
    
    async def _estimate_complexity(
        self,
        prompt: str,
        **kwargs
    ) -> str:
        """
        Estimate task complexity based on prompt characteristics.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional context
            
        Returns:
            Complexity level
        """
        prompt_length = len(prompt)
        
        # Check for complexity indicators
        complexity_keywords = [
            "analyze", "compare", "explain", "reasoning",
            "complex", "detailed", "comprehensive"
        ]
        has_complexity_keywords = any(kw in prompt.lower() for kw in complexity_keywords)
        
        # Simple heuristics
        if prompt_length < 500 and not has_complexity_keywords:
            return TaskComplexity.SIMPLE
        elif prompt_length < 2000 and not has_complexity_keywords:
            return TaskComplexity.MEDIUM
        elif prompt_length < 5000:
            return TaskComplexity.COMPLEX
        else:
            return TaskComplexity.VERY_COMPLEX
    
    async def _select_provider(
        self,
        prompt: str,
        force_cloud: bool = False,
        **kwargs
    ) -> LLMProvider:
        """
        Select the best provider based on task characteristics.
        
        Args:
            prompt: Input prompt
            force_cloud: Force cloud provider usage
            **kwargs: Additional context
            
        Returns:
            Selected provider
        """
        # Force cloud if requested
        if force_cloud:
            return self.cloud_provider or self.fallback_provider
        
        # Check if local provider is available
        if not self.local_provider:
            return self.cloud_provider or self.fallback_provider
        
        # Check local provider health
        if not await self.local_provider.health_check():
            logger.warning("Local provider unhealthy, using cloud")
            return self.cloud_provider or self.fallback_provider
        
        # Estimate complexity
        complexity = await self._estimate_complexity(prompt, **kwargs)
        
        # Check max tokens
        max_tokens = kwargs.get("max_tokens", 2000)
        if max_tokens > self.max_local_tokens:
            logger.info(f"Tokens {max_tokens} exceed local limit, using cloud")
            return self.cloud_provider or self.fallback_provider
        
        # Route based on complexity and preferences
        complexity_levels = [
            TaskComplexity.SIMPLE,
            TaskComplexity.MEDIUM,
            TaskComplexity.COMPLEX,
            TaskComplexity.VERY_COMPLEX
        ]
        
        threshold_idx = complexity_levels.index(self.complexity_threshold)
        current_idx = complexity_levels.index(complexity)
        
        if current_idx >= threshold_idx and not self.prefer_local:
            logger.info(f"Complexity {complexity} meets threshold, using cloud")
            return self.cloud_provider or self.fallback_provider
        
        # Default to local if prefer_local is True
        if self.prefer_local:
            logger.info("Using local provider (preferred)")
            return self.local_provider
        
        return self.cloud_provider or self.local_provider
    
    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        force_cloud: bool = False,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion with intelligent routing.
        
        Args:
            prompt: Input prompt
            model: Optional model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            force_cloud: Force cloud provider usage
            **kwargs: Additional parameters
            
        Returns:
            LLMResponse from selected provider
        """
        start_time = time.time()
        
        # Select provider
        provider = await self._select_provider(
            prompt,
            force_cloud=force_cloud,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Track stats
        if provider == self.local_provider:
            self.stats["local_calls"] += 1
        else:
            self.stats["cloud_calls"] += 1
        
        try:
            response = await provider.generate(
                prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Track latency
            latency = time.time() - start_time
            self.stats["total_latency"] += latency
            
            # Estimate cost savings if used local
            if provider == self.local_provider and self.cloud_provider:
                cloud_info = await self.cloud_provider.get_model_info()
                if cloud_info.cost_per_1k_input_tokens:
                    tokens = response.usage.get("total_tokens", 0) if response.usage else 0
                    saved = (tokens / 1000) * cloud_info.cost_per_1k_input_tokens
                    self.stats["cost_saved"] += saved
            
            return response
            
        except Exception as e:
            logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
            
            # Try fallback if enabled
            if self.enable_fallback and self.fallback_provider and provider != self.fallback_provider:
                logger.info("Attempting fallback provider")
                self.stats["fallback_calls"] += 1
                
                try:
                    return await self.fallback_provider.generate(
                        prompt,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise
            
            raise
    
    async def stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        force_cloud: bool = False,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Stream completion with intelligent routing.
        
        Args:
            prompt: Input prompt
            model: Optional model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            force_cloud: Force cloud provider usage
            **kwargs: Additional parameters
            
        Yields:
            Text chunks from selected provider
        """
        # Select provider
        provider = await self._select_provider(
            prompt,
            force_cloud=force_cloud,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # Track stats
        if provider == self.local_provider:
            self.stats["local_calls"] += 1
        else:
            self.stats["cloud_calls"] += 1
        
        try:
            async for chunk in provider.stream(
                prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            
            # Try fallback
            if self.enable_fallback and self.fallback_provider and provider != self.fallback_provider:
                logger.info("Attempting fallback streaming")
                self.stats["fallback_calls"] += 1
                
                async for chunk in self.fallback_provider.stream(
                    prompt,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                ):
                    yield chunk
            else:
                raise
    
    async def get_model_info(self, model: Optional[str] = None) -> ModelInfo:
        """Get model info from primary provider."""
        provider = self.cloud_provider or self.local_provider
        if not provider:
            raise ValueError("No provider available")
        return await provider.get_model_info(model)
    
    async def health_check(self) -> bool:
        """Check health of all providers."""
        results = {}
        
        if self.local_provider:
            results["local"] = await self.local_provider.health_check()
        
        if self.cloud_provider:
            results["cloud"] = await self.cloud_provider.health_check()
        
        if self.fallback_provider:
            results["fallback"] = await self.fallback_provider.health_check()
        
        # Healthy if at least one provider is available
        return any(results.values())
    
    async def list_models(self) -> list[str]:
        """List models from all providers."""
        models = []
        
        if self.local_provider:
            try:
                local_models = await self.local_provider.list_models()
                models.extend([f"local:{m}" for m in local_models])
            except Exception as e:
                logger.warning(f"Failed to list local models: {e}")
        
        if self.cloud_provider:
            try:
                cloud_models = await self.cloud_provider.list_models()
                models.extend([f"cloud:{m}" for m in cloud_models])
            except Exception as e:
                logger.warning(f"Failed to list cloud models: {e}")
        
        return models
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get router statistics.
        
        Returns:
            Dictionary with usage stats
        """
        total_calls = self.stats["local_calls"] + self.stats["cloud_calls"]
        
        return {
            "total_calls": total_calls,
            "local_calls": self.stats["local_calls"],
            "cloud_calls": self.stats["cloud_calls"],
            "fallback_calls": self.stats["fallback_calls"],
            "local_percentage": (self.stats["local_calls"] / total_calls * 100) if total_calls > 0 else 0,
            "average_latency": (self.stats["total_latency"] / total_calls) if total_calls > 0 else 0,
            "estimated_cost_saved": self.stats["cost_saved"]
        }
