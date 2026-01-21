from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY, AGENT_CONFIG_ID, MAX_CONCURRENT_TASKS
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

def get_chat_history(user_id: str, agent_id: str, limit: int = 20):
    print(f"Fetching chat history for user: {user_id}, agent: {agent_id}")
    response = supabase.table('chat_messages').select('*').eq('user_id', user_id).eq('agent_id', agent_id).order('created_at', desc=False).limit(limit).execute()
    print(f"Fetched {len(response.data)} messages")
    return response.data

def insert_message(user_id: str, agent_id: str, message_text: str, sender_type: str, task_id: str = None):
    print(f"Inserting {sender_type} message")
    data = {
        'user_id': user_id,
        'agent_id': agent_id,
        'message_text': message_text,
        'sender_type': sender_type,
        'task_id': task_id
    }
    response = supabase.table('chat_messages').insert(data).execute()
    print(f"Message inserted: {response.data[0]['id']}")
    return response.data[0]

def create_task(user_id: str, agent_id: str, title: str, description: str):
    print(f"Creating task: {title}")
    data = {
        'user_id': user_id,
        'agent_id': agent_id,
        'title': title,
        'description': description,
        'status': 'pending'
    }
    response = supabase.table('tasks').insert(data).execute()
    print(f"Task created: {response.data[0]['id']}")
    return response.data[0]

def update_task_status(task_id: str, status: str, result: dict = None, error_message: str = None):
    print(f"Updating task {task_id} to status: {status}")
    data = {'status': status}
    
    if status == 'running':
        data['started_at'] = datetime.utcnow().isoformat()
    elif status in ['completed', 'failed', 'cancelled']:
        data['completed_at'] = datetime.utcnow().isoformat()
    
    if result:
        data['result'] = result
    if error_message:
        data['error_message'] = error_message
    
    response = supabase.table('tasks').update(data).eq('id', task_id).execute()
    print(f"Task status updated: {task_id}")
    return response.data[0]

def get_user_concurrent_tasks(user_id: str):
    print(f"Checking concurrent tasks for user: {user_id}")
    response = supabase.table('tasks').select('id').eq('user_id', user_id).in_('status', ['pending', 'running']).execute()
    count = len(response.data)
    print(f"User has {count} concurrent tasks")
    return count

def get_recent_tasks(user_id: str, agent_id: str, limit: int = 10):
    print(f"Fetching recent tasks for user: {user_id}, agent: {agent_id}")
    response = supabase.table('tasks').select('id, title, status, created_at').eq('user_id', user_id).eq('agent_id', agent_id).order('created_at', desc=True).limit(limit).execute()
    print(f"Fetched {len(response.data)} tasks")
    return response.data

def get_task(task_id: str):
    print(f"Fetching task: {task_id}")
    response = supabase.table('tasks').select('*').eq('id', task_id).single().execute()
    print(f"Task fetched: {response.data['title']}")
    return response.data

def insert_task_execution(task_id: str, execution_log: dict, tokens_used: int = None, execution_time_ms: int = None):
    print(f"Inserting task execution for: {task_id}")
    data = {
        'task_id': task_id,
        'agent_execution_log': execution_log,
        'tokens_used': tokens_used,
        'execution_time_ms': execution_time_ms
    }
    response = supabase.table('task_executions').insert(data).execute()
    print(f"Task execution logged: {response.data[0]['id']}")
    return response.data[0]