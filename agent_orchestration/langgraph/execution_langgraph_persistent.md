--------------------------------------------------------
Control Flow : Program "langgraph_persistent.py"
---------------------------------------------------------

Turn 1 (First Message)

    You call graph.invoke({"messages": [{"role": "user", "content": "Hi, my name is Alice"}]}, config).

    Control flows to START ➔ assistant_node.

    Inside the node, state["messages"] has the new message, and assistant_node calls llm.invoke() with the system prompt + messages.

    The dictionary you pass into graph.invoke() defines the initial state. Therefore, inside assistant_node, state["messages"] will contain that initial user message: [HumanMessage(content="Hi, my name is Alice")].

    The LLM generates a response (result_1).

    The node returns {"messages": [result_1]}.

    LangGraph updates the state, and the checkpointer (MemorySaver) saves this state to thread_abc_123.

    graph.invoke() finishes and returns the final state to you.

Turn 2 (Second Message)

    You call graph.invoke({"messages": [{"role": "user", "content": "What is my name?"}]}, config) using the same thread_id.

    Before any node runs, the checkpointer steps in and restores the history from Turn 1.

    The new message ("What is my name?") is appended to that history. Now state["messages"] has both the first message, response, and the second message.

    Control flows to assistant_node again.

    Inside the node, assistant_node calls llm.invoke() with the system prompt + the full accumulated state["messages"]. Because the history was saved by the checkpointer, the LLM reads that your name is Alice!

    The LLM generates the answer (result_2).

    The node returns the new response, the checkpointer updates again, and graph.invoke() returns result_2 to you.