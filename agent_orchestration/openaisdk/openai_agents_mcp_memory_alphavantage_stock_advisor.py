"""
================================================================
AlphaVantage Remote HTTP MCP Server and Memory Stdio MCP Server
===============================================================
"""

import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import (
    MCPServerStdio,
    MCPServerStreamableHttp,
    MCPServerStreamableHttpParams
)

# Load environment variables
load_dotenv(override=True)

# 1. Setup Memory MCP Server (stdio via npx)
memory_dir = os.path.abspath("memory")
os.makedirs(memory_dir, exist_ok=True)
memory_path = os.path.join(memory_dir, "memory.json")

memory_params = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": {"MEMORY_FILE_PATH": memory_path}
}

# 2. Setup Alpha Vantage Remote MCP Server (HTTP Stream)
alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")

if not alpha_vantage_key:
    raise ValueError("ALPHA_VANTAGE_API_KEY is missing from your .env file.")

av_http_params = MCPServerStreamableHttpParams(
    url=f"https://mcp.alphavantage.co/mcp?apikey={alpha_vantage_key}"
)

# MAIN Function
async def main():
    # Connect to local stdio memory server and remote HTTP Alpha Vantage server simultaneously
    async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=60) as memory_server, \
               MCPServerStreamableHttp(params=av_http_params, client_session_timeout_seconds=60) as alpha_server:

        INST = (
            "1. You are a stock advisor agent.\n"
            "2. Use the memory tools to retrieve user preferences.\n"
            "3. Use the Alpha Vantage tools to get live market data for those stocks.\n"
            "4. If there is a mention of any new stock, save it to memory."
        )

        agent = Agent(
            name="stockAdviserAgent",
            instructions=INST,
            model="gpt-4o",
            mcp_servers=[memory_server, alpha_server]
        )

        print("=== Stock Advisor Agent Active (type 'exit' or 'quit' to end) ===\n")

        # LOOP 

        history = []
        while True:
            user_input = input("You: ").strip()

            history.append({"role": "user", "content":user_input})

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue
            
            
            with trace("memory and alpha"):
                result = await Runner.run(agent, history) # result here is a python object, LLMs dont understand it, so to_input_list() is used
                history = result.to_input_list() # adds the complete history as a dictionary for the LLM

            print("\n_________ FINAL OUTPUT ___________")
            print(result.final_output)
            print("-" * 50 + "\n")



# Call main
if __name__ == "__main__":
    asyncio.run(main())