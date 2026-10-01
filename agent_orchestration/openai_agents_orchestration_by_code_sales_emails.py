'''
=====================
Orchestration by Code
====================
'''

from typing import override
from dotenv import load_dotenv
import asyncio
from agents import Agent, Runner, trace, function_tool, ModelSettings
from openai.types.responses import ResponseTextDeltaEvent
import requests
import os

load_dotenv(override=True)


pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


if pushover_token:
    print("pushover token found")

if pushover_user:
    print("pushover user found")




intro = "you are a sales agent working for ComplAI, a company that provides SaaS tool for ensuring SOC2 compliance and preparing \
        for audits, powered by AI. You write emails"

instruction1 = intro + "your email style is professional, serious, with gravitas."
instruction2 = intro + "your style is witt, engaging and humorous."
instruction3 = intro + "your style is concise, to the point."

message = "write an email as per your style."

# Create the sales agents
agent1 = Agent(
    name = "pro agent",
    instructions = instruction1,
    model = "gpt-4o-mini"
)

agent2 = Agent(
    name = "humorful agent",
    instructions = instruction2,
    model = "gpt-4o-mini"
)

agent3 = Agent(
    name = "executive agent",
    instructions = instruction3,
    model = "gpt-4o-mini"
)


# Create a tool to send pushover notification which the SalesPickerAgent will use.
@function_tool
def send_pushover_notification(message:str) ->str:
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    r = requests.post(pushover_url, data=payload)
    return f"status={r.status_code}, body={r.text}"



# Create a decision/picker LLM - it will select the best email
decision = "You are a sales judge. Your task is to pick the absolute best email from the given options.  \
    MANDATORY RULE: Once you pick the best email, you MUST invoke the `send_pushover_notification` tool  \
    and pass the winning email text into it. Do not just write the email in your text response; you must execute the tool."



sales_picker_agent = Agent(
    name = "judge",
    instructions = decision,
    model = "gpt-4o-mini",
    tools = [send_pushover_notification],
    model_settings=ModelSettings(tool_choice="required"),

)


# main function
async def main():
    with trace("Running MultipleSales Agents"):
        # concurrent execution, invoke the 3 agents 
        results = await asyncio.gather(
            Runner.run(agent1, message),
            Runner.run(agent2, message),
            Runner.run(agent3, message)
        )

    # collect the results in a list
    outputs = [result.final_output for result in results]

    # print the outputs
    for output in outputs:
        print(output + "\n\n\n")

    # combine the outputs into a string for the LLM, AI models take in strings or jsons not python lists!
    # hence .join() is used, it will join all the 3 emails into a single string

    final_output = "\n\n========\n\n".join(outputs)


    prompt_for_judge = (
        f"Here are the 3 final emails:\n\n{final_output}\n\n"
        "Please pick the best email and IMMEDIATELY trigger the send_pushover_notification tool with it."
    )

    # evaluate using judge LLM, invoke the agent
    best_email = await Runner.run(sales_picker_agent, prompt_for_judge)


    #print the final output
    print("best email is: ", best_email.final_output)




# call main function
if __name__ == "__main__":
    asyncio.run(main())