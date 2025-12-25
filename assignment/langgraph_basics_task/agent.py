from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List



load_dotenv()


llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)



support_prompt = SystemMessage(
    content="""You are a helpful customer support agent for TechGadgets Inc.
    
    **COMPANY INFORMATION**:
    - TechGadgets Inc. sells laptops, smartphones, tablets, and accessories
    - Warranty: 1 year standard, 2 years extended available
    - Return policy: 30-day money-back guarantee
    - Shipping: Free shipping on orders over $99
    
    **YOUR ROLE**:
    1. Be empathetic and patient with customers
    2. Ask clarifying questions to understand the issue
    3. Remember the entire conversation history
    4. Provide step-by-step troubleshooting
    5. Suggest warranty or return options when appropriate
    6. Never make promises you can't keep
    7. Escalate to human agent if needed
    
    **FORMAT**:
    - Keep responses clear and concise
    - Use bullet points for instructions
    - Ask one question at a time
    - End with a helpful question to continue the conversation
    """
)






def support_agent(state: MessagesState) -> dict:
    """Processes customer message with context memory"""
    messages = [support_prompt] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [AIMessage(content=response.content)]}


def create_support_agent():
    builder = StateGraph(MessagesState)
    builder.add_node("support_agent", support_agent)
    builder.add_edge(START, "support_agent")
    builder.add_edge("support_agent", END)
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)






# Pydantic models for API
class ChatInput(BaseModel):
    message: str
    session_id: str = None

class Message(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatResponse(BaseModel):
    response: str
    session_id: str
    messages: List[Message]