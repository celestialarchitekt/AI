"""
_______

Create a MCP server with multiple tools 

______
"""

import os
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv
import requests


load_dotenv(override=True)

mcp = FastMCP("AlphaVantageServer")

ALPHA_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


@mcp.tool
async def get_moving_average(symbol:str, time_period:int, interval:str)->str:
    if not ALPHA_KEY:
        print("key not found")
        return -1

    url = "https://www.alphavantage.co/query"

    params={
        "function"    : "SMA",
        "symbol"      : symbol.upper(),
        "interval"    : interval,
        "time_period" : time_period,
        "series_type" : "close",
        "apikey"      : ALPHA_KEY
    }

    # makes the GET call to the server
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

    key = "Technical Analysis: SMA"

    if key in data:
        latest_date= list(data[key].keys())[0]
        sma_value  = data[key][latest_date]["SMA"]
        return f"As of {latest_date}, the {time_period}-{interval} SMA for {symbol.upper()} is {sma_value}"


    return f"failed to retrieve data: {data}"


@mcp.tool
def get_stock_price(symbol:str)->str:
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_KEY}"

    # requests is a sync lib , hence async and await not used
    response =  requests.get(url)
    data =  response.json()

    key="Global Quote"
    if key in data and data[key]:
        quote = data[key]
        price = quote.get("05. price", "N/A")
        change_pct = quote.get("10. change percent", "N/A")

        return f"current stock price for {symbol.upper()} is {price} (Daily Change:{change_pct})"

    return f"Failed to get stock price data: {data}"


if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
    
