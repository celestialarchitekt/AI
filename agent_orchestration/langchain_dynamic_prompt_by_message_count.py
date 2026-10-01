"""
====================================================
LangChain - State : short term memory using thread
====================================================
"""


from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.checkpoint.memory import InMemorySaver

# load ENV VARs
load_dotenv(override=True)


@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    message_count = len(request.messages)
    print(f"[DEBUG] Current thread message count: {message_count}")

    if message_count > 10:
        return "You are a concise assistant. Provide answers in 1 line only."
    else:
        return "You are a detailed, helpful assistant. Answer fully."

agent = create_agent(
    model="gpt-4o-mini",
    middleware=[state_aware_prompt],
    checkpointer=InMemorySaver()
)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "munich_session"}}

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "What is the capital of Bavaria?"}]},
        config=config
    )

    print("\n--------- FINAL RESULT -----------")
    print(response["messages"][-1].content)