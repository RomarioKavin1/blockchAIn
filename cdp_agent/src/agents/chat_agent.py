from .base import BaseAgent, AgentConfig, AgentRequest, AgentResponse
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class ChatAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self.model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=config.temperature
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", config.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        messages = [HumanMessage(content=request.message)]
        chain = self.prompt | self.model
        response = chain.invoke({"messages": messages})
        return AgentResponse(content=response.content)