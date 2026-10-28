
"""
============================================================================================
Sandbox - E2B, here we run the sync lib of the Sandbox, although Sandbox also comes in Async
============================================================================================
"""

import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from e2b_code_interpreter import Sandbox
import os

# load the most recent ENV VARs
load_dotenv(override=True)

e2b_api_key     = os.getenv("E2B_API_KEY")
openai_api_key  = os.getenv("OPENAI_API_KEY")


if e2b_api_key:
    print(f"found e2b key, it starts with {e2b_api_key[:5]}")
else:
    print("e2b key not found")
    
if openai_api_key:
    print(f"found openai key, starts with {openai_api_key[:5]}")
else:
    print("openai key not found")


@function_tool
# sync version of the sandbox lib
def execute_python_in_sandbox(code:str)->str:
        try:
            with Sandbox.create() as sandbox:
                # execute the code which the Agent created in the sandbox
                execution = sandbox.run_code(code)
                return execution.text or "Success"
        except Exception as e:
            print(f"\n[DEBUG] E2B Failed with: {e}\n")  # <-- Print the exact network error
            raise ValueError(f"E2B Sandbox execution failed: {e}")


        if execution.error:
            raise ValueError(
                f"Code Execution Failed:\n"
                f"Error Name: {execution.error.name}\n"
                f"Error Value: {execution.error.value}\n"
                f"Traceback:\n{execution.error.traceback}"
            )

        output_parts = []
        
        if execution.text:
            output_parts.append("------ STDOUT ----- \n", {execution.text})
            
        if execution.results:
            for idx, res in enumerate(execution.results):
                output_parts.append("-- RESULT [{idx}] --- \n{res}")
                
        # this function returns a string, Runner.run() hands over this result back to LLM not the user!
        return "\n".join(output_parts) if output_parts else "Code executed successfully with no output."
        
        

#agent
agent1 = Agent(
    name = "data analyst",
    instructions= "You are a data analyst. When asked to perform calculations or data processing, "
        "write Python code and execute it using the `execute_python_in_sandbox` tool. "
        "Do not guess calculations—always verify them using the sandbox.",
    model = "gpt-4o-mini",
    tools= [execute_python_in_sandbox]
)


# MAIN
async def main():
    with trace("sandbox"):
        prompt = "Write a Python script to calculate the first 10 numbers in the Fibonacci sequence " \
            "and print their sum. Execute it in the sandbox."
            
        result = await Runner.run(agent1, prompt)
        print("----- FINAL ANSWER ------")
        print(result.final_output)
        
        
# CALL MAIN
if __name__ == "__main__":
    asyncio.run(main())
    
    
    
    
    
"""
============ FLOW CONTROL ==========================================================================="
Phase 1: Local Script Setup & Tool Registration
    1. Script Initiation: You run python .\sandbox.py in your local PowerShell terminal.

    2. Schema Extraction: The @function_tool decorator inspects your local Python function execute_python_in_sandbox(code: str) and converts its name, docstring, and type hints into an OpenAI-compatible JSON Tool Schema.

    3. Agent Registration: Agent(tools=[execute_python_in_sandbox]) attaches this JSON tool schema to the agent instance so the LLM knows the function exists and what parameters (code: str) it requires.

    4. Runner Dispatch: You execute result = Runner.run(agent1, prompt) locally, which hands control to the framework's execution loop.


Phase 2: First LLM Request & Code GenerationAPI 
    1. API Call: Runner.run makes an HTTP request to the OpenAI API containing:The user prompt ("Calculate the first 10 Fibonacci numbers").The registered JSON Tool Schema for execute_python_in_sandbox.

    2. LLM Decision: gpt-4o-mini evaluates the prompt, realizes it needs precise math execution, writes the Python script string, and decides to call your tool.

    3. API Response (OpenAI->Local): OpenAI sends back a JSON response instructing Runner.run to call your function, containing a tool_call_id and the generated code payload: {"code": "def fibonacci(n): ..."}.


Phase 3: Tool Dispatch & Remote Sandbox Execution

    1. Local Function Invocation: Runner.run intercepts the API instruction and locally calls your function: execute_python_in_sandbox(code="...").
    
    2. Sandbox Provisioning: Inside your local function, calling Sandbox.create() sends a network request to E2B Cloud servers to spin up an isolated Firecracker MicroVM.
    
    3. Code Submission: Your local function calls sandbox.run_code(code), transmitting the Python code string over a WebSocket/HTTP connection to the E2B cloud sandbox.
    
    4. Remote Execution: E2B runs the Python code inside the isolated MicroVM.
    
    5. Execution Result Returned: The sandbox captures standard output (stdout), errors (stderr), or display results, and transmits an Execution object back over the network to your local function.
    
    6. Local Output Formatting: Your function evaluates execution.error, execution.text, or execution.results, constructs a string (e.g., "\n".join(output_parts)), closes the E2B session, and returns that text string to Runner.run().



========================================================================
"""