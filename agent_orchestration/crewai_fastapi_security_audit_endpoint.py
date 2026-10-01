"""
=================
CrewAI - FastAPI
=================
"""

from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Process, Agent, Task, Crew

# FastAPI
app = FastAPI()


class CodeRequest(BaseModel):
    code: str


audit_agent = Agent(
    role = "Security Auditor",
    goal = "Identify security risks in Python code",
    backstory = "You are an expert in finding security vulnerabilities",
    llm = "gpt-4o-mini"
)


patch_agent = Agent(
    role = "Code Patcher",
    goal = "Fix vulnerabilities in Python code",
    backstory = "You write secure Python code patches.",
    llm = "gpt-4o-mini"
)

audit_task = Task(
    description = "Audit the following code for vulnerabilities: {code}",
    expected_output = "Short description of vulnerability or 'No issues found'.",
    agent = audit_agent
)


patch_task = Task(
    description = "Write a secure Python patch for the code: {code}",
    expected_output = "Only the corrected Python code snippet",
    agent = patch_agent
)


security_crew = Crew(
    agents = [audit_agent,patch_agent],
    tasks = [audit_task,patch_task],
    process = Process.sequential
)

#define the fastAPI endpoint
@app.post("/audit")
def audit_code(request: CodeRequest):
    response = security_crew.kickoff(inputs={"code":request.code})

    return {
        "status": "success",
        "result": str(response.raw)
    }

@app.get("/")
def read_root():
    return {"status": "online", "message": "CrewAI app is running."}


@app.get("/status")
def get_system_status():
    return{
        "active_agents" : ["security auditor", "code patcher"],
        "llm_model"     : "gpt-4o-mini",

    }




# run the code
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)