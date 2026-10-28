"""
=============================
Langchain - State and Store
=============================
"""


from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

load_dotenv(override=True)

# 1. Initialize Long-Term Store (Cross-Thread) & Short-Term Checkpointer (Thread-Scoped)
store = InMemoryStore()
checkpointer = InMemorySaver()


# Populate long-term store with global user profile data
store.put(
    namespace=("users", "user_123"),
    key="profile",
    value={
        "name": "Alex",
        "preferred_language": "German",
        "role": "Software Engineer"
    }
)


# 2. Define Context Engineering Middleware
@dynamic_prompt
def state_and_store_aware_prompt(request: ModelRequest) -> str:
    # --- Context Source 1: Short-Term Thread State ---
    message_count = len(request.messages)

    # --- Context Source 2: Long-Term Store ---
    # Safely extract user_id from request.runtime.config or request.config
    runtime_config = getattr(request.runtime, "config", {}) if hasattr(request, "runtime") else getattr(request, "config", {})
    configurable = runtime_config.get("configurable", {}) if isinstance(runtime_config, dict) else {}
    
    user_id = configurable.get("user_id", "default_user")
    
    user_data = store.get(namespace=("users", user_id), key="profile")
    
    profile = user_data.value if user_data else {}
    user_name = profile.get("name", "User")
    preferred_lang = profile.get("preferred_language", "English")
    user_role = profile.get("role", "General")

    # Dynamic verbosity rule based on Thread State
    if message_count > 10:
        length_instruction = "The conversation is long. Keep your answers brief (1-2 sentences)."
    else:
        length_instruction = "Provide clear, standard-length answers."

    # Assemble unified System Prompt
    system_prompt = (
        f"You are an AI assistant helping {user_name} (Role: {user_role}).\n"
        f"Always respond in {preferred_lang}.\n"
        f"Instruction: {length_instruction}"
    )

    print(f"\n[DEBUG Middleware] Injected System Prompt:\n{system_prompt}\n")
    return system_prompt


# 3. Create Agent with Middleware, Store, and Checkpointer
agent = create_agent(
    model="gpt-4o-mini",
    middleware=[state_and_store_aware_prompt],
    checkpointer=checkpointer,
    store=store
)


if __name__ == "__main__":
    # --- THREAD 1: First conversation session ---
    config_thread_1 = {
        "configurable": {
            "thread_id": "session_001",  # Short-term thread key
            "user_id": "user_123"        # Long-term store key
        }
    }

    print("=== Execution 1: Thread 001 (First Turn) ===")
    response_1 = agent.invoke(
        {"messages": [{"role": "user", "content": "What is the capital of France?"}]},
        config=config_thread_1
    )
    print("--- AI Output ---")
    print(response_1["messages"][-1].content)


    # --- THREAD 2: Completely new conversation thread for the SAME user ---
    config_thread_2 = {
        "configurable": {
            "thread_id": "session_002",  # New thread (Short-term state resets)
            "user_id": "user_123"        # Same user (Long-term store persists)
        }
    }

    print("\n=== Execution 2: Thread 002 (New Thread, Same User) ===")
    response_2 = agent.invoke(
        {"messages": [{"role": "user", "content": "Recommend a programming topic for me to study."}]},
        config=config_thread_2
    )
    print("--- AI Output ---")
    print(response_2["messages"][-1].content)



"""
[Incoming Request]
       │
       ▼
1.  user_id      = Extract from request.runtime.config ["configurable"]["user_id"]
       │
       ▼
2.  user_data    = Query Store using namespace ("users", user_id)
       │
       ▼
3.  profile      = Extract dictionary payload from user_data (user_data.value)
       │
       ▼
4.  user_role    = Extract specific key from profile (profile.get("role"))
       │
       ▼
[Inject into System Prompt]

"""