
from langchain.agents import create_agent
from dotenv import load_dotenv
from langchain.tools import tool
from tavily import TavilyClient
import os

# 1. Load environment variables
load_dotenv(override=True)

# 2. Retrieve key
api_key = os.getenv("TAVILY_API_KEY")

print(f"Loaded key")  

# 3. Explicitly pass the key to the client
tavily_client = TavilyClient(api_key=api_key)

@tool
def search(query:str)->str:
    """ searches online for data"""
    
    response = tavily_client.search(query)
    return response
 

agent = create_agent(
    model = "gpt-5.4-mini",
    system_prompt = "you a an experienced financial analyst",
    tools = [search]
)

result=agent.invoke(
    {"messages": [{"role":"user", "content":"tell me financial health of Expleo GmbH. for the year 2026, use search tool {search} if needed"}]}
)

print("--------- RESULT--------------")
print(result["messages"][-1].content_blocks)