"""
=========================
LangGraph - checkpointers : used to store short term memory, uses threads to store snaphshots of the graph.
1. human in loop
2. memory for conversations
3. fault tolerance
4. time travel
==========================
"""

# --------- Imports --------------------------------
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from typing import Annotated, TypedDict 
from operator import add

# 1. User defined state class
class State(TypedDict):
    foo: str
    bar: Annotated[list[str], add]

# 2. User defined node functions
def node_a(state: State):
    print(f"Running node_a with state: {state}")
    return {"foo": "hello from a", "bar": ["item_a"]}

def node_b(state: State):
    print(f"Running node_b with state: {state}")
    return {"foo": "hello from b", "bar": ["item_b"]}

# 3. Create the graph workflow
workflow = StateGraph(State)

# Add nodes (using function names as keys)
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)

# Define edges
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a", "node_b")
workflow.add_edge("node_b", END)

# 4. Create the in-memory checkpointer for short-term memory / threads
checkpointer = InMemorySaver()

# 5. Compile the graph with the checkpointer attached
graph = workflow.compile(checkpointer=checkpointer)

# 6. Configure a thread identifier
config: RunnableConfig = {"configurable": {"thread_id": "thread_1"}}

# 7. Run the graph
result = graph.invoke({"foo": "initial", "bar": []}, config)

print("\n--- Final Graph Result ---")
print(result)


print("\n--- Debugging Checkpointer ---")

for state in graph.get_state_history(config): 
    print(f"Checkpointer ID: {state.config['configurable']['checkpoint_id']}")
    print(f"Super-step (Step): {state.metadata.get('step')}")
    print(f"Next Node to run : {state.next}")
    print(f"State Values: {state.values}")
