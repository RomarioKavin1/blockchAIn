from .chat_agent import ChatAgent, AgentResponse, AgentRequest

class RapAgent(ChatAgent):
    """Agent that responds in rap form"""
    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        response = await super().process(request, thread_id)
        
        return AgentResponse(
            content=response.content,
            metadata={
                **response.metadata,
                "style": "rap",
                "beats_per_minute": 90  # Example of agent-specific metadata
            }
        )
