from crewai.tools import BaseTool
from pydantic import BaseModel, Field, create_model
from typing import Type, Dict, Any, Optional
import requests
import json


def create_input_schema(tool_data: Dict[str, Any]) -> Type[BaseModel]:
    """
    Dynamically create a Pydantic model for tool input based on tool configuration.
    Combines query_params and body_params into a single input schema.
    """
    fields = {}
    
    # Process query parameters
    query_params = tool_data.get('query_params', {})
    if query_params:
        for param_name, param_config in query_params.items():
            description = param_config.get('description', f'{param_name} parameter')
            required = param_config.get('required', False)
            default_value = param_config.get('default', ...)
            
            if not required and default_value == ...:
                default_value = None
            
            fields[param_name] = (
                Optional[str] if not required else str,
                Field(default=default_value, description=description)
            )
    
    # Process body parameters
    body_params = tool_data.get('body_params', {})
    if body_params:
        for param_name, param_config in body_params.items():
            description = param_config.get('description', f'{param_name} parameter')
            required = param_config.get('required', False)
            default_value = param_config.get('default', ...)
            
            if not required and default_value == ...:
                default_value = None
            
            fields[param_name] = (
                Optional[str] if not required else str,
                Field(default=default_value, description=description)
            )
    
    # If no parameters defined, create a simple schema with a message field
    if not fields:
        fields['input_data'] = (
            Optional[str],
            Field(default=None, description="Optional input data for the tool")
        )
    
    # Create the dynamic model
    model_name = f"{tool_data['tool_name'].replace(' ', '_')}_Input"
    return create_model(model_name, **fields)


def create_api_tool(tool_data: Dict[str, Any]) -> BaseTool:
    """
    Create a CrewAI BaseTool instance from database tool configuration.
    
    Args:
        tool_data: Dictionary containing tool configuration from api_tools table
        
    Returns:
        An instance of a dynamically created BaseTool subclass
    """
    # Create input schema
    InputSchema = create_input_schema(tool_data)
    
    # Create the tool class dynamically
    class DynamicAPITool(BaseTool):
        name: str = tool_data['tool_name']
        description: str = tool_data['tool_description']
        args_schema: Type[BaseModel] = InputSchema
        
        # Store tool configuration as class attributes
        _url: str = tool_data['url']
        _method: str = tool_data['http_method']
        _headers: Dict[str, str] = tool_data.get('headers', {})
        _static_query_params: Dict[str, Any] = {}
        _static_body_params: Dict[str, Any] = {}
        _timeout: int = tool_data.get('timeout_seconds', 30)
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            # Extract static values from param configs
            query_params = tool_data.get('query_params', {})
            for param_name, param_config in query_params.items():
                if 'static_value' in param_config:
                    self._static_query_params[param_name] = param_config['static_value']
            
            body_params = tool_data.get('body_params', {})
            for param_name, param_config in body_params.items():
                if 'static_value' in param_config:
                    self._static_body_params[param_name] = param_config['static_value']
        
        def _run(self, **kwargs) -> str:
            """
            Execute the API call with provided arguments.
            """
            try:
                # Prepare query parameters
                query_params = self._static_query_params.copy()
                
                # Add dynamic query params from kwargs
                tool_query_params = tool_data.get('query_params', {})
                for param_name in tool_query_params.keys():
                    if param_name in kwargs and kwargs[param_name] is not None:
                        query_params[param_name] = kwargs[param_name]
                
                # Prepare body parameters
                body_data = self._static_body_params.copy()
                
                # Add dynamic body params from kwargs
                tool_body_params = tool_data.get('body_params', {})
                for param_name in tool_body_params.keys():
                    if param_name in kwargs and kwargs[param_name] is not None:
                        body_data[param_name] = kwargs[param_name]
                
                # Prepare headers
                headers = self._headers.copy()
                if body_data and self._method == 'POST':
                    headers['Content-Type'] = headers.get('Content-Type', 'application/json')
                
                # Make the API request
                if self._method == 'GET':
                    response = requests.get(
                        self._url,
                        params=query_params,
                        headers=headers,
                        timeout=self._timeout
                    )
                elif self._method == 'POST':
                    response = requests.post(
                        self._url,
                        params=query_params,
                        json=body_data if body_data else None,
                        headers=headers,
                        timeout=self._timeout
                    )
                else:
                    return f"Error: Unsupported HTTP method {self._method}"
                
                # Check response status
                response.raise_for_status()
                
                # Try to parse JSON response
                try:
                    result = response.json()
                    return json.dumps(result, indent=2)
                except json.JSONDecodeError:
                    return response.text
                
            except requests.exceptions.Timeout:
                return f"Error: Request timed out after {self._timeout} seconds"
            except requests.exceptions.RequestException as e:
                return f"Error making API request: {str(e)}"
            except Exception as e:
                return f"Unexpected error: {str(e)}"
    
    # Return an instance of the dynamic tool
    return DynamicAPITool()


def build_tools_for_agent(tools_data: list) -> list:
    """
    Build a list of CrewAI tools from database tool configurations.
    
    Args:
        tools_data: List of tool configuration dictionaries from database
        
    Returns:
        List of BaseTool instances ready to be used by CrewAI agents
    """
    tools = []
    
    for tool_data in tools_data:
        try:
            tool = create_api_tool(tool_data)
            tools.append(tool)
            print(f"Successfully created tool: {tool_data['tool_name']}")
        except Exception as e:
            print(f"Error creating tool {tool_data.get('tool_name', 'unknown')}: {str(e)}")
            # Continue with other tools even if one fails
            continue
    
    return tools