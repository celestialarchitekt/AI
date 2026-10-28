"""
LangChain - shortTerm memory
"""

from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv

load_dotenv(override=True)

@tool
def get_user_info()->str:
    """get user details"""
    return "no user profile on file"


agent = create_agent(
    model = "gpt-4o-mini",
    tools=[get_user_info],
    

    #checkpointer enables state persistence in memory in the langgraph
    #checkpointer saves a snapshot of current state into memory
    
    checkpointer=InMemorySaver()
)



thread_config = {"configurable": {"thread_id": "1"}}         
if __name__ == "__main__":
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "My name is X"}]},
        thread_config,
    )
    
    print(response["messages"][-1].content)
    
    response = agent.invoke(
        {"messages": [{"role":"user", "content": "what is my name?"}]},
        thread_config
    )
    
    print(response["messages"][-1].content)