'''
===========================================================================================================
We look at the use of 'to_input_list() - used to manage history manually' function with the OpenAI SDK Agent
==========================================================================================================
'''

import asyncio
from agents import Runner, Agent
from dotenv import load_dotenv

# load the OpenAI Key
load_dotenv()

agent = Agent(
    name = "Math Tutor",
    instructions = "help with math problems",
    model = "gpt-4o-mini" 
)



async def main():
    #turn 1
    result = await Runner.run(agent, "what is  2*3?")
    print("agent: ", result.final_output)

    #1. grab the conversation history from turn1
    # to_input_list() returns the entire conversation history in a list
    history = result.to_input_list()

    #2. append the new user follow-up
    history.append({"role":"user", "content": "now multiply that answer by 10"})

    #3. pass this history as new user follow-up
    result2 = await Runner.run(agent, input=history)
    print("agent: ", result2.final_output)

    #4. append new history again
    history.append({"role": "user", "content": "divide the answer by 100"})

    #5. pass it again to model
    result3 = await Runner.run(agent, input = history)
    print("agent: ", result3.final_output)




if __name__ == "__main__":
    asyncio.run(main())