from typing import Dict, List, Optional
from pydantic import BaseModel
from cdp import Wallet
import json

class Message(BaseModel):
    from_agent: str
    to_agent: str
    content: str
    request_type: Optional[str]

class BaseAgent:
    def __init__(self, agent_id: str, wallet: Wallet, capabilities: List[str]):
        self.id = agent_id
        self.wallet = wallet
        self.capabilities = capabilities
        self.active = True
        self.message_queue: List[Message] = []
        
    async def process_message(self, message: Message):
        if not self.active:
            return None
        return await self._handle_message(message)
        
    async def _handle_message(self, message: Message):
        raise NotImplementedError