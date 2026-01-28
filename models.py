from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskCreate(BaseModel):
    user_id: str
    agent_id: str
    task_name: str
    task_description: Optional[str] = None
    tool_name: str
    tool_params: Dict[str, Any]

class Task(BaseModel):
    id: str
    user_id: str
    agent_id: str
    task_name: str
    task_description: Optional[str]
    status: TaskStatus
    tool_name: str
    tool_params: Dict[str, Any]
    result: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_duration: int
    progress: int

class TaskState(BaseModel):
    id: str
    name: str
    status: TaskStatus
    progress: int
    created_at: datetime

class Message(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    user_id: str
    agent_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    task_updates: Optional[List[Dict[str, Any]]] = None