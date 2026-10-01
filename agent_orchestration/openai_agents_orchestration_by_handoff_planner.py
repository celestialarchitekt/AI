"""
=============
Orchestration by Handoff

With handoffs: control does not come back.
A handoff transfers conversation ownership — the receiving agent responds directly to the user, and the new agent fully takes over rather than returning a result to an orchestrator. Once agent A hands off to agent B, it's as though the new agent takes over the conversation, seeing the entire previous history. Agent A is essentially out of the loop from that point forward — there's no automatic mechanism for B to finish and hand back to A. If you need A to regain control, you'd have to explicitly register a handoff back to A from B, and rely on B's model correctly deciding to invoke it.


==============
"""

import requests
from dotenv import load_dotenv
from agents import Agent, trace, Runner, function_tool
import asyncio
import os

# load the ENV VARs
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

# Prompts for Agents
intro = "You are an automotive analyst who gives the market trend for Chinese vs German automotive for the year 2027. "
ins1 = intro + "You provide the analysis in a clever, cunning, and manipulative manner."
ins2 = intro + "You provide the analysis in a stupid, dumb, and slow manner."

# create the Agents
agent_1 = Agent(
    name="clever_agent",
    instructions=ins1,
    model="gpt-4o-mini"
)

agent_2 = Agent(
    name="dumb_agent",
    instructions=ins2,
    model="gpt-4o-mini"
)


# Pushover Function
@function_tool
def send_pushover(message: str) -> str:
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    r = requests.post(pushover_url, data=payload)
    return f"status={r.status_code}, body={r.text}"


# Email Picker Agent with the Pushover tool
email_picker_agent = Agent(
    name="email_picker",
    instructions=(
        "You have received the conversation containing two email drafts. "
        "Review them, pick the single most moral and ethically correct email, "
        "and call the `send_pushover` tool EXACTLY ONCE with that one email. Do not call send_pushover twice!."
    ),
    model="gpt-4o-mini",
    tools=[send_pushover]
)

# Tools & Handoffs, agent1 and agent2 wrapped as tools
tool1 = agent_1.as_tool(tool_name="clever_tool", tool_description="Drafts an email in a clever, cunning, manipulative manner.")
tool2 = agent_2.as_tool(tool_name="dumb_tool", tool_description="Drafts an email in a stupid, dumb, slow manner.")
tools = [tool1, tool2]

# Handoffs (Passing to email_picker_agent for final decision and sending)
handoffs = [email_picker_agent]

# Prompt for planner agent
task = (
    "You are the planning agent. Follow these steps:\n"
    "1. Draft 2 emails using the tools clever_tool and dumb_tool.\n"
    "2. Call and give the control using handoffs to email_picker_agent, with the two generated emails. "
    "The handoff agent will select one and send it using pushover"
)

# Planner Agent
agent_planner = Agent(
    name="planner",
    instructions="You are the planner agent. You use clever_tool and dumb_tool to draft emails, and then hand them off to the email_picker agent.",
    model="gpt-4o-mini",
    tools=tools,
    handoffs=handoffs
)


# Main function
async def main():
    with trace("orchestrating by handoff"):
        result = await Runner.run(agent_planner, task)

    print(f"Result is: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())