'''
=============================
Guardrails - Output Example2
============================
'''

import asyncio      
import os
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool, output_guardrail, GuardrailFunctionOutput
from pydantic import BaseModel, Field
from agents.exceptions import OutputGuardrailTripwireTriggered
import requests


#load the ENV VARs
load_dotenv(override=True)

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"



# structured output for LLM Agent
class Patient(BaseModel):
    name:str             = Field(description="the name of the patient")
    registration_id:str  = Field(description="registration id of the patient")
    age:int              = Field(description="age of the patient")
    diagnosis:str        = Field(description="disease diagnosed with the patient")
    prescription:str     = Field(description="Give the medical prescription for the problem")
    




@output_guardrail
async def check_output(ctx, agent, output):
    
    condition_flag=False

    # here output is a pydantic object
    if not output.registration_id or output.registration_id in ["None", "null", "", "none", "NONE"]:
        condition_flag=True

    return GuardrailFunctionOutput(
        output_info = {"reason = cannot issue prescription id"},
        tripwire_triggered=condition_flag
    )

# add a tool for Pushover
@function_tool
def send_pushover(message:str)->str:
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    result = requests.post(pushover_url, data=payload).status_code
    return f"Push notification sent with API status code {result}"



# define the agent
agent1 = Agent(
    name = "Dr_Agent",
    instructions= "You act as a Dr who writes prescriptions to patients.Use the tool send_pushover to send a notification",
    model = "gpt-4o-mini",
    output_type=Patient,
    output_guardrails=[check_output],
    tools = [send_pushover]
)





# MAIN Function
async def main():
    with trace("Guardrail Output 2"):
        max_retries = 2
        prompt = "Write a prescription for John Doe, age 40, diagnosed with hypertension. Do not provide a registration ID."

        for x in range(1,max_retries+1):
            try:
                result = await Runner.run(agent1, prompt)
                print(f"Result: {result.final_output}")
            except OutputGuardrailTripwireTriggered as e:
                print(f"Prescription denied to unregistered patient")
                prompt="Write a prescription for John Doe, age 40, diagnosed with hypertension. Provide a registration ID."


# call the main
if __name__ == "__main__":
    asyncio.run(main())