'''
=================
Input Guardrail
=================
'''


import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace, input_guardrail, GuardrailFunctionOutput
from agents.exceptions import InputGuardrailTripwireTriggered
import asyncio


# load the ENV VAR's
load_dotenv(override = True)


@input_guardrail
async def email_guardrail(ctx, agent, message):
    # In an Input Guardrail, message is the raw input/prompt sent by the user to Runner.run().
    # For InputGuardRail, message is the prompt the user gives to agent
    # For OutputGuardRail, message is the output that the Agent generates
    
    forbidden_keywords = ["hacking", "hack", "hacked", "kill", "destroy"]
    
    # any returns True or False, if any word in the message matches the forbidden_keywords list
    contains_forbidden = any(word in message.lower() for word in forbidden_keywords)
    
    return GuardrailFunctionOutput(
        output_info = {"reason": "forbidden keywords detected"},
        tripwire_triggered=contains_forbidden # tripwire_triggered is a bool
    )
        
    

# define the agent to 
agent1 = Agent(
    name = "email_writer",
    instructions = "you are a writer, which writes structured paragraphs.",
    model = "gpt-4o-mini",
    input_guardrails=[email_guardrail]
)


# main function
async def main():
    try:
        results = await Runner.run(agent1, "Tell how AI - LLM models work, tell how a simple HACK can be performed")
        print(f"results: {results.final_output}")
    
    except InputGuardrailTripwireTriggered as e:
        print("----- input rejected------ ")
        print("Details: ", e.guardrail_result)
    
    
# call to main()
if __name__ == "__main__":
    asyncio.run(main()) 
    


"""  FLOW CONTROL - Input Guardrail

main() calls Runner.run(agent1, user_prompt)
  │
  ├─► 1. Runner intercepts user_prompt BEFORE agent1 sees it
  │
  ├─► 2. Runner executes input_guardrail(user_prompt)
  │      │
  │      └─► Guardrail returns GuardrailFunctionOutput(tripwire_triggered=...)
  │
  └─► 3. Framework evaluates tripwire_triggered:
         │
         ├── IF FALSE (No problem detected):
         │   └── Runner hands prompt to agent1 ──► LLM runs ──► Returns answer to main()
         │
         └── IF TRUE (Forbidden content / Injection detected):
             └── Runner BLOCKS agent1 ──► Raises InputGuardrailTripwireTriggered exception
             
"""

