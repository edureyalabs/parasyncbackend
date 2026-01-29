from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from agent_manager import agent_manager
from models import ChatMessage, ChatResponse
from database import db
from config import SERVER_CONFIG, LLM_CONFIG
from tools import get_available_tools
import asyncio
from pydantic import BaseModel
import traceback
from fastapi import FastAPI, HTTPException

# Add this model near the top with your other models
class ProcessChatRequest(BaseModel):
    message_id: str
    user_id: str
    agent_id: str
    message: str


app = FastAPI(title="Living AI Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    asyncio.create_task(periodic_cleanup())

async def periodic_cleanup():
    while True:
        await asyncio.sleep(300)
        await agent_manager.cleanup_idle_agents()

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Living AI Agent Backend",
        "active_agents": agent_manager.get_active_agent_count()
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat/process")
async def process_chat(request: ProcessChatRequest):
    try:
        print(f"Processing chat request: user_id={request.user_id}, agent_id={request.agent_id}")
        
        agent = await agent_manager.get_or_create_agent(request.user_id, request.agent_id)
        print(f"Agent created/retrieved successfully")
        
        response = await agent.handle_message(request.message)
        print(f"Message handled, response: {response[:100]}...")
        
        return {
            "success": True,
            "response": response,
            "execution_time_ms": 0,
            "model": LLM_CONFIG["model"],
            "tools_available": len(get_available_tools())
        }
    
    except Exception as e:
        print(f"ERROR in process_chat: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{user_id}/{agent_id}")
async def get_tasks(user_id: str, agent_id: str):
    try:
        agent = await agent_manager.get_or_create_agent(user_id, agent_id)
        
        active_tasks = agent.get_active_task_states()
        
        all_tasks = await db.get_user_agent_tasks(user_id, agent_id)
        
        return {
            "active_tasks": active_tasks,
            "all_tasks": [
                {
                    "id": task.id,
                    "task_name": task.task_name,
                    "status": task.status.value,
                    "tool_name": task.tool_name,
                    "result": task.result,
                    "error_message": task.error_message,
                    "created_at": task.created_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                }
                for task in all_tasks
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tasks/cancel")
async def cancel_task(user_id: str, agent_id: str, task_id: str):
    try:
        agent = await agent_manager.get_or_create_agent(user_id, agent_id)
        
        await agent.cancel_task(task_id)
        
        return {"status": "cancelled", "task_id": task_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/active")
async def get_active_agents():
    return {
        "active_agent_count": agent_manager.get_active_agent_count()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=SERVER_CONFIG["host"],
        port=SERVER_CONFIG["port"],
        reload=SERVER_CONFIG["reload"]
    )