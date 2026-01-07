from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import ToolMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

from tools import calculator, search, lookup_dictionary, get_weather

load_dotenv()


llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

tools = [calculator, search, lookup_dictionary, get_weather]
llm = llm.bind_tools(tools)


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

    You can use tools when helpful:
    - Use the calculator tool for any math or numeric reasoning
    - Use the search tool for company policies, warranty, returns, or shipping
    - Use dictionary or weather tools when relevant
    Always prefer tools over guessing.
    
    **FORMAT**:
    - Keep responses clear and concise
    - Use bullet points for instructions
    - Ask one question at a time
    - End with a helpful question to continue the conversation
    """
)


def support_agent(state: MessagesState) -> dict:
    """
    LLM reasoning step.
    Runs BOTH before and after tool execution.
    """
    messages = [support_prompt] + state["messages"]
    response = llm.invoke(messages)

    return {"messages": [response]}


def tool_executor(state: MessagesState) -> dict:
    """
    Executes tool calls decided by the LLM.
    """
    last_message = state["messages"][-1]

    if not last_message.tool_calls:
        return {}

    tool_messages = []

    for call in last_message.tool_calls:
        tool_name = call["name"]
        tool_args = call["args"]

        tool_fn = {
            "calculator": calculator,
            "search": search,
            "lookup_dictionary": lookup_dictionary,
            "get_weather": get_weather,
        }.get(tool_name)

        if not tool_fn:
            continue

        result = tool_fn.invoke(tool_args)

        tool_messages.append(
            ToolMessage(
                tool_call_id=call["id"],
                content=str(result)
            )
        )

    return {"messages": tool_messages}


def should_use_tools(state: MessagesState) -> str:
    """
    Conditional routing:
    - If LLM requested tools → tools node
    - Otherwise → END
    """
    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "end"


def create_support_agent():
    """
    Builds and compiles the LangGraph agent.
    """

    builder = StateGraph(MessagesState)

    builder.add_node("support_agent", support_agent)
    builder.add_node("tools", tool_executor)

    builder.add_edge(START, "support_agent")

    builder.add_conditional_edges(
        "support_agent",
        should_use_tools,
        {
            "tools": "tools",
            "end": END
        }
    )

    # Critical loop: tools → agent (reason again)
    builder.add_edge("tools", "support_agent")

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)
