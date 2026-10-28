'''
=============
Adding Tool
=============
'''

from dis import Instruction
import os
import requests
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool


load_dotenv()

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


if pushover_token:
    print("pushover token found")

if pushover_user:
    print("pushover user found")




# decorator used to tell OpenAI this is a tool!
@function_tool
# tells openAI that this function takes a message of type string and return a string
def push_tool(message: str) -> str:
    payload = {"user": pushover_user, "token": pushover_token, "message": message}

    result = requests.post(pushover_url, data=payload).status_code
    return f"Push notification sent with API status code {result}"

# create the Agent
agent = Agent(
    name = "assistant",
    instructions = "reply to the users message",
    model = "gpt-4o-mini",
    tools = [push_tool]

)


async def main():
    with trace("Push notification with OpenAI SDK Tool"):
        result = await Runner.run(agent, "Send a push notification: Hi I am Mayank")
    
    print("Result:", result.final_output)




if __name__ == "__main__":
    asyncio.run(main())