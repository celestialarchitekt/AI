"""
CrewAI - Step 2: Self-Correction Loop with Custom AST Deterministic Tool
"""

# region --- Imports --- 
import ast
from crewai import Agent, Task, Process, Crew
from crewai.tools import tool
from crewai.flow.flow import Flow, listen, start, router
from pydantic import BaseModel
# endregion


# region --- Custom AST Deterministic Tool ---
@tool("Python AST Security Linter")
def analyze_code_ast(code_snippet: str) -> str:
    """Checks Python code for dangerous patterns like os.system, eval, exec, or shell=True."""
    issues = []

    dangerous_patterns = ["os.system(", "eval(", "exec(", "shell=True"]

    for pattern in dangerous_patterns:
        if pattern in code_snippet:
            issues.append(f"Dangerous pattern found: '{pattern}'")

    if issues:
        return "AST_AUDIT_FAILED:\n" + "\n".join(issues)
    return "AST_AUDIT_PASSED: No high-risk patterns detected."
# endregion


# region --- Class State ----
class State(BaseModel):
    code_snippet: str = ""
    audit_report: str = ""
    patched_code: str = ""
    max_retry: int = 3
    retry_count: int = 0
# endregion


# region --- Agent and Tasks ----
# Attached the AST tool to audit_agent
audit_agent = Agent(
    role="Code_Auditor",
    goal="Find security vulnerabilities in the provided code using static AST analysis.",
    backstory="Expertise in finding code vulnerabilities and running deterministic AST static analysis.",
    tools=[analyze_code_ast],
    llm="gpt-4o-mini"
)

patch_agent = Agent(
    role="Code_Patcher",
    goal="Write a patch for the code vulnerability.",
    backstory="Expertise in writing Python code patches/fixes for vulnerabilities.",
    llm="gpt-4o-mini"
)

# Instruct task to utilize the AST tool first
audit_task = Task(
    description=(
        "1. First, run the 'Python AST Security Linter' tool against the code snippet: {code}\n"
        "2. Review the tool output and explain any security issues found.\n"
        "3. End your final response with EXACTLY 'VULNERABILITY: YES' or 'VULNERABILITY: NO'."
    ),
    expected_output="Text report stating vulnerabilities in code and ending with VULNERABILITY: YES or VULNERABILITY: NO",
    agent=audit_agent
)

patch_task = Task(
    description="Write a security patch for code: {code} given the audit report: {audit}. Return ONLY the Python code block.",
    expected_output="Complete python patch fix code",
    agent=patch_agent
)
# endregion


# region ---- Crew Instances -----
audit_crew = Crew(agents=[audit_agent], tasks=[audit_task], process=Process.sequential)
patcher_crew = Crew(agents=[patch_agent], tasks=[patch_task], process=Process.sequential)
# endregion


class SelfCorrect(Flow[State]):
    
    @start()
    def start_method(self):
        print(f"\n--- Starting code audit (Attempt {self.state.retry_count + 1}) ---")

        target_code = self.state.patched_code if self.state.patched_code else self.state.code_snippet
        result = audit_crew.kickoff(inputs={"code": target_code})

        self.state.audit_report = str(result.raw)
        return self.state.audit_report

    @router(start_method)
    def route_method(self):
        print("---- Calculating Route ----")

        if self.state.retry_count >= self.state.max_retry:
            return "escalate"

        if "VULNERABILITY: YES" in self.state.audit_report.upper():
            return "vulnerable"
        else:
            return "clear"

    @listen("clear")
    def pass_code(self):
        print("\n Code passed security verification!")
        final_code = self.state.patched_code if self.state.patched_code else self.state.code_snippet
        return f"Clean code verified:\n\n{final_code}"

    @listen("vulnerable")
    def check_code(self):
        self.state.retry_count += 1
        print(f"Vulnerability found. Writing patch (Retry {self.state.retry_count}/{self.state.max_retry})...")

        target_code = self.state.patched_code if self.state.patched_code else self.state.code_snippet

        response = patcher_crew.kickoff(inputs={
            "code": target_code,
            "audit": self.state.audit_report
        })

        # Save clean patch without Markdown code blocks
        raw_patch = str(response.raw)
        clean_patch = raw_patch.replace("```python", "").replace("```", "").strip()
        self.state.patched_code = clean_patch

        print("Completed patch, re-submitting for verification...")

        # Re-run audit and return final result
        self.start_method()

        if "VULNERABILITY: NO" in self.state.audit_report.upper():
            return self.pass_code()
        else:
            if self.state.retry_count >= self.state.max_retry:
                return self.escalate_code()
            return self.check_code()

    @listen("escalate")
    def escalate_code(self):
        print("\n Exceeded maximum retries!")
        return f"Exceeded maximum tries ({self.state.max_retry}) to fix code.\nLast Audit:\n{self.state.audit_report}"


# region --- Execution ---
if __name__ == "__main__":
    vulnerable_code = """
import os

def run_user_cmd(cmd):
    os.system(cmd) # Security flaw: Arbitrary shell command execution
"""

    selfCorrect = SelfCorrect()
    selfCorrect.state.code_snippet = vulnerable_code

    result = selfCorrect.kickoff()

    print("\n================ FINAL RESULT ================")
    print(result)
# endregion