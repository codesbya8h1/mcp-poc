#!/usr/bin/env python3
"""
MCP Agent Handler for managing LLM interactions and tool execution
"""

import os
from typing import List, Optional
from dotenv import load_dotenv

from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import McpToolSpec
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.tools import BaseTool

# Load environment variables
load_dotenv()

class MCPAgentHandler:
    """
    Handler class for managing MCP agents with LLM integration
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the MCP Agent Handler
        
        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.llm = self._initialize_llm()
        self.system_prompt = self._get_system_prompt()
    
    def _initialize_llm(self) -> OpenAI:
        """
        Initialize the OpenAI LLM instance
        
        Returns:
            OpenAI LLM instance
        """
        return OpenAI(
            api_key=self.api_key,
            model="gpt-4-turbo-preview",
            temperature=0.1,
            max_tokens=1000
        )
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for the agent
        
        Returns:
            System prompt string
        """
        return """You are a helpful AI assistant with access to various tools through the Model Context Protocol (MCP).

You can help users with:
- Health calculations (BMI)
- Weather information
- Financial calculations (compound interest, tip calculations)
- Utility functions (password generation, temperature conversion)
- Inspirational quotes

Always be helpful, accurate, and provide clear explanations for your responses.
When using tools, explain what you're doing and interpret the results in a user-friendly way.
If a tool returns an error, explain the issue and suggest how to fix it.

Be conversational and friendly while maintaining professionalism."""
    
    def get_agent(self, tools: List[McpToolSpec]) -> FunctionCallingAgentWorker:
        """
        Create and return a function calling agent with the provided MCP tools
        
        Args:
            tools: List of MCP tool specifications
            
        Returns:
            FunctionCallingAgentWorker instance
        """
        # Convert MCP tools to LlamaIndex tools if needed
        agent_tools = []
        for tool in tools:
            if isinstance(tool, McpToolSpec):
                # Convert McpToolSpec to BaseTool
                agent_tools.extend(tool.to_tool_list())
            elif isinstance(tool, BaseTool):
                agent_tools.append(tool)
        
        # Create the agent worker
        agent_worker = FunctionCallingAgentWorker.from_tools(
            tools=agent_tools,
            llm=self.llm,
            system_prompt=self.system_prompt,
            verbose=True
        )
        
        return agent_worker
    
    def create_agent_workflow(self, tools: List[McpToolSpec]) -> AgentWorkflow:
        """
        Create an agent workflow with the provided tools
        
        Args:
            tools: List of MCP tool specifications
            
        Returns:
            AgentWorkflow instance
        """
        agent_worker = self.get_agent(tools)
        
        # Create workflow
        workflow = AgentWorkflow(
            agent_worker=agent_worker,
            timeout=60.0,
            verbose=True
        )
        
        return workflow
    
    async def process_query(self, query: str, tools: List[McpToolSpec]) -> str:
        """
        Process a user query using the agent with provided tools
        
        Args:
            query: User query string
            tools: List of MCP tool specifications
            
        Returns:
            Agent response string
        """
        try:
            agent_worker = self.get_agent(tools)
            
            # Create agent executor
            agent = agent_worker.as_agent()
            
            # Process the query
            response = await agent.achat(query)
            
            return str(response)
            
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    def get_available_tools_info(self, tools: List[McpToolSpec]) -> List[dict]:
        """
        Get information about available tools
        
        Args:
            tools: List of MCP tool specifications
            
        Returns:
            List of tool information dictionaries
        """
        tools_info = []
        
        for tool in tools:
            if isinstance(tool, McpToolSpec):
                tool_list = tool.to_tool_list()
                for t in tool_list:
                    tools_info.append({
                        "name": t.metadata.name,
                        "description": t.metadata.description,
                        "parameters": getattr(t.metadata, 'fn_schema', None)
                    })
        
        return tools_info

# Factory function for easy agent creation
def create_mcp_agent_handler(api_key: Optional[str] = None) -> MCPAgentHandler:
    """
    Factory function to create an MCP Agent Handler
    
    Args:
        api_key: OpenAI API key (optional)
        
    Returns:
        MCPAgentHandler instance
    """
    return MCPAgentHandler(api_key=api_key)
