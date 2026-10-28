"""
=============================================
LangChain - guardrails as middleware and hil 
=============================================
"""



from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv(override=True)

# 1. Define the actual tool that matches your middleware key
@tool
def send_email(recipient: str, body: str) -> str:
    """Sends an email to a specified recipient."""
    return f"Email successfully sent to {recipient}!"

# 2. Attach tools to the agent
agent = create_agent(
    model="gpt-4o-mini",
    tools=[send_email],  # <--- Bind the tool here
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                'send_email': True,
                'delete_database': True,
                'search': False,
            }
        )
    ],
    checkpointer=InMemorySaver(),
)


# creates a thread
config = {"configurable": {"thread_id": "001"}}


# runs the code
if __name__ == "__main__":
    # Response 1: Will trigger an interrupt asking for human approval
    response1 = agent.invoke(
        {"messages": [{"role": "user", "content": "send email to team@example.com saying Hi"}]},
        config=config
    )
    
    print("---- RESPONSE 1 (Interrupted State) -------")
    print(response1["messages"][-1].content_blocks)

    answer = input("Do you approve [Y/n]:").strip().lower()

    if answer == "y":
        flag = [{"type": "approve"}]

    if answer == "n":
        flag = [{"type": "reject"}]

    # Response 2: Resumes execution and calls send_email
    response2 = agent.invoke(
        Command(resume={"decisions": flag}),
        config=config
    )

    print("\n------ RESPONSE 2 (After Approval) --------")
    print(response2["messages"][-1].content_blocks)