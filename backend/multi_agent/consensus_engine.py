"""
Consensus Engine - Multi-agent decision making

Enables multiple agents to reach consensus on decisions through voting,
weighted opinions, and conflict resolution.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VotingStrategy(Enum):
    """Voting strategies for consensus"""
    MAJORITY = "majority"
    WEIGHTED = "weighted"
    UNANIMOUS = "unanimous"
    THRESHOLD = "threshold"


@dataclass
class AgentOpinion:
    """Represents an agent's opinion on a decision"""
    agent_id: str
    decision: str
    confidence: float  # 0.0 to 1.0
    reasoning: str
    weight: float = 1.0


@dataclass
class ConsensusResult:
    """Result of a consensus process"""
    decision: str
    confidence: float
    participating_agents: List[str]
    opinions: List[AgentOpinion]
    voting_strategy: VotingStrategy
    metadata: Dict[str, Any]


class ConsensusEngine:
    """
    Facilitate multi-agent decision making through consensus.
    
    Features:
    - Multiple voting strategies
    - Weighted voting based on agent expertise
    - Conflict resolution
    - Confidence scoring
    """

    def __init__(self, default_strategy: VotingStrategy = VotingStrategy.WEIGHTED):
        self.default_strategy = default_strategy
        self.agent_weights: Dict[str, float] = {}

    def set_agent_weight(self, agent_id: str, weight: float):
        """Set voting weight for an agent (0.0 to 1.0)"""
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")
        self.agent_weights[agent_id] = weight

    async def reach_consensus(
        self,
        opinions: List[AgentOpinion],
        strategy: Optional[VotingStrategy] = None,
        threshold: float = 0.5,
    ) -> ConsensusResult:
        """
        Reach consensus based on agent opinions.
        
        Args:
            opinions: List of agent opinions
            strategy: Voting strategy to use
            threshold: Threshold for threshold-based voting (0.0 to 1.0)
            
        Returns:
            ConsensusResult with the decided outcome
        """
        strategy = strategy or self.default_strategy

        if not opinions:
            raise ValueError("No opinions provided")

        # Apply agent weights
        for opinion in opinions:
            if opinion.agent_id in self.agent_weights:
                opinion.weight = self.agent_weights[opinion.agent_id]

        # Calculate consensus based on strategy
        if strategy == VotingStrategy.MAJORITY:
            result = self._majority_vote(opinions)
        elif strategy == VotingStrategy.WEIGHTED:
            result = self._weighted_vote(opinions)
        elif strategy == VotingStrategy.UNANIMOUS:
            result = self._unanimous_vote(opinions)
        elif strategy == VotingStrategy.THRESHOLD:
            result = self._threshold_vote(opinions, threshold)
        else:
            raise ValueError(f"Unknown voting strategy: {strategy}")

        logger.info(
            f"Consensus reached: {result.decision} "
            f"(confidence: {result.confidence:.2f}, strategy: {strategy.value})"
        )

        return result

    def _majority_vote(self, opinions: List[AgentOpinion]) -> ConsensusResult:
        """Simple majority voting"""
        vote_counts: Dict[str, int] = {}
        for opinion in opinions:
            vote_counts[opinion.decision] = vote_counts.get(opinion.decision, 0) + 1

        decision = max(vote_counts, key=vote_counts.get)
        confidence = vote_counts[decision] / len(opinions)

        return ConsensusResult(
            decision=decision,
            confidence=confidence,
            participating_agents=[o.agent_id for o in opinions],
            opinions=opinions,
            voting_strategy=VotingStrategy.MAJORITY,
            metadata={"vote_counts": vote_counts},
        )

    def _weighted_vote(self, opinions: List[AgentOpinion]) -> ConsensusResult:
        """Weighted voting based on agent weights and confidence"""
        weighted_scores: Dict[str, float] = {}
        total_weight = sum(o.weight * o.confidence for o in opinions)

        for opinion in opinions:
            score = opinion.weight * opinion.confidence
            weighted_scores[opinion.decision] = (
                weighted_scores.get(opinion.decision, 0.0) + score
            )

        decision = max(weighted_scores, key=weighted_scores.get)
        confidence = weighted_scores[decision] / total_weight if total_weight > 0 else 0.0

        return ConsensusResult(
            decision=decision,
            confidence=confidence,
            participating_agents=[o.agent_id for o in opinions],
            opinions=opinions,
            voting_strategy=VotingStrategy.WEIGHTED,
            metadata={"weighted_scores": weighted_scores},
        )

    def _unanimous_vote(self, opinions: List[AgentOpinion]) -> ConsensusResult:
        """Unanimous voting - all agents must agree"""
        decisions = set(o.decision for o in opinions)

        if len(decisions) == 1:
            decision = list(decisions)[0]
            avg_confidence = sum(o.confidence for o in opinions) / len(opinions)
            return ConsensusResult(
                decision=decision,
                confidence=avg_confidence,
                participating_agents=[o.agent_id for o in opinions],
                opinions=opinions,
                voting_strategy=VotingStrategy.UNANIMOUS,
                metadata={"unanimous": True},
            )
        else:
            # No consensus - return most confident opinion
            best_opinion = max(opinions, key=lambda o: o.confidence)
            return ConsensusResult(
                decision=best_opinion.decision,
                confidence=0.0,  # No consensus
                participating_agents=[o.agent_id for o in opinions],
                opinions=opinions,
                voting_strategy=VotingStrategy.UNANIMOUS,
                metadata={"unanimous": False, "disagreement": True},
            )

    def _threshold_vote(
        self, opinions: List[AgentOpinion], threshold: float
    ) -> ConsensusResult:
        """Threshold voting - decision must reach specified threshold"""
        vote_counts: Dict[str, int] = {}
        for opinion in opinions:
            vote_counts[opinion.decision] = vote_counts.get(opinion.decision, 0) + 1

        decision = max(vote_counts, key=vote_counts.get)
        confidence = vote_counts[decision] / len(opinions)

        return ConsensusResult(
            decision=decision,
            confidence=confidence,
            participating_agents=[o.agent_id for o in opinions],
            opinions=opinions,
            voting_strategy=VotingStrategy.THRESHOLD,
            metadata={
                "vote_counts": vote_counts,
                "threshold": threshold,
                "threshold_met": confidence >= threshold,
            },
        )
