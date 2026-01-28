import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from models import TaskState, TaskStatus, Message
from database import db
from llm_client import llm_client
from tools import execute_tool, get_available_tools
from config import AGENT_CONFIG

class LivingAgent:
    def __init__(self, user_id: str, agent_id: str):
        self.user_id = user_id
        self.agent_id = agent_id
        self.agent_data: Optional[Dict[str, Any]] = None
        self.conversation_context: List[Message] = []
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.task_states: Dict[str, TaskState] = {}
        self.last_activity = datetime.now()
    
    async def initialize(self):
        self.agent_data = await db.get_agent_data(self.agent_id)
        
        network = await db.get_user_agent_network(self.user_id, self.agent_id)
        if not network:
            raise ValueError(f"Agent {self.agent_id} not in user {self.user_id} network")
        
        recent_messages = await db.get_recent_messages(
            self.user_id,
            self.agent_id,
            limit=AGENT_CONFIG["max_conversation_history"]
        )
        
        for msg in recent_messages:
            self.conversation_context.append(
                Message(
                    role="user" if msg["sender_type"] == "user" else "assistant",
                    content=msg["message_text"]
                )
            )
        
        await self._resume_pending_tasks()
    
    async def _resume_pending_tasks(self):
        pending_tasks = await db.get_pending_tasks(self.user_id, self.agent_id)
        
        for task in pending_tasks:
            background_task = asyncio.create_task(
                self._execute_task(task.id, task.tool_name, task.tool_params)
            )
            
            self.active_tasks[task.id] = background_task
            self.task_states[task.id] = TaskState(
                id=task.id,
                name=task.task_name,
                status=TaskStatus.RUNNING,
                progress=0,
                created_at=task.created_at
            )
    
    async def handle_message(self, message_text: str) -> str:
        self.last_activity = datetime.now()
        
        self.conversation_context.append(Message(role="user", content=message_text))
        
        if len(self.conversation_context) > AGENT_CONFIG["max_conversation_history"]:
            self.conversation_context = self.conversation_context[-AGENT_CONFIG["max_conversation_history"]:]
        
        system_prompt = self._build_system_prompt()
        
        messages = [{"role": msg.role, "content": msg.content} for msg in self.conversation_context]
        
        response = await llm_client.chat(
            messages=messages,
            tools=get_available_tools(),
            system=system_prompt
        )
        
        if response["tool_calls"]:
            await self._handle_tool_calls(response["tool_calls"])
            
            tool_response = "I've started the requested tasks. I'll notify you when they complete."
            self.conversation_context.append(Message(role="assistant", content=tool_response))
            return tool_response
        
        assistant_message = response["content"]
        self.conversation_context.append(Message(role="assistant", content=assistant_message))
        
        return assistant_message
    
    def _build_system_prompt(self) -> str:
        task_summary = self._get_task_summary()
        
        agent_name = self.agent_data.get("display_name", "AI Agent")
        agent_role = self.agent_data.get("role", "AI Assistant")
        agent_goal = self.agent_data.get("goal", "Help users accomplish their tasks")
        
        return f"""You are {agent_name}, a {agent_role}.

Your goal: {agent_goal}

Current active tasks:
{task_summary}

You can:
1. Answer questions about running tasks
2. Start new tasks using available tools (add_numbers, multiply_numbers, divide_numbers, calculate_sin, calculate_power)
3. Provide status updates on tasks
4. Have natural conversations while tasks run in background

All tool operations take 60 seconds to complete. When starting a task, acknowledge it and let the user know you'll notify them when it completes.

Be conversational and helpful. Always be aware of task context when responding."""
    
    def _get_task_summary(self) -> str:
        if not self.task_states:
            return "No active tasks"
        
        summary = []
        for task_id, state in self.task_states.items():
            summary.append(
                f"- {state.name}: {state.status.value} ({state.progress}% complete)"
            )
        return "\n".join(summary)
    
    async def _handle_tool_calls(self, tool_calls: List[Dict[str, Any]]):
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            params = tool_call["arguments"]
            
            task_name = f"{tool_name}({', '.join(f'{k}={v}' for k, v in params.items())})"
            
            task_data = {
                "user_id": self.user_id,
                "agent_id": self.agent_id,
                "task_name": task_name,
                "task_description": f"Execute {tool_name} with parameters {params}",
                "tool_name": tool_name,
                "tool_params": params,
                "status": TaskStatus.PENDING.value,
                "estimated_duration": 60,
                "progress": 0
            }
            
            task = await db.create_task(task_data)
            
            background_task = asyncio.create_task(
                self._execute_task(task.id, tool_name, params)
            )
            
            self.active_tasks[task.id] = background_task
            self.task_states[task.id] = TaskState(
                id=task.id,
                name=task_name,
                status=TaskStatus.RUNNING,
                progress=0,
                created_at=task.created_at
            )
    
    async def _execute_task(self, task_id: str, tool_name: str, params: Dict[str, Any]):
        try:
            await db.update_task(task_id, {
                "status": TaskStatus.RUNNING.value,
                "started_at": datetime.now().isoformat()
            })
            
            if task_id in self.task_states:
                self.task_states[task_id].status = TaskStatus.RUNNING
            
            result = await execute_tool(tool_name, params)
            
            await db.update_task(task_id, {
                "status": TaskStatus.COMPLETED.value,
                "completed_at": datetime.now().isoformat(),
                "result": result,
                "progress": 100
            })
            
            task = await db.get_task(task_id)
            await self._notify_user(
                f"Task '{task.task_name}' completed! Result: {result.get('result')}"
            )
            
        except Exception as e:
            await db.update_task(task_id, {
                "status": TaskStatus.FAILED.value,
                "completed_at": datetime.now().isoformat(),
                "error_message": str(e)
            })
            
            task = await db.get_task(task_id)
            await self._notify_user(
                f"Task '{task.task_name}' failed: {str(e)}"
            )
        
        finally:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
            if task_id in self.task_states:
                del self.task_states[task_id]
    
    async def _notify_user(self, message: str):
        await db.insert_chat_message(
            user_id=self.user_id,
            agent_id=self.agent_id,
            message_text=message,
            sender_type="agent",
            status="completed"
        )
    
    async def cancel_task(self, task_id: str):
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            
            await db.update_task(task_id, {
                "status": TaskStatus.CANCELLED.value,
                "completed_at": datetime.now().isoformat()
            })
            
            if task_id in self.task_states:
                del self.task_states[task_id]
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    def get_active_task_states(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": state.id,
                "name": state.name,
                "status": state.status.value,
                "progress": state.progress,
                "created_at": state.created_at.isoformat()
            }
            for state in self.task_states.values()
        ]
    
    async def shutdown(self):
        for task_id in list(self.active_tasks.keys()):
            self.active_tasks[task_id].cancel()
        
        self.active_tasks.clear()
        self.task_states.clear()
        self.conversation_context.clear()