from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import uvicorn

from langchain_core.messages import HumanMessage
import os

from agent import create_support_agent, ChatInput, ChatResponse

app = FastAPI(
    title="TechGadgets Customer Support API",
    description="AI-powered customer support agent for TechGadgets Inc.",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage
sessions = {}

class SessionCreate(BaseModel):
    customer_name: Optional[str] = "Guest"
    email: Optional[str] = None
    issue_type: Optional[str] = "general"

class SessionInfo(BaseModel):
    session_id: str
    customer_name: str
    created_at: str
    message_count: int
    last_activity: str

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    messages: List[Message]

@app.get("/")
async def root():
    return {
        "message": "TechGadgets Customer Support API",
        "version": "1.0.0",
        "endpoints": {
            "create_session": "/api/sessions/create",
            "get_session": "/api/sessions/{session_id}",
            "chat": "/api/chat",
            "list_sessions": "/api/sessions"
        }
    }

@app.post("/api/sessions/create", response_model=SessionInfo)
async def create_session(session_data: SessionCreate):
    """Create a new customer support session"""
    session_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    sessions[session_id] = {
        "session_id": session_id,
        "customer_name": session_data.customer_name,
        "email": session_data.email,
        "issue_type": session_data.issue_type,
        "created_at": now,
        "last_activity": now,
        "messages": [],
        "agent": create_support_agent()  
    }
    
    return SessionInfo(
        session_id=session_id,
        customer_name=session_data.customer_name,
        created_at=now,
        message_count=0,
        last_activity=now
    )

@app.get("/api/sessions", response_model=List[SessionInfo])
async def list_sessions():
    """List all active sessions"""
    session_list = []
    for session_id, session_data in sessions.items():
        session_list.append(SessionInfo(
            session_id=session_id,
            customer_name=session_data["customer_name"],
            created_at=session_data["created_at"],
            message_count=len(session_data["messages"]),
            last_activity=session_data["last_activity"]
        ))
    return session_list

@app.get("/api/sessions/{session_id}", response_model=Dict)
async def get_session(session_id: str):
    """Get session details and conversation history"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_info": SessionInfo(
            session_id=session_id,
            customer_name=session["customer_name"],
            created_at=session["created_at"],
            message_count=len(session["messages"]),
            last_activity=session["last_activity"]
        ),
        "messages": session["messages"]
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest):
    """Send a message to the customer support agent"""
    
    # If no session_id provided, create a new session
    if not chat_request.session_id:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "session_id": session_id,
            "customer_name": "Guest",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "messages": [],
            "agent": create_support_agent()
        }
    else:
        session_id = chat_request.session_id
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    agent = session["agent"]
    
    # Add user message to session history
    user_message = Message(
        role="user",
        content=chat_request.message,
        timestamp=datetime.now().isoformat()
    )
    session["messages"].append(user_message.dict())
    
    # Get response from LangGraph agent
    try:
        response = agent.invoke(
            {"messages": [HumanMessage(content=chat_request.message)]},
            config={"configurable": {"thread_id": session_id}}
        )
        
        assistant_response = response['messages'][-1].content
        
        # Add assistant message to session history
        assistant_message = Message(
            role="assistant",
            content=assistant_response,
            timestamp=datetime.now().isoformat()
        )
        session["messages"].append(assistant_message.dict())
        
        # Update last activity
        session["last_activity"] = datetime.now().isoformat()
        
        return ChatResponse(
            response=assistant_response,
            session_id=session_id,
            messages=session["messages"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
        return {"message": "Session deleted successfully"}
    raise HTTPException(status_code=404, detail="Session not found")

if __name__ == "__main__":
    uvicorn.run("customer_support:app", host="0.0.0.0", port=8000, reload=True)