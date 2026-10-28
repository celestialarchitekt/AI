import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStdio, MCPServerStdioParams

load_dotenv()

async def main():
    env = os.environ.copy()

    # Use the active NPM package 'yahoo-finance-mcp-server'
    server_params = MCPServerStdioParams(
        command="npx",
        args=["-y", "-p", "yahoo-finance2", "yahoo-finance-mcp"],  # -p installs the package, then runs the "yahoo-finance-mcp" bin from it
        env=env,
        timeout=120.0
    )

    async with MCPServerStdio(name="yahoo_finance", params=server_params) as server:
        agent = Agent(
            name="BMW Financial Analyst",
            instructions=(
                 "You are an equity research analyst. Use the yahoo-finance2 MCP tools to "
                "retrieve data for BMW (BMW.DE).\n\n"
                "When calling quoteSummary, only use these valid module names: "
                "price, summaryDetail, financialData, incomeStatementHistory, "
                "incomeStatementHistoryQuarterly, earnings, earningsTrend, "
                "defaultKeyStatistics, balanceSheetHistory, cashflowStatementHistory. "
                "There is NO module called 'financials' — use 'financialData' or "
                "'incomeStatementHistory' for revenue/income data instead.\n\n"
                "Retrieve key financial statements, metrics, and current stock information "
                "to analyze BMW's performance and projected growth."
            ),
            model="gpt-4o-mini",
            mcp_servers=[server]
        )

        # Note: BMW trades on the German XETRA exchange under ticker 'BMW.DE'
        query = "Fetch the financial summary, P/E ratio, and recent revenue for BMW (BMW.DE) and summarize key findings."
        
        result = await Runner.run(agent, query)
        print("\n--- AGENT RESPONSE ---")
        print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())