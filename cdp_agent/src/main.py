import os
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agents.base import BaseAgent, AgentRequest, AgentResponse
from config.agents import AGENT_CONFIGS, AGENT_CLASSES
from config.cdp_config import initialize_cdp

# Initialize CDP before creating FastAPI app
initialize_cdp()
# Load environment variables
load_dotenv()

# Validate OpenAI API key
if not os.getenv('OPENAI_API_KEY'):
    raise ValueError("OPENAI_API_KEY environment variable is not set")

app = FastAPI(title="Modular Multi-Agent Chat API")

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
agents: Dict[str, BaseAgent] = {}

for agent_id, config in AGENT_CONFIGS.items():
    # Get the appropriate agent class
    agent_class = AGENT_CLASSES.get(agent_id) or AGENT_CLASSES["default"]
    agents[agent_id] = agent_class(config)

@app.post("/{agent_id}/{thread_id}", response_model=AgentResponse)
async def chat_with_agent(
    agent_id: str,
    thread_id: str,
    request: AgentRequest
):
    """Generic endpoint for chatting with any agent"""
    if agent_id not in agents:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_id}' not found. Available agents: {list(agents.keys())}"
        )
    
    try:
        return await agents[agent_id].process(request, thread_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents")
async def list_agents():
    """List all available agents and their descriptions"""
    return {
        agent_id: {
            "name": config.name,
            "description": config.description
        }
        for agent_id, config in AGENT_CONFIGS.items()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)