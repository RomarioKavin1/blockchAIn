from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class AgentConfig(BaseModel):
    """Base configuration for any agent"""
    name: str
    description: str
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    system_prompt: str
    
    class Config:
        extra = "allow"  # Allows additional fields for specific agent types

class AgentRequest(BaseModel):
    """Base request model for agent interactions"""
    message: str
    from_user: str = Field(..., alias="from")

    class Config:
        populate_by_name = True

class AgentResponse(BaseModel):
    """Base response model for agent interactions"""
    content: str
    metadata: Dict[str, Any] = {}

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    def __init__(self, config: AgentConfig):
        self.config = config
        self.setup()
    
    @abstractmethod
    def setup(self):
        """Setup agent-specific configurations"""
        pass
    
    @abstractmethod
    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        """Process incoming request and return response"""
        pass
