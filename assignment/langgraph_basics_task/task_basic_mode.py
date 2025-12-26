from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

support_prompt = SystemMessage(
    content="""You are a helpful customer support agent for TechGadgets Inc.
    - Be empathetic and patient
    - Ask clarifying questions when needed
    - Remember customer issues across conversation
    - Only provide information you're certain about
"""
)

def support_agent(state: MessagesState) -> dict:
    """processes customer message with context memory"""

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

support_bot = create_support_agent()





# CLI conversation test
while True:
    query = input("Customer: ")
    thread_id="customer_223"

    response = support_bot.invoke(
        {"messages": [HumanMessage(content=query)]},
        config={"configurable": {"thread_id": thread_id}}
    )
    print(f"assistant: {response['messages'][-1].content}\\n")






# Multi-turn conversation test
# conversations = [
#     "I bought a laptop last week",
#     "It won't turn on",
#     "Yes, I tried that already",
#     "Can I get a replacement?"
# ]

# thread_id = "customer_123"
# for message in conversations:
#     result = support_bot.invoke(
#         {"messages": [HumanMessage(content=message)]},
#         config={"configurable": {"thread_id": thread_id}}
#     )
#     print(f"👤 Customer: {message}")
#     print(f"🤖 Support: {result['messages'][-1].content}\\n")