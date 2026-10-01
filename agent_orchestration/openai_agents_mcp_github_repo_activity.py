"""
==============
Using the openai sdk agent to connect to a github mcp server and reading the status of a repo

===============
"""


import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio, MCPServerStdioParams

load_dotenv()

async def main():
    # Wrap server arguments inside MCPServerStdioParams
    server_params = MCPServerStdioParams(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN", "")},
        timeout = 30.0
    )

    async with MCPServerStdio(
        name="github_server",
        params=server_params  # <-- Pass via 'params'
    ) as server:

        agent = Agent(
            name="GitHub Assistant",
            instructions="Help the user interact with GitHub repositories.",
            model="gpt-4o-mini",
            mcp_servers=[server]
        )

        result = await Runner.run(agent, "Summarize recent activity for repo https://github.com/celestialarchitekt/cpp-essentials for the user https://github.com/celestialarchitekt")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())