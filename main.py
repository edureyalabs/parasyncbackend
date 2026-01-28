from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Living AI Agent Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Living AI Agent Backend",
        "message": "Hello from Railway!"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat/process")
async def process_chat(
    message_id: str,
    user_id: str,
    agent_id: str,
    message: str
):
    return {
        "success": True,
        "response": f"Echo: {message}",
        "execution_time_ms": 0,
        "model": "test-model"
    }