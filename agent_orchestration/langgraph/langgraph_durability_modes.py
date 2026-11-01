"""
=======================================
LangGraph : durability modes - exit, async, sync : Performance VS DataSafety

exit -  checkpoints are written only when the graph completely exits; human in loop, or error or success, or interupt

sync - checkpointers are written before the next execution step starts (after every super step); max safety, but leads to frequent writes to the database

async - checkpointers are written in background, when the next step is already executing.

DATA SAFETY : sync method
PERFORMANCE : async method or exit

NOTE: compile the graph using a checkpointer
====================================
"""


import os
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

api_key = os.environ.get("LANGSMITH_API_KEY", "")
print("Loaded LangSmith API Key starts with:", api_key[:10] if api_key else "NOT FOUND!")

# imports
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict


# create instance of LLM
llm = ChatOpenAI(model="gpt-4o")


# define the function
def real_llm_node(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}


#create the graph
graph = StateGraph(MessagesState)
graph.add_node("llm", real_llm_node)
graph.add_edge(START, "llm")
graph.add_edge("llm", END)



# checkpointer
checkpointer = MemorySaver()

# compile with checkpointer
graph = graph.compile(checkpointer = checkpointer)

# define a thread for memory
config = {"configurable": {"thread_id": "thread-1"}}

# invoke using a durability method
result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hi, trace this!"}]},
    config,
    durability= "async")


# result 
print("----------- RESULT 1 Async -----------")
print(result["messages"][-1].content)



# invoke using a durability method
result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hi, trace this!"}]},
    config,
    durability= "sync")


# result 
print("----------- RESULT 2 Sync -----------")
print(result["messages"][-1].content)


# invoke using a durability method
result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hi, trace this!"}]},
    config,
    durability= "exit")


# result 
print("----------- RESULT 3 Exit -----------")
print(result["messages"][-1].content)