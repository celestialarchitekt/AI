"""
===============
LangGraph state management and time travel: getState, getStateHistory, Replay, Update
===============
"""

# ---- imports
from dotenv import load_dotenv

# ---- load the ENV VARs
load_dotenv(override=True)

# ---- imports
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig
from typing import Annotated, TypedDict
from operator import add

# ---- define State Class
class State(TypedDict):
    foo: str
    bar : Annotated[list[str],add]

# ---- define the nodes
def node_a(state:State):
    print("node a executed")
    return  {"bar":["item_a"]}


def node_b(state:State):
    print("node b executed")
    return {"bar": ["item_b"]}


# ----- build the graph
workflow = StateGraph(State)
workflow.add_node("node_a", node_a)
workflow.add_node("node_b", node_b)
workflow.add_edge(START, "node_a")
workflow.add_edge("node_a","node_b")
workflow.add_edge("node_b", END)


# ----- create the checkpointer
checkpointer = InMemorySaver()

# ---- compile the graph
graph = workflow.compile(checkpointer = checkpointer)

# --- create the config
config : RunnableConfig = {"configurable": {"thread_id":"thread_time_travel"}}


# --- FirstRun
print("----- First Run ----")
result = graph.invoke({"foo": "start", "bar": []}, config)
print("Initial Result:", result)
print("\n" +  "-"*100 +  "\n")


# getState
print("------- Running graph.get_state() -------")
latest_snapshot = graph.get_state(config)
print("Latest Value: ", latest_snapshot)
print("Next Node Queued: ", latest_snapshot.values)


# getStateHistory
print("------- Running graph.get_state_history() -------")
for state in graph.get_state_history(config):
    print("CheckpointID: ", state.config["configurable"]["checkpoint_id"])



# updateState
print(" ------ Running graph.update_state() -----")
print("State Before Update: ", graph.get_state(config).values)
graph.update_state(config, {"foo": "overwritten_foo"}) # creates a new checkpoint after the lastOne, still a linear history

print("State After Update: ", graph.get_state(config).values)
print("\n" + "-"*100 + "\n")


# timeTravel
print("----------- Time Travel ---------")
history = list(graph.get_state_history(config))
print("History: ", history)

past_config = history[0].config
print("Past Config: ", past_config)
past_cp_id = past_config["configurable"]["checkpoint_id"]
print(past_cp_id)

# Jump back to the checkpoint 'past_cp_id'
replay = graph.invoke(None, past_config)
print("---- Replay Result ----")
print(replay)


# updateState by going to a checkpoint before the lastOne, non linear graph, a fork is created
print("\n" + "-"*100 +"\n")
print("Updating Checkpoint ...")
past_checkpoint_config = history[2].config # take a checkpoint in history
new_config = graph.update_state(past_checkpoint_config, {"foo":"branching from past"}) # update and create a new checkpoint from there

result_branched = graph.invoke(None, new_config) 
print("result_branched: ", result_branched)


# ----- END OF CODE -----