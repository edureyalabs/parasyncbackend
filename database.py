from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY, AGENT_CONFIG_ID
from datetime import datetime

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_agent_data(agent_id: str):
    print(f"Fetching agent data for: {agent_id}")
    response = supabase.table('agents').select('*').eq('id', agent_id).single().execute()
    print(f"Agent data fetched: {response.data['username']}")
    return response.data

def get_agent_config():
    print(f"Fetching agent config: {AGENT_CONFIG_ID}")
    response = supabase.table('agent_config').select('*').eq('id', AGENT_CONFIG_ID).single().execute()
    print("Agent config fetched successfully")
    return response.data

def get_chat_history(user_id: str, agent_id: str, limit: int = 10):
    print(f"Fetching chat history for user: {user_id}, agent: {agent_id}")
    response = (supabase.table('chat_messages')
        .select('*')
        .eq('user_id', user_id)
        .eq('agent_id', agent_id)
        .eq('status', 'completed')  # Only get completed messages
        .order('created_at', desc=False)
        .limit(limit)
        .execute())
    print(f"Fetched {len(response.data)} messages")
    return response.data