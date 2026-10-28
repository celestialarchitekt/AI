
"""
Langchain - ContextEngg Store: RAM Storage
"""

from textwrap import wrap
from typing import TypedDict, Annotated, Callable
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langgraph.graph.message import add_messages
from langgraph.store.memory import InMemoryStore

# load api keys
load_dotenv(override=True)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]



@wrap_model_call
def store_memory_middleware(
    request: ModelRequest,
    handler : Callable[[ModelRequest], ModelResponse]
)->ModelResponse:
    runtime = getattr(request, "runtime", None)
    store = getattr(runtime, "store", None) if runtime else None

    config = getattr(request, "config", {})
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")

    if store and user_id:
        memory = store.get(namespace=("users", user_id), key="preferences")

        if memory and memory.value:
            prefs = memory.value

            context_str = (
                f"[Persistent User Profile]\n"
                f"-Name: {prefs.get('name')}\n"
                f"-Coding Preferences: {prefs.get('pref')}\n"
            )

            existing_messages = list(request.messages)
            if existing_messages:
                last_msg = existing_messages.pop()
                messages = [
                    *existing_messages, #unpack messages using *
                    {"role": "user", "content": "context_str"}, # context
                    last_msg # users question
                ]

                request = request.override(messages=messages)

    return handler(request)

# create instance of store
store = InMemoryStore()

store.put(
    namespace = ("users", "usr_001"),
    key="preferences",
    value={
        "name": "Marcus",
        "pref": "write clean, async python code with concise explanations"
    }
)

# create the agent
agent = create_agent(
    model = "gpt-4o-mini",
    middleware = [store_memory_middleware],
    state_schema = AgentState,
    store = store
)

# execute
if __name__ == "__main__":
    user_config = {
        "configurable": {
            "user_id": "usr_001"
        }
    }

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "give a python code to add 2 numbers and explain it"}]},
        config=user_config
    )

    print("----- LLM Response -----")
    print(response["messages"][-1].content)