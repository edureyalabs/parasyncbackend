import os
from dotenv import load_dotenv

# Load .env file if it exists (for local development)
# In production (Railway), this will do nothing and env vars come from the platform
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate required environment variables
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set")
if not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_SERVICE_KEY environment variable is not set")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

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
    "port": int(os.getenv("PORT", 8000)),  # Railway automatically sets PORT
    "reload": False,
}