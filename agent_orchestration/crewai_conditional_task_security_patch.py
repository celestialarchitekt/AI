import os
from crewai import Agent, Task, Crew, Process
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput

# 1. Define Agents
auditor = Agent(
    role="Security Auditor",
    goal="Scan code for potential security vulnerabilities.",
    backstory="You are a strict security researcher looking for security flaws.",
    verbose=True
)

patcher = Agent(
    role="Security Patch Engineer",
    goal="Fix identified security vulnerabilities in Python code.",
    backstory="You write robust security patches for vulnerable code.",
    verbose=True
)

publisher = Agent(
    role="Deployment Manager",
    goal="Prepare final release report.",
    backstory="You summarize audit and fix results for deployment.",
    verbose=True
)

# 2. Define Initial Audit Task (note: {code_to_check} placeholder is required
# for the input to actually be substituted in)
audit_task = Task(
    description=(
        "Analyze the following Python code for security vulnerabilities:\n\n"
        "{code_to_check}\n\n"
        "State your findings, and end your response with exactly "
        "'VULNERABLE: Yes' or 'VULNERABLE: No'."
    ),
    expected_output="An audit statement ending with VULNERABLE: Yes or VULNERABLE: No.",
    agent=auditor
)

# 3. Define Condition Evaluator Function
def is_vulnerable(output: TaskOutput) -> bool:
    """Evaluates output from audit_task. Returns True if patching is required."""
    print("---- Result from Audit ----")
    print(output.raw)
    return "VULNERABLE: YES" in output.raw.upper() # checks if VULBERABLE:YES is in output, returns True

# 4. Define Conditional Task (Runs ONLY if condition returns True)
patch_task = ConditionalTask(
    description=(
        "Write a security patch resolving the issues identified in the audit "
        "for this code:\n\n{code_to_check}"
    ),
    expected_output="Patched, secure Python code.",
    condition=is_vulnerable,
    agent=patcher
)

# 5. Final Report Task
report_task = Task(
    description="Compile a final deployment summary based on the audit (and patch, if one was produced).",
    expected_output="Final deployment summary.",
    agent=publisher
)

# 6. Execute Crew
sec_crew = Crew(
    agents=[auditor, patcher, publisher],
    tasks=[audit_task, patch_task, report_task], # this is the order of tasks, be careful ! if using sequential
    process=Process.sequential,
    verbose=False
)

target_code = """
import os
def execute_command(user_input):
    os.system(user_input)  # Dangerous vulnerability
"""

# Kick off the crew with the input code
result = sec_crew.kickoff(inputs={"code_to_check": target_code})

#
print(result)