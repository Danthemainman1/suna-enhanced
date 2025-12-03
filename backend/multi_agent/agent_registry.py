"""
Agent Registry - Dynamic agent registration and discovery

The registry maintains a catalog of available agent types, their capabilities,
and configuration. It enables dynamic agent discovery and selection based on
task requirements.
"""

import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AgentCategory(Enum):
    """Agent categories"""
    RESEARCH = "research"
    CODE = "code"
    DATA = "data"
    WRITING = "writing"
    PLANNING = "planning"
    CRITIQUE = "critique"
    EXECUTION = "execution"
    MEMORY = "memory"
    GENERAL = "general"


@dataclass
class AgentCapability:
    """Represents a capability that an agent can perform"""
    id: str
    name: str
    description: str
    category: AgentCategory
    required_tools: List[str] = field(default_factory=list)
    optional_tools: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentType:
    """Represents a type of agent that can be registered"""
    id: str
    name: str
    description: str
    category: AgentCategory
    capabilities: List[AgentCapability]
    version: str = "1.0.0"
    author: str = "Suna Ultra"
    tags: List[str] = field(default_factory=list)
    config_schema: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """
    Registry for agent types and their capabilities.
    
    Features:
    - Register and discover agent types
    - Query agents by capability
    - Validate agent configurations
    - Track agent versions
    """

    def __init__(self):
        self.agent_types: Dict[str, AgentType] = {}
        self.capabilities: Dict[str, AgentCapability] = {}
        self._initialize_default_agents()

    def _initialize_default_agents(self):
        """Initialize default agent types"""
        
        # Research Agent
        research_capabilities = [
            AgentCapability(
                id="web_research",
                name="Web Research",
                description="Search and extract information from the web",
                category=AgentCategory.RESEARCH,
                required_tools=["web_search", "web_scraper"],
            ),
            AgentCapability(
                id="data_synthesis",
                name="Data Synthesis",
                description="Synthesize information from multiple sources",
                category=AgentCategory.RESEARCH,
                required_tools=["llm"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="research_agent",
            name="Research Agent",
            description="Specialized agent for conducting research and gathering information",
            category=AgentCategory.RESEARCH,
            capabilities=research_capabilities,
            tags=["research", "web", "data-gathering"],
        )

        # Code Agent
        code_capabilities = [
            AgentCapability(
                id="code_writing",
                name="Code Writing",
                description="Write code in multiple programming languages",
                category=AgentCategory.CODE,
                required_tools=["llm", "code_interpreter"],
            ),
            AgentCapability(
                id="code_review",
                name="Code Review",
                description="Review code for quality, security, and best practices",
                category=AgentCategory.CODE,
                required_tools=["llm", "static_analyzer"],
            ),
            AgentCapability(
                id="debugging",
                name="Debugging",
                description="Debug and fix code issues",
                category=AgentCategory.CODE,
                required_tools=["llm", "code_interpreter", "debugger"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="code_agent",
            name="Code Agent",
            description="Specialized agent for writing, reviewing, and debugging code",
            category=AgentCategory.CODE,
            capabilities=code_capabilities,
            tags=["code", "programming", "development"],
        )

        # Data Agent
        data_capabilities = [
            AgentCapability(
                id="data_analysis",
                name="Data Analysis",
                description="Analyze datasets and generate insights",
                category=AgentCategory.DATA,
                required_tools=["llm", "data_analyzer"],
            ),
            AgentCapability(
                id="visualization",
                name="Data Visualization",
                description="Create charts and visualizations",
                category=AgentCategory.DATA,
                required_tools=["visualization_tool"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="data_agent",
            name="Data Agent",
            description="Specialized agent for data analysis and visualization",
            category=AgentCategory.DATA,
            capabilities=data_capabilities,
            tags=["data", "analytics", "visualization"],
        )

        # Writer Agent
        writer_capabilities = [
            AgentCapability(
                id="content_writing",
                name="Content Writing",
                description="Write articles, blog posts, and other content",
                category=AgentCategory.WRITING,
                required_tools=["llm"],
            ),
            AgentCapability(
                id="editing",
                name="Content Editing",
                description="Edit and improve written content",
                category=AgentCategory.WRITING,
                required_tools=["llm"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="writer_agent",
            name="Writer Agent",
            description="Specialized agent for content creation and editing",
            category=AgentCategory.WRITING,
            capabilities=writer_capabilities,
            tags=["writing", "content", "editing"],
        )

        # Planner Agent
        planner_capabilities = [
            AgentCapability(
                id="task_planning",
                name="Task Planning",
                description="Break down complex tasks into subtasks",
                category=AgentCategory.PLANNING,
                required_tools=["llm"],
            ),
            AgentCapability(
                id="scheduling",
                name="Scheduling",
                description="Schedule and prioritize tasks",
                category=AgentCategory.PLANNING,
                required_tools=["llm"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="planner_agent",
            name="Planner Agent",
            description="Specialized agent for task planning and scheduling",
            category=AgentCategory.PLANNING,
            capabilities=planner_capabilities,
            tags=["planning", "scheduling", "coordination"],
        )

        # Critic Agent
        critic_capabilities = [
            AgentCapability(
                id="output_review",
                name="Output Review",
                description="Review and critique outputs from other agents",
                category=AgentCategory.CRITIQUE,
                required_tools=["llm"],
            ),
            AgentCapability(
                id="quality_check",
                name="Quality Check",
                description="Verify quality and accuracy of work",
                category=AgentCategory.CRITIQUE,
                required_tools=["llm"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="critic_agent",
            name="Critic Agent",
            description="Specialized agent for reviewing and critiquing other agents' work",
            category=AgentCategory.CRITIQUE,
            capabilities=critic_capabilities,
            tags=["review", "quality", "critique"],
        )

        # Executor Agent
        executor_capabilities = [
            AgentCapability(
                id="command_execution",
                name="Command Execution",
                description="Execute system commands and scripts",
                category=AgentCategory.EXECUTION,
                required_tools=["shell", "sandbox"],
            ),
            AgentCapability(
                id="api_calls",
                name="API Calls",
                description="Make API calls to external services",
                category=AgentCategory.EXECUTION,
                required_tools=["http_client"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="executor_agent",
            name="Executor Agent",
            description="Specialized agent for executing commands and API calls",
            category=AgentCategory.EXECUTION,
            capabilities=executor_capabilities,
            tags=["execution", "automation", "integration"],
        )

        # Memory Agent
        memory_capabilities = [
            AgentCapability(
                id="context_storage",
                name="Context Storage",
                description="Store and retrieve conversation context",
                category=AgentCategory.MEMORY,
                required_tools=["vector_db"],
            ),
            AgentCapability(
                id="knowledge_retrieval",
                name="Knowledge Retrieval",
                description="Retrieve relevant knowledge from storage",
                category=AgentCategory.MEMORY,
                required_tools=["vector_db", "llm"],
            ),
        ]
        
        self.register_agent_type(
            agent_id="memory_agent",
            name="Memory Agent",
            description="Specialized agent for managing long-term memory and context",
            category=AgentCategory.MEMORY,
            capabilities=memory_capabilities,
            tags=["memory", "context", "knowledge"],
        )

    def register_agent_type(
        self,
        agent_id: str,
        name: str,
        description: str,
        category: AgentCategory,
        capabilities: List[AgentCapability],
        version: str = "1.0.0",
        author: str = "Suna Ultra",
        tags: Optional[List[str]] = None,
        config_schema: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentType:
        """Register a new agent type"""
        if agent_id in self.agent_types:
            raise ValueError(f"Agent type {agent_id} is already registered")

        agent_type = AgentType(
            id=agent_id,
            name=name,
            description=description,
            category=category,
            capabilities=capabilities,
            version=version,
            author=author,
            tags=tags or [],
            config_schema=config_schema,
            metadata=metadata or {},
        )

        self.agent_types[agent_id] = agent_type

        # Register capabilities
        for capability in capabilities:
            self.capabilities[capability.id] = capability

        logger.info(f"Registered agent type: {agent_id} ({name})")
        return agent_type

    def get_agent_type(self, agent_id: str) -> Optional[AgentType]:
        """Get an agent type by ID"""
        return self.agent_types.get(agent_id)

    def list_agent_types(
        self,
        category: Optional[AgentCategory] = None,
        tags: Optional[List[str]] = None,
    ) -> List[AgentType]:
        """List agent types, optionally filtered"""
        agents = list(self.agent_types.values())

        if category:
            agents = [a for a in agents if a.category == category]

        if tags:
            tag_set = set(tags)
            agents = [a for a in agents if tag_set.intersection(set(a.tags))]

        return agents

    def find_agents_by_capability(self, capability_id: str) -> List[AgentType]:
        """Find agents that have a specific capability"""
        result = []
        for agent_type in self.agent_types.values():
            if any(c.id == capability_id for c in agent_type.capabilities):
                result.append(agent_type)
        return result

    def get_capability(self, capability_id: str) -> Optional[AgentCapability]:
        """Get a capability by ID"""
        return self.capabilities.get(capability_id)

    def list_capabilities(
        self, category: Optional[AgentCategory] = None
    ) -> List[AgentCapability]:
        """List all capabilities, optionally filtered by category"""
        capabilities = list(self.capabilities.values())
        if category:
            capabilities = [c for c in capabilities if c.category == category]
        return capabilities
