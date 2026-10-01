import os
import json
import requests
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv(override=True)

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

if ALPHA_VANTAGE_API_KEY:
    print("loaded alpha vantage api key")


@tool
def alphaVantage(symbol: str) -> str:
    """Find daily stock values for a given stock ticker symbol (e.g., 'BMW.DEX', 'IBM', 'AAPL')."""
    print(f"alpha vantage tool invoked for symbol: {symbol}...")
    
    # Clean symbol format if colon was passed by mistake
    formatted_symbol = symbol.replace(":", ".")
    
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={formatted_symbol}&apikey={ALPHA_VANTAGE_API_KEY}'
    
    r = requests.get(url)
    
    # requests over HTTP , gets a python dictionary
    data = r.json() 
    
    # Return JSON string so the LLM gets full structured output, it serializes dict or list to a string
    return json.dumps(data)


agent = create_agent(
    model="gpt-4o-mini",
    system_prompt="You are an experienced financial analyst. You have access to the tool 'alphaVantage' to find stock values.",
    tools=[alphaVantage],
)


if __name__ == "__main__":
  
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user", 
                    "content": "Find the latest daily stock values for BMW using symbol BMW.DEX"
                }
            ]
        }
    )
    
    print("--------- RESULT -----------")
    print(result["messages"][-1].content)
    
    
""" 
json.dumps() - converts a python dict or list to a string, LLMs only understand strings or JSON
json.loads() - takes a string and converts to python dictionary
"""