"""
===========================
LangChain - RunTime & Store
=============================
"""

from dotenv import load_dotenv
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore


# load ENV VARs
load_dotenv(override=True)


@dataclass
class Context:
    user_id : str
    
    

@tool
def save_user_performance(preference_key:str, value:str, runtime: ToolRuntime[Context])->str:
    """save a user preference to long term memory"""
    
    user_id = runtime.context.user_id
    
    #store memory under a namespace
    runtime.store.put(
        namespace = ("users", user_id),
        key = preference_key,
        value = {"settings": value}
    )
    
    return f"saved preferences {preference_key} = {value} for user {user_id}"


@tool
def get_user_preference(preference_key:str, runtime: ToolRuntime[Context])->str:
    """retrieve the users preference saved in long term memory"""
    
    user_id = runtime.context.user_id
    
    #fetch from the same namespace
    
    data = runtime.store.get(
        namespace = ("users", user_id),
        key = preference_key
    )
    
    if data :
        return f"Retrieved data is {data}"
    
    return f"No preference found for {preference_key}"


# init the memory
shared_store = InMemoryStore()


# create agent
agent = create_agent(
    model = "gpt-5.4-mini",
    tools = [save_user_performance, get_user_preference],
    context_schema = Context,
    store = shared_store # memory
)

# run the code
if __name__ == "__main__":
    print("------- session1 -------")
    agent.invoke({
        "messages" : [{"role": "user", "content": "my fav food is pizza"}]},
        context = Context(user_id = "123")
    )
    
    print("----- session2 -----------")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "what is my fav food"}]},
        context = Context(user_id = "123")
    )
    
    print("------ RESULT ------")
    print(response["messages"][-1].content)


# ---------------------------------------------------------------------------
"""


"""