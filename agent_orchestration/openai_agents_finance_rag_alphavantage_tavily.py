""" 
______________________________________________
AlphaVantage + Memory + Tavily + Agentic RAG
______________________________________________
"""

import os
import asyncio
import shutil
from dotenv import load_dotenv
from tavily import TavilyClient

from agents import Agent, Runner, trace, function_tool
from agents.mcp import MCPServerStdio, MCPServerStreamableHttp, MCPServerStreamableHttpParams

# Load the ENV VARs
load_dotenv(override=True)

# Load the Keys
alpha_vantage_api = os.getenv("ALPHA_VANTAGE_API_KEY")
tavily_api = os.getenv("TAVILY_API_KEY")

# Check for Keys
if alpha_vantage_api and tavily_api:
    print("Keys found")
else:
    print("Keys not found")

# Create Tavily Client
tavily_client = TavilyClient(api_key=tavily_api)

# Create the memory directory
memory_dir = os.path.abspath("memory")
os.makedirs(memory_dir, exist_ok=True)
memory_path = os.path.join(memory_dir, "memory.json")

# Dynamically resolve npx executable path
npx_path = shutil.which("npx") or "npx.cmd"

# Set the memory params
memory_params = {
    "command": npx_path,
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": {"MEMORY_FILE_PATH": memory_path}  # Fixed env key
}

# Create the alpha-server params
av_server_params = MCPServerStreamableHttpParams(
    url=f"https://mcp.alphavantage.co/mcp?apikey={alpha_vantage_api}"
)

# Create Tavily WebSearch Tool
@function_tool
def web_search(query: str, search_depth: str = "advanced") -> str:
    response = tavily_client.search(
        query=query,
        search_depth=search_depth,
        max_results=5,
        include_answer=True
    )

    results = response.get("results", [])
    
    # DEBUG PRINT: Check exact count returned by Tavily API
    print(f"\n[DEBUG] Tavily retrieved {len(results)} items from web search.")
        
    
    ai_answer = response.get("answer", "")
    
    formatted_output = []
    if ai_answer:
        formatted_output.append(f"=== TAVILY RAG SYNTHESIS ===\n{ai_answer}\n")

    formatted_output.append("=== RETRIEVED SOURCE DOCUMENTS ===")
    for idx, r in enumerate(results, 1):
        formatted_output.append(
            f"Source [{idx}]\n"
            f"Title: {r.get('title')}\n"
            f"URL: {r.get('url')}\n"
            f"Snippet: {r.get('content')}\n"
        )

    return "\n\n".join(formatted_output)

# MAIN FUNCTION
async def main():
    INS = (
    "You are an agentic financial analyst equipped with RAG capabilities.\n"
    "Workflow Rules:\n"
    "1. Check the memory for user preferences for stocks.\n"
    "2. Use AlphaVantage MCP for stock quotes, metrics, and financial data.\n"
    "3. Use the tavily search tool as RAG for market sentiment, broad news, and narrative context.\n"
    "4. Evaluate the retrieved context. If search data is irrelevant or missing, rewrite the query and run tavily search again.\n"
    "5. When presenting web search RAG results, synthesize insights across ALL retrieved sources (up to 5) rather than picking just one, and explicitly cite multiple sources if available.\n"
    "6. Store the retrieved data in the memory using the MCP memory server with timestamps." \
    "7. Format the results clearly with bold metrics, bullet points, and clean structure."
)

    async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=100) as memory_server, \
               MCPServerStreamableHttp(params=av_server_params, client_session_timeout_seconds=100) as alpha_server:
        
        agent = Agent(
            name="Alpha-Memory-Web-RAG_Agent",
            instructions=INS,
            model="gpt-4o",
            mcp_servers=[memory_server, alpha_server],
            tools=[web_search]  # Passed as a list
        )
    
        history = []
        
        while True:
            user_input = input("You: ").strip()
            
            # Fixed .lower() method call
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue

            history.append({"role": "user", "content": user_input})
            
            with trace("AlphaVantage-Memory-TavilyRAG"):
                # Added missing await
                result = await Runner.run(agent, history)

            history = result.to_input_list()
            
            print("\n------------ RESULT --------------\n")
            print(result.final_output)
            print("-" * 35 + "\n")

# Call Main
if __name__ == "__main__":
    asyncio.run(main())