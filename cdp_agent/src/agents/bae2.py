from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    AGENT = "agent"

class AgentConfig(BaseModel):
    name: str
    description: str
    temperature: float = 0.7
    system_prompt: str
    allowed_interactions: List[str] = Field(default_factory=list)

class AgentRequest(BaseModel):
    message: str
    from_user: str = Field(..., alias="from")
    available_agents: Dict[str, str]
    context: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        populate_by_name = True

class AgentResponse(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    to: str
    message_type: MessageType
    required_format: Optional[Dict[str, str]] = None
    follow_up: List[str] = Field(default_factory=list)

class BaseAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
    
    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        raise NotImplementedError

    def _requires_specific_format(self, content: str) -> bool:
        return False

    def _determine_message_type(self, content: str, available_agents: Dict[str, str]) -> MessageType:
        return MessageType.USER if not any(f"@{agent}" in content for agent in available_agents) else MessageType.AGENT

    def _extract_target(self, content: str, available_agents: Dict[str, str]) -> str:
        for agent in available_agents:
            if f"@{agent}" in content:
                return agent
        return "user"