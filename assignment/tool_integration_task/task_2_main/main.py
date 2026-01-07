# main.py

from agent import create_support_agent
from langchain_core.messages import HumanMessage
import uuid

def main():
    print("TechGadgets Support Agent")
    print("Type 'exit' to quit\n")

    agent = create_support_agent()

    # unique session ID for memory
    session_id = str(uuid.uuid4())

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye 👋")
            break

        # invoke graph
        result = agent.invoke(
            {
                "messages": [HumanMessage(content=user_input)]
            },
            config={
                "configurable": {
                    "thread_id": session_id
                }
            }
        )

        # last message is the assistant response
        assistant_message = result["messages"][-1]
        print(f"\nAgent: {assistant_message.content}\n")


if __name__ == "__main__":
    main()
