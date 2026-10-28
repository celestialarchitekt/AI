"""
=====
Context Enginerring - long term memory using Knowledge Graphs

====
"""

import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio, MCPServerStdioParams
import asyncio

# load the ENV VARs
load_dotenv(override=True)

# create the dir
memory_dir = os.path.abspath("memory")
os.makedirs(memory_dir, exist_ok=True)
memory_path = os.path.join(memory_dir, "memory.json")

memory_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"], "env": {"MEMORY_FILE_PATH":memory_path}}



# MAIN FUNCTION
async def main():

    async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=60) as server:
        #memory_tools = await server.list_tools()
        #print(memory_tools)

        agent = Agent(
            name = "memoryAgent",
            instructions = "you have access to a knowledge graph memory server. Always check memory for existing context before answering,"
                            "and save important entities/observations to memory when learned.",
            model="gpt-4o-mini",
            mcp_servers=[server]
        )


        # First run: Save information
        result = await Runner.run(agent, "My favorite stock is NVDA and I prefer daily technical indicators.")
        print("=== Run 1 Output ===")
        print(result.final_output)

        print("\n--- Testing Retrieval ---\n")

        # Second run: Retrieve information from memory.json
        result2 = await Runner.run(agent, "What is my favorite stock and what indicators do I prefer?")
        print("=== Run 2 Output ===")
        print(result2.final_output)



# Call MAIN
if __name__ == "__main__":
    asyncio.run(main())