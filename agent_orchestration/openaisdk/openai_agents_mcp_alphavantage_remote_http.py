import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams

load_dotenv(override=True)

async def main():
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise ValueError("Missing ALPHA_VANTAGE_API_KEY in environment variables.")

    # Official Alpha Vantage Remote MCP Server Endpoint
    server_params = MCPServerStreamableHttpParams(
        url=f"https://mcp.alphavantage.co/mcp?apikey={api_key}"
    )

    async with MCPServerStreamableHttp(name="alpha_vantage", params=server_params) as server:
        agent = Agent(
            name="AlphaVantageBot",
            instructions="Analyze daily stock price movements and technical indicators.",
            model="gpt-4o-mini",
            mcp_servers=[server]
        )

        result = await Runner.run(
            agent, 
            "What is the 50-day moving average for NVDA?"
        )
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())