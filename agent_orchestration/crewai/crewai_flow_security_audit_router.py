import os
from crewai import Agent, Task, Crew, Process
from crewai.flow.flow import Flow, start, listen, router
from pydantic import BaseModel


# ==========================================
# 1. Define State Management (Pydantic)
# ==========================================
class SecurityState(BaseModel):
    code_snippet: str = ""
    audit_report: str = ""
    is_vulnerable: bool = False
    patched_code: str = ""
    final_status: str = ""


# ==========================================
# 2. Define Agents & Tasks
# ==========================================
# Agents
auditor_agent = Agent(
    role="Security Auditor",
    goal="Scan code for security vulnerabilities thoroughly.",
    backstory="You are an expert security researcher specializing in identifying unsafe code practices.",
    verbose=True
)

patcher_agent = Agent(
    role="Security Patch Engineer",
    goal="Fix identified vulnerabilities in Python code.",
    backstory="You write secure, production-grade security patches for vulnerable code snippets.",
    verbose=True
)

# Tasks
audit_task = Task(
    description="Analyze this Python code: {code_to_check}. State 'VULNERABLE: Yes' if insecure, or 'VULNERABLE: No' if safe.",
    expected_output="An audit assessment ending with VULNERABLE: Yes or VULNERABLE: No.",
    agent=auditor_agent
)

patch_task = Task(
    description="Review the vulnerable code {code_to_check} and the audit report {audit_report}, then rewrite it into secure Python code.",
    expected_output="Fully patched and secure Python code snippet.",
    agent=patcher_agent
)

# Crews
audit_crew = Crew(agents=[auditor_agent], tasks=[audit_task], process=Process.sequential)
patch_crew = Crew(agents=[patcher_agent], tasks=[patch_task], process=Process.sequential)


# ==========================================
# 3. Define the CrewAI Flow (Conditional Routing)
# ==========================================
class SecurityPipelineFlow(Flow[SecurityState]):

    @start()
    def run_security_audit(self):
        """Step 1: Execute the security audit crew."""
        print("\n[FLOW START] Executing Security Audit Crew...")
        
        # Kick off the audit crew with the initial input code
        result = audit_crew.kickoff(inputs={"code_to_check": self.state.code_snippet})
        self.state.audit_report = str(result.raw)
        
        # Determine vulnerability flag
        if "VULNERABLE: YES" in self.state.audit_report.upper():
            self.state.is_vulnerable = True
        else:
            self.state.is_vulnerable = False
            
        return self.state.is_vulnerable

    @router(run_security_audit)
    def route_vulnerability_status(self):
        """Step 2: Dynamically route flow execution based on vulnerability state."""
        if self.state.is_vulnerable:
            print("[ROUTER] Vulnerability detected -> Routing to Security Patch Crew...")
            return "trigger_patch_crew"
        else:
            print("[ROUTER] Code is clean -> Routing to Direct Approval...")
            return "trigger_direct_approval"



    @listen("trigger_patch_crew")
    def execute_patch(self):
        """Path A: Triggered when vulnerabilities are found."""
        print("\n[PATH A] Executing Security Patch Crew...")
        
        patch_result = patch_crew.kickoff(
            inputs={
                "code_to_check": self.state.code_snippet,
                "audit_report": self.state.audit_report
            }
        )
        
        self.state.patched_code = str(patch_result.raw)
        self.state.final_status = f"CODE PATCHED SUCCESSFULLY:\n\n{self.state.patched_code}"
        return self.state.final_status

    @listen("trigger_direct_approval")
    def approve_deployment(self):
        """Path B: Triggered when no vulnerabilities are found."""
        print("\n[PATH B] Code passed security audit without issues.")
        self.state.final_status = "CODE APPROVED FOR PRODUCTION: No security vulnerabilities identified."
        return self.state.final_status


# ==========================================
# 4. Run the Pipeline
# ==========================================
if __name__ == "__main__":
    # Test Code 1: Vulnerable code (Triggers Path A)
    vulnerable_code = """
import os
def run_user_cmd(cmd):
    os.system(cmd) # Security flaw: Arbitrary shell command execution
"""

    print("============================================")
    print("      RUNNING TEST 1: VULNERABLE CODE       ")
    print("============================================")
    
    flow_instance = SecurityPipelineFlow()
    flow_instance.state.code_snippet = vulnerable_code
    
    # Run the flow
    final_output = flow_instance.kickoff()
    
    print("\n--------------------------------------------")
    print("FINAL FLOW RESULT:")
    print("--------------------------------------------")
    print(final_output)