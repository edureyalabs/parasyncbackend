import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")
if not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_SERVICE_KEY environment variable is required")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")

LLM_CONFIG = {
    "model": "llama-3.3-70b-versatile",
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 1.0,
}

AGENT_CONFIG = {
    "max_conversation_history": 20,
    "task_check_interval": 5,
    "agent_idle_timeout": 3600,
}

SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": False,
}