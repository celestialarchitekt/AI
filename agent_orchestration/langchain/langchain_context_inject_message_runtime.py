"""
LangChain - injecting message during runtime
"""

from dotenv import load_dotenv
from typing import TypedDict, Annotated, Callable
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langgraph.graph.message import add_messages

# load api keys
load_dotenv(override=True)
