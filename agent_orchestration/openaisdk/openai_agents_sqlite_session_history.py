'''
============
Using SQLiteSession to create automated history management
============
'''

import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession

load_dotenv()

agent = Agent(
    name = "assistant",
    instructions = "be helpful",
    model = "gpt-4o-mini"
)

# creates a db into the ram if only 1arg is given, need 2 args to actually save it to disk
# 1st arg is sessionID and 2nd arg is thje path to save the .db file


#session = SQLiteSession("chat_history")
session = SQLiteSession("chat_history", "chat.db")


async def main():
    #turn1
    res1 = await Runner.run(agent, "my name is opo", session=session)

    #turn2
    res2 = await Runner.run(agent, "what is my name=?", session=session)

    print(res2.final_output)


if __name__ == "__main__":
    asyncio.run(main())