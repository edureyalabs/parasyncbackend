from agent_builder import build_agent
from database import get_agent_data, get_agent_config, get_chat_history
from crewai import Task, Crew
import time

def process_chat_message(user_id: str, agent_id: str, message: str):
    print(f"Processing chat message for user: {user_id}")
    start_time = time.time()
    
    try:
        agent_data = get_agent_data(agent_id)
        config_data = get_agent_config()
        agent = build_agent(agent_data, config_data)
        
        # Get chat history for context
        chat_history = get_chat_history(user_id, agent_id, limit=10)
        context = "\n".join([
            f"{msg['sender_type'].upper()}: {msg['message_text']}" 
            for msg in chat_history 
            if msg['status'] == 'completed'
        ])
        
        # Create task with context
        full_prompt = f"""Previous conversation:
{context}

Current user message: {message}

Respond naturally and helpfully to the user's message."""

        # Create CrewAI Task
        task = Task(
            description=full_prompt,
            expected_output="A helpful response to the user's message",
            agent=agent
        )
        
        # Create and execute Crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=config_data.get('verbose', False)
        )
        
        print("Executing crew kickoff")
        result = crew.kickoff()
        
        # Extract response text
        response = str(result)
        
        execution_time = int((time.time() - start_time) * 1000)
        print(f"Agent response generated in {execution_time}ms")
        
        return {
            'response': response,
            'execution_time_ms': execution_time,
            'model': config_data.get('llm', 'groq/llama-3.1-8b-instant')
        }
    except Exception as e:
        print(f"Error in process_chat_message: {str(e)}")
        raise