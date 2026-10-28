"""
_____

MCP Client

____
"""



import os
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerSse, MCPServerSseParams
from dotenv import load_dotenv


load_dotenv(override=True)


async def main():
    server_params= MCPServerSseParams(
        url = "http://localhost:8000/sse"   
    )

    instructions = (
        "You are a helpful financial assistant. Use your tools to fetch live stock prices "
        "and technical indicators when requested, and perform accurate mathematical calculations."
    )
   

    async with MCPServerSse(name="client alphaVantage", params=server_params) as server:
        agent = Agent(
            name = "alpha client",
            instructions=instructions,
            model="gpt-4o-mini",
            mcp_servers=[server]
        )
        user_prompt = (
            "Check the current price of NVDA and its 50-day SMA. "
            "Calculate how far (in percentage) the current price is above or below its 50-day SMA, "
            "and tell me whether the stock is currently trading in bullish or bearish territory relative to that average."
        )

        result = await Runner.run(agent, user_prompt)
        print (result.final_output)



if __name__ == "__main__":
    asyncio.run(main())



"""
------------------------------------
Control Flow - MCP Client and Server
------------------------------------
[ Runner.run() starts ]
       │
       ├─► 1. Send query + tool definitions to LLM
       │
       ├─► 2. LLM responds: "Call `get_sma(symbol='NVDA', time_period='50')`"
       │
       ├─► 3. Client sends SSE request to localhost:8000
       │         └─► Server calls Alpha Vantage API
       │         └─► Server formats string & returns it via SSE
       │
       ├─► 4. Client sends tool result back to LLM
       │
       └─► 5. LLM generates final response -> assigned to `result`
[ Runner.run() finishes ]


-----------------------------------

1. Initialization (Tool Discovery): When MCPServerSse connects to http://localhost:8000/sse, the client framework immediately asks the server for its tool schemas via JSON-RPC (tools/list).

2. Prompt Submission: Runner.run() takes your user prompt plus the schemas of all discovered server tools and sends them together in the first API call to the LLM.

3. Tool Selection: The LLM inspects the prompt, sees that it needs market data, and picks get_stock_price and get_moving_average from the schema list. It returns a request: "Execute tool X with argument Y."

4. Server Execution: The client receives the model's request and sends an SSE request to your local MCP server. The server executes the Python function, fetches data from Alpha Vantage, and sends the raw response back to the client.

5. Tool Result Loop: The client feeds the server's raw data back to the LLM. (If more tool calls are needed, steps 3–5 repeat).

6. Synthesis: The LLM processes the data, performs the math, formats the natural language response, and returns the final answer to Runner.run().

-------------------------------------

This is what a tool schema, looks like. server returns this to the client.

{
  "name": "get_moving_average",
  "description": "Fetch Simple Moving Average (SMA) for a given stock symbol.",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g. NVDA)"
      },
      "time_period": {
        "type": "integer",
        "default": 50
      },
      "interval": {
        "type": "string",
        "default": "daily"
      }
    },
    "required": ["symbol"]
  }
}


{
  "name": "get_moving_average",
  "description": "Fetch Simple Moving Average (SMA) for a given stock symbol.",
  "parameters": {
    "type": "object",
    "properties": {
      "symbol": {
        "type": "string",
        "description": "Stock ticker symbol (e.g., NVDA, AAPL)"
      },
      "time_period": {
        "type": "integer",
        "default": 50,
        "description": "Number of periods to calculate the SMA over"
      },
      "interval": {
        "type": "string",
        "default": "daily",
        "description": "Time interval between data points (e.g., daily, weekly, 5min)"
      }
    },
    "required": [
      "symbol"
      "time_period",
      "interval"
    ]
  }
}


LLMs only understand text or json, this schema is sent to the LLM with the prompt


------------------------------------
"""