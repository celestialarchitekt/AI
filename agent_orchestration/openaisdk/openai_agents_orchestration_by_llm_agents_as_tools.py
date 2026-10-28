"""
=====================
Orchestrating by LLM - invoking agents by a planning agent using agents as tools.

The alternative — agents-as-tools — does return control:
Agents-as-tools keep an orchestrator in charge: the orchestrator calls a specialist as a regular tool call and incorporates the result into its own response. This is architecturally closer to what CrewAI's hierarchical process does with a manager agent, or what your "LLM orchestration" approach was likely doing — one agent stays in charge, delegates a sub-task, gets a return value, and continues
=====================
"""

import os
import asyncio
#from typing import override
import requests
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool

# load the ENV VAR
load_dotenv(override=True)


#region Pushover
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


if pushover_token:
    print("pushover token found")

if pushover_user:
    print("pushover user found")
#endregion



intro = "You are an analyst. You are to create an email, telling the user about the latest financial market 2027 for Germany." 
instruction1 = intro + "You are precise, analytical, concise, no fluff."
instruction2 = intro + "You are manipulative, clever, cunning and deceptive."


#region Create Agents 
agent1 = Agent(
    name = "precise_agent",
    instructions = instruction1,
    model = "gpt-4o-mini",

)


agent2 = Agent(
    name = "clever_agent",
    instructions = instruction2,
    model = "gpt-4o-mini"
)
#endregion



#region Tool Pushover Notification
@function_tool # tells OpenAI this python function is to be used as a tool
def send_pushover(message:str)->str:
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    r = requests.post(pushover_url, data=payload)
    return f"status={r.status_code}, body={r.text}"

#endregion



#region Create tools for each Agent, agents wrappeda as tools
tool_precise_agent = agent1.as_tool(tool_name="email_writer_precise", tool_description="Use this tool to write a precise, concise, and analytical email about the German financial market.")
tool_clever_agent = agent2.as_tool(tool_name="email_writer_clever", tool_description="Use this tool to write a clever and manipulative email about the German financial market.")

tools = [tool_clever_agent, tool_precise_agent, send_pushover]
#endregion



#region Create the Planning Agent which will invoke the 2 agents
agent3 = Agent(
    name = "manager_agent",
    instructions = "you are a manager, you will implement the task given to you step by step precisely.",
    model = "gpt-4o-mini",
    tools = tools
)

task = "Follow the steps: \
        1. Use both email_write_precise and email_writer_clever to draft an email. \
        2. Review the draft, return both emails in result. \
        3. Select the best one morally and send that email over a pushover notification using the tool send_pushover."


#endregion


#region MAIN Function
async def main():
    with trace("Planning Agent Invoking"):
        result = await Runner.run(agent3, task)

    print(f"Result is: {result.final_output}")



#endregion


if __name__ == "__main__":
    asyncio.run(main())