"""
========================
LangChain - Guardrails - filter and validate inputs and outputs to build a safer AI system.
1. deterministic guardrails - write the rules and code
2. model based guardrails - llms evaluate 
========================
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain.tools import tool


load_dotenv(override=True)



# create Agent
agent = create_agent(
    model = "gpt-4o-mini",
    middleware = [
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input = True
        ),

        PIIMiddleware(
            "credit_card",
            strategy = "mask",
            apply_to_input = True
        ),

        PIIMiddleware(
            "api_key",
            detector = r"sk-[a-zA-Z0-9]{32}",
            strategy = "block",
            apply_to_input = True
        )

    ]
)



# Run Code
if __name__ == "__main__":
    response = agent.invoke({
        "messages" : [{"role": "user", "content": "My email is john.doe@example.com and card is 5105-1051-0510-5100"}]
    })


    last_message = response["messages"][-1]

    # Extract text from the first dictionary in content_blocks
    if hasattr(last_message, "content_blocks") and last_message.content_blocks:
        text_content = last_message.content_blocks[0]["text"]
        print(text_content)