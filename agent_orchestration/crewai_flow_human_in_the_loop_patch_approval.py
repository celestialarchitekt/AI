"""
=====================================
CrewAI - human in loop (hil) approval
=====================================
"""

from crewai import Agent, Process, Task, Crew
from crewai.tools import tool
from pydantic import BaseModel
from crewai.flow.flow import Flow, router, listen, start


# -------- State Class
class State_Machine(BaseModel):
    code_snippet: str = ""
    audit_report: str = ""
    patched_code: str = ""


# -------- Tools
@tool("code check tool")
def check_code(code_snippet: str) -> str:
    """Check code for security events"""
    warning_words = ["os.system(", "eval(", "exec(", "shell=True"]
    
    for pattern in warning_words:
        if pattern in code_snippet:
            return "AUDIT: FAIL"
            
    return "AUDIT: PASS"


# --------- Agents
audit_agent = Agent(
    role="Vulnerability_Checker",
    goal="Find security vulnerabilties in the code",
    backstory="You have expertise as a security vulnerability checker in code",
    tools=[check_code],
    llm="gpt-4o-mini"
)

patcher_agent = Agent(
    role="PythonCode_Patcher",
    goal="Write python code patch or fix",
    backstory="You have expertise in writing clean, precise python code for security vulnerabilities",
    llm="gpt-4o-mini"
)


# ----------- Tasks
audit_task = Task(
    description="Audit the code {code} and find security vulnerabilities, create an audit report, use the tool provided",
    expected_output="Clean and precise audit report stating security vulnerability in code, ending with IS_VULNERABLE: Yes or IS_VULNERABLE: No",
    agent=audit_agent
)

patcher_task = Task(
    description="Fixing the code by writing the python patch for {code} using {audit}, return python code only!",
    expected_output="Python code snippet fix",
    agent=patcher_agent
)


# ----------- Crew Instances
audit_crew = Crew(
    agents=[audit_agent],
    tasks=[audit_task],
    process=Process.sequential
)

patch_crew = Crew(
    agents=[patcher_agent],
    tasks=[patcher_task],
    process=Process.sequential
)


# ----------- Flow Class
class TestCode(Flow[State_Machine]):
    
    @start()
    def start_method(self):
        print("\n--- Starting Audit ---")

        target_code = self.state.patched_code if self.state.patched_code else self.state.code_snippet

        response = audit_crew.kickoff(inputs={
            "code": target_code
        })

        self.state.audit_report = str(response.raw)        
        return f"Code Audited with report: {self.state.audit_report}"

    @router(start_method)
    def route_method(self):
        print(f"\nAudit Findings:\n{self.state.audit_report}\n")

        user_input = input("Re-check/Patch the code? [Y/n]: ").strip().lower()
        
        if user_input in ["y", "yes"]:
            return "vulnerable"
        else:
            return "clear"

    @listen("vulnerable")
    def patch_code(self):
        print("\n--- Running Patch Code Fix ---")

        target_code = self.state.patched_code if self.state.patched_code else self.state.code_snippet

        response = patch_crew.kickoff(inputs={
            "code": target_code,
            "audit": self.state.audit_report
        })

        self.state.patched_code = str(response.raw)
        
        # Return to start_method to loop back into audit & human decision
        return self.start_method()

    @listen("clear")
    def pass_code(self):
        final_code = self.state.patched_code if self.state.patched_code else self.state.code_snippet
        return f"\n✅ Code cleared! Final Code Output:\n\n{final_code}"


# ------------- Execution
if __name__ == "__main__":
    vulnerable_code = """
import os

def run_user_cmd(cmd):
    os.system(cmd) # Security flaw: Arbitrary shell command execution
"""
    
    test = TestCode()
    test.state.code_snippet = vulnerable_code

    result = test.kickoff()

    print("\n================ FINAL RESULT ================")
    print(result)