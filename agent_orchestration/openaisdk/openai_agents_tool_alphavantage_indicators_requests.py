import os
import requests
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

load_dotenv(override=True)

@function_tool
def get_alpha_vantage_indicator(symbol: str, function: str = "SMA", interval: str = "daily", time_period: int = 50) -> str:
    """
    Fetches technical indicators or sentiment data from Alpha Vantage.
    
    Args:
        symbol: Ticker symbol (e.g., 'NVDA', 'AAPL').
        function: Alpha Vantage function (e.g., 'SMA', 'EMA', 'RSI', 'NEWS_SENTIMENT').
        interval: Time interval ('daily', 'weekly', 'monthly').
        time_period: Number of data points for calculation (e.g., 50).
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    
    if not api_key:
        return "Error: ALPHA_VANTAGE_API_KEY environment variable is not set."

    if function == "NEWS_SENTIMENT":
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={api_key}"
    else:
        url = (
            f"https://www.alphavantage.co/query?function={function}&symbol={symbol}"
            f"&interval={interval}&time_period={time_period}&series_type=close&apikey={api_key}"
        )

    response = requests.get(url).json()

    # Parse Indicator Data
    key = f"Technical Analysis: {function}"
    if key in response:
        time_series = response[key]
        latest_date = list(time_series.keys())[0]
        latest_value = time_series[latest_date][function]
        return f"As of {latest_date}, {symbol} {time_period}-{interval} {function} is {latest_value}."

    # Parse News/Sentiment Data
    if "feed" in response:
        feed = response["feed"][:3]
        summaries = [f"- {item['title']} (Sentiment: {item['overall_sentiment_label']})" for item in feed]
        return f"Recent News Sentiment for {symbol}:\n" + "\n".join(summaries)

    return f"API Response: {response}"

async def main():
    agent = Agent(
        name="alphaVantageBot",
        instructions="Analyze daily stock price movements, technical indicators, and volume trends.",
        model="gpt-4o-mini",
        tools=[get_alpha_vantage_indicator]
    )

    result = await Runner.run(
        agent, 
        "What is the 50-day moving average and current news sentiment for NVIDIA (NVDA)?"
    )
    print("\n--- AGENT RESPONSE ---")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())