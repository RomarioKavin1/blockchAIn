from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from .base import BaseAgent, AgentConfig, AgentRequest, AgentResponse

class ChatAgent(BaseAgent):
    """Standard chat agent using LangChain"""
    def setup(self):
        self.model = ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.config.system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])
        
        def call_model(state: MessagesState):
            chain = self.prompt | self.model
            response = chain.invoke(state)
            return {"messages": [AIMessage(content=response.content)]}
        
        workflow = StateGraph(state_schema=MessagesState)
        workflow.add_edge(START, "model")
        workflow.add_node("model", call_model)
        
        memory = MemorySaver()
        self.chain = workflow.compile(checkpointer=memory)
    
    async def process(self, request: AgentRequest, thread_id: str) -> AgentResponse:
        input_messages = [HumanMessage(content=request.message)]
        config = {"configurable": {"thread_id": thread_id}}
        output = self.chain.invoke({"messages": input_messages}, config)
        response = output["messages"][-1].content
        
        return AgentResponse(
            content=response,
            metadata={
                "agent_name": self.config.name,
                "from_user": request.from_user
            }
        )