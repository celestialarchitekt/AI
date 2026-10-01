"""
BASIC RUNTIME
-------------
LangChain - Runtime provides dependency injection for tools and middleware.
Inject runtime dependencies like database connection, user ID, when invoking the agent.

"""

from dotenv import load_dotenv
from dataclasses import dataclass
from langchain.agents import create_agent

load_dotenv(override=True)


@dataclass
class Context:
    user_name:str


agent = create_agent(
    model = "gpt-4o-mini",
    # context_schema defines the type structure passed at runtime, in this case a class Context
    context_schema = Context
)

if __name__ == "__main__":
    response = agent.invoke(
        {"messages": [{"role": "user", "content": "what is my name?"}]},
        context = Context(user_name = "john smith")
    )

    print(response["messages"][-1].content)