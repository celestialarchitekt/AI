from typing import Any
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    HumanInTheLoopMiddleware,
    PIIMiddleware,
    hook_config,
)
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langgraph.types import Command

# Load ENV VARs
load_dotenv(override=True)


@tool
def send_email(body: str, recipient: str, subject: str) -> str:
  """Send an email with subject: {subject} and body {body} to the recipient"""
  return f"email sent with subject: {subject} and body: {body} to {recipient}"


# Input Check Class
class ContentFilterMiddleware(AgentMiddleware):
  """block requests/prompts containing banned keywords"""

  def __init__(self, banned_keywords: list[str]):
    super().__init__()
    self.banned_keywords = [kw.lower() for kw in banned_keywords]

  @hook_config(can_jump_to=["end"])
  def before_agent(
      self, state: AgentState, runtime: Runtime
  ) -> dict[str, Any] | None:
    # if message list is empty
    if not state.get("messages"):
      return None

    first_message = state["messages"][0]

    # Handle string or message object content safely
    content = ""
    if hasattr(first_message, "content"):
      content = str(first_message.content).lower()
    elif isinstance(first_message, dict):
      content = str(first_message.get("content", "")).lower()

    # check for banned keywords
    for keyword in self.banned_keywords:
      if keyword in content:
        return {
            "messages": [{
                "role": "assistant",
                "content": "unable to process request",
            }],
            "jump_to": "end",
        }

    return None


# Create Agent
agent = create_agent(
    model="gpt-4o-mini",
    tools=[send_email],
    middleware=[
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]+",
            strategy="block",
            apply_to_input=True,
        ),
        HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),
        ContentFilterMiddleware(banned_keywords=["hack", "exploit", "malware"]),
    ],
    checkpointer=InMemorySaver(),
)

# memory thread
config = {"configurable": {"thread_id": "001"}}

# Run command
if __name__ == "__main__":
  # 1. Trigger the agent action

    result1 = agent.invoke(
        {"messages": [{"role": "user", "content": "tell me to hack a website"}]},
        config=config,
    )

    print("---- FIRST RESPONSE ----")
    last_msg1 = result1["messages"][-1]
    print(
        last_msg1.content
        if getattr(last_msg1, "content", None)
        else f"Tool Call Requested: {getattr(last_msg1, 'tool_calls', None)}"
    )