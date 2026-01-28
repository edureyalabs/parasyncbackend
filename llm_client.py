from groq import Groq
from config import GROQ_API_KEY, LLM_CONFIG
from typing import List, Dict, Any, Optional
import json

class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = LLM_CONFIG["model"]
        self.temperature = LLM_CONFIG["temperature"]
        self.max_tokens = LLM_CONFIG["max_tokens"]
        self.top_p = LLM_CONFIG["top_p"]
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system: Optional[str] = None
    ) -> Dict[str, Any]:
        
        formatted_messages = messages.copy()
        
        if system:
            formatted_messages.insert(0, {
                "role": "system",
                "content": system
            })
        
        kwargs = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**kwargs)
        
        message = response.choices[0].message
        
        result = {
            "content": message.content or "",
            "tool_calls": []
        }
        
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tool_call in message.tool_calls:
                result["tool_calls"].append({
                    "id": tool_call.id,
                    "name": tool_call.function.name,
                    "arguments": json.loads(tool_call.function.arguments)
                })
        
        return result

llm_client = LLMClient()