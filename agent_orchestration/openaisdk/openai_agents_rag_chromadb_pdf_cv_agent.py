"""
======
RAG - Retrieval Augmented Generation and Chroma Vector DB

Steps for DB:
1. Create local directory for ChromaDB
2. Create persistent connection client
3. Create collection with automatic embedding handling
======
"""

import os
import asyncio
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

from agents import Agent, Runner, trace, function_tool

# 1. Load Environment Variables
if load_dotenv(override=True):
    print("Environment variables loaded successfully.")

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("Missing OPENAI_API_KEY in .env file.")

openai = OpenAI(api_key=openai_api_key)

# 2. Setup ChromaDB Storage Path
chroma_dir = os.path.abspath("chromadb")
os.makedirs(chroma_dir, exist_ok=True)

# 3. Persistent Client & Collection Initialization
client = chromadb.PersistentClient(path=chroma_dir)

# Automatic embedding function handles vector conversion automatically
embedding_fn = OpenAIEmbeddingFunction(
    model_name="text-embedding-3-small",
    api_key=openai_api_key
)

collection = client.get_or_create_collection(
    name="my_data",
    embedding_function=embedding_fn
)


# 4. Function Tools

@function_tool
def read_pdf(file_path: str = "cv.pdf") -> str:
    """Reads text content page-by-page from a local PDF file."""
    try:
        reader = PdfReader(file_path)
        extracted_text = []
        for idx, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text:
                extracted_text.append(f"--- Page {idx} ---\n{text}")
        
        return "\n\n".join(extracted_text) if extracted_text else "No extractable text found in PDF."
    except Exception as e:
        return f"Error reading PDF file: {str(e)}"


@function_tool
def search_database(query: str, n_results: int = 3) -> str:
    """
    Performs a semantic vector search on the local Chroma database using a plain text query.
    ChromaDB handles vector conversion automatically.
    """
    try:
        # Chroma converts `query_texts` into embeddings automatically
        results = collection.query(query_texts=[query], n_results=n_results)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        if not documents:
            return "No matching records found in database."

        formatted_output = []
        for idx, (doc, meta) in enumerate(zip(documents, metadatas), 1):
            source_info = meta.get("source", "Unknown") if meta else "No Metadata"
            formatted_output.append(f"Match [{idx}] (Source: {source_info}):\n{doc}")

        return "\n\n---\n\n".join(formatted_output)

    except Exception as e:
        return f"Database query error: {str(e)}"


@function_tool
def store_database(document: str, doc_id: str, source: str = "user_input") -> str:
    """
    Stores document text and metadata into the local Chroma vector database.
    
    Args:
        document: The text content/chunk to store.
        doc_id: Unique string identifier for the record.
        source: Optional string label indicating data origin (e.g. 'cv.pdf').
    """
    try:
        # Chroma expects lists for documents, ids, and metadatas
        collection.add(
            documents=[document],
            ids=[doc_id],
            metadatas=[{"source": source}]
        )
        return f"Database updated successfully. Stored document ID: '{doc_id}'."
    except Exception as e:
        return f"Database update failed: {str(e)}"


# 5. Execution Loop
async def main():
    SYSTEM_INSTRUCTIONS = (
        "You are an intelligent RAG Assistant capable of reading PDFs, searching local vector memory, "
        "and storing new insights into ChromaDB.\n\n"
        "WORKFLOW:\n"
        "1. When asked to process documents (like CVs), use `read_pdf` to extract content.\n"
        "2. Save important facts using `store_database`.\n"
        "3. When answering questions about saved knowledge, check the vector database using `search_database`."
    )

    agent = Agent(
        name="RAG_AGENT",
        instructions=SYSTEM_INSTRUCTIONS,
        model="gpt-4o-mini",
        tools=[read_pdf, store_database, search_database]
    )

    print("=== Local Vector RAG Agent Active (type 'exit' to quit) ===\n")
    history = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["quit", "exit"]:
            print("Goodbye!")
            break

        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})

        with trace("rag-cv-agentai"):
            result = await Runner.run(agent, history)

        history = result.to_input_list()

        print("\n------------ RESPONSE --------------\n")
        print(result.final_output)
        print("-" * 35 + "\n")


if __name__ == "__main__":
    asyncio.run(main())