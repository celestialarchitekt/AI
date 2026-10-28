"""
==============================
LangGraph - using persistence
=============================
"""

import os
from dotenv import load_dotenv


load_dotenv(override=True)

#imports
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

# instances
checkpointer = InMemorySaver() # thread scoped memory, short term, conversation continuity, time travel
store = InMemoryStore() # cross thread memory, long term

# llm
llm = ChatOpenAI(model="gpt-4o-mini")

# function
def assistant_node(state:MessagesState, config):

    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id", "default_user")

    namespace = ("users", user_id)
    stored_item = store.get(namespace, "preferences")

    if not stored_item:
        store.put(namespace, "preferences", {"fav_topic": "ai and coding"}) #write
        stored_item = store.get(namespace, "preferences") # fetch

    # create the system prompt
    system_prompt = f"user long term preferences: {stored_item.value}"

    # create the message
    messages = [{"role": "system", "content": system_prompt}] + state["messages"] # holds chat history

    # invoke the llm
    result = llm.invoke(messages)
    return {"messages": [result]}




# create the graph
graph = StateGraph(MessagesState)
graph.add_node("assistant",assistant_node) # "assitant" here is a label for the graph, second one is a function
graph.add_edge(START, "assistant")
graph.add_edge("assistant", END)

# compile the graph with checkpointer and store
graph = graph.compile(checkpointer=checkpointer, store=store)


# thread
config= {
    "configurable": {
        "thread_id": "thread_001", # for short term
        "user_id" : "user_001" # used with store for long term memory
    }
}

# run the llm
result_1 = graph.invoke({"messages": [{"role": "user", "content": "hi, my name is alice"}]}, config)
print(" ----- RUN 1 ------")
print(result_1["messages"][-1].content)


result_2 = graph.invoke({"messages": [{"role": "user", "content": "what is my name?"}]}, config)

print("-------- RESULT -----------")
print(result_2["messages"][-1].content)


