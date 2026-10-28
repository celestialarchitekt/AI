"""
======
CrewAI - memory
=====
"""""

import logging

# Turn on debug logging for HTTP requests and storage
logging.basicConfig(level=logging.INFO)


from crewai import Agent, Crew, Process, Task

# 1. Agents (including backstory)
researcher = Agent(
    role="Researcher",
    goal="Investigate security issues in Python code.",
    backstory="You are an expert cybersecurity researcher specializing in static code analysis.",
    llm="gpt-4o-mini",
)

patcher = Agent(
    role="Patcher",
    goal="Fix code vulnerabilities safely.",
    backstory="You are a senior software engineer who writes secure, clean Python patches.",
    llm="gpt-4o-mini",
)

# 2. Tasks (including expected_output)
task1 = Task(
    description="Analyze code vulnerability: {code}",
    expected_output="A concise summary of identified vulnerabilities.",
    agent=researcher,
)

task2 = Task(
    description="Generate a secure patch for the vulnerabilities found in: {code}",
    expected_output="Corrected and secure Python code snippet.",
    agent=patcher,
)

# 3. Crew with memory enabled
crew = Crew(
    agents=[researcher, patcher],
    tasks=[task1, task2],
    process=Process.sequential,
    memory=True,  # Enables Short-Term, Long-Term, and Entity Memory
    verbose=True,
)

# 4. Kick off
result = crew.kickoff(
    inputs={"code": "import os\ndef run_user_cmd(cmd):\n    os.system(cmd)"}
)

print(result)



"""


You have captured the **core conceptual loop** of how Retrieval-Augmented Generation (RAG) and vector memory work in agentic frameworks like CrewAI.

To make it 100% precise regarding how the data flows behind the scenes, here is a small refinement to two specific steps:

### Refinements to your description

1. **How the Patch Agent receives information:**
The `patcher` agent **does not directly query the Vector DB itself**. Instead, the **Crew orchestrator** handles all database queries *before* invoking the `patcher` agent.
* The Crew takes `task2`'s description, converts it into an embedding query, queries the Vector DB, and retrieves the matching text.
* The Crew then compiles a single, fully enriched prompt containing:
* Patcher's role & backstory
* Task 2 description
* The direct output from Task 1
* The retrieved text memories from the Vector DB


* The Crew hands this complete text prompt to `gpt-4o-mini` (the model powering the `patcher`).


2. **What comes back from the Vector DB:**
Vector databases store vectors alongside their original raw text (metadata). When a vector search is run, the database does not return numbers back to the agent—it uses vector similarity to find the matching vectors, but **returns the corresponding raw text snippets**.

---

### Step-by-Step Flow

```
[User Input: Raw Code]
        │
        ▼
1. Crew invokes Researcher (gpt-4o-mini)
        │
        ▼
2. Researcher outputs Audit Report (Text)
        │
        ├──► [Crew sends Audit Report text to OpenAI Embedding Model]
        │            │
        │            ▼
        │    [Embeddings stored in Vector DB]
        │
        ▼
3. Crew prepares Task 2 for Patcher:
        ├──► Sends Task 2 prompt to OpenAI Embedding Model
        ├──► Queries Vector DB using query vector
        └──► Vector DB returns matching text snippets
        │
        ▼
4. Crew combines (Task 2 Prompt + Task 1 Output + Retrieved DB Text)
   and sends the compiled prompt to Patcher (gpt-4o-mini)
        │
        ▼
5. Patcher generates secure code patch
        │
        ▼
[Final Result Returned to User]

```


"""