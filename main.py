import modal
from modal import Image, Stub, asgi_app
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

image = Image.debian_slim().pip_install(
    "crewai==0.95.2",
    "supabase==2.9.1",
    "python-dotenv==1.0.0",
    "litellm==1.52.12",
    "fastapi==0.115.5",
    "pydantic==2.10.3"
)

stub = Stub("ai-agent-backend", image=image)

app = FastAPI()

class ChatProcessRequest(BaseModel):
    message_id: str
    user_id: str
    agent_id: str
    message: str

@stub.function(
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("groq-secret")
    ],
    timeout=600
)
@asgi_app()
def fastapi_app():
    from database import get_agent_data, get_agent_config, get_chat_history
    from agent_processor import process_chat_message
    
    @app.post("/chat/process")
    async def process_chat(request: ChatProcessRequest):
        print(f"Processing message: {request.message_id}")
        
        try:
            result = process_chat_message(
                request.user_id, 
                request.agent_id, 
                request.message
            )
            
            return {
                'success': True,
                'response': result['response'],
                'execution_time_ms': result['execution_time_ms'],
                'model': result.get('model', 'groq/llama-3.2-90b-text-preview')
            }
        except Exception as e:
            print(f"Error in process_chat: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app