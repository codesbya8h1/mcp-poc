#!/usr/bin/env python3
"""
FastAPI Backend Server for MCP Proof of Concept
"""

import asyncio
import json
import os
from typing import Dict, Any, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

from llama_index.tools.mcp import McpToolSpec
from mcp_agents.handler_agent import create_mcp_agent_handler, MCPAgentHandler

# Load environment variables
load_dotenv()

# Global variables
mcp_client = None
agent_handler = None
mcp_tools = None

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    tools_used: List[str] = []

async def initialize_mcp_client():
    """Initialize MCP client connection"""
    global mcp_client, mcp_tools
    
    try:
        # Create MCP tool spec connecting to local server
        mcp_tools = McpToolSpec(
            server_url="http://127.0.0.1:8001",  # MCP server URL
            timeout=30.0
        )
        
        print("✅ MCP client initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize MCP client: {e}")
        return False

async def initialize_agent_handler():
    """Initialize the agent handler"""
    global agent_handler
    
    try:
        agent_handler = create_mcp_agent_handler()
        print("✅ Agent handler initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize agent handler: {e}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    print("🚀 Starting MCP Backend Server...")
    
    # Initialize components
    mcp_success = await initialize_mcp_client()
    agent_success = await initialize_agent_handler()
    
    if not mcp_success or not agent_success:
        print("⚠️  Some components failed to initialize, but server will continue")
    
    yield
    
    print("🛑 Shutting down MCP Backend Server...")

# Create FastAPI app
app = FastAPI(
    title="MCP Proof of Concept Backend",
    description="Backend server for Model Context Protocol demonstration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MCP Proof of Concept Backend",
        "status": "running",
        "mcp_connected": mcp_client is not None,
        "agent_ready": agent_handler is not None
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "mcp_client": mcp_client is not None,
            "agent_handler": agent_handler is not None,
            "tools": mcp_tools is not None
        }
    }

@app.get("/tools")
async def get_available_tools():
    """Get list of available MCP tools"""
    global mcp_tools, agent_handler
    
    if not mcp_tools or not agent_handler:
        raise HTTPException(status_code=503, detail="MCP client or agent handler not initialized")
    
    try:
        tools_info = agent_handler.get_available_tools_info([mcp_tools])
        return {
            "tools": tools_info,
            "count": len(tools_info)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tools: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Main chat endpoint for processing user queries"""
    global mcp_tools, agent_handler
    
    if not mcp_tools or not agent_handler:
        raise HTTPException(status_code=503, detail="MCP client or agent handler not initialized")
    
    try:
        # Process the query using the agent
        response = await agent_handler.process_query(
            query=request.message,
            tools=[mcp_tools]
        )
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            tools_used=[]  # TODO: Track which tools were used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Streaming chat endpoint for real-time responses"""
    global mcp_tools, agent_handler
    
    if not mcp_tools or not agent_handler:
        raise HTTPException(status_code=503, detail="MCP client or agent handler not initialized")
    
    async def generate_response():
        try:
            # For now, we'll simulate streaming by yielding the full response
            # In a real implementation, you'd integrate with streaming LLM APIs
            response = await agent_handler.process_query(
                query=request.message,
                tools=[mcp_tools]
            )
            
            # Simulate streaming by yielding chunks
            words = response.split()
            for i, word in enumerate(words):
                chunk = {
                    "response": word + " ",
                    "session_id": request.session_id,
                    "is_final": i == len(words) - 1
                }
                yield f"data: {json.dumps(chunk)}\n\n"
                await asyncio.sleep(0.05)  # Small delay for streaming effect
                
        except Exception as e:
            error_chunk = {
                "error": str(e),
                "session_id": request.session_id,
                "is_final": True
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

@app.post("/tools/test/{tool_name}")
async def test_tool(tool_name: str, parameters: Dict[str, Any] = None):
    """Test a specific MCP tool"""
    global mcp_tools, agent_handler
    
    if not mcp_tools or not agent_handler:
        raise HTTPException(status_code=503, detail="MCP client or agent handler not initialized")
    
    try:
        # Create a test query for the tool
        if parameters:
            param_str = ", ".join([f"{k}={v}" for k, v in parameters.items()])
            test_query = f"Use the {tool_name} tool with parameters: {param_str}"
        else:
            test_query = f"Use the {tool_name} tool"
        
        response = await agent_handler.process_query(
            query=test_query,
            tools=[mcp_tools]
        )
        
        return {
            "tool_name": tool_name,
            "parameters": parameters,
            "response": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing tool: {str(e)}")

# Add startup message
@app.on_event("startup")
async def startup_event():
    print("🎯 MCP Backend Server is ready!")
    print("📡 Endpoints available:")
    print("   - GET  /         : Server status")
    print("   - GET  /health   : Health check")
    print("   - GET  /tools    : Available tools")
    print("   - POST /chat     : Chat endpoint")
    print("   - POST /chat/stream : Streaming chat")

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting MCP Backend Server...")
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 