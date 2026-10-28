"""
===============================
LangGraph - a simple hello world program using langGraph
Note: no LLM is called here!
=============================
"""


from langgraph.graph import StateGraph, MessagesState, START, END

# hard coded response
def mock_llm(state: MessagesState):
    return {"messages": [{"role": "ai", "content": "hello world"}]}

# create the nodes and edges and the Graph
graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, "mock_llm")
graph.add_edge("mock_llm", END)
graph = graph.compile()

# get the result
result = graph.invoke({"messages": [{"role":"user", "content": "hi!"}]})
print("-> final output ", result)