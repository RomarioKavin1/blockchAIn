from pydantic import BaseModel, Field
from typing import Dict, Any

class AgentConfig(BaseModel):
    name: str
    description: str
    temperature: float = 0.7
    system_prompt: str

class AgentRequest(BaseModel):
    message: str
    from_user: str = Field(..., alias="from")

    class Config:
        populate_by_name = True

class AgentResponse(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class BaseAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
    
    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        raise NotImplementedError