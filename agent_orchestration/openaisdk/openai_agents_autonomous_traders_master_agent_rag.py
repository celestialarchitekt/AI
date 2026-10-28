"""
============================================================================
Autonomous Traders - Multiple Agents, Web Search, Local RAG
============================================================================
"""

# region Imports
import asyncio
import os
import shutil
from dotenv import load_dotenv
from openai import OpenAI
from tavily import TavilyClient
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from agents import Agent, Runner, trace, function_tool
from agents.mcp import MCPServerStdio, MCPServerStreamableHttp, MCPServerStreamableHttpParams
# endregion

# region Load ENV Vars & Keys
load_dotenv(override=True)

alpha_key = os.getenv("ALPHA_VANTAGE_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")
openai_key = os.getenv("OPENAI_API_KEY")

if not (alpha_key and tavily_key and openai_key):
    raise ValueError("Missing one or more required API keys in .env file.")

print("All API keys successfully loaded.")
# endregion

# region Setup Memory Params (MCP Server)
memory_dir = os.path.abspath("memory")
os.makedirs(memory_dir, exist_ok=True)
memory_path = os.path.join(memory_dir, "memory.json")

npx_path = shutil.which("npx") or "npx.cmd"

memory_params = {
    "command": npx_path,
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": {"MEMORY_FILE_PATH": memory_path}
}
# endregion

# region Alpha Vantage HttpParams
av_http_params = MCPServerStreamableHttpParams(
    url=f"https://mcp.alphavantage.co/mcp?apikey={alpha_key}"
)
# endregion

# region Setup Chroma DB & Embedding Function
chroma_dir = os.path.abspath("AutonomousTradersDatabase")
os.makedirs(chroma_dir, exist_ok=True)

chroma_client = chromadb.PersistentClient(path=chroma_dir)

openai_ef = OpenAIEmbeddingFunction(
    api_key=openai_key,
    model_name="text-embedding-3-small"
)

collection = chroma_client.get_or_create_collection(
    name="financial_data",
    embedding_function=openai_ef
)
# endregion

# region Create Tavily & OpenAI Clients
tavily_client = TavilyClient(api_key=tavily_key)
openai_client = OpenAI(api_key=openai_key)
# endregion

# region Tavily Function Tool
@function_tool
def tavily_search_tool(query: str) -> str:
    """Performs web search to fetch market news, qualitative analysis, and recent updates."""
    print(f"\n[Tool Execution] Tavily search fired for query: '{query}'")
    try:
        response = tavily_client.search(query=query, max_results=5)
        results = response.get("results", [])
        
        if not results:
            return "No relevant web search results found."

        formatted_results = []
        for idx, item in enumerate(results, 1):
            title = item.get("title", "No Title")
            content = item.get("content", "")
            formatted_results.append(f"Source [{idx}]: {title}\nContent: {content}")

        return "\n\n---\n\n".join(formatted_results)
    except Exception as e:
        return f"Error executing web search: {str(e)}"
# endregion

# region ChromaDB Function Tools
@function_tool
def store_in_vector_db(text_chunk: str, doc_id: str) -> str:
    """Stores incoming qualitative or quantitative text data into the local Chroma vector database."""
    print(f"\n[Tool Execution] Storing chunk '{doc_id}' into local vector DB...")
    try:
        collection.add(
            documents=[text_chunk],
            ids=[doc_id],
            metadatas=[{"source": "autonomous_trader_run"}]
        )
        return f"Successfully stored context '{doc_id}' in vector database."
    except Exception as e:
        return f"Error storing data in ChromaDB: {str(e)}"

@function_tool
def database_tool(query: str) -> str:
    """Queries the local Chroma vector database using semantic RAG search to pull historical context."""
    print(f"\n[Tool Execution] Local Vector RAG database search for: '{query}'")
    try:
        results = collection.query(query_texts=[query], n_results=3)
        documents = results.get("documents", [[]])[0]

        if not documents:
            return "No matching records found in local vector DB."

        return "\n\n---\n\n".join(documents)
    except Exception as e:
        return f"Error querying local database: {str(e)}"
# endregion

# region MAIN FUNCTION
async def main():
    async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=100) as memory_server, \
               MCPServerStreamableHttp(params=av_http_params, client_session_timeout_seconds=100) as alpha_server:

        # 1. Qualitative Search Agent
        web_agent = Agent(
            name="web_search_agent",
            instructions=(
                "You are a qualitative financial market analyst. Use 'tavily_search_tool' to get recent market news, "
                "gossip, earnings reports, and qualitative market updates. Synthesize and return a clean summary."
            ),
            model="gpt-4o-mini",
            tools=[tavily_search_tool]
        )

        # 2. Quantitative Financial Agent
        alpha_vantage_agent = Agent(
            name="alpha_vantage_agent",
            instructions=(
                "You are a quantitative financial analyst. Use the Alpha Vantage MCP tools to fetch live stock quotes, "
                "price metrics, valuation ratios, and financial metrics. Return a clear quantitative breakdown."
            ),
            model="gpt-4o-mini",
            mcp_servers=[alpha_server]
        )

        # 3. Local RAG & Storage Agent
        local_rag_agent = Agent(
            name="local_rag_agent",
            instructions=(
                "You manage local memory and RAG. First, use 'store_in_vector_db' to save qualitative and quantitative data. "
                "Then use 'database_tool' to perform semantic local RAG retrieval and return synthesized historical insights."
            ),
            model="gpt-4o-mini",
            tools=[store_in_vector_db, database_tool]
        )

        # Wrap specialist agents as tools for the master agent
        tool_web_search_agent = web_agent.as_tool(
            tool_name="web_search_agent",
            tool_description="Fetches qualitative market sentiment, news, and search updates."
        )
        tool_alpha_vantage_agent = alpha_vantage_agent.as_tool(
            tool_name="alpha_vantage_agent",
            tool_description="Fetches quantitative financial data, quotes, and metrics via Alpha Vantage."
        )
        tool_local_rag_agent = local_rag_agent.as_tool(
            tool_name="local_rag_agent",
            tool_description="Stores data into local vector DB and executes semantic local RAG queries."
        )

        # Master Orchestrator Agent
        master_agent = Agent(
            name="master_agent",
            instructions=(
                "You are the master orchestrating agent for Autonomous Traders.\n"
                "Follow this sequential workflow:\n"
                "1. Call `web_search_agent` to get recent qualitative news and sentiment.\n"
                "2. Call `alpha_vantage_agent` to fetch quantitative stock price metrics.\n"
                "3. Call `local_rag_agent` to store these insights in the vector DB and run a local RAG query.\n"
                "4. Synthesize all findings into a comprehensive, professionally formatted **Markdown Report**."
            ),
            model="gpt-4o-mini",
            mcp_servers=[memory_server],
            tools=[tool_web_search_agent, tool_alpha_vantage_agent, tool_local_rag_agent]
        )

        user_prompt = "Fetch comprehensive data on NVIDIA (NVDA) stock: quantitative metrics, recent qualitative news, and execute local vector RAG."

        print("\n================ STARTING AGENTIC RUN (STREAMING) ================\n")

        # Execute run with live markdown streaming
        result = await Runner.run(master_agent, user_prompt)
        
        print(result.final_output)

        print("\n\n================ RUN COMPLETED ================")

# endregion

if __name__ == "__main__":
    asyncio.run(main())