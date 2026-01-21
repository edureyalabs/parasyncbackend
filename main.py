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

class ChatRequest(BaseModel):
    user_id: str
    agent_id: str
    message: str
    task_id: str = None

class TaskCreateRequest(BaseModel):
    user_id: str
    agent_id: str
    message: str

class TaskListRequest(BaseModel):
    user_id: str
    agent_id: str
    limit: int = 10

@stub.function(
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("groq-secret")
    ],
    timeout=600
)
@asgi_app()
def fastapi_app():
    from database import insert_message, create_task, update_task_status, get_user_concurrent_tasks, get_recent_tasks, insert_task_execution
    from agent_processor import process_chat_message, process_task_execution
    from config import MAX_CONCURRENT_TASKS
    
    @app.post("/chat/send")
    async def send_chat(request: ChatRequest):
        print(f"Received chat request from user: {request.user_id}")
        
        try:
            insert_message(request.user_id, request.agent_id, request.message, 'user', request.task_id)
            
            result = process_chat_message(request.user_id, request.agent_id, request.message, request.task_id)
            
            agent_message = insert_message(
                request.user_id, 
                request.agent_id, 
                result['response'], 
                'agent', 
                request.task_id
            )
            
            return {
                'success': True,
                'message': agent_message,
                'execution_time_ms': result['execution_time_ms']
            }
        except Exception as e:
            print(f"Error in send_chat: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/task/create")
    async def create_task_endpoint(request: TaskCreateRequest):
        print(f"Received task create request from user: {request.user_id}")
        
        try:
            concurrent_count = get_user_concurrent_tasks(request.user_id)
            if concurrent_count >= MAX_CONCURRENT_TASKS:
                raise HTTPException(
                    status_code=429, 
                    detail=f"Maximum concurrent tasks limit reached ({MAX_CONCURRENT_TASKS})"
                )
            
            message_clean = request.message.replace('/create', '').strip()
            title = message_clean[:100] if len(message_clean) > 100 else message_clean
            
            task = create_task(request.user_id, request.agent_id, title, message_clean)
            
            insert_message(request.user_id, request.agent_id, request.message, 'user', task['id'])
            
            execute_task_async.spawn(task['id'], request.user_id, request.agent_id, message_clean)
            
            return {
                'success': True,
                'task': task
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            print(f"Error in create_task: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/task/list")
    async def list_tasks(request: TaskListRequest):
        print(f"Received task list request from user: {request.user_id}")
        
        try:
            tasks = get_recent_tasks(request.user_id, request.agent_id, request.limit)
            return {
                'success': True,
                'tasks': tasks
            }
        except Exception as e:
            print(f"Error in list_tasks: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

@stub.function(
    secrets=[
        modal.Secret.from_name("supabase-secrets"),
        modal.Secret.from_name("groq-secret")
    ],
    timeout=3600
)
async def execute_task_async(task_id: str, user_id: str, agent_id: str, description: str):
    from database import update_task_status, insert_message, insert_task_execution
    from agent_processor import process_task_execution
    
    print(f"Starting async task execution: {task_id}")
    
    try:
        update_task_status(task_id, 'running')
        
        result = process_task_execution(task_id, user_id, agent_id, description)
        
        if result['success']:
            update_task_status(task_id, 'completed', result={'output': result['result']})
            
            response_text = f"Task completed successfully:\n\n{result['result']}"
            insert_message(user_id, agent_id, response_text, 'agent', task_id)
            
            insert_task_execution(
                task_id, 
                {'status': 'completed'}, 
                execution_time_ms=result['execution_time_ms']
            )
        else:
            update_task_status(task_id, 'failed', error_message=result['error'])
            
            response_text = f"Task failed: {result['error']}"
            insert_message(user_id, agent_id, response_text, 'agent', task_id)
            
            insert_task_execution(
                task_id, 
                {'status': 'failed', 'error': result['error']}, 
                execution_time_ms=result['execution_time_ms']
            )
        
        print(f"Task execution completed: {task_id}")
    except Exception as e:
        print(f"Critical error in execute_task_async: {str(e)}")
        update_task_status(task_id, 'failed', error_message=str(e))
        insert_message(user_id, agent_id, f"Task failed: {str(e)}", 'agent', task_id)
