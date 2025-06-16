# MCP Proof of Concept

This is a proof of concept project for MCP (Model Context Protocol) featuring a React TypeScript frontend, FastAPI backend, and multiple utility tools.

## Project Structure

```
mcp-poc/
├── frontend/          # React TypeScript frontend
├── backend/           # FastAPI backend server
├── mcp_agents/        # LLM agent handlers
├── mcp_server/        # MCP server with tools
├── pyproject.toml     # Python dependencies
└── README.md
```

## Features

### Frontend
- Modern React TypeScript chat interface
- Responsive design with Tailwind CSS
- Real-time chat with the MCP-powered AI assistant
- Connection status indicator
- Example queries for easy testing

### Backend
- FastAPI server with async support
- CORS enabled for frontend communication
- Health check and tool discovery endpoints
- Streaming chat support (planned)

### MCP Tools
- **BMI Calculator**: Calculate Body Mass Index
- **Weather Info**: Get weather information for cities
- **Random Quotes**: Inspirational quote generator
- **Compound Interest**: Financial calculations
- **Password Generator**: Secure password creation
- **Temperature Converter**: Convert between C/F/K
- **Tip Calculator**: Bill splitting and tip calculation

## Prerequisites

- Python 3.9+ with uv package manager
- Node.js 18+ and npm
- OpenAI API key

## Setup Instructions

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
cp env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Backend Setup

Install Python dependencies using uv:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .
```

### 3. Frontend Setup

Install Node.js dependencies:

```bash
cd frontend
npm install
cd ..
```

## Running the Application

### Option 1: Manual Start (Recommended for Development)

1. **Start the MCP Server** (Terminal 1):
```bash
cd mcp_server
python multi_tool_mcp_server.py
```

2. **Start the Backend Server** (Terminal 2):
```bash
cd backend
python main.py
```

3. **Start the Frontend** (Terminal 3):
```bash
cd frontend
npm start
```

### Option 2: Using Background Processes

```bash
# Start MCP server in background
cd mcp_server && python multi_tool_mcp_server.py &

# Start backend in background
cd backend && python main.py &

# Start frontend
cd frontend && npm start
```

## API Endpoints

### Backend Server (Port 8000)

- `GET /` - Server status
- `GET /health` - Health check
- `GET /tools` - Available tools
- `POST /chat` - Send chat message
- `POST /chat/stream` - Streaming chat (planned)
- `POST /tools/test/{tool_name}` - Test specific tool

### MCP Server (Port 8001)

- Provides tool definitions and execution
- Communicates with backend via MCP protocol

## Frontend (Port 3000)

- Modern chat interface
- Real-time communication with backend
- Tool status indicators

## Usage Examples

Once all services are running, you can try these example queries in the chat interface:

1. **BMI Calculation**: "Calculate BMI for 70kg and 1.75m height"
2. **Weather**: "What's the weather in Tokyo?"
3. **Random Quote**: "Give me a random quote"
4. **Finance**: "Calculate compound interest for $1000 at 5% for 10 years"
5. **Utilities**: "Generate a strong password"
6. **Conversion**: "Convert 100°F to Celsius"

## Development

### Code Structure

- **Frontend**: React TypeScript with Tailwind CSS
- **Backend**: FastAPI with async/await patterns
- **MCP Agents**: LlamaIndex integration with OpenAI
- **MCP Server**: FastMCP with multiple tool decorators

### Adding New Tools

1. Add a new function in `mcp_server/multi_tool_mcp_server.py`
2. Use the `@mcp.tool()` decorator
3. The tool will automatically be available to the agent

### Debugging

- Check console logs in browser developer tools
- Backend logs appear in the terminal
- Use `/health` endpoint to verify component status

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure all services are running on correct ports
2. **OpenAI API Issues**: Verify your API key in `.env`
3. **Frontend Build Issues**: Run `npm install` in frontend directory
4. **Python Import Errors**: Run `uv pip install -e .` from root directory

### Port Configuration

- Frontend: 3000
- Backend: 8000
- MCP Server: 8001

Make sure these ports are available.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This is a proof of concept project for educational purposes. 