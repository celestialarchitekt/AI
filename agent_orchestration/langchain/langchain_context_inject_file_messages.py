"""
LangChain - Context Engineering: State-Driven Message Injection
"""

from typing import TypedDict, Annotated, Callable
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langgraph.graph.message import add_messages

load_dotenv(override=True)


# 1. Define custom Graph State Schema
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # Required for message history tracking
    uploaded_files: list                    # Custom session state


# 2. Middleware to intercept ModelRequest and inject file context
@wrap_model_call
def inject_file_context(
    request: ModelRequest, 
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    # Read custom state directly off request.state
    state = getattr(request, "state", {}) if hasattr(request, "state") else {}
    uploaded_files = state.get("uploaded_files", [])

    if uploaded_files:
        # Build description list from state
        file_descriptions = [
            f"- {f['name']} ({f['type']}): {f['summary']}"
            for f in uploaded_files
        ]
        
        file_context = (
            "Files available in this conversation:\n"
            + "\n".join(file_descriptions)
            + "\nReference these files when answering questions."
        )

        # Prepend context right before the user's active message
        existing_messages = list(request.messages)
        if existing_messages:
            last_message = existing_messages.pop()
            messages = [
                *existing_messages,
                {"role": "user", "content": f"[System Context]\n{file_context}"},
                last_message
            ]
        else:
            messages = [{"role": "user", "content": file_context}]

        # Apply updated message list to the model payload
        request = request.override(messages=messages)

    # call the AI LLM with the request object
    return handler(request)


# 3. Create Agent with state_schema registered
agent = create_agent(
    model="gpt-4o-mini",
    middleware=[inject_file_context],
    state_schema=AgentState  # Registers 'uploaded_files' in the graph state
)


# 4. Execution
if __name__ == "__main__":
    payload = {
        "messages": [{"role": "user", "content": "What files do I have available?"}],
        "uploaded_files": [
            {
                "name": "Q3_Report.pdf", 
                "type": "PDF", 
                "summary": "Financial summaries for Q3 showing 15% revenue growth."
            },
            {
                "name": "Architecture.png", 
                "type": "Image", 
                "summary": "System diagram of cloud microservices."
            }
        ]
    }

    response = agent.invoke(payload)

    print("------ Final Result ------")
    print(response["messages"][-1].content)