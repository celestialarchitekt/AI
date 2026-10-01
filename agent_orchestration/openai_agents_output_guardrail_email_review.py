'''
===============
Guardrails - are the safety mechanism for AI/LLMs, they check for input, outputs and control the execution of the LLM.
Here we see output guardrail in action
================
'''

import os
from dotenv import load_dotenv
from agents import Agent, trace, Runner, output_guardrail, GuardrailFunctionOutput, function_tool
from pydantic import BaseModel, Field
import asyncio
from agents.exceptions import OutputGuardrailTripwireTriggered

# load the keys
load_dotenv(override=True)


# for structured output
class EmailReview(BaseModel):
    is_professional: bool       = Field(description="Whether the email is professional and appropriate")
    number_of_sentences: int    = Field(description="The number of sentences in the body of the email, not including the greeting and signature")
    contains_placeholders: bool = Field(description="Whether the email contains placeholders for personalization")


# checker agent
checker = Agent(name="Checker", instructions="You review potential sales emails", model="gpt-4o-mini", output_type=EmailReview)



# create the guardrail
@output_guardrail
async def email_guardrail(ctx, agent, message):
    # Runner.run() calls the checker agent to evaluate , message here contains the email drafted by agent1
    result = await Runner.run(checker, message, context=ctx.context)
    
    #returns a python object , structured output as defined by the class, otherwise it would be a string.
    review = result.final_output
    
    # check if placeholder is present and if email is professional or not
    is_problem = review.contains_placeholders or not review.is_professional
    
    # if tripwire = True, then an exception is raised, else the email is passed to the main()
    # returns an object to Runner.run() in main()
    return GuardrailFunctionOutput(output_info = {"review": review}, tripwire_triggered=is_problem)
    


# Agent to create an email
agent1 = Agent(
    name = "email_creator",
    instructions = "You write a sales email regarding the 2027 financial situation for German Automotive. "
        "CRITICAL: Do NOT use bracketed placeholders like [Name] or [Company]. "
        "Invent realistic names and company details directly in the text.",
    model = "gpt-4o-mini",
    output_guardrails = [email_guardrail]
)


async def main():
    max_retries = 3
    prompt = "write a sales email"
    
    for attempt in range(1, max_retries+1):
    
        try:
            # Runner.run() invokes the Agent1 and the guardrail, it receives an OpenAI SDK object from GuardrailFunctionOutput()
            # if that object is TRUE then exception runs, if FALSE then the message that Agent1 created goes to main()
            result = await Runner.run(agent1, prompt)
            print("-------- email approved ----------")
            # returns the email
            print(result.final_output)
            
        except OutputGuardrailTripwireTriggered as e:
            print(" ------------ email declined -----------")
            print("--- Email Rejected by Guardrail! ---")
            # returns the exception with email
            print("Guardrail result:", e.guardrail_result)
            prompt = """
                "write a sales email. CRITICAL: The previous draft contained bracketed placeholders "
                "or was unprofessional. Do NOT use placeholders like [Name]. Use realistic fake names."
            """
            
    
    
if __name__ == "__main__":
    asyncio.run(main())
    
    
""" FLOW CONTROL - Output GuardRail

main() calls Runner.run(agent1, user_prompt)
  │
  ├─► 1. Runner invokes agent1 (LLM generates draft response)
  │
  ├─► 2. Runner intercepts agent1's generated text
  │
  ├─► 3. Runner executes output_guardrail(draft_text)
  │      │
  │      ├─► 4. output_guardrail (optionally runs checker agent)
  │      │
  │      └─► 5. Returns GuardrailFunctionOutput(tripwire_triggered=...)
  │
  └─► 6. Runner evaluates tripwire_triggered:
         │
         ├── IF FALSE (No problem / Safe output):
         │   └── Runner releases agent1's draft ──► Delivered to main() as result.final_output
         │
         └── IF TRUE (Placeholders, unprofessional, unsafe output):
             └── Runner BLOCKS agent1's draft ──► Raises OutputGuardrailTripwireTriggered in main()


"""