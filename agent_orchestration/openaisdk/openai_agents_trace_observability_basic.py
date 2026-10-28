'''
===============================
Use of trace for observability
===============================
'''

import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace


load_dotenv()


agent = Agent(
    name = "helper",
    instructions = "you are an assistant be humble",
    model = "gpt-4o-mini"
)


async def main():
    with trace("Global Finance Market"):
        result = await Runner.run(agent,"How is the global market doing today?")

    print("Result: ", result.final_output)



if __name__ == "__main__":
    asyncio.run(main())

