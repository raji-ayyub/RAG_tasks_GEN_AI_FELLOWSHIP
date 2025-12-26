# Note: for quicker testing and overview, use task_basic_mode.py
# but full project uses agent.py and customer_support.py


# TechGadgets Customer Support - LangGraph AI Agent

A modern, production-ready customer support chatbot built with LangGraph, FastAPI, and a responsive frontend interface. This application demonstrates state management, conversation memory, and agentic workflows using LangGraph.

## Features

### Backend (FastAPI + LangGraph)
- Stateful conversation management with LangGraph
- Context-aware memory across sessions
- RESTful API with CORS support
- Session management with unique thread IDs
- OpenAI GPT-3.5 integration
- Error handling and validation
- Health monitoring endpoints

### Frontend (HTML/CSS/JS)
- Modern, responsive chat interface
- Real-time messaging with typing indicators
- Session management UI
- Quick action buttons for common queries
- Markdown support for AI responses
- Chat export functionality
- Mobile-responsive design
- Notification system

## Quick Start

### Prerequisites
- Python 3.8+, recommendably python 3.11
- OpenAI API key


### Step 1: Clone/Download the Project

### Step 2: Set Up Backend

#### 2.1 project structure:
```
techgadgets-support/
├── agent.py
├── customer_support.py
├── .env
├── requirements.txt
└── ui/
    ├── index.html
    ├── style.css
    └── script.js
```

#### 2.2 Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

#### 2.3 Create `requirements.txt`:
```txt
fastapi
uvicorn
pydantic
dotenv
langgraph
langchain-openai
langchain-core
```

#### 2.4 Install Python dependencies:
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Run the Backend Server
```bash
# Run the FastAPI server
python customer_support.py
```

You should see output like:
```
Starting TechGadgets Customer Support API...
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/health
Frontend should connect to: http://localhost:8000

Press Ctrl+C to stop the server

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 4: Serve the Frontend

#### Option A: Using Python (Simplest)
```bash
# Open a new terminal
cd frontend
python -m http.server 3000
```

### Step 5: Access the Application

1. **API Documentation**: http://localhost:8000/docs
2. **Frontend Interface**: http://localhost:3000
3. **Health Check**: http://localhost:8000/health

## 📖 Usage Guide

### Starting a New Session
1. Open http://localhost:3000 in your browser
2. Enter customer information (name, email, issue type)
3. Click "Start Session"
4. Begin chatting with the AI support agent

### Using Quick Actions
- Click on quick action buttons (Power Issues, Return Request, etc.)
- These buttons automatically populate common queries

### Managing Sessions
- **New Session**: Start fresh conversation
- **Export Chat**: Download conversation as text file
- **Clear Chat**: Remove messages from view

## 🛠️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API root information |
| GET | `/health` | Health check endpoint |
| POST | `/api/sessions/create` | Create new chat session |
| POST | `/api/chat` | Send message to agent |
| GET | `/api/sessions` | List all active sessions |
| GET | `/api/sessions/{id}` | Get session details |
| DELETE | `/api/sessions/{id}` | Delete session |
