import asyncio
import math
from typing import Dict, Any, List

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_numbers",
            "description": "Add two numbers together. This operation takes 60 seconds to complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "Multiply two numbers. This operation takes 60 seconds to complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "divide_numbers",
            "description": "Divide first number by second number. This operation takes 60 seconds to complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Numerator"
                    },
                    "b": {
                        "type": "number",
                        "description": "Denominator (cannot be zero)"
                    }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_sin",
            "description": "Calculate sine of an angle in radians. This operation takes 60 seconds to complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "angle": {
                        "type": "number",
                        "description": "Angle in radians"
                    }
                },
                "required": ["angle"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_power",
            "description": "Calculate a raised to power b. This operation takes 60 seconds to complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Base number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Exponent"
                    }
                },
                "required": ["a", "b"]
            }
        }
    }
]

async def execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    await asyncio.sleep(60)
    
    if tool_name == "add_numbers":
        result = params["a"] + params["b"]
        return {"result": result}
    
    elif tool_name == "multiply_numbers":
        result = params["a"] * params["b"]
        return {"result": result}
    
    elif tool_name == "divide_numbers":
        if params["b"] == 0:
            raise ValueError("Cannot divide by zero")
        result = params["a"] / params["b"]
        return {"result": result}
    
    elif tool_name == "calculate_sin":
        result = math.sin(params["angle"])
        return {"result": result}
    
    elif tool_name == "calculate_power":
        result = math.pow(params["a"], params["b"])
        return {"result": result}
    
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

def get_available_tools() -> List[Dict[str, Any]]:
    return AVAILABLE_TOOLS