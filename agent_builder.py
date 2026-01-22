from crewai import Agent, LLM

def build_agent(agent_data, config_data):
    print(f"Building agent: {agent_data['display_name']}")
    
    llm_model = config_data.get('llm', 'groq/llama-3.1-8b-instant')
    
    llm = LLM(
        model=llm_model,
        temperature=0.7
    )
    
    function_calling_llm = None
    if config_data.get('function_calling_llm'):
        function_calling_llm = LLM(
            model=config_data['function_calling_llm'],
            temperature=0.7
        )
    
    agent = Agent(
        role=agent_data.get('role', 'AI Assistant'),
        goal=agent_data.get('goal', 'Assist the user'),
        backstory=agent_data.get('backstory', 'An experienced AI assistant'),
        llm=llm,
        function_calling_llm=function_calling_llm,
        verbose=config_data.get('verbose', False),
        allow_delegation=config_data.get('allow_delegation', False),
        max_iter=config_data.get('max_iter', 20),
        max_rpm=config_data.get('max_rpm'),
        max_execution_time=config_data.get('max_execution_time'),
        max_retry_limit=config_data.get('max_retry_limit', 2),
        allow_code_execution=config_data.get('allow_code_execution', False),
        code_execution_mode=config_data.get('code_execution_mode', 'safe'),
        respect_context_window=config_data.get('respect_context_window', True),
        use_system_prompt=config_data.get('use_system_prompt', True),
        multimodal=config_data.get('multimodal', False),
        inject_date=config_data.get('inject_date', False),
        date_format=config_data.get('date_format', '%Y-%m-%d'),
        reasoning=config_data.get('reasoning', False),
        max_reasoning_attempts=config_data.get('max_reasoning_attempts'),
        tools=[],
        knowledge_sources=config_data.get('knowledge_sources'),
        embedder=config_data.get('embedder'),
        system_template=config_data.get('system_template'),
        prompt_template=config_data.get('prompt_template'),
        response_template=config_data.get('response_template'),
        step_callback=None
    )
    
    print(f"Agent built successfully: {agent_data['username']}")
    return agent