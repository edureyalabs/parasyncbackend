import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AGENT_CONFIG_ID = "ceb4e732-184c-4dfb-9291-5a294368f6fe"
MAX_CONCURRENT_TASKS = 5