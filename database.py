from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY
from typing import List, Dict, Any, Optional
from models import Task, TaskStatus

class Database:
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    async def get_agent_data(self, agent_id: str) -> Dict[str, Any]:
        response = self.client.table('agents').select('*').eq('id', agent_id).single().execute()
        return response.data
    
    async def get_user_agent_network(self, user_id: str, agent_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table('user_network_agents').select('*').eq('user_id', user_id).eq('agent_id', agent_id).execute()
            
            # Check if any data was returned
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            print(f"Error fetching user agent network: {e}")
            return None
    
    async def create_task(self, task_data: Dict[str, Any]) -> Task:
        response = self.client.table('tasks').insert(task_data).execute()
        return Task(**response.data[0])
    
    async def update_task(self, task_id: str, update_data: Dict[str, Any]) -> Task:
        response = self.client.table('tasks').update(update_data).eq('id', task_id).execute()
        return Task(**response.data[0])
    
    async def get_task(self, task_id: str) -> Optional[Task]:
        try:
            response = self.client.table('tasks').select('*').eq('id', task_id).execute()
            
            if response.data and len(response.data) > 0:
                return Task(**response.data[0])
            return None
        except Exception as e:
            print(f"Error fetching task: {e}")
            return None
    
    async def get_user_agent_tasks(self, user_id: str, agent_id: str, status: Optional[str] = None) -> List[Task]:
        query = self.client.table('tasks').select('*').eq('user_id', user_id).eq('agent_id', agent_id)
        
        if status:
            query = query.eq('status', status)
        
        response = query.order('created_at', desc=True).execute()
        return [Task(**task) for task in response.data]
    
    async def get_pending_tasks(self, user_id: str, agent_id: str) -> List[Task]:
        return await self.get_user_agent_tasks(user_id, agent_id, TaskStatus.PENDING.value)
    
    async def insert_chat_message(self, user_id: str, agent_id: str, message_text: str, sender_type: str, status: str = "completed"):
        message_data = {
            "user_id": user_id,
            "agent_id": agent_id,
            "message_text": message_text,
            "sender_type": sender_type,
            "status": status
        }
        self.client.table('chat_messages').insert(message_data).execute()
    
    async def get_recent_messages(self, user_id: str, agent_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        response = self.client.table('chat_messages').select('*').eq('user_id', user_id).eq('agent_id', agent_id).order('created_at', desc=False).limit(limit).execute()
        return response.data

db = Database()