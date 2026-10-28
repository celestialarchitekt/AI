"""
================================================================
Local Vector DB RAG + Memory MCP + AlphaVantage MCP
================================================================
"""

import os
import asyncio
import shutil
from dotenv import load_dotenv

import chromadb
from openai import OpenAI

from agents import Agent, Runner, trace, function_tool
from agents.mcp import MCPServerStdio, MCPServerStreamableHttp, MCPServerStreamableHttpParams

# 1. Environment Setup & Validation
load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")

if not openai_api_key or not alpha_vantage_key:
    raise ValueError("Missing OPENAI_API_KEY or ALPHA_VANTAGE_API_KEY in .env file.")

openai_client = OpenAI(api_key=openai_api_key)

# 2. Vector DB Setup (ChromaDB + OpenAI Embeddings)
chroma_dir = os.path.abspath("chroma_db")
os.makedirs(chroma_dir, exist_ok=True)

# Initialize local persistent vector store
chroma_client = chromadb.PersistentClient(path=chroma_dir)
vector_collection = chroma_client.get_or_create_collection(name="financial_docs")


def get_embedding(text: str) -> list[float]:
    """Generates a dense vector representation using OpenAI's embedding model."""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def seed_vector_db():
    """Seeds the local vector database with sample financial context if empty."""
    if vector_collection.count() == 0:
        sample_documents = [
            {
                "id": "doc_1",
                "text": "NVIDIA (NVDA) Q2 Earnings Report: Data center revenue grew 154% year-over-year driven by Hopper GPU architecture demand. Blackwell platform sampling is underway with strong customer demand.",
                "metadata": {"ticker": "NVDA", "source": "Q2_Earnings_Release"}
            },
            {
                "id": "doc_2",
                "text": "Tesla (TSLA) Vehicle Deliveries: Full Self-Driving (FSD) Supervised version 12 rollout continues across North America. Energy storage deployment hit a record high megawatt-hour capacity.",
                "metadata": {"ticker": "TSLA", "source": "Q2_Update_Letter"}
            },
            {
                "id": "doc_3",
                "text": "Market Risk Factors: AI hardware supply constraints and export restrictions on advanced semiconductors remain key monitoring risks for tech sector investments.",
                "metadata": {"topic": "Risk_Analysis", "source": "Market_Outlook_2026"}
            }
        ]

        for doc in sample_documents:
            embedding = get_embedding(doc["text"])
            vector_collection.add(
                ids=[doc["id"]],
                embeddings=[embedding],
                documents=[doc["text"]],
                metadatas=[doc["metadata"]]
            )
        print("[Vector DB] Seeded initial financial documents into ChromaDB.")


# Seed the vector database on startup
seed_vector_db()


# 3. Vector DB RAG Search Tool
@function_tool
def local_vector_rag_search(query: str, n_results: int = 3) -> str:
    """
    Search the internal vector database for relevant financial documents, earnings notes, and analysis.
    Use this to retrieve ground-truth internal documentation rather than web searches.
    """

    print("RAG Search Fired...")

    try:
        query_vector = get_embedding(query)
        results = vector_collection.query(
            query_embeddings=[query_vector],
            n_results=n_results
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return "No relevant internal documents found in the vector database."

        formatted_output = ["=== LOCAL VECTOR DB RETRIEVED CONTEXT ==="]
        for idx, (doc, meta) in enumerate(zip(documents, metadatas), 1):
            formatted_output.append(
                f"Document [{idx}]\n"
                f"Source: {meta.get('source', 'Unknown')}\n"
                f"Content: {doc}\n"
            )

        return "\n\n".join(formatted_output)

    except Exception as e:
        return f"Error executing vector search: {str(e)}"


# 4. Setup MCP Parameters
memory_dir = os.path.abspath("memory")
os.makedirs(memory_dir, exist_ok=True)
memory_path = os.path.join(memory_dir, "memory.json")

npx_path = shutil.which("npx") or "npx.cmd"

memory_params = {
    "command": npx_path,
    "args": ["-y", "@modelcontextprotocol/server-memory"],
    "env": {"MEMORY_FILE_PATH": memory_path}
}

av_server_params = MCPServerStreamableHttpParams(
    url=f"https://mcp.alphavantage.co/mcp?apikey={alpha_vantage_key}"
)


# 5. Main Execution Loop
async def main():
    SYSTEM_INSTRUCTIONS = (
        "You are an agentic financial analyst equipped with Local Vector RAG capabilities.\n\n"
        "WORKFLOW RULES:\n"
        "1. **User Preferences**: Check Memory MCP for user favorite stocks or past settings.\n"
        "2. **Real-time Live Data**: Use Alpha Vantage MCP for stock quotes, market metrics, and real-time prices.\n"
        "3. **Internal Domain Knowledge**: Use `local_vector_rag_search` to pull internal document chunks, earnings summaries, and qualitative reports from the local vector DB.\n"
        "4. **Query Refinement**: If vector search results do not contain relevant context, rewrite your query terms and call `local_vector_rag_search` again.\n"
        "5. **Synthesis**: Clearly state live metrics (Alpha Vantage), internal document context (Vector DB), and user preferences (Memory MCP)."
    )

    async with MCPServerStdio(params=memory_params, client_session_timeout_seconds=100) as memory_server, \
               MCPServerStreamableHttp(params=av_server_params, client_session_timeout_seconds=100) as alpha_server:

        agent = Agent(
            name="VectorRAGFinancialAgent",
            instructions=SYSTEM_INSTRUCTIONS,
            model="gpt-4o",
            mcp_servers=[memory_server, alpha_server],
            tools=[local_vector_rag_search]
        )

        print("=== Local Vector RAG Agent Active (type 'exit' to quit) ===\n")
        history = []

        while True:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            history.append({"role": "user", "content": user_input})

            with trace("ChromaDB-RAG-AlpgaVantage"):
                result = await Runner.run(agent, history)

            history = result.to_input_list()

            print("\n------------ RESULT --------------\n")
            print(result.final_output)
            print("-" * 35 + "\n")


if __name__ == "__main__":
    asyncio.run(main())