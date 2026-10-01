'''
==============================
Created multiple agents using OPENAI SDK and use Pythons Asyncio Library
==============================
'''

import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner

load_dotenv()


us_agent = Agent(
    name = "US specialist",
    instructions = "provide concise market insights focussed on USA financial market",
    model = "gpt-4o-mini"
)

eu_agent = Agent(
    name = "EU specialist",
    instructions = "provide concise market insights focussed on EU financial market",
    model = "gpt-4o-mini"
)


tech_agent = Agent(
    name = "tech agent",
    instructions = "provide concise insights on the tech sector around the world",
    model = "gpt-4o-mini"
)


async def main():
    print("Firing off 3 agent requests concurrently...")

    # concurrent execution, it fires off all 3 requests at the same time and waits for OpenAI API to respond
    results = await asyncio.gather(
        Runner.run(us_agent, "what is 2027 market outlook for USA?"),
        Runner.run(eu_agent, "what is 2027 market outlook for EU?"),
        Runner.run(tech_agent, "what is the global tech scene in 2027?")
    )


    '''
    Sequential Execution:
    res1 = await Runner.run(us_agent, ...)
    res2 = await Runner.run(eu_agent, ...)
    res3 = await Runner.run(tech_agent, ...)

    here, Python will wait for each reques to complete before it fires off the next request
    '''

    print("\n Priting results: ",results)

    # process the RunResult objects
    us_res, eu_res, tech_res = results

    print("\n ----- US -----")
    print(us_res.final_output)


    print("\n ------ EU -----")
    print(eu_res.final_output)

    print("\n ---- Tech -----")
    print(tech_res.final_output)



if __name__ == "__main__":
    asyncio.run(main())