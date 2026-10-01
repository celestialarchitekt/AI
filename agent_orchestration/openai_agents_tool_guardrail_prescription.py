'''
====================
Guardrails - tools 
====================
'''

import asyncio      
import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from pydantic import BaseModel, Field


#load the ENV VARs
load_dotenv(override=True)


# structured output for LLM Agent
class Patient(BaseModel):
    name:str             = Field(description="the name of the patient")
    registration_id:str  = Field(description="registration id of the patient")
    age:int              = Field(description="age of the patient")
    diagnosis:str        = Field(description="disease diagnosed with the patient")
    prescription:str     = Field(description="Give the medical prescription for the problem")
    

@function_tool
async def write_prescription(registration_id:str)->str:
    if not registration_id or registration_id.lower() in ["none", "None", "", "null"]:
        raise ValueError("patient not registered")

    return f"successfully written prescription to patient."


# define the agent
agent1 = Agent(
    name = "Dr_Agent",
    instructions= "You act as a Dr who writes precise and correct prescriptions to patients, use the tool `write_prescription`. \
                   If registration_id is missing, provide an empty string to the tool and set prescription to DENIED.",
    model = "gpt-4o-mini",
    tools = [write_prescription],
    output_type=Patient
)


# define the main, tool exceptions are caught internally by Runner.run(), so no try-except needed
async def main():
    with trace("Tool Guardrail"):
        prompt = "Write a prescription for John Doe, age 40, diagnosed with hypertension. Do not provide a registration ID."
        
        result = await Runner.run(agent1, prompt)
        print(f"Result: {result.final_output}")


# call the main
if __name__ == "__main__":
    asyncio.run(main())