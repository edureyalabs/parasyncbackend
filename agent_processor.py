from agent_builder import build_agent
from database import get_agent_data, get_agent_config, get_chat_history
import time

def process_chat_message(user_id: str, agent_id: str, message: str, task_id: str = None):
    print(f"Processing chat message for user: {user_id}")
    start_time = time.time()
    
    agent_data = get_agent_data(agent_id)
    config_data = get_agent_config()
    agent = build_agent(agent_data, config_data)
    
    chat_history = get_chat_history(user_id, agent_id, limit=10)
    context = "\n".join([f"{msg['sender_type']}: {msg['message_text']}" for msg in chat_history])
    
    full_prompt = f"Context:\n{context}\n\nUser: {message}\n\nRespond naturally:"
    
    print("Executing agent kickoff")
    response = agent.execute_task(full_prompt)
    
    execution_time = int((time.time() - start_time) * 1000)
    print(f"Agent response generated in {execution_time}ms")
    
    return {
        'response': response,
        'execution_time_ms': execution_time
    }

def process_task_execution(task_id: str, user_id: str, agent_id: str, description: str):
    print(f"Processing task execution: {task_id}")
    start_time = time.time()
    
    try:
        agent_data = get_agent_data(agent_id)
        config_data = get_agent_config()
        agent = build_agent(agent_data, config_data)
        
        prompt = f"Task: {description}\n\nExecute this task and provide detailed results:"
        
        print("Executing task agent kickoff")
        result = agent.execute_task(prompt)
        
        execution_time = int((time.time() - start_time) * 1000)
        print(f"Task completed in {execution_time}ms")
        
        return {
            'success': True,
            'result': result,
            'execution_time_ms': execution_time
        }
    except Exception as e:
        print(f"Task execution failed: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'execution_time_ms': int((time.time() - start_time) * 1000)
        }