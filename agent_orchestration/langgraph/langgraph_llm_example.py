"""
LangGraph - calling OpenAI LLM
"""

import os
from dotenv import load_dotenv

# 1. Load environment variables from the .env file
load_dotenv()

api_key = os.environ.get("LANGSMITH_API_KEY", "")
print("Loaded LangSmith API Key starts with:", api_key[:10] if api_key else "NOT FOUND!")


from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END

# LangSmith automatically detects LANGSMITH_TRACING and LANGSMITH_API_KEY from the environment
llm = ChatOpenAI(model="gpt-4o")


def real_llm_node(state: MessagesState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(MessagesState)
graph.add_node("llm", real_llm_node)
graph.add_edge(START, "llm")
graph.add_edge("llm", END)
graph = graph.compile()


# 2. When you run this, a trace will automatically be sent to your LangSmith dashboard
result = graph.invoke({"messages": [{"role": "user", "content": "Hi, trace this!"}]})
print(result["messages"][-1].content)