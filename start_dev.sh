#!/bin/bash

# MCP Proof of Concept - Development Startup Script

echo "🚀 Starting MCP Proof of Concept Development Environment"
echo "======================================================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please create one with your OpenAI API key."
    echo "   Example: cp env.example .env"
    echo "   Then edit .env and add your OpenAI API key."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command_exists uv; then
    echo "❌ uv not found. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command_exists npm; then
    echo "❌ npm not found. Please install Node.js first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
uv pip install -e . || {
    echo "❌ Failed to install Python dependencies"
    exit 1
}

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install || {
    echo "❌ Failed to install frontend dependencies"
    exit 1
}
cd ..

echo "✅ Dependencies installed successfully"

# Start services
echo "🔧 Starting services..."

# Kill any existing processes on the ports we need
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:8001 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

# Start MCP server in background
echo "🛠️  Starting MCP Server (port 8001)..."
cd mcp_server
python multi_tool_mcp_server.py &
MCP_PID=$!
cd ..

# Wait a moment for MCP server to start
sleep 2

# Start backend server in background
echo "🚀 Starting Backend Server (port 8000)..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend (this will block and show output)
echo "🎨 Starting Frontend Server (port 3000)..."
echo "📱 Frontend will open in your browser automatically"
echo ""
echo "🎯 Services running:"
echo "   - MCP Server:    http://127.0.0.1:8001"
echo "   - Backend API:   http://127.0.0.1:8000"
echo "   - Frontend:      http://127.0.0.1:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo "======================================="

cd frontend

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $MCP_PID 2>/dev/null || true
    kill $BACKEND_PID 2>/dev/null || true
    # Kill any remaining processes on our ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Set up cleanup trap
trap cleanup INT TERM

# Start frontend (blocking)
npm start

# If we get here, npm start exited, so cleanup
cleanup 