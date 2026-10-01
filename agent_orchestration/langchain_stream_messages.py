"""
==============================================
LangChain - Streaming using stream()
===============================================
"""

from dotenv import load_dotenv
from langchain.tools import tool
from langchain.agents import create_agent
from uuid import uuid4
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv(override=True)

agent = create_agent(
    model = "gpt-4o-mini",
    checkpointer=InMemorySaver()
)

config = {"configurable": {"thread_id": str(uuid4())}}

# run code, stream data
if __name__ == "__main__":
    stream = agent.stream(
        {"messages": [{"role":"user", "content": "Tell me about financial health of BMW" }]},
        
        config=config,
        stream_mode="messages"
    )
    
    for message_chunk, metadata in stream:
        if message_chunk.content:
            print(message_chunk.content, end="", flush=True)
            
